import json
import logging
import os
import time
import uuid
from flask import Flask, g, jsonify, request

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('loja-veloz')

def create_app(service):
    app = Flask(service)
    app.config['SERVICE_NAME'] = service
    counters = {'requests': 0, 'errors': 0}

    @app.before_request
    def before():
        g.started = time.monotonic()
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())

    @app.after_request
    def after(response):
        counters['requests'] += 1
        if response.status_code >= 500:
            counters['errors'] += 1
        response.headers['X-Request-ID'] = g.request_id
        logger.info(json.dumps({'service': service, 'request_id': g.request_id,
            'method': request.method, 'path': request.path, 'status': response.status_code,
            'duration_ms': round((time.monotonic()-g.started)*1000, 2)}))
        return response

    @app.get('/health')
    def health():
        return jsonify(status='ok', service=service)

    @app.get('/ready')
    def ready():
        return jsonify(status='ready', service=service)

    @app.get('/metrics')
    def metrics():
        from flask import Response
        data = (f'# TYPE veloz_http_requests_total counter\n'
                f'veloz_http_requests_total{{service="{service}"}} {counters["requests"]}\n'
                f'# TYPE veloz_http_errors_total counter\n'
                f'veloz_http_errors_total{{service="{service}"}} {counters["errors"]}\n')
        return Response(data, mimetype='text/plain; version=0.0.4')
    return app

def database_url():
    return os.getenv('DATABASE_URL', 'postgresql://veloz:devlocal@localhost:5432/veloz')

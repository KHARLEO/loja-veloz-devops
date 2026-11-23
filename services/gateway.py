import os
import requests
from flask import g, jsonify, request, Response
from services.common import create_app

ROUTES = {'pedidos': 'PEDIDOS_URL', 'estoque':'ESTOQUE_URL'}
DEFAULT_PATHS = {'pedidos': 'pedidos', 'estoque': 'itens'}

def create_gateway():
    app = create_app('gateway')

    @app.route('/api/<service>', defaults={'path': ''}, methods=['GET','POST','PUT','DELETE'])
    @app.route('/api/<service>/<path:path>', methods=['GET','POST','PUT','DELETE'])
    def proxy(service, path):
        if service not in ROUTES:
            return jsonify(error='Serviço desconhecido'), 404
        base = os.environ.get(ROUTES[service], f'http://{service}:8080')
        url = f'{base}/{path or DEFAULT_PATHS[service]}'
        try:
            res = requests.request(request.method, url, params=request.args,
                data=request.get_data(), headers={'Content-Type':request.headers.get('Content-Type','application/json'),
                'X-Request-ID':g.request_id}, timeout=8)
            return Response(res.content, res.status_code,
                content_type=res.headers.get('Content-Type','application/json'))
        except requests.RequestException:
            return jsonify(error='Serviço temporariamente indisponível'), 503

    @app.get('/')
    def root():
        return jsonify(projeto='Loja Veloz', endpoints=['/api/pedidos', '/api/estoque'])
    return app

from flask import jsonify, request
from services.common import create_app

def create_pagamentos():
    app = create_app('pagamentos')

    @app.post('/cobrar')
    def cobrar():
        body = request.get_json(silent=True) or {}
        if not isinstance(body, dict) or not body.get('pedido_ref'):
            return jsonify(error='pedido_ref obrigatório'),400
        # Integração externa simulada: não processa dinheiro real.
        if body.get('simular_falha') is True:
            return jsonify(status='recusado'),402
        return jsonify(status='aprovado', transacao=f"demo-{body['pedido_ref']}"),200
    return app

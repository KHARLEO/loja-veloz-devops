import psycopg
from flask import jsonify, request
from services.common import create_app, database_url

INITIAL_ITEMS = [('camiseta', 20), ('fone', 15), ('mouse', 30)]

def create_estoque():
    app = create_app('estoque')

    @app.get('/itens')
    def listar():
        try:
            with psycopg.connect(database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT sku, quantidade FROM estoque ORDER BY sku')
                    return jsonify([{'sku': sku, 'quantidade': q} for sku,q in cur.fetchall()])
        except psycopg.Error:
            return jsonify(error='Banco indisponível'), 503

    @app.post('/reservar')
    def reservar():
        body = request.get_json(silent=True) or {}
        if not isinstance(body, dict):
            return jsonify(error='Informe sku e quantidade positiva'), 400
        sku, quantidade = body.get('sku'), body.get('quantidade')
        if not isinstance(sku, str) or type(quantidade) is not int or quantidade < 1:
            return jsonify(error='Informe sku e quantidade positiva'), 400
        try:
            with psycopg.connect(database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute('UPDATE estoque SET quantidade = quantidade - %s WHERE sku = %s AND quantidade >= %s RETURNING quantidade', (quantidade,sku,quantidade))
                    row = cur.fetchone()
                    if row is None:
                        return jsonify(error='Item inexistente ou estoque insuficiente'), 409
            return jsonify(sku=sku, reservado=quantidade), 200
        except psycopg.Error:
            return jsonify(error='Banco indisponível'), 503

    @app.post('/devolver')
    def devolver():
        # Endpoint interno de compensação; em produção requer autenticação entre serviços.
        body = request.get_json(silent=True) or {}
        if not isinstance(body, dict):
            return jsonify(error='Dados inválidos'), 400
        sku, quantidade = body.get('sku'), body.get('quantidade')
        if not isinstance(sku,str) or type(quantidade) is not int or quantidade < 1:
            return jsonify(error='Dados inválidos'), 400
        try:
            with psycopg.connect(database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute('UPDATE estoque SET quantidade = quantidade + %s WHERE sku = %s RETURNING quantidade',(quantidade,sku))
                    if cur.fetchone() is None:
                        return jsonify(error='Item inexistente'),404
            return jsonify(status='devolvido'),200
        except psycopg.Error:
            return jsonify(error='Banco indisponível'),503
    return app

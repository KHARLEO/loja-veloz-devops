import os
import uuid
import psycopg
import requests
from flask import g, jsonify, request
from services.common import create_app, database_url

ESTOQUE = lambda: os.getenv('ESTOQUE_URL', 'http://estoque:8080')
PAGAMENTOS = lambda: os.getenv('PAGAMENTOS_URL', 'http://pagamentos:8080')

def validate_order(body):
    return (isinstance(body, dict) and isinstance(body.get('sku'), str) and bool(body['sku'].strip())
        and type(body.get('quantidade')) is int and body['quantidade'] > 0)

def create_pedidos():
    app = create_app('pedidos')

    @app.get('/pedidos')
    def listar():
        try:
            with psycopg.connect(database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT id, sku, quantidade, status FROM pedidos ORDER BY criado_em DESC LIMIT 100')
                    return jsonify([dict(id=str(i),sku=s,quantidade=q,status=st) for i,s,q,st in cur.fetchall()])
        except psycopg.Error:
            return jsonify(error='Banco indisponível'),503

    @app.post('/pedidos')
    def criar():
        body = request.get_json(silent=True) or {}
        if not validate_order(body):
            return jsonify(error='Informe sku e quantidade inteira positiva'),400
        ref = str(uuid.uuid4())
        headers = {'X-Request-ID': g.request_id}
        try:
            reserved = requests.post(ESTOQUE()+'/reservar', json={'sku':body['sku'], 'quantidade':body['quantidade']},headers=headers,timeout=5)
            if reserved.status_code != 200:
                return jsonify(error='Não foi possível reservar estoque', detalhe=reserved.json()), reserved.status_code
            try:
                payment = requests.post(PAGAMENTOS()+'/cobrar', json={'pedido_ref':ref,'simular_falha':body.get('simular_falha_pagamento',False)},headers=headers,timeout=5)
                if payment.status_code != 200:
                    return jsonify(error='Pagamento não aprovado; compensação solicitada', compensacao=_devolver(body,headers)), 402
                with psycopg.connect(database_url()) as conn:
                    with conn.cursor() as cur:
                        cur.execute('INSERT INTO pedidos(id,sku,quantidade,status) VALUES (%s,%s,%s,%s)',(ref,body['sku'],body['quantidade'],'confirmado'))
                return jsonify(id=ref,sku=body['sku'],quantidade=body['quantidade'],status='confirmado'),201
            except (requests.RequestException, psycopg.Error):
                return jsonify(error='Falha após reserva; compensação solicitada', compensacao=_devolver(body,headers)),503
        except requests.RequestException:
            return jsonify(error='Estoque indisponível'),503

    return app

def _devolver(body,headers):
    try:
        result = requests.post(ESTOQUE()+'/devolver',json={'sku':body['sku'],'quantidade':body['quantidade']},headers=headers,timeout=5)
        return 'concluida' if result.ok else 'falhou; requer reconciliacao'
    except requests.RequestException:
        return 'falhou; requer reconciliacao'

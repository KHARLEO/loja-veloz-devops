import unittest
from unittest.mock import patch
from services.estoque import create_estoque
from services.pedidos import create_pedidos, validate_order
from services.pagamentos import create_pagamentos
from services.gateway import create_gateway

class LojaVelozTests(unittest.TestCase):
    def test_validacao_pedido(self):
        self.assertTrue(validate_order({'sku':'mouse','quantidade':2}))
        self.assertFalse(validate_order({'sku':'mouse','quantidade':0}))
        self.assertFalse(validate_order({'sku':'mouse','quantidade':True}))

    def test_pagamento_simulado(self):
        client = create_pagamentos().test_client()
        self.assertEqual(client.post('/cobrar',json={'pedido_ref':'abc'}).status_code,200)
        self.assertEqual(client.post('/cobrar',json={'pedido_ref':'abc','simular_falha':True}).status_code,402)

    def test_gateway_health(self):
        self.assertEqual(create_gateway().test_client().get('/health').status_code,200)

    def test_pedidos_invalidos(self):
        self.assertEqual(create_pedidos().test_client().post('/pedidos',json={'sku':'x','quantidade':-1}).status_code,400)

    def test_json_que_nao_e_objeto(self):
        endpoints = [
            (create_pedidos(), '/pedidos'),
            (create_pagamentos(), '/cobrar'),
            (create_estoque(), '/reservar'),
            (create_estoque(), '/devolver'),
        ]
        for app, path in endpoints:
            with self.subTest(service=app.name, path=path):
                self.assertEqual(app.test_client().post(path, json=['invalido']).status_code, 400)

    @patch('services.gateway.requests.request')
    def test_rotas_anunciadas_e_correlacao(self, upstream):
        upstream.return_value.status_code = 200
        upstream.return_value.content = b'[]'
        upstream.return_value.headers = {'Content-Type': 'application/json'}
        client = create_gateway().test_client()
        with patch.dict('os.environ', {'PEDIDOS_URL': 'http://pedidos:8080', 'ESTOQUE_URL': 'http://estoque:8080'}):
            for path, url in [
                ('/api/pedidos', 'http://pedidos:8080/pedidos'),
                ('/api/estoque', 'http://estoque:8080/itens'),
                ('/api/pedidos/pedidos', 'http://pedidos:8080/pedidos'),
            ]:
                with self.subTest(path=path):
                    response = client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(upstream.call_args.args, ('GET', url))
                    self.assertEqual(
                        upstream.call_args.kwargs['headers']['X-Request-ID'],
                        response.headers['X-Request-ID'],
                    )

if __name__ == '__main__':
    unittest.main()

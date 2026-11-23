import os
from services.gateway import create_gateway
from services.pedidos import create_pedidos
from services.pagamentos import create_pagamentos
from services.estoque import create_estoque

factories = {'gateway':create_gateway, 'pedidos':create_pedidos,
             'pagamentos':create_pagamentos, 'estoque':create_estoque}
service = os.environ.get('SERVICE', 'gateway')
if service not in factories:
    raise ValueError(f'Serviço inválido: {service}')
app = factories[service]()

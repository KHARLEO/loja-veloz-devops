CREATE TABLE IF NOT EXISTS estoque (
    sku TEXT PRIMARY KEY,
    quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
);
INSERT INTO estoque (sku, quantidade) VALUES ('camiseta', 20), ('fone', 15), ('mouse', 30)
ON CONFLICT (sku) DO NOTHING;
CREATE TABLE IF NOT EXISTS pedidos (
    id UUID PRIMARY KEY,
    sku TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    status TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

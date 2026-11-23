# Roteiro de pitch — até 4 minutos

**0:00–0:35 | Problema.** "A Loja Veloz enfrenta falhas em deploys, dificuldades para escalar e pouca visibilidade. Nossa proposta usa microsserviços e automação DevOps."

**0:35–1:20 | Arquitetura.** Mostre gateway, serviços Pedidos, Estoque e Pagamentos, além do PostgreSQL. Diga que pagamentos são simulados. Mostre pastas `services`, `db` e `compose.yaml`.

**1:20–2:10 | Demo.** Execute `docker compose ps`, mostre `GET /api/estoque/itens`, crie pedido com POST e consulte pedidos. Mostre logs ou resposta. Se não funcionar, não simule uma execução: explique o bloqueio.

**2:10–3:05 | Kubernetes/CI.** Abra `k8s/02-pedidos.yaml`, aponte probes, Rolling Update e HPA, depois `.github/workflows/ci.yml` e seus passos de teste e publicação.

**3:05–3:45 | Observabilidade/segurança.** Mostre `/metrics`, `docker compose logs`, secrets sem commit, usuário não-root e Terraform. Explique a diferença entre `X-Request-ID` e tracing OpenTelemetry completo.

**3:45–4:00 | Fechamento.** "O MVP prioriza reprodutibilidade, validações antes da publicação e caminho de evolução para produção."

Depois: publicar no YouTube, inserir link no README e nos dois PDFs, e conferir o acesso ao repositório.

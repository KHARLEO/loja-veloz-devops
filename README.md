# Loja Veloz — MVP Cloud DevOps

Projeto acadêmico: gateway HTTP, pedidos, pagamentos simulados, estoque e PostgreSQL. **Não executa pagamentos reais.**

## Requisitos

Docker Desktop + Docker Compose. Para Kubernetes opcionalmente kubectl, cluster local e metrics-server. Para CI: repositório GitHub.

## Iniciar localmente (Windows PowerShell)

```powershell
Copy-Item .env.example .env
# Edite POSTGRES_PASSWORD no arquivo .env antes de iniciar

docker compose up --build -d
docker compose ps
```

API: http://localhost:8080/ ; saúde: http://localhost:8080/health

```powershell
Invoke-RestMethod http://localhost:8080/api/estoque/itens
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/pedidos/pedidos -ContentType 'application/json' -Body '{"sku":"mouse","quantidade":2}'
Invoke-RestMethod http://localhost:8080/api/pedidos/pedidos
```

Para simular pagamento recusado, envie `{"sku":"fone","quantidade":1,"simular_falha_pagamento":true}` ao mesmo POST. O sistema tenta devolver a reserva. **Importante:** esta compensação síncrona não oferece garantia transacional diante de falhas de rede; o ambiente real exigiria mensageria/outbox e reconciliador idempotente.

```powershell
docker compose logs -f pedidos
docker compose down             # mantém volume de dados
docker compose down -v          # apaga dados locais (cuidado)
```

## Testes sem Docker

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Kubernetes (exemplo local, não produção pronta)

1. Habilite Kubernetes no Docker Desktop ou use kind/minikube. Instale metrics-server se quiser ver HPA funcionando.
2. Ajuste as quatro referências `ghcr.io/SEU_USUARIO/loja-veloz-*:dev` nos YAMLs para imagens reais publicadas no GHCR (CI publica tags pelo SHA do commit). Alternativamente, carregue imagens locais no cluster, com nomes iguais aos YAMLs.
3. Crie namespace e ConfigMap: `kubectl apply -f k8s/00-namespace-config.yaml`.
4. Crie SQL ConfigMap: `kubectl -n loja-veloz create configmap veloz-init-sql --from-file=init.sql=db/init.sql`.
5. Crie Secret **sem commitá-lo**: `kubectl -n loja-veloz create secret generic veloz-db --from-literal=password=SENHA_FORTE --from-literal=database-url=postgresql://veloz:SENHA_FORTE@db:5432/veloz`. Evite caracteres especiais sem codificação em URLs; em produção use secret manager e injeção segura.
6. Execute `kubectl apply -f k8s/01-postgres.yaml` e aguarde `kubectl -n loja-veloz rollout status statefulset/db`.
7. Execute `kubectl apply -f k8s/02-estoque.yaml -f k8s/02-pagamentos.yaml -f k8s/02-pedidos.yaml -f k8s/02-gateway.yaml`.
8. Execute `kubectl apply -f k8s/03-hpa.yaml -f k8s/04-networkpolicy.yaml`. Depois `kubectl -n loja-veloz port-forward svc/gateway 8080:8080`.
9. Inspecione: `kubectl -n loja-veloz get pods,svc,hpa` e `kubectl -n loja-veloz rollout status deploy/pedidos`.

**Observação:** `k8s/00-namespace-config.yaml` e `terraform/main.tf` são duas opções para criar o mesmo namespace; use **uma** delas para gerenciar o namespace, evitando disputa de ownership. PostgreSQL no cluster é demonstrativo (não há backup gerenciado, HA ou criptografia de volume configurada). Para produção, preferir banco gerenciado com backups.

## CI/CD

Workflow `.github/workflows/ci.yml` executa compilação, testes, validação Compose e, em push para `main`, build/push de 4 imagens versionadas por SHA no GitHub Container Registry (GHCR). Não implanta em produção automaticamente: a etapa CD de deploy fica como **proposta** a ser protegida por aprovação, autenticação OIDC e rollback. Nunca comitar tokens/senhas.

## Observabilidade e escala

- `GET /health`, `GET /ready`: probes básicas; endpoints **não** testam dependências externas, portanto readiness é limitada.
- `GET /metrics`: contadores básicos Prometheus de requisições e erros; demonstrativo, sem coleta/armazenamento configurados.
- Logs: linhas JSON com serviço, `request_id`, rota, duração e status, visíveis em `docker compose logs`.
- Tracing: propagação de `X-Request-ID` para correlação inicial; **não** é tracing distribuído completo. Em produção adicionar OpenTelemetry Collector e Jaeger/Tempo, spans e context propagation.
- Rolling Update `maxSurge:1` / `maxUnavailable:0`, readiness/liveness e HPA 2–6 réplicas da API pedidos (CPU 70%). HPA requer métricas funcionais no cluster.
- Segurança: usuário não-root, FS de aplicação somente leitura, seccomp, capabilities removidas, NetworkPolicy demonstrativa e segredo K8s externo ao repositório. A NetworkPolicy atual restringe acesso ao banco, mas não isola toda a malha.

## Referências oficiais

- Exemplo concreto: Online Boutique — GoogleCloudPlatform: https://github.com/GoogleCloudPlatform/microservices-demo
- Docker Compose: https://docs.docker.com/compose/gettingstarted/
- Kubernetes HPA: https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/
- Kubernetes Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- OpenTelemetry: https://opentelemetry.io/docs/concepts/observability-primer/
- Terraform: https://developer.hashicorp.com/terraform/docs

## Entrega acadêmica

Relatório teórico (2–3 páginas), relatório prático (3–6 páginas) e pitch até 4 minutos na pasta `entrega/`. Substituir os campos abaixo após publicação:

- Repositório GitHub: **[COLOCAR LINK]**
- Vídeo YouTube (pode ser não listado): **[COLOCAR LINK]**

**Verificação desta revisão:** seis testes Python passaram. O fluxo de pedido confirmado, recusa com devolução e falta de estoque foi verificado com clientes Flask e PostgreSQL simulado. Compose e Kubernetes passaram pela leitura dos YAMLs e pela conferência de referências. O workflow passou no actionlint. Build das imagens, execução em contêiner, implantação no cluster e publicação no GHCR ainda precisam de evidência de execução.

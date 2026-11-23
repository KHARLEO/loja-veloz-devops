# Esqueleto IaC: gerencia namespace; workloads são aplicados via kubectl.
# Em produção, evoluir para módulos e backend remoto com state protegido.
resource "kubernetes_namespace_v1" "app" {
  metadata {
    name = var.namespace
    labels = {
      "pod-security.kubernetes.io/enforce" = "restricted"
    }
  }
}
output "namespace" {value = kubernetes_namespace_v1.app.metadata[0].name}

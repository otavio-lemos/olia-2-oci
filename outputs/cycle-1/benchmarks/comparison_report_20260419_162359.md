# Evaluation Comparison Report

**Generated:** 2026-04-19 18:10:22
**Total Evaluated:** 200

## External Judge Evaluation (mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.00 | 3.73 | +0.72 |
| depth | 3.06 | 3.82 | +0.76 |
| structure | 3.50 | 4.63 | +1.14 |
| hallucination | 3.62 | 4.46 | +0.84 |
| clarity | 3.20 | 3.98 | +0.77 |
| overall | 3.27 | 4.12 | +0.85 |
| **Evaluated** | 200 | 200 | - |

## Detailed Results

| # | Category | Base | FT | Delta |
|---|---------|------|----|-------|
| 1 | compute/custom-images | 2.80 | 4.60 | +1.80 |
| 2 | compute/instances | 4.60 | 4.80 | +0.20 |
| 3 | compute/scaling | 4.40 | 4.20 | -0.20 |
| 4 | container/instances | 1.40 | 3.40 | +2.00 |
| 5 | container/oke | 2.60 | 5.00 | +2.40 |
| 6 | database/autonomous | 4.00 | 1.60 | -2.40 |
| 7 | database/autonomous-json | 1.20 | 3.40 | +2.20 |
| 8 | database/exadata | 4.00 | 5.00 | +1.00 |
| 9 | database/exadata-cloud | 4.60 | 3.20 | -1.40 |
| 10 | database/mysql | 4.20 | 3.60 | -0.60 |
| 11 | database/nosql | 1.60 | 4.20 | +2.60 |
| 12 | database/postgresql | 1.00 | 4.40 | +3.40 |
| 13 | devops/artifacts | 4.80 | 5.00 | +0.20 |
| 14 | devops/ci-cd | 4.40 | 4.60 | +0.20 |
| 15 | devops/resource-manager | 4.60 | 4.80 | +0.20 |
| 16 | devops/secrets | 1.60 | 4.20 | +2.60 |
| 17 | finops/cost-optimization | 4.60 | 5.00 | +0.40 |
| 18 | finops/rightsizing | 3.80 | 4.80 | +1.00 |
| 19 | finops/showback-chargeback | 4.60 | 4.80 | +0.20 |
| 20 | finops/storage-tiering | 4.40 | 3.80 | -0.60 |
| 21 | governance/audit-readiness | 3.80 | 4.80 | +1.00 |
| 22 | governance/budgets-cost | 2.40 | 5.00 | +2.60 |
| 23 | governance/compartments | 2.40 | 4.40 | +2.00 |
| 24 | governance/compliance | 1.00 | 3.60 | +2.60 |
| 25 | governance/landing-zone | 4.80 | 3.20 | -1.60 |
| 26 | governance/policies-guardrails | 4.40 | 4.60 | +0.20 |
| 27 | governance/resource-discovery | 1.40 | 4.40 | +3.00 |
| 28 | governance/tagging | 1.40 | 4.00 | +2.60 |
| 29 | lb/load-balancer | 5.00 | 4.60 | -0.40 |
| 30 | migration/aws-compute | 5.00 | 4.60 | -0.40 |
| 31 | migration/aws-database | 1.40 | 4.40 | +3.00 |
| 32 | migration/aws-storage | 2.40 | 2.00 | -0.40 |
| 33 | migration/azure-compute | 1.80 | 4.60 | +2.80 |
| 34 | migration/azure-database | 3.60 | 3.00 | -0.60 |
| 35 | migration/azure-storage | 0.80 | 2.60 | +1.80 |
| 36 | migration/data-transfer | 4.80 | 4.20 | -0.60 |
| 37 | migration/gcp-compute | 1.60 | 4.60 | +3.00 |
| 38 | migration/gcp-database | 2.40 | 3.40 | +1.00 |
| 39 | migration/gcp-storage | 3.00 | 1.40 | -1.60 |
| 40 | migration/onprem-compute | 2.80 | 5.00 | +2.20 |
| 41 | migration/onprem-database | 2.60 | 4.60 | +2.00 |
| 42 | migration/onprem-storage | 2.20 | 4.60 | +2.40 |
| 43 | migration/onprem-vmware | 4.40 | 4.60 | +0.20 |
| 44 | networking/connectivity | 2.20 | 4.40 | +2.20 |
| 45 | networking/security | 4.20 | 4.60 | +0.40 |
| 46 | networking/vcn | 2.40 | 2.40 | +0.00 |
| 47 | observability/apm | 1.60 | 5.00 | +3.40 |
| 48 | observability/logging | 4.60 | 4.60 | +0.00 |
| 49 | observability/monitoring | 4.60 | 3.00 | -1.60 |
| 50 | observability/stack-monitoring | 2.00 | 4.60 | +2.60 |
| 51 | platform/backup-governance | 2.80 | 4.60 | +1.80 |
| 52 | platform/sre-operations | 2.20 | 3.60 | +1.40 |
| 53 | security/cloud-guard | 4.60 | 4.60 | +0.00 |
| 54 | security/dynamic-groups | 1.40 | 4.80 | +3.40 |
| 55 | security/encryption | 4.60 | 4.60 | +0.00 |
| 56 | security/federation | 4.40 | 3.60 | -0.80 |
| 57 | security/iam-basics | 1.60 | 4.60 | +3.00 |
| 58 | security/policies | 1.80 | 3.40 | +1.60 |
| 59 | security/posture-management | 5.00 | 4.80 | -0.20 |
| 60 | security/vault-keys | 4.00 | 4.60 | +0.60 |
| 61 | security/vault-secrets | 3.20 | 4.60 | +1.40 |
| 62 | security/waf | 1.40 | 4.60 | +3.20 |
| 63 | security/zero-trust | 4.40 | 3.20 | -1.20 |
| 64 | serverless/api-gateway | 4.20 | 2.40 | -1.80 |
| 65 | serverless/functions | 4.40 | 4.60 | +0.20 |
| 66 | storage/block | 1.20 | 4.40 | +3.20 |
| 67 | storage/file | 2.40 | 2.60 | +0.20 |
| 68 | storage/object | 1.00 | 4.60 | +3.60 |
| 69 | terraform/compute | 4.40 | 3.40 | -1.00 |
| 70 | terraform/container | 2.60 | 4.40 | +1.80 |
| 71 | terraform/database | 5.00 | 3.40 | -1.60 |
| 72 | terraform/devops | 4.00 | 4.00 | +0.00 |
| 73 | terraform/load-balancer | 3.80 | 4.80 | +1.00 |
| 74 | terraform/networking | 2.20 | 4.40 | +2.20 |
| 75 | terraform/observability | 3.60 | 4.80 | +1.20 |
| 76 | terraform/provider | 2.00 | 2.60 | +0.60 |
| 77 | terraform/security | 3.40 | 4.60 | +1.20 |
| 78 | terraform/serverless | 4.00 | 4.60 | +0.60 |
| 79 | terraform/state | 4.60 | 3.80 | -0.80 |
| 80 | terraform/storage | 4.80 | 4.20 | -0.60 |
| 81 | troubleshooting/authentication | 2.00 | 4.60 | +2.60 |
| 82 | troubleshooting/compute | 4.60 | 4.40 | -0.20 |
| 83 | troubleshooting/connectivity | 4.20 | 4.40 | +0.20 |
| 84 | troubleshooting/database | 4.20 | 4.60 | +0.40 |
| 85 | troubleshooting/functions | 1.80 | 3.40 | +1.60 |
| 86 | troubleshooting/oke | 1.40 | 4.40 | +3.00 |
| 87 | troubleshooting/performance | 1.00 | 4.80 | +3.80 |
| 88 | troubleshooting/storage | 4.20 | 4.80 | +0.60 |
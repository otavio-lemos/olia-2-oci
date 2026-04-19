# Evaluation Comparison Report

**Generated:** 2026-04-19 00:26:48
**Total Evaluated:** 200

## Summary

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.67 | 4.51 | +0.84 |
| depth | 3.11 | 3.93 | +0.82 |
| structure | 3.47 | 4.45 | +0.98 |
| hallucination | 3.23 | 3.95 | +0.72 |
| clarity | 3.07 | 3.06 | -0.01 |
| overall | 3.31 | 3.98 | +0.67 |

## External Judge Evaluation (mlx-community/Meta-Llama-3.1-8B-Instruct-4bit)

| Metric | Base Model | Fine-Tuned | Delta |
|--------|-------------|------------|-------|
| technical_correctness | 3.94 | 4.29 | +0.35 |
| depth | 4.04 | 4.58 | +0.54 |
| structure | 3.91 | 4.46 | +0.55 |
| hallucination | 4.17 | 4.33 | +0.16 |
| clarity | 3.97 | 4.36 | +0.39 |
| overall | 4.01 | 4.40 | +0.40 |
| **Evaluated** | 200 | 200 | - |

## Detailed Results

| # | Category | Base | FT | Delta |
|---|---------|------|----|-------|
| 1 | compute/custom-images | 2.59 | 3.81 | +1.22 |
| 2 | compute/instances | 2.91 | 4.34 | +1.43 |
| 3 | compute/scaling | 3.56 | 4.45 | +0.89 |
| 4 | container/instances | 2.08 | 3.90 | +1.82 |
| 5 | container/oke | 2.77 | 3.38 | +0.61 |
| 6 | database/autonomous | 2.72 | 3.31 | +0.60 |
| 7 | database/autonomous-json | 4.17 | 4.00 | -0.17 |
| 8 | database/exadata | 3.68 | 3.78 | +0.09 |
| 9 | database/exadata-cloud | 2.43 | 4.14 | +1.71 |
| 10 | database/mysql | 3.77 | 4.21 | +0.44 |
| 11 | database/nosql | 2.83 | 4.12 | +1.29 |
| 12 | database/postgresql | 2.06 | 3.64 | +1.58 |
| 13 | devops/artifacts | 3.95 | 3.94 | -0.01 |
| 14 | devops/ci-cd | 2.99 | 4.34 | +1.34 |
| 15 | devops/resource-manager | 3.84 | 4.02 | +0.18 |
| 16 | devops/secrets | 3.72 | 4.07 | +0.35 |
| 17 | finops/cost-optimization | 3.76 | 4.01 | +0.25 |
| 18 | finops/rightsizing | 3.78 | 4.04 | +0.26 |
| 19 | finops/showback-chargeback | 3.88 | 4.39 | +0.51 |
| 20 | finops/storage-tiering | 4.09 | 4.37 | +0.27 |
| 21 | governance/audit-readiness | 2.99 | 4.38 | +1.39 |
| 22 | governance/budgets-cost | 3.24 | 3.79 | +0.55 |
| 23 | governance/compartments | 2.98 | 4.13 | +1.16 |
| 24 | governance/compliance | 2.21 | 2.74 | +0.53 |
| 25 | governance/landing-zone | 3.37 | 4.28 | +0.91 |
| 26 | governance/policies-guardrails | 4.16 | 4.27 | +0.10 |
| 27 | governance/resource-discovery | 2.92 | 3.91 | +0.99 |
| 28 | governance/tagging | 1.78 | 3.98 | +2.20 |
| 29 | lb/load-balancer | 3.89 | 4.21 | +0.32 |
| 30 | migration/aws-compute | 4.00 | 3.95 | -0.06 |
| 31 | migration/aws-database | 4.22 | 4.18 | -0.03 |
| 32 | migration/aws-storage | 4.31 | 4.48 | +0.17 |
| 33 | migration/azure-compute | 3.12 | 4.07 | +0.94 |
| 34 | migration/azure-database | 3.63 | 4.28 | +0.65 |
| 35 | migration/azure-storage | 3.43 | 4.39 | +0.97 |
| 36 | migration/data-transfer | 2.67 | 3.92 | +1.25 |
| 37 | migration/gcp-compute | 3.97 | 4.18 | +0.21 |
| 38 | migration/gcp-database | 3.85 | 4.12 | +0.27 |
| 39 | migration/gcp-storage | 3.00 | 4.29 | +1.29 |
| 40 | migration/onprem-compute | 2.89 | 4.04 | +1.15 |
| 41 | migration/onprem-database | 3.93 | 4.03 | +0.11 |
| 42 | migration/onprem-storage | 2.69 | 4.27 | +1.57 |
| 43 | migration/onprem-vmware | 4.04 | 3.82 | -0.22 |
| 44 | networking/connectivity | 3.39 | 4.13 | +0.74 |
| 45 | networking/security | 3.82 | 3.52 | -0.31 |
| 46 | networking/vcn | 2.68 | 3.62 | +0.94 |
| 47 | observability/apm | 4.15 | 3.68 | -0.47 |
| 48 | observability/logging | 3.80 | 4.35 | +0.54 |
| 49 | observability/monitoring | 4.04 | 3.89 | -0.15 |
| 50 | observability/stack-monitoring | 2.71 | 4.10 | +1.39 |
| 51 | platform/backup-governance | 4.11 | 4.42 | +0.31 |
| 52 | platform/sre-operations | 3.72 | 4.11 | +0.40 |
| 53 | security/cloud-guard | 2.73 | 4.31 | +1.58 |
| 54 | security/dynamic-groups | 3.27 | 3.94 | +0.67 |
| 55 | security/encryption | 3.96 | 3.91 | -0.05 |
| 56 | security/federation | 3.94 | 4.08 | +0.14 |
| 57 | security/iam-basics | 2.67 | 3.96 | +1.29 |
| 58 | security/policies | 3.95 | 2.69 | -1.26 |
| 59 | security/posture-management | 1.92 | 4.17 | +2.24 |
| 60 | security/vault-keys | 4.17 | 4.00 | -0.17 |
| 61 | security/vault-secrets | 2.94 | 3.95 | +1.01 |
| 62 | security/waf | 2.17 | 4.01 | +1.84 |
| 63 | security/zero-trust | 3.50 | 3.85 | +0.36 |
| 64 | serverless/api-gateway | 3.59 | 3.63 | +0.04 |
| 65 | serverless/functions | 2.93 | 3.59 | +0.66 |
| 66 | storage/block | 3.94 | 4.11 | +0.17 |
| 67 | storage/file | 2.87 | 3.88 | +1.00 |
| 68 | storage/object | 2.04 | 3.05 | +1.00 |
| 69 | terraform/compute | 3.65 | 4.02 | +0.37 |
| 70 | terraform/container | 3.19 | 4.17 | +0.98 |
| 71 | terraform/database | 3.24 | 3.80 | +0.56 |
| 72 | terraform/devops | 2.83 | 4.15 | +1.32 |
| 73 | terraform/load-balancer | 2.95 | 4.00 | +1.05 |
| 74 | terraform/networking | 4.29 | 4.13 | -0.16 |
| 75 | terraform/observability | 2.65 | 3.60 | +0.96 |
| 76 | terraform/provider | 3.81 | 3.31 | -0.50 |
| 77 | terraform/security | 2.75 | 4.11 | +1.36 |
| 78 | terraform/serverless | 4.22 | 4.32 | +0.10 |
| 79 | terraform/state | 1.95 | 3.95 | +2.00 |
| 80 | terraform/storage | 3.51 | 4.11 | +0.60 |
| 81 | troubleshooting/authentication | 3.11 | 4.31 | +1.20 |
| 82 | troubleshooting/compute | 3.42 | 3.39 | -0.03 |
| 83 | troubleshooting/connectivity | 3.73 | 4.04 | +0.31 |
| 84 | troubleshooting/database | 3.34 | 3.61 | +0.27 |
| 85 | troubleshooting/functions | 1.98 | 3.84 | +1.86 |
| 86 | troubleshooting/oke | 3.51 | 4.07 | +0.57 |
| 87 | troubleshooting/performance | 2.63 | 3.37 | +0.74 |
| 88 | troubleshooting/storage | 3.64 | 4.13 | +0.48 |
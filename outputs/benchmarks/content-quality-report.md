# Dataset Content Quality Report

**Total examples analyzed:** 9940
**Examples with issues:** 9014 (90.7%)
**Total issues found:** 15657

## Summary by Severity

| Severity | Count |
|----------|-------|
| Critical | 4934 |
| Warning | 10723 |

## Issue Types

| Issue Type | Count | Description |
|------------|-------|-------------|
| Compute params in non-compute category | 7840 |
| Compute shape mentioned in wrong category | 2883 |
| Generic 4-step template (Passo 1-4) | 1708 |
| Generic best practices template | 1309 |
| Generic troubleshooting template | 1032 |
| Generic security audit checklist | 473 |
| Generic integration pattern | 315 |
| Wrong CLI command for category | 97 |

## Diacritics

**Total missing diacritics:** 70956


## Issues by Category

| Category | Total Issues | Critical | Warning |
|----------|-------------|----------|---------|
| compute/custom-images | 71 | 71 | 0 |
| compute/instances | 60 | 60 | 0 |
| compute/scaling | 60 | 60 | 0 |
| container/instances | 303 | 94 | 209 |
| container/oke | 280 | 80 | 200 |
| database/autonomous | 240 | 60 | 180 |
| database/autonomous-json | 240 | 60 | 180 |
| database/exadata | 240 | 60 | 180 |
| database/mysql | 240 | 60 | 180 |
| database/nosql | 257 | 71 | 186 |
| database/postgresql | 240 | 60 | 180 |
| devops/artifacts | 308 | 112 | 196 |
| devops/ci-cd | 280 | 71 | 209 |
| devops/resource-manager | 280 | 94 | 186 |
| devops/secrets | 303 | 117 | 186 |
| lb/load-balancer | 60 | 60 | 0 |
| migration/aws-compute | 196 | 28 | 168 |
| migration/aws-database | 187 | 24 | 163 |
| migration/aws-storage | 196 | 28 | 168 |
| migration/azure-compute | 196 | 28 | 168 |
| migration/azure-database | 187 | 24 | 163 |
| migration/azure-storage | 196 | 28 | 168 |
| migration/data-transfer | 196 | 28 | 168 |
| migration/gcp-compute | 196 | 28 | 168 |
| migration/gcp-database | 187 | 24 | 163 |
| migration/gcp-storage | 196 | 28 | 168 |
| migration/onprem-compute | 196 | 28 | 168 |
| migration/onprem-database | 187 | 24 | 163 |
| migration/onprem-storage | 196 | 28 | 168 |
| migration/onprem-vmware | 210 | 24 | 186 |
| networking/connectivity | 280 | 71 | 209 |
| networking/security | 280 | 100 | 180 |
| networking/vcn | 300 | 100 | 200 |
| observability/apm | 240 | 60 | 180 |
| observability/logging | 260 | 60 | 200 |
| observability/monitoring | 240 | 60 | 180 |
| observability/stack-monitoring | 257 | 71 | 186 |
| security/cloud-guard | 280 | 94 | 186 |
| security/dynamic-groups | 303 | 117 | 186 |
| security/encryption | 308 | 112 | 196 |
| security/federation | 303 | 117 | 186 |
| security/iam-basics | 303 | 117 | 186 |
| security/policies | 303 | 117 | 186 |
| security/vault-keys | 280 | 94 | 186 |
| security/vault-secrets | 280 | 94 | 186 |
| security/waf | 280 | 80 | 200 |
| serverless/api-gateway | 280 | 80 | 200 |
| serverless/functions | 260 | 60 | 200 |
| storage/block | 60 | 60 | 0 |
| storage/file | 71 | 71 | 0 |
| storage/object | 80 | 80 | 0 |
| terraform/compute | 280 | 70 | 210 |
| terraform/container | 303 | 70 | 233 |
| terraform/database | 280 | 70 | 210 |
| terraform/devops | 280 | 56 | 224 |
| terraform/load-balancer | 280 | 47 | 233 |
| terraform/networking | 326 | 93 | 233 |
| terraform/observability | 280 | 56 | 224 |
| terraform/provider | 336 | 112 | 224 |
| terraform/security | 308 | 84 | 224 |
| terraform/serverless | 303 | 70 | 233 |
| terraform/state | 280 | 70 | 210 |
| terraform/storage | 257 | 47 | 210 |
| troubleshooting/authentication | 112 | 112 | 0 |
| troubleshooting/compute | 84 | 84 | 0 |
| troubleshooting/connectivity | 112 | 112 | 0 |
| troubleshooting/database | 71 | 71 | 0 |
| troubleshooting/functions | 84 | 84 | 0 |
| troubleshooting/oke | 94 | 94 | 0 |
| troubleshooting/performance | 71 | 71 | 0 |
| troubleshooting/storage | 84 | 84 | 0 |

## Top 20 Most Affected Examples

| Line | Category | Issues |
|------|----------|--------|
| 423 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 429 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 435 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 441 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 447 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 453 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 459 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 465 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 471 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 477 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 483 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 489 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 495 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 501 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 507 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 513 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 519 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 525 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 531 | container/instances | shape_in_response, generic_best_practices, context_pollution |
| 537 | container/instances | shape_in_response, generic_best_practices, context_pollution |

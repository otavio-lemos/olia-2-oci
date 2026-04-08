# Prompt Template: oci-security/cloud-guard

## Context

Generate examples about OCI Cloud Guard security posture service.

## Topics

- Cloud Guard configuration
- Detector recipes
- Responder rules
- Security scores
- Target configurations
- Security findings

## Difficulty Distribution

- beginner (30%): Basic Cloud Guard setup
- intermediate (50%): Detector and responder configuration
- advanced (20%): Custom recipes, complex scenarios

## Quality Rules

- Include specific Cloud Guard resource names
- Reference security best practices
- Explain security score implications
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### Cloud Guard Configuration

```bash
# Enable Cloud Guard
oci cloud-guard cloud-guard-cli-service summarize-tenancy-status \
  --registry-credential-id ocid1.credential.oc1..<unique-id>

# Create Cloud Guard configuration
oci cloud-guard configuration create-or-update --compartment-id ocid1.compartment.oc1..<unique-id> \
  --status ENABLED \
  --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id> \
  --responder-recipe-id ocid1.responderrecipe.oc1..<unique-id>

# Get configuration
oci cloud-guard configuration get --compartment-id ocid1.compartment.oc1..<unique-id>
```

### Target Management

```bash
# Create target (scope for Cloud Guard)
oci cloud-guard target create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name ProductionTargets \
  --target-resource-type COMPARTMENT \
  --target-resource-id ocid1.compartment.oc1..<unique-id> \
  --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id> \
  --responder-recipe-id ocid1.responderrecipe.oc1..<unique-id>

# List targets
oci cloud-guard target list --compartment-id ocid1.compartment.oc1..<unique-id>

# Update target
oci cloud-guard target update --target-id ocid1.target.oc1..<unique-id> \
  --display-name UpdatedTargets
```

### Detector Recipes

```bash
# List detector recipes
oci cloud-guard detector-recipe list --compartment-id ocid1.compartment.oc1..<unique-id>

# Create custom detector recipe
oci cloud-guard detector-recipe create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name CustomSecurityRecipe \
  --detector-rules '[{"detectorRuleId": "rule-id", "enabled": true, "riskLevel": "HIGH"}]'

# Get detector recipe details
oci cloud-guard detector-recipe get --detector-recipe-id ocid1.detectorrecipe.oc1..<unique-id>
```

### Responder Rules

```bash
# List responder recipes
oci cloud-guard responder-recipe list --compartment-id ocid1.compartment.oc1..<unique-id>

# Create custom responder rule
oci cloud-guard responder-rule create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name AutoRemediateS3 \
  --type AUTO_ACTER \
  --condition "problem[0].severity == HIGH" \
  --action "[{\"script\": \"remediate.sh\"}]"

# Enable responder
oci cloud-guard responder-rule update --responder-rule-id ocid1.responderrule.oc1..<unique-id> \
  --enabled true
```

### Security Findings

```bash
# List security findings
oci cloud-guard problem list --compartment-id ocid1.compartment.oc1..<unique-id> \
  --lifecycle-state ACTIVE

# Get finding details
oci cloud-guard problem get --problem-id ocid1.problem.oc1..<unique-id>

# Dismiss finding
oci cloud-guard problem update --problem-id ocid1.problem.oc1..<unique-id> \
  --lifecycle-state RESOLVED

# Get security score
oci cloud-guard security-score list-summaries --compartment-id ocid1.compartment.oc1..<unique-id>
```

## OCID Format

```
Target:             ocid1.target.oc1..<unique-id>
Detector Recipe:    ocid1.detectorrecipe.oc1..<unique-id>
Responder Recipe:   ocid1.responderrecipe.oc1..<unique-id>
Problem/Finding:    ocid1.problem.oc1..<unique-id>
Configuration:     ocid1.cloudguardconfig.oc1..<unique-id>
```

## Examples by Topic

### Basic Cloud Guard Setup

```bash
# Enable Cloud Guard in tenancy
oci cloud-guard configuration create-or-update --compartment-id ocid1.compartment.oc1..aaaaaa \
  --status ENABLED

# Create target for root compartment
oci cloud-guard target create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name RootCompartmentTarget \
  --target-resource-type COMPARTMENT \
  --target-resource-id ocid1.compartment.oc1..aaaaaa

# Target OCID: ocid1.target.oc1..bbbbbb
```

### Custom Detector Recipe

```bash
# Create detector recipe with custom rules
oci cloud-guard detector-recipe create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name ProductionDetector \
  --detector-rules '[
    {"displayName": "Check Public Buckets", "detector": "CLOUD_GUARD", "riskLevel": "HIGH"},
    {"displayName": "Check Unrestricted SSH", "detector": "CLOUD_GUARD", "riskLevel": "CRITICAL"}
  ]'

# Enable specific detector rules
oci cloud-guard detector-rule update --detector-rule-id ocid1.detectorrule.oc1..cccccc \
  --enabled true
```

### Responder Rules

```bash
# Create auto-remediation responder
oci cloud-guard responder-recipe create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name AutoRemediation \
  --responder-rules '[
    {
      "displayName": "Close Public Bucket",
      "type": "AUTO_ACTER",
      "responderRuleId": "close-public-bucket"
    }
  ]'

# Enable responder on target
oci cloud-guard target update --target-id ocid1.target.oc1..bbbbbb \
  --responder-recipe-id ocid1.responderrecipe.oc1..dddddd
```

### Security Score and Findings

```bash
# Get security score summary
oci cloud-guard security-score list-summaries --compartment-id ocid1.compartment.oc1..aaaaaa

# Sample output shows:
# - critical: 5
# - high: 12  
# - medium: 30
# - low: 45

# List active problems
oci cloud-guard problem list --compartment-id ocid1.compartment.oc1..aaaaaa \
  --lifecycle-state ACTIVE \
  --risk-level HIGH

# Remediate and update status
oci cloud-guard problem update --problem-id ocid1.problem.oc1..eeeeee \
  --lifecycle-state RESOLVED
```

## Anti-Patterns (Never generate)

1. ❌ Enable Cloud Guard without explaining it requires admin privileges in root compartment
2. ❌ Create targets without understanding scoping (can scan entire tenancy or specific compartments)
3. ❌ Use placeholder OCIDs: `ocid1.cloudguard.<region>.<id>` - correct is `ocid1.target.oc1..<unique-id>`
4. ❌ Enable all detector rules without testing (some may cause false positives)
5. ❌ Configure auto-responders without testing in non-production first
6. ❌ Ignore security score - it aggregates all findings [MUTABLE: recalculates every 24 hours]
7. ❌ Claim Cloud Guard replaces manual security audits
8. ❌ Enable responders without understanding the actions they perform
9. ❌ Mix up detector recipes vs responder recipes (detection vs action)
10. ❌ Forget that Cloud Guard findings can trigger events to other services
11. ❌ Configure targets on wrong compartment level
12. ❌ Dismiss findings without actual remediation

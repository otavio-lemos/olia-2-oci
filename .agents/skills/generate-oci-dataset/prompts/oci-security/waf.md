# Prompt Template: oci-security/waf

## Context

Generate examples about OCI Web Application Firewall (WAF).

## Topics

- WAF policies
- Access rules
- Rate limiting
- IP blocking
- SQL injection protection
- Cross-site scripting (XSS) protection
- CAPTCHA challenges

## Difficulty Distribution

- beginner (30%): Basic WAF configuration
- intermediate (50%): Access rules, rate limiting
- advanced (20%): Custom rules, advanced protection

## Quality Rules

- Include specific WAF policy examples
- Reference OCI WAF documentation
- Explain protection mechanisms
- Tag mutable content with [MUTABLE]

## OCI CLI Syntax

### WAF Policy Commands

```bash
# Create WAF policy
oci waf waf-policy create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name EcommerceWAF \
  --domain "api.example.com" \
  --response-code-obj-keep-alive-seconds 30

# List WAF policies
oci waf waf-policy list --compartment-id ocid1.compartment.oc1..<unique-id>

# Get WAF policy details
oci waf waf-policy get --waf-policy-id ocid1.wafpolicy.oc1..<unique-id>

# Update WAF policy
oci waf waf-policy update --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --display-name UpdatedWAF
```

### Access Rules

```bash
# Create access rule (allow/block)
oci waf access-rule create --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --rule-name BlockSuspiciousIPs \
  --condition "url = '/admin*'" \
  --action ALLOW \
  --type ACCESS_RULE

# Create rate limiting rule
oci waf rate-limiting-rule create --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --rule-name APILimit \
  --condition "url = '/api/*'" \
  --requests-limit 100 \
  --window-seconds 60 \
  --action DETECT_AND_ALERT \
  --type RATE_LIMITING

# Create IP address list for blocking
oci waf address-list create --compartment-id ocid1.compartment.oc1..<unique-id> \
  --display-name BlockedIPs \
  --type IP_ADDRESS_LIST \
  --addresses '["192.0.2.0/24", "198.51.100.0/24"]'
```

### Protection Rules

```bash
# Create protection rule (SQL injection)
oci waf protection-rule create --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --rule-name SQLInjectionProtection \
  --type SQL_INJECTION \
  --action BLOCK \
  --description "Block SQL injection attempts"

# Create XSS protection rule
oci waf protection-rule create --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --rule-name XSSProtection \
  --type XSS \
  --action BLOCK \
  --description "Block XSS attacks"

# Create CAPTCHA challenge rule
oci waf captcha-rule create --waf-policy-id ocid1.wafpolicy.oc1..<unique-id> \
  --rule-name BotChallenge \
  --type CAPTCHA \
  --action BLOCK \
  --description "Challenge suspected bots"
```

## OCID Format

```
WAF Policy:     ocid1.wafpolicy.oc1..<unique-id>
Address List:   ocid1.addresslist.oc1..<unique-id>
Protection Rule: ocid1.protectionrule.oc1..<unique-id>
```

Example full OCIDs:
```
ocid1.wafpolicy.oc1..aaaaaaaa1234567890abcdef1234567890abcdef
ocid1.addresslist.oc1..bbbbbbbb1234567890abcdef1234567890abcdef
```

## Examples by Topic

### Basic WAF Setup

```bash
# Create WAF policy for API
oci waf waf-policy create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name APIShield \
  --domain "api.myservice.com" \
  --response-code-obj-keep-alive-seconds 60

# Policy OCID: ocid1.wafpolicy.oc1..bbbbbb

# Add access rule to block admin
oci waf access-rule create --waf-policy-id ocid1.wafpolicy.oc1..bbbbbb \
  --rule-name BlockAdmin \
  --condition "url = '/admin*'" \
  --action BLOCK \
  --type ACCESS_RULE
```

### Rate Limiting Configuration

```bash
# Create rate limiting for API endpoints
oci waf rate-limiting-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name APIRateLimit \
  --condition "url = '/api/*'" \
  --requests-limit 1000 \
  --window-seconds 60 \
  --action BLOCK \
  --type RATE_LIMITING

# Different limits for different paths
oci waf rate-limiting-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name LoginRateLimit \
  --condition "url = '/auth/login'" \
  --requests-limit 10 \
  --window-seconds 60 \
  --action BLOCK \
  --type RATE_LIMITING
```

### IP Blocking

```bash
# Create blocked IP list
oci waf address-list create --compartment-id ocid1.compartment.oc1..aaaaaa \
  --display-name ThreatIntelIPs \
  --type IP_ADDRESS_LIST \
  --addresses '["10.0.0.0/8", "172.16.0.0/12"]'

# Apply as access rule
oci waf access-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name BlockThreatIPs \
  --condition "clientIp in ocid1.addresslist.oc1..ccccc" \
  --action BLOCK \
  --type ACCESS_RULE
```

### Protection Rules Configuration

```bash
# Enable SQL injection protection
oci waf protection-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name SQLInjection \
  --type SQL_INJECTION \
  --action BLOCK \
  --description "Block SQL injection"

# Enable XSS protection
oci waf protection-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name XSSAttack \
  --type XSS \
  --action BLOCK \
  --description "Block XSS attacks"

# Enable HTTP protocol validation
oci waf protection-rule create --waf-policy-id ocid1.wafpolicy.oc1..aaaaaa \
  --rule-name HTTPValidation \
  --type HTTP_PROTOCOL \
  --action BLOCK \
  --description "Block malformed HTTP"
```

## Anti-Patterns (Never generate)

1. ❌ Use WAF without explaining that it requires Load Balancer or Frontend (not standalone)
2. ❌ Set rate limits too low for production [MUTABLE: adjust based on traffic patterns]
3. ❌ Block all traffic instead of alerting on anomalies initially
4. ❌ Use placeholder OCIDs: `ocid1.waf.<region>.<id>` - correct is `ocid1.wafpolicy.oc1..<unique-id>`
5. ❌ Create overly broad rules that block legitimate traffic
6. ❌ Forget that WAF policies are regional - deploy to needed regions
7. ❌ Mix up WAF action types: DETECT_AND_ALERT vs BLOCK vs ALLOW
8. ❌ Create rules without testing in DETECT_AND_ALERT mode first
9. ❌ Use IP blocking without considering legitimate users behind NAT
10. ❌ Claim WAF replaces proper input validation in applications
11. ❌ Configure WAF without enabling all protection rule types
12. ❌ Forget that WAF needs to be attached to a load balancer or frontend

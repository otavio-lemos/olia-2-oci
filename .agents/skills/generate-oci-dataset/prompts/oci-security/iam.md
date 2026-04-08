# Prompt Template: oci-security/iam

## Context

Generate examples about OCI IAM including compartments, policies, groups, users, dynamic groups, authentication, MFA.

## Topics

- Compartments (hierarchy, naming conventions)
- Policies (syntax, permissions, compartments vs tenancy)
- Groups and Users
- Dynamic Groups
- Federation (IDCS, Okta)
- MFA and authentication
- Service principals

## Difficulty Distribution

- beginner (30%): Basic compartment creation, user management
- intermediate (40%): Policy syntax, groups
- advanced (30%): Dynamic groups, federation, complex policy architectures

## Quality Rules

- Use correct terminology: compartment, policy, group (not "folder", "permission")
- Explain difference between tenancy-level and compartment-level policies
- Include real policy syntax examples using OCI format
- Tag mutable content (limits, quotas) with [MUTABLE]
- Reference actual OCI service limits

## POLICY SYNTAX - ABSOLUTE REQUIREMENT

**CRITICAL**: Every response about policies MUST use OCI policy syntax. Do not explain policies using JSON, tables, or any other format.

### CORRECT Format (Use This)

```
Allow group <group-name> to <verb> <resource-type> in <location>
```

**CORRECT Examples** (use these as templates):
```
Allow group NetworkAdmins to manage virtual-network-family in compartment NetworkCompartment
Allow group Developers to use database-family in compartment AppDev
Allow any-user to read object-family in bucket DataBucket
Allow service fnFunction to manage functions-family in compartment AppCompartment
Allow dynamic-group AutoScaleGroup to manage instance-family in compartment ComputeCompartment
Allow group StorageAdmins to manage object-family in tenancy
Allow group DBAs to use database-family in tenancy
```

### WRONG Formats (Never Produce These)

**NEVER write policies like this**:
```
❌ JSON format:
{
  "effect": "allow",
  "action": ["object:*"],
  "resource": "arn:oci:..."
}

❌ AWS-style IAM:
{
  "Version": "2012-10-17",
  "Statement": [...]
}

❌ Azure-style:
"actions": ["Microsoft.Storage/*/read"]

❌ With placeholders:
Allow group [group-name] to [action] in [compartment]
Allow group <admins> to manage * in <location>

❌ Markdown tables:
| Group | Permission | Resource |
|-------|------------|----------|
| Admins | manage | all-resources |
```

### OCI Condition Syntax (when needed)

For conditions within policies:
```
Allow group Analysts to read object-family in bucket ReportsBucket
where any {request.permission == 'OBJECT_READ', request.permission == 'OBJECT_LIST'}

Allow service dataflow to manage job-family in compartment DataCompartment
where all {request.operation == 'CreateJob', request.permission != 'JobDelete'}
```

## Grammar Rules

1. **ALWAYS start** policy statements with `Allow` (capital A)
2. **ALWAYS specify** principal: `group <name>`, `dynamic-group <name>`, `service <name>`, or `any-user`
3. **ALWAYS specify** verb: `manage`, `use`, `read`, `inspect`, `create`, `delete`
4. **ALWAYS specify** resource-type: `virtual-network-family`, `object-family`, `database-family`, `instance-family`, `bucket`, `file-family`
5. **ALWAYS specify** location: `tenancy` or `compartment <CompartmentName>`
6. **NEVER use** placeholders like `<name>`, `[ocid]`, [condition] in final output
7. **NEVER use** JSON, curly braces, or "effect"/"action" fields
8. **NEVER use** AWS IAM or Azure RBAC syntax

## Examples by Topic

### Compartments
```
To create a compartment "ProjectA" under "root":
1. Open Console → Identity → Compartments
2. Click "Create Compartment"
3. Name: ProjectA, Description: Project A resources, Parent: root
4. Click "Create"
OCID format: ocid1.compartment.oc1..<unique-id>
```

### Groups and Policies
```
To grant NetworkAdmins access to VCN management:
1. Create group NetworkAdmins (Identity → Groups → Create Group)
2. Create policy "NetworkAdmin-Policy" in root compartment:
   Allow group NetworkAdmins to manage virtual-network-family in tenancy
3. Add users to NetworkAdmins group
```

### Dynamic Groups
```
To create a dynamic group for auto-scaling instances:
1. Identity → Dynamic Groups → Create Dynamic Group
2. Name: AutoScaleInstances, Description: Auto-scaling compute
3. Rule: `ANY {instance.compartment.name == 'ComputeCompartment'}`
4. Create policy:
   Allow dynamic-group AutoScaleInstances to use instance-family in compartment ComputeCompartment
```

### Service Principals
```
To grant OCI Functions access to Object Storage:
Allow service fnFunction to manage object-family in compartment AppCompartment
```

## Anti-Patterns (Never generate)

1. ❌ JSON policy structures
2. ❌ Placeholder text: `<ocid>`, `[group]`, [condition], <resource>
3. ❌ Markdown tables for policy syntax
4. ❌ AWS IAM format (arn:oci:...)
5. ❌ Azure RBAC format (Microsoft.Storage/...)
6. ❌ Policy without group/dynamic-group/service/any-user principal
7. ❌ Policy without verb (manage/use/read)
8. ❌ Policy without resource-type (virtual-network-family, etc.)
9. ❌ Policy without location (tenancy or compartment <name>)

"""OCI Technical Metadata for LLM Grounding.
Extracted from legacy template scripts to ensure CLI/SDK accuracy.
"""

OCI_CLI_COMMANDS = {
    "compute/instances": {
        "create": "oci compute instance launch",
        "list": "oci compute instance list",
        "get": "oci compute instance get",
        "update": "oci compute instance update",
        "delete": "oci compute instance terminate",
    },
    "compute/scaling": {
        "create": "oci autoscaling auto-scaling-configuration create",
        "list": "oci autoscaling auto-scaling-configuration list",
    },
    "networking/vcn": {
        "create": "oci network vcn create",
        "list": "oci network vcn list",
    },
    "networking/security": {
        "create": "oci network security-list create",
        "list": "oci network security-list list",
    },
    "database/autonomous": {
        "create": "oci db autonomous-database create",
        "list": "oci db autonomous-database list",
    },
    "storage/object": {
        "create": "oci os bucket create",
        "list": "oci os bucket list",
    }
    # Adicionaremos mais conforme necessário
}

OCI_PYTHON_SDK = {
    "compute/instances": {
        "client": "oci.core.ComputeClient",
        "create_method": "launch_instance",
    },
    "networking/vcn": {
        "client": "oci.core.VirtualNetworkClient",
        "create_method": "create_vcn",
    }
}

OCI_TERRAFORM_RESOURCES = {
    "compute/instances": "oci_core_instance",
    "networking/vcn": "oci_core_vcn",
    "database/autonomous": "oci_database_autonomous_database"
}

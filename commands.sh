# Tree-printer
git ls-tree -r --name-only HEAD | tree --fromfile

# List schema for terraform resource or block
terraform providers schema -json | jq '.provider_schemas."registry.terraform.io/hashicorp/aws".resource_schemas."aws_instance" | keys'

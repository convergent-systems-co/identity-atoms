terraform {
  required_version = ">= 1.7.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.0"
    }
  }
}

# CLOUDFLARE_API_TOKEN from env, never in code. See ~/.ai/Common.md §4.
# Token scopes required for this module (mirrors the core-infra token
# decomposition at convergent-systems-co/core-infra/terraform/cloudflare/*):
#
#   - Account → Cloudflare Pages → Edit
#       (created by terraform/cloudflare/account-token in core-infra)
#   - Zone → DNS → Edit  on the identity-atoms.com zone
#       (created by terraform/cloudflare/dns-token in core-infra)
#
# The intended operator workflow is: apply core-infra's token modules
# once, capture the value into the org secret store, then export that
# value as CLOUDFLARE_API_TOKEN before running this module.
provider "cloudflare" {}

module "pages_project" {
  source = "git::https://github.com/convergent-systems-co/core-infra.git//terraform/cloudflare/pages-project?ref=v0.1.0"

  cloudflare_account_id = var.cloudflare_account_id
  project_name          = "identity-atoms"
  production_branch     = "main"
  custom_domain         = "identity-atoms.com"
  zone_id               = var.zone_id
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID that owns the Pages project."
  type        = string
}

variable "zone_id" {
  description = "Cloudflare zone ID for identity-atoms.com."
  type        = string
}

output "project_name" {
  value = module.pages_project.project_name
}

output "subdomain" {
  value       = module.pages_project.subdomain
  description = "Default *.pages.dev hostname for the project."
}

output "custom_domain" {
  value       = module.pages_project.custom_domain
  description = "Custom hostname attached to the Pages project."
}

# Architecture

(Replace this stub. See `docs/adr/` for individual decisions.)

## Repository layout

```
web/                    Front-end sites
  site/                 primary Astro site (TypeScript, static)
  <other-site>/         additional sites if needed
  README.md             multi-site convention
infra/                  Infrastructure-as-code
  terraform/
    modules/            reusable Terraform modules
    envs/{dev,stg,prod}/  Cloudflare provider stubs
docs/                   Project documentation
  adr/                  MADR-format architecture decisions
scripts/                Project tooling
```

## High-level

(Describe the major components and how they communicate. Default stack: Astro
static build deployed to Cloudflare Pages. Terraform provisions the Pages
project, DNS records, and any supporting Cloudflare resources.)

## Diagram

(Mermaid or PlantUML. Source-not-binary per Code.md §9.2.)

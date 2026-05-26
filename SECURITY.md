# Security Policy

## Reporting a vulnerability

**Do not file a public issue** for a vulnerability. Public issues alert attackers before the fix lands.

Report privately by emailing the maintainer at `thomas.polliard@jmfamily.com` with:

- A clear description of the vulnerability.
- Steps to reproduce (or a proof-of-concept) — enough detail to confirm the issue.
- The affected component: catalog atoms, build tooling, the Astro site, the deploy pipeline, or a dependency.
- Your assessment of severity and impact.
- Whether you've disclosed elsewhere (other vendors, public mailing lists, etc.).

We aim to acknowledge within 3 business days and to ship a fix or remediation timeline within 14 days for verified vulnerabilities. If the issue is in a downstream dependency, we coordinate disclosure with that project's maintainers.

## Scope

In scope:

- The build / validate / emit pipeline (`scripts/`, `tools/`).
- The Astro site (`web/`) and its deploy chain.
- The CDN distribution (`identity-atoms.com/`).
- Repository configuration: workflows, branch protection, secrets handling, dependency pins.

Out of scope:

- Disagreements about atom content or schema design (open a regular issue or PR).
- Stale provenance or incorrect field values (regular issue or one-commit PR — welcome, but not a security report).
- Third-party services we link to but don't operate (Cloudflare Pages, GitHub Actions, upstream web properties).

## What we publish about a fixed vulnerability

After a fix is live, we publish:

- A short post-mortem in the commit message of the fix.
- An entry in `CHANGELOG.md` if the fix changed user-visible behavior or required action by consumers.

We do **not** publish:

- Working exploit code or step-by-step exploitation guides.
- Identifying details about the reporter without their explicit permission.

## Coordinated disclosure

If you've disclosed to another vendor first (e.g., a dependency we ship), we'll coordinate timing with you. If you haven't yet, we ask for a coordinated disclosure window — typically 30 days from acknowledgement — before public discussion. Critical exploitable issues compress this window.

## Secrets

If your report involves a leaked secret — an API key, token, credential, or PII — replace the secret with `[REDACTED:<kind>]` in your report. We coordinate rotation through the appropriate channel.

## Acknowledgements

When a researcher reports a valid vulnerability and consents to attribution, we credit them in the fix commit and in the relevant release notes. We don't run a paid bug-bounty.
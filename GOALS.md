# identity-atoms — Goals

> Identity primitives unified across vendors — auth methods, claim types, trust frameworks, key and certificate types — defined once and composable into identity profiles, federated setups, and persona templates.

*This document is derived from `aish/ARCHITECTURE.md` (now `xdao/xdao/ARCHITECTURE.md` §The *-Atoms Catalogs). Sections marked **Generated** are pattern-based and are intended as a starting point for revision, not as decided plan.*

---

## What this catalog makes civilization-grade

Identity is wildly fragmented across vendors. Each provider invents its own claim shapes, trust frameworks, key types. Every SSO integration is bespoke. Every key-rotation policy is reinvented per organization.

By cataloging the primitives, `identity-atoms` turns this domain from opaque-and-ephemeral to typed, versioned, composable, machine-readable, and open — the civilization-grade properties the ecosystem requires.

## What it catalogs

### Atom types

- **`auth-method`** — OAuth 2.1, OIDC, SAML, WebAuthn/passkeys, SSH-key, mTLS — typed and capability-annotated.
- **`claim-type`** — Standard claim shapes (sub, iss, aud, custom claims) with semantic meaning.
- **`trust-framework`** — Trust chain configurations (root CAs, federation trust, web-of-trust).
- **`key-cert-type`** — Key and certificate kinds (Ed25519, RSA, ECDSA, x.509, JWK, hardware-backed).

### Compositions: `identities`

An identity composition assembles auth methods + claim types + trust framework + key types into an identity profile (persona template). Federated setups compose multiple profiles with trust chains between them.

### Rule types

- **`trust-chain`** — How trust flows from root CA through intermediates to leaf identity.
- **`claim-validation`** — Required claim presence, format, and value constraints.
- **`key-rotation`** — Rotation cadence and grace-window rules.

## Runtime consumers

- **aish** — v0.3 Identity & Secrets engine. Persona switching swaps SSH key + AWS profile + kube context + git config + OAuth bindings atomically. Identity-atoms provides the typed schema.
- **universal-bus** — Service-to-service auth across the ecosystem uses identity-atoms primitives.

## Status & priority

**Current status:** `proposed`

**Priority tier:** Tier 3 — Build when supporting runtimes mature

**Trigger / activation condition:** aish v0.3 ships. Universal Bus needs identity for service auth.

## Roadmap *(Generated — milestone shapes mirror aish's roadmap pattern; revise as actual work begins)*

### v0.1 — Bootstrap & spec acceptance

**Goal:** Schema accepted. Seed atoms for the 6 most-common auth methods.

**Success criterion:** aish v0.3 persona system loads and validates personas against identity-atoms schema.

**Kill criterion:** Vendor-specific extension explosion outpaces the catalog — pivot to per-vendor profiles.

**Work:**

- [ ] XAIP: identity composition schema (persona template)
- [ ] Define 4 atom type schemas
- [ ] Seed atoms: OAuth2.1, OIDC, SAML, WebAuthn, SSH-key, mTLS
- [ ] Integrate with aish v0.3 persona loader
- [ ] Key-rotation rule evaluator

### v0.2 — Adoption & expansion

**Goal:** Federation across multiple identity providers.

**Work:**

- [ ] Federated identity composition schema
- [ ] Trust-chain validation
- [ ] Cross-org identity bridging examples

### v1.0 — Operational

**Goal:** Default identity primitive vocabulary across the ecosystem and adjacent open-source projects.

## Concrete atom example *(Generated — illustrative, not seed content)*

```yaml
identities/aish-work-persona/definition.yml
---
id: aish-work-persona
type: composition
version: 1.0.0
auth_methods:
  - { type: auth-method-ref, ref: atoms/auth-method/oidc }
  - { type: auth-method-ref, ref: atoms/auth-method/ssh-key }
keys:
  - { type: key-cert-ref, ref: atoms/key-cert-type/ed25519, location: keychain }
claims:
  required: [sub, iss, aud, groups]
trust_framework: { ref: atoms/trust-framework/corp-ca }
```

## Adoption strategy *(Generated)*

aish v0.3 is the first runtime consumer. Universal Bus adopts when service-to-service auth becomes a real requirement.

## Civilization-grade property checklist

Every catalog must satisfy these before v1.0. Failing any blocks a release.

| Property | Mechanism in this catalog |
|---|---|
| Typed | JSON Schema in `schemas/` validates every atom, composition, rule |
| Versioned | Every atom has a semver `version` field; compositions reference atoms by version-pinned ID |
| Machine-readable | `exports/catalog.json` published on every release |
| Composable | Compositions reference atoms by ID; CI verifies references resolve and no circular dependencies |
| Open | Apache-2.0 licensed; LICENSE file present |
| Durable | No external dependencies for primary content (no remote image URLs, no vendor APIs in the hot path) |

## Related

- **Spec:** [atoms-spec](https://github.com/convergent-systems-co/atoms-spec) — the canonical structure every catalog conforms to
- **Tools:** [atoms-tools](https://github.com/convergent-systems-co/atoms-tools) — CLI for validate / export / bootstrap / resolve
- **Federation:** [xdao](https://github.com/convergent-systems-co/xdao) — ecosystem directory and discovery
- **Umbrella:** [atoms](https://github.com/convergent-systems-co/atoms) — every catalog as a git submodule
- **Manifest:** [`ATOMS.yml`](./ATOMS.yml) — this catalog's machine-readable manifest
- **Standard:** [`README.md`](./README.md) — catalog overview and contribution flow

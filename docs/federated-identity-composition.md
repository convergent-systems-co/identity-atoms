# Federated Identity Composition Schema

## What federation means for identity-atoms

A federated identity composition assembles auth methods, claims, and trust frameworks from multiple origins into a portable identity assertion that works across organizational boundaries.

## Composition structure

```json
{
  "schema": "https://identity-atoms.com/schemas/composition-v1.json",
  "type": "identity",
  "id": "<slug>",
  "version": "1.0.0",
  "name": "...",
  "references": {
    "trust_framework": {
      "ref": "identity-atoms://atoms/trust-framework/<slug>",
      "version": "1.0.0"
    },
    "auth_methods": [
      { "ref": "identity-atoms://atoms/auth-method/<slug>", "version": "1.0.0" }
    ],
    "claim_types": [
      { "ref": "identity-atoms://atoms/claim-type/<slug>", "version": "1.0.0" }
    ]
  }
}
```

## Trust escalation rules

- `anonymous` → `authenticated` via primary auth method
- `authenticated` → `signed` when a claim is cryptographically attested
- `signed` → `verified` when the trust framework endorses the issuer

## Cross-catalog integration

- **policy-atoms:** identity compositions gate policy evaluation via `min_trust_level`
- **persona-atoms:** personas can require a minimum trust level via `policy_floor`
- **key-atoms:** key-cert atoms provide the cryptographic attestation layer for the `signed` tier

## Federation policy values

| Value | Meaning |
|---|---|
| `accept-from-listed-issuers` | Only issuers explicitly enumerated in the trust framework are accepted |
| `accept-signed` | Any issuer whose assertion is cryptographically signed is accepted |
| `strict-local` | Only locally-issued identities are accepted; no external federation |

## Adding a new composition

1. Add a JSON file to `identities/<slug>.json` that conforms to `schemas/composition-v1.json`.
2. Reference existing atom slugs from `atoms/auth-method/`, `atoms/claim-type/`, and `atoms/trust-framework/`.
3. Run `python3 scripts/build-exports.py` to validate and update `exports/catalog.json`.

# XAIP: Identity Composition Schema

**Atom type:** `identity`
**Version:** 0.1
**Audience:** Identity architects, federation engineers, platform integrators

---

## 1. Purpose

An identity composition assembles `auth-method`, `claim-type`, and `trust-framework` atoms into a portable identity definition that works across organizational boundaries. The composed identity is the artifact that policy engines, compliance frameworks, and service catalogs use to make access decisions — not raw credentials.

---

## 2. Composition Structure

An identity composition is a JSON document at the path `atoms/<slug>/v<version>/atom.json` within the identity-atoms catalog.

```json
{
  "atom_type": "identity",
  "atom_id": "convergent-systems-co/org-member",
  "version": "1",
  "display_name": "Convergent Systems Organization Member",
  "auth_methods": [
    {
      "auth_method_ref": "auth-method:oidc-pkce",
      "primary": true,
      "issuer_allowlist": ["https://accounts.google.com", "https://login.microsoftonline.com"]
    },
    {
      "auth_method_ref": "auth-method:api-key-hmac",
      "primary": false,
      "scoped_to": ["machine-to-machine"]
    }
  ],
  "claim_types": [
    {
      "claim_type_ref": "claim-type:email-verified",
      "required": true
    },
    {
      "claim_type_ref": "claim-type:org-membership",
      "required": true,
      "value_constraint": "convergent-systems-co"
    },
    {
      "claim_type_ref": "claim-type:role",
      "required": false
    }
  ],
  "trust_framework_ref": "trust-framework:oidc-federation-v1",
  "federation_policy": "accept-from-listed-issuers",
  "trust_level": "authenticated",
  "metadata": {
    "catalog_ref": "identity-atoms.convergent-systems.co"
  }
}
```

### 2.1 Required fields

| Field | Type | Description |
|---|---|---|
| `atom_type` | string | Always `"identity"` |
| `atom_id` | string | Stable, namespaced identifier |
| `auth_methods` | array | One or more auth-method atom references |
| `claim_types` | array | Claims required or permitted for this identity |
| `trust_framework_ref` | URI | The trust-framework atom governing this identity |
| `federation_policy` | enum | One of the values in §3 |
| `trust_level` | enum | One of the levels in §4 |

---

## 3. Federation Policy

The `federation_policy` field controls which external identity providers are accepted when an identity is presented across organizational boundaries.

### 3.1 Policy values

| Value | Behavior |
|---|---|
| `accept-from-listed-issuers` | Accept tokens from issuers in `auth_method.issuer_allowlist` only. Tokens from unlisted issuers are rejected at ingress. |
| `accept-signed` | Accept any token whose signature is valid against the issuer's published JWKS. No issuer allowlist enforced. Suitable for open-federation contexts. |
| `strict-local` | Accept tokens issued by the local identity provider only. No federation. Suitable for air-gapped or high-security contexts. |

### 3.2 Choosing a policy

```
High security (air-gapped, regulated)  →  strict-local
Enterprise federation (known partners)  →  accept-from-listed-issuers
Open federation (public API, OSS)       →  accept-signed
```

When `accept-signed` is used, trust escalation (§4) and claim validation (§2 `claim_types`) become the primary trust controls.

---

## 4. Trust Escalation

Trust escalation is the process by which an identity moves from a lower to a higher trust level. Levels are ordered and cumulative: an identity at a higher level satisfies all requirements for lower levels.

### 4.1 Trust level ladder

```
anonymous  →  authenticated  →  signed  →  verified
```

| Level | Definition | Typical auth-method |
|---|---|---|
| `anonymous` | No identity assertion. Requestor is unknown. | None (public access) |
| `authenticated` | Identity asserted via a credential the system trusts. | OIDC, SAML, API key |
| `signed` | Identity asserted and the assertion is cryptographically signed by the identity holder. | JWT with holder's private key; mTLS client cert |
| `verified` | Identity asserted, signed, and independently verified against an external authority (CA, KYC provider, org directory). | key-cert atom (see §5.2); verified-email claim; org-directory lookup |

### 4.2 Escalation rules

- Escalation is always upward. An identity cannot claim a higher level than its auth-method + claim set supports.
- Policy engines evaluate the `trust_level` field to determine minimum acceptable level for a resource. If `required_trust_level: signed` and the presented identity is `authenticated`, access is denied and an escalation challenge is issued.
- Escalation challenges specify what additional steps raise the identity to the required level (e.g., "provide a signed assertion from your key-cert atom").

### 4.3 Example escalation flow

```
1. User presents OIDC token  →  trust_level: authenticated
2. Service requires trust_level: signed
3. System issues escalation challenge: "Sign this nonce with your registered key"
4. User's client signs nonce using key registered in key-atoms catalog
5. System verifies signature against key-cert atom
6. trust_level promoted to: signed
7. Access granted
```

---

## 5. Cross-Catalog References

Identity compositions reference atoms from other catalogs to complete the trust picture.

### 5.1 persona-atoms: minimum trust level requirement

A `persona` atom in persona-atoms MAY declare a minimum identity trust level:

```json
{
  "atom_type": "persona",
  "atom_id": "convergent-systems-co/senior-engineer",
  "required_identity": {
    "identity_ref": "https://identity-atoms.convergent-systems.co/atoms/org-member/v1/atom.json",
    "min_trust_level": "signed"
  }
}
```

When a persona requires `min_trust_level: signed`, the identity composition governs what auth-method + claim combination achieves that level. The persona does not re-specify trust; it delegates to the identity composition.

### 5.2 key-atoms: cryptographic attestation

The `verified` trust level requires cryptographic attestation. The attestation layer is provided by a `key-cert` atom from the key-atoms catalog:

```json
{
  "trust_level_attestation": {
    "target_level": "verified",
    "key_cert_ref": "https://key-atoms.convergent-systems.co/atoms/org-member-signing-cert/v1/atom.json",
    "verification_method": "x509-chain",
    "ca_ref": "https://key-atoms.convergent-systems.co/atoms/convergent-ca-root/v1/atom.json"
  }
}
```

The key-cert atom carries the public key and certificate chain. The identity atom carries only the reference; private key material never enters the catalog.

---

## 6. Composition Conventions

| Convention | Value |
|---|---|
| Identity atom path | `atoms/<slug>/v<version>/atom.json` |
| Auth-method atom path | `atoms/auth-methods/<slug>/v<version>/atom.json` |
| Claim-type atom path | `atoms/claim-types/<slug>/v<version>/atom.json` |
| Trust-framework atom path | `atoms/trust-frameworks/<slug>/v<version>/atom.json` |
| Cross-catalog ref format | Fully-qualified HTTPS URI to the remote atom |

---

## 7. Integration Summary

| Downstream system | How it uses the identity composition |
|---|---|
| **policy-atoms** | Policy stacks bind floors to identities via `identity_scope` refs |
| **compliance-atoms** | Compliance frameworks bind control obligations to identity scopes |
| **persona-atoms** | Personas declare minimum trust level, delegating to the identity composition |
| **key-atoms** | Key-cert atoms provide the cryptographic attestation for `verified` level |
| **service-atoms** | Service auth schemes reference auth-method atoms from this catalog |

---

## 8. Related Atoms and Docs

- `auth-method` atom — credential mechanism (OIDC, SAML, API key, mTLS)
- `claim-type` atom — schema for a single claim (email, role, org-membership)
- `trust-framework` atom — governance rules for a federation trust domain
- persona-atoms: `xaip-persona-composition.md` — how personas declare identity requirements
- key-atoms: key-cert atom specification — cryptographic attestation for `verified` trust level
- compliance-atoms: `xaip-framework-composition.md` — identity compliance bindings
- policy-atoms: `xaip-policy-composition.md` — identity-bound policy floors

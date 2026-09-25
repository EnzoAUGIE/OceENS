# OcéEns

EPF's course evaluation platform: *sondages* are created per program, students answer them, and the responses are exported, visualised and summarised into *synthèses*.

## Language boundary

The application's user interface is in French, and the product's own vocabulary stays in French wherever it appears, in documentation included: *sondage*, *synthèse*, and the other terms the interface shows users. Code identifiers keep their existing names (`Survey`, `Summary`, `sondage_loader.py`…).

Everything else is written in English: documentation (`README.md`, this file, `docs/`, ADRs), issues and pull requests.

## Language

### Authentication

**Development login** (`AUTH_MODE=dev`):
Sign-in without an identity provider: you pick a user's e-mail address and are signed in as that user, with no proof of identity. It only exists when `AUTH_MODE=dev` and must never be used in production.
_Avoid_: impersonation, spoofing, fake login

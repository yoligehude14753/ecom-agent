# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅        |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

Email: security@ecomagent.dev (or open a private GitHub security advisory)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We aim to respond within 48 hours and will keep you informed of progress.

## Security Considerations

EcomAgent stores your LLM API keys and Amazon credentials in a local `.env` file.
- Never commit `.env` to version control
- Use Docker secrets or a secrets manager in production deployments
- The `.gitignore` already excludes `.env`

Scraped data and snapshots are stored in your local PostgreSQL and Redis instances.
No data is sent to any EcomAgent server (there is none — it's fully self-hosted).

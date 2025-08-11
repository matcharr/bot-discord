# Security Guidelines

## Security-First Mindset
This Discord bot handles sensitive moderation data and must maintain high security standards.

## Data Protection Standards
- All sensitive data MUST be encrypted (warnings, user info)
- Use hashed identifiers for Discord IDs (SHA-256 + salt + pepper)
- Never log sensitive data in plain text
- Implement proper GDPR compliance (soft deletes, data export)

## Security Checks Before Push
```bash
# Check for hardcoded secrets
grep -r "token\|password\|key\|secret" project/ --exclude-dir=__pycache__ | grep -v "# Safe comment"

# Check for SQL injection vulnerabilities
grep -r "f\".*{.*}.*\"" project/database/ | grep -v "# Safe f-string"

# Verify encryption is used for sensitive fields
grep -r "reason\|user_id" project/database/models.py
```

## Environment Security
- Never commit .env files with real tokens
- Use .env.example for templates only
- Rotate encryption keys in production
- Validate all user inputs before database operations

## Database Security
- Use parameterized queries (SQLAlchemy ORM handles this)
- Encrypt sensitive columns (reason field in warnings)
- Hash identifiable data (Discord IDs)
- Implement proper access controls

## Code Review Security Checklist
- [ ] No hardcoded secrets or tokens
- [ ] Sensitive data is encrypted
- [ ] User inputs are validated
- [ ] SQL injection protection in place
- [ ] Proper error handling (no data leaks)
- [ ] GDPR compliance maintained

## Security Testing
```bash
# Run security-focused tests
python -m pytest tests/database/test_security.py -v

# Check for common vulnerabilities
bandit project/ -r -f json
```

## Incident Response
- If security issue found: Fix immediately, don't push
- Document security decisions in steering files
- Regular security audits of encryption implementation
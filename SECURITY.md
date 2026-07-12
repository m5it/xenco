# Security Policy

## Supported Versions

We release patches for security vulnerabilities. The following versions are currently supported:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in xEnco, please report it responsibly.

### How to Report

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

Instead, please report privately by email:

📧 **Security Contact:** w4d4f4k@gmail.com

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Possible impact
- Suggested fix (if any)
- Your name/handle for attribution (optional)

### What to Expect

1. **Acknowledgment** - We will acknowledge receipt within 48 hours
2. **Investigation** - We will investigate and validate the vulnerability
3. **Timeline** - We will provide an estimated timeline for a fix
4. **Resolution** - Once fixed, we will:
   - Release a security patch
   - Credit you in the release notes (with your permission)
   - Publish a security advisory

## Security Best Practices

### When Using xEnco

1. **Keep keys secure** - Key files (.xenco) contain sensitive mapping data
2. **Don't commit keys** - Add `*.xenco` to your `.gitignore`
3. **Use HTTPS** - When generating keys from URLs, prefer HTTPS sources
4. **Validate sources** - Ensure your key source is trustworthy
5. **Rotate keys** - Periodically generate new keys for sensitive data

### Key File Security

Key files contain character mappings that could be used to decode messages. Protect them like passwords:

```bash
# Set restrictive permissions
chmod 600 mykey.xenco

# Never share key files publicly
# Don't email keys unless encrypted
```

### Encoding vs Encryption

**Important:** xEnco provides encoding, not encryption. 

- **Encoding** - Obscures text but is reversible with the key
- **Encryption** - Requires mathematical operations to reverse

Use xEnco for:
- Obfuscation
- Format transformation
- Simple message hiding

Do NOT use xEnco for:
- Protecting highly sensitive data
- Financial information
- Medical records
- Passwords or credentials

For these use cases, use proper encryption like AES, RSA, or libraries like `cryptography`.

## Known Limitations

1. **Deterministic mapping** - Same input + same key = same output
2. **Key required** - Anyone with the key can decode
3. **No integrity check** - Encoded text could be modified
4. **Character set limited** - Depends on source material's ASCII range

## Security Updates

Subscribe to security announcements:
- Watch the GitHub repository
- Check the [CHANGELOG.md](CHANGELOG.md) for security fixes

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities.

---

**Last Updated:** 2026-07-12  
**Contact:** w4d4f4k@gmail.com | https://grandekos.com

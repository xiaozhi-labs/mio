## 1. Implementation
- [x] Update server startup to prefer TLS by default and fall back to in-memory self-signed certs when files are missing.
- [x] Ensure generated cert includes SANs for localhost/loopback and configured host/IP.
- [x] Add logging that indicates whether TLS uses file certs or in-memory certs.
- [x] Update configuration defaults/behavior documentation if needed.

## 2. Validation
- [ ] Manual: start server without cert files and confirm HTTPS works locally without TLS handshake errors.
- [ ] Manual: start server with cert files and confirm file-backed TLS is used.

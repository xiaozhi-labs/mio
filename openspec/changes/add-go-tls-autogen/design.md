# Design Notes

## Decision Summary
- Always enable TLS unless explicitly disabled.
- If TLS cert/key files are missing, generate a self-signed cert/key pair in memory and use `http.Server.TLSConfig`.

## Certificate Generation
- Use Go `crypto/x509` to generate a short-lived self-signed certificate.
- SANs include:
  - `localhost`
  - `127.0.0.1`
  - `::1`
  - Configured host if set (both DNS/IP variants where applicable).
- Private key is ephemeral and never written to disk.

## Compatibility
- Keeps existing behavior when cert files are present.
- TLS-required mode no longer fails due to missing cert files.

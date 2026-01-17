## ADDED Requirements

### Requirement: TLS auto-generation
The server SHALL generate a self-signed TLS certificate in memory when TLS is enabled and no certificate files are available.

#### Scenario: Missing cert files
- **GIVEN** TLS is enabled and certificate files are missing
- **WHEN** the server starts
- **THEN** it uses an in-memory self-signed certificate without writing to disk

### Requirement: TLS default behavior
The server SHALL prefer TLS by default unless explicitly configured to disable it.

#### Scenario: Default startup
- **GIVEN** no explicit TLS-disable configuration
- **WHEN** the server starts
- **THEN** it serves HTTPS

### Requirement: Subject alternative names
The generated certificate SHALL include loopback and configured host SANs to avoid local trust errors.

#### Scenario: Loopback access
- **GIVEN** the server generates a certificate
- **WHEN** a client connects via localhost or loopback IPs
- **THEN** the certificate SANs include `localhost`, `127.0.0.1`, and `::1`

# Security

FMAPI is pre-release software with an offline mock adapter. There are no maintained stable release branches yet. Security fixes currently target the development branch.

The host's capability grants and command allowlists govern access through FMAPI contracts. They are not a sandbox for untrusted code in the same process. Hosts are responsible for deciding which mod assemblies to load. Future game adapters must document their own execution and recovery constraints.

## Reporting a vulnerability

When this repository is hosted, use its **Security → Advisories → Report a vulnerability** option if the host enables private reporting. No dedicated private contact has been established in this initialization. If private reporting is unavailable, open an issue asking for a private contact without including exploit details or sensitive data.

A useful report includes the affected commit, prerequisites, a minimal reproduction using synthetic data where possible, expected impact, and any proposed mitigation. Do not include game binaries, saves, credentials, or personal information. This project does not promise a fixed response time.

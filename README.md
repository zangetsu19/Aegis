# AEGIS

Autonomous AI Agent Platform.

AEGIS is designed as a modular, provider-agnostic agent system with persistent memory, tool use, autonomous task execution, model routing, and synchronized phone/laptop clients.

## Initial architecture

- `apps/` — user-facing applications
- `services/` — backend services
- `packages/` — shared libraries and contracts
- `infra/` — deployment and infrastructure
- `docs/` — architecture and design documentation

## Development principles

1. Fast first response and streaming execution.
2. Model-provider independence through a model router.
3. Persistent, structured memory rather than context-only memory.
4. Explicit permissions for consequential actions.
5. Modular tools that can be replaced or upgraded independently.
6. Local/open-source inference support alongside hosted models.
7. Phone and laptop clients share one authoritative agent state.

## Security

Never commit API keys, wallet private keys, tokens, or other secrets. Use environment variables and a secrets manager in production.

## Status

Early foundation — architecture and core implementation are being built incrementally.

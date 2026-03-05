# PayJarvis Blockchain — Trust & Proof Layer

Enterprise module that adds cryptographic proof and blockchain anchoring to the PayJarvis ecosystem.

**This is NOT a payment system.** It provides proof, auditability, and reputation for AI agents.

## Architecture

| Component | Purpose |
|-----------|---------|
| **Smart Contracts** | On-chain agent registry + Merkle root anchoring (Polygon) |
| **Anchoring Service** | Builds Merkle trees from audit events, anchors roots on-chain |
| **Registry Service** | Registers/revokes AI agents on-chain with certification criteria |
| **Credentials (VC)** | Issues W3C Verifiable Credentials for agents and anchor proofs |
| **REST API** | Fastify API exposing proofs, agents, and credentials endpoints |

## Quick Start

```bash
# Install dependencies
npm install

# Copy env and configure
cp .env.example .env

# Generate Prisma client
npm run db:generate

# Run database migrations
npm run db:migrate

# Compile smart contracts
npm run compile

# Run contract tests
npm run test:contracts

# Deploy to testnet (Amoy)
npm run deploy:testnet

# Start API server
npm run dev
```

## Smart Contracts

- **PayJarvisRegistry** — On-chain agent registration and revocation
- **PayJarvisAnchoring** — Merkle root anchoring for audit trail proof

### Deploy

```bash
npm run deploy:testnet   # Polygon Amoy testnet
npm run deploy:mainnet   # Polygon mainnet
```

## API Endpoints

All endpoints require `x-api-key` header.

### Proofs
- `POST /api/v1/proofs/anchor` — Anchor events on-chain
- `POST /api/v1/proofs/merkle` — Build Merkle tree (off-chain)
- `POST /api/v1/proofs/verify` — Verify event proof
- `GET /api/v1/proofs/:index` — Get on-chain record
- `GET /api/v1/proofs/latest` — Get latest record
- `GET /api/v1/proofs/count` — Total records count

### Agents
- `POST /api/v1/agents/register` — Register agent on-chain
- `POST /api/v1/agents/revoke` — Revoke agent
- `GET /api/v1/agents/active?name=X&vendor=Y` — Check agent status
- `GET /api/v1/agents/details?name=X&vendor=Y` — Get agent details

### Credentials
- `POST /api/v1/credentials/issue/agent` — Issue agent VC
- `POST /api/v1/credentials/issue/anchor-proof` — Issue anchor proof VC

## License

MIT

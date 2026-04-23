# ZeroBot — 0G Mainnet Telegram Bot

A production-grade Telegram bot providing access to the 0G (Zero Gravity) blockchain ecosystem: embedded wallets, decentralized storage, compute purchases, staking, and price alerts — all on **0G mainnet** (chain ID 480).

## Features

### Wallet
- `/connect` — Create or view your 0G wallet (address only, no private key shown)
- `/balance` — Check your OG token balance
- `/portfolio` — Full portfolio overview
- `/export_key` — Export your private key (with confirmation)
- `/import_wallet <private_key>` — Import an existing wallet

### Storage
- `/store` — Upload a file to 0G decentralized storage (real on-chain tx)
- `/retrieve <root_hash>` — Retrieve a file by its merkle root
- `/files` — List your uploaded files

### Compute
- `/buy_compute [gpu_type] [hours]` — Purchase GPU compute (A100/H100/V100/T4/CPU)
- `/job_status <job_id>` — Check a compute job's status

### Staking
- `/stake <amount>` — Stake OG tokens
- `/stake_info` — View validator list

### Explorer
- `/explorer` — Latest block info
- `/tx <hash>` — Look up a transaction

### Market
- `/prices` — Current OG price
- `/alerts` — Manage price alerts

### Misc
- `/faucet` — Faucet info (mainnet)
- `/help` — Command list

## Production Features

- Real on-chain transactions (no simulation, no mocks)
- Balance checks before every write operation
- Incoming transaction notifications via background monitor
- Rate limiting (10 commands/minute per user)
- Structured JSON logging (automatic on Render)
- Multi-stage Docker build with non-root user
- Health endpoint on `/`
- Fernet-encrypted private keys in SQLite

## Setup

```bash
cp .env.example .env
# Generate a Fernet key:
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste as WALLET_ENCRYPTION_KEY in .env
pip install -r requirements.txt
python -m bot.main
```

## Docker

```bash
docker build -t zerobot .
docker run --env-file .env -p 10000:10000 zerobot
```

## Deploy to Render

1. Create a new Web Service from this repo
2. Select Docker runtime
3. Set environment variables (see `.env.example`)
4. Deploy

## License

MIT

# ZeroBot

ZeroBot is a Telegram control layer for the 0G mainnet stack. It gives users an embedded wallet, 0G Storage uploads, 0G Compute discovery, compute purchase intents, and explorer access from chat.

## Hackathon Summary

- Project name: `ZeroBot`
- One-line description: `Telegram-native 0G mainnet agent wallet that lets users store files, inspect compute providers, and execute anchored compute actions from chat.`
- Prize track fit:
  - `Track 1: Agentic Infrastructure & OpenClaw Lab`
  - `Track 3: Agentic Economy & Autonomous Applications`
- 0G components used:
  - `0G Chain`
  - `0G Storage`
  - `0G Compute`

## What It Does

ZeroBot turns Telegram into a lightweight 0G operator console:

- Creates an embedded 0G wallet per user
- Uploads files to 0G Storage and keeps local file metadata
- Anchors uploaded storage roots to a bot-owned 0G mainnet contract
- Lists live 0G Compute network status and provider/model information through the 0G Compute CLI
- Sends payable compute purchase intents to a bot-owned 0G mainnet contract
- Exposes explorer and transaction lookup flows for on-chain inspection

## Problem It Solves

Most users cannot comfortably work with the 0G stack from raw RPCs, CLI commands, or separate wallets. ZeroBot reduces that friction by making storage, compute discovery, and on-chain intent execution accessible from a familiar chat interface.

## 0G Integration Proof

- Mainnet contract: `0x3C1F34D1f93793Cc07747BE639A472C1e14f3f5f`
- Explorer: `https://chainscan.0g.ai/address/0x3C1F34D1f93793Cc07747BE639A472C1e14f3f5f`
- Deployment tx: `https://chainscan.0g.ai/tx/0x6f811b52c2b1a349e4f95e0cb2d94a875055f4ba3b1249a0e395eec2ed06cb18`
- Contract role:
  - `purchaseCompute(...)` records payable compute intents from the bot flow
  - `anchorStorage(...)` records uploaded storage roots on-chain

## Commands

- `/start` overview and wallet summary
- `/commands` command list without rerunning onboarding
- `/stack` live 0G stack summary used by the bot
- `/connect` create or view the user wallet
- `/balance` wallet balance
- `/portfolio` portfolio snapshot
- `/store` upload a file to 0G Storage
- `/retrieve <root_hash>` inspect a stored file reference
- `/files` list uploaded files
- `/compute_market` list 0G Compute mainnet providers through CLI fallback
- `/models` list 0G Compute model catalog
- `/compute_account` show 0G Compute CLI network and account status
- `/buy_compute [gpu_type] [hours]` submit a payable compute intent
- `/job_status <job_id>` check the broadcasted compute intent state
- `/explorer` latest block info
- `/tx <hash>` transaction lookup
- `/prices` token market data
- `/alerts` price alerts
- `/faucet` mainnet funding guidance

## Architecture

- Telegram bot layer:
  - command handlers in `bot/handlers`
- On-chain layer:
  - Web3.py wallet and transaction service on 0G mainnet
  - `ZeroBotMainnetRegistry.sol` for anchored compute and storage events
- Storage layer:
  - `OG_STORAGE_INDEXER` upload endpoint on 0G Storage
- Compute discovery layer:
  - `0g-compute-cli` or `npx @0glabs/0g-serving-broker`
  - runtime-generated CLI config for 0G mainnet
- Persistence layer:
  - SQLite for local user/file metadata

## Local Run

```bash
cp .env.example .env
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
pip install -r requirements.txt
python -m bot.main
```

Required env values:

- `TELEGRAM_BOT_TOKEN`
- `WALLET_ENCRYPTION_KEY`

Mainnet env defaults already included:

- `OG_RPC_URL=https://evmrpc.0g.ai`
- `OG_CHAIN_ID=16661`
- `OG_STORAGE_INDEXER=https://indexer-storage.0g.ai`
- `ZEROBOT_CONTRACT_ADDRESS=0x3C1F34D1f93793Cc07747BE639A472C1e14f3f5f`

## Docker / Render

```bash
docker build -t zerobot .
docker run --env-file .env -p 10000:10000 zerobot
```

Render notes:

- Docker image installs Node.js and the 0G Compute CLI fallback
- health endpoint is exposed on `/`
- the bot relies on polling, so no Telegram webhook setup is required

## Repository

- GitHub: `https://github.com/TS-mfon/zerobot`

## Reviewer Notes

- Fund a generated wallet with mainnet tokens before `/store` or `/buy_compute`
- `/store` writes to 0G Storage and then anchors the returned root to the ZeroBot contract when the contract address is configured
- `/compute_market`, `/models`, and `/compute_account` use the 0G Compute CLI and may take longer than wallet-only commands

## Source Layout

- `bot/main.py` bot entrypoint
- `bot/handlers` Telegram command surface
- `bot/services` wallet, chain, storage, compute, and CLI integrations
- `contracts/ZeroBotMainnetRegistry.sol` 0G mainnet contract source

## License

MIT

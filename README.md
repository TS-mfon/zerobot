# ZeroBot - 0G Telegram Bot

A Telegram bot providing access to the **0G (Zero Gravity)** blockchain ecosystem.

## Features

- Embedded wallet creation and management (Fernet-encrypted)
- Balance and portfolio queries via 0G EVM RPC
- Decentralised storage (store / retrieve files)
- Compute marketplace interaction
- Staking overview
- Block explorer look-ups
- Price feeds and custom alerts
- Testnet faucet integration

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your secrets
python -m bot.main
```

## Docker

```bash
docker build -t zerobot .
docker run --env-file .env zerobot
```

## Project Structure

```
bot/
  main.py          - entry point
  config.py        - Pydantic Settings
  handlers/        - Telegram command handlers
  services/        - business logic (wallet, storage, compute, chain)
  models/          - SQLAlchemy-style data models (plain dataclasses)
  db/              - async SQLite via aiosqlite
  utils/           - encryption helpers, message formatting
```

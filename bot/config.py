"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Bot-wide settings backed by .env / environment variables."""

    telegram_bot_token: str = Field(..., description="Telegram Bot API token")
    og_rpc_url: str = Field(
        default="https://evmrpc.0g.ai",
        description="0G EVM-compatible JSON-RPC endpoint (mainnet)",
    )
    wallet_encryption_key: str = Field(
        ..., description="Fernet-compatible base64 key for wallet encryption"
    )
    database_path: str = Field(
        default="zerobot.db", description="SQLite database file path"
    )

    # 0G mainnet settings
    og_chain_id: int = Field(default=16661, description="0G mainnet chain ID")
    og_explorer_url: str = Field(
        default="https://chainscan.0g.ai",
        description="0G block explorer base URL",
    )
    og_faucet_url: str = Field(
        default="https://faucet.0g.ai", description="0G faucet URL"
    )
    og_storage_indexer: str = Field(
        default="https://indexer-storage.0g.ai",
        description="0G decentralised storage indexer URL",
    )
    og_compute_cli_bin: str = Field(
        default="0g-compute-cli",
        description="Preferred 0G Compute CLI binary name",
    )
    og_compute_cli_rpc: str = Field(
        default="https://evmrpc.0g.ai",
        description="0G Compute CLI RPC endpoint",
    )
    og_compute_cli_network: str = Field(
        default="mainnet",
        description="0G Compute CLI network profile",
    )
    zerobot_contract_address: str = Field(
        default="",
        description="Optional ZeroBot mainnet registry contract address",
    )
    webhook_base_url: str = Field(
        default="",
        description="Public HTTPS base URL used for Telegram webhooks on Render",
    )
    og_compute_provider_tag: str = Field(
        default="0g-mainnet-compute",
        description="Human-readable provider label used in on-chain compute intents",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

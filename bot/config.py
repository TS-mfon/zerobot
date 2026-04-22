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
    og_chain_id: int = Field(default=480, description="0G mainnet chain ID")
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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Bot-wide settings backed by .env / environment variables."""

    telegram_bot_token: str = Field(..., description="Telegram Bot API token")
    og_rpc_url: str = Field(
        default="https://evmrpc-testnet.0g.ai",
        description="0G EVM-compatible JSON-RPC endpoint",
    )
    wallet_encryption_key: str = Field(
        ..., description="Fernet-compatible base64 key for wallet encryption"
    )
    database_path: str = Field(
        default="zerobot.db", description="SQLite database file path"
    )

    # Optional overrides
    og_chain_id: int = Field(default=16600, description="0G testnet chain ID")
    og_explorer_url: str = Field(
        default="https://chainscan-newton.0g.ai",
        description="0G block explorer base URL",
    )
    og_faucet_url: str = Field(
        default="https://faucet.0g.ai", description="0G testnet faucet URL"
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

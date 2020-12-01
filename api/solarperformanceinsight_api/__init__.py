from typing import Optional
from pydantic import BaseSettings, Json
from ._version import version as __version__  # NOQA


class Settings(BaseSettings):
    auth_token_url: str = "https://solarperformanceinsight.us.auth0.com/oauth/token"
    auth_jwk_url: str = (
        "https://solarperformanceinsight.us.auth0.com/.well-known/jwks.json"
    )
    auth_key: Json
    auth_audience: str = "https://app.solarperformanceinsight.org/api"
    auth_issuer: str = "https://solarperformanceinsight.us.auth0.com/"
    auth_client_id: str = "G1YyfLdseYn10RQo11Lqee2ThXj5l5fh"

    traces_sample_rate: Optional[float] = None

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "apiuser"
    mysql_password: str = "terriblepasswordtochange"
    mysql_database: str = "spi_data"
    mysql_use_ssl: bool = True

    class Config:
        env_prefix = "spi_"


settings = Settings()

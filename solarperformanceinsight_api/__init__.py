from pydantic import BaseSettings, Json


class Settings(BaseSettings):
    auth_token_url: str = "https://solarperformanceinsight.us.auth0.com/oauth/token"
    auth_jwk_url: str = (
        "https://solarperformanceinsight.us.auth0.com/.well-known/jwks.json"
    )
    auth_key: Json
    auth_audience: str = "https://app.solarperformanceinsight.org/api"
    auth_issuer: str = "https://solarperformanceinsight.us.auth0.com/"

    class Config:
        env_prefix = "spi"


settings = Settings()

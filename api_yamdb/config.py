from dataclasses import dataclass

from environs import Env


@dataclass
class EmailSettings:
    """Конфигурационные настройки smtp Django."""

    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USE_TLS: bool
    EMAIL_USE_SSL: bool
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    DEFAULT_FROM_EMAIL: str


@dataclass
class Config:
    """Конфигурационные настройки всего проекта."""

    email: EmailSettings


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        email=EmailSettings(
            EMAIL_HOST=env('EMAIL_HOST'),
            EMAIL_PORT=env.int('EMAIL_PORT'),
            EMAIL_USE_TLS=env.bool('EMAIL_USE_TLS'),
            EMAIL_USE_SSL=env.bool('EMAIL_USE_SSL'),
            EMAIL_HOST_USER=env('EMAIL_HOST_USER'),
            EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD'),
            DEFAULT_FROM_EMAIL=env('DEFAULT_FROM_EMAIL'),
        )
    )

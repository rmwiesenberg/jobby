from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Optional

import yaml
from jobby.provider import Provider

PROVIDERS = {p.__key__: p for p in Provider.__subclasses__()}

@dataclass
class Config:
    name: str
    output_dir: Path

    providers: list[Provider]

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls, path: Path) -> Optional["Config"]:
        providers = []

        with path.open("r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                logging.warning(exc)
                return None

        search_info = config.get("search", {})
        for provider_key, provider_configs in search_info.get("providers", {}).items():
            if not provider_key in PROVIDERS:
                logging.error(f"Unknown provider {provider_key}")
                continue

            for sub_key, sub_config in provider_configs.items():
                provider = PROVIDERS[provider_key].from_config(sub_key, sub_config)
                if provider is None:
                    logging.error(f"Issue unpacking {provider_key} {sub_key}")
                    continue

                providers.append(provider)

        return Config(
            name=config.get("name", "jobby"),
            output_dir=Path(config.get("output_dir", Path.cwd())),
            providers=providers
        )

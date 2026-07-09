from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from reidcli.diagnostics.logger import get_logger
from reidcli.provider.anthropic import AnthropicProvider
from reidcli.provider.base import BaseProvider
from reidcli.provider.encrypted_store import EncryptedProviderRecord, EncryptedProviderStore, get_encrypted_store
from reidcli.provider.ollama import OllamaProvider
from reidcli.provider.openai import OpenAICompatibleProvider, OpenAIProvider
from reidcli.provider.registry import ProviderRegistry

log = get_logger("reidcli.provider.store")

SUPPORTED_KINDS = ("anthropic", "openai", "openai-compatible", "ollama")


@dataclass
class ProviderRecord:
    name: str
    kind: str
    base_url: str = ""
    api_key: str = ""
    default_model: str = ""


def build_provider(record: ProviderRecord) -> BaseProvider:
    kind = record.kind
    if kind == "anthropic":
        return AnthropicProvider(
            api_key=record.api_key,
            base_url=record.base_url or "https://api.anthropic.com",
            default_model=record.default_model,
        )
    if kind == "openai":
        return OpenAIProvider(
            api_key=record.api_key,
            base_url=record.base_url,
            default_model=record.default_model,
        )
    if kind == "openai-compatible":
        return OpenAICompatibleProvider(
            api_key=record.api_key,
            base_url=record.base_url,
            default_model=record.default_model,
        )
    if kind == "ollama":
        return OllamaProvider(
            base_url=record.base_url,
            default_model=record.default_model,
            api_key=record.api_key,
        )
    raise ValueError(f"unsupported provider kind: {kind}")


class ProviderStore:
    def __init__(self, storage_root: Path) -> None:
        self.legacy_path = Path(storage_root) / "providers.json"
        self.encrypted_store = get_encrypted_store()

    def _migrate_legacy(self) -> None:
        if not self.legacy_path.exists():
            return

        try:
            data = json.loads(self.legacy_path.read_text(encoding="utf-8"))
            legacy_providers = data.get("providers", [])
            if not legacy_providers:
                return

            log.info("Migrating %d legacy providers to encrypted store", len(legacy_providers))
            for entry in legacy_providers:
                try:
                    record = ProviderRecord(**entry)
                    self.encrypted_store.save(record)
                except (TypeError, ValueError):
                    log.warning("Skipping malformed legacy provider: %s", entry)

            backup_path = self.legacy_path.with_suffix(".json.bak")
            self.legacy_path.rename(backup_path)
            log.info("Legacy providers migrated; backup at %s", backup_path)

        except (OSError, ValueError) as e:
            log.warning("Failed to migrate legacy providers: %s", e)

    def _ensure_migrated(self) -> None:
        if not hasattr(self, "_migrated"):
            self._migrate_legacy()
            self._migrated = True

    def list(self) -> list[ProviderRecord]:
        self._ensure_migrated()
        return self.encrypted_store.list()

    def get(self, name: str) -> ProviderRecord | None:
        self._ensure_migrated()
        return self.encrypted_store.get(name)

    def save(self, record: ProviderRecord) -> None:
        self._ensure_migrated()
        self.encrypted_store.save(record)

    def delete(self, name: str) -> bool:
        self._ensure_migrated()
        return self.encrypted_store.delete(name)


def load_into(registry: ProviderRegistry, storage_root: Path) -> list[str]:
    added: list[str] = []
    store = ProviderStore(storage_root)
    for record in store.list():
        try:
            registry.register(record.name, build_provider(record))
            added.append(record.name)
        except (ValueError, TypeError):
            log.exception("skipping provider %s (kind=%s): failed to build", record.name, record.kind)
    return added
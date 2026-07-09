from __future__ import annotations

import base64
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from reidcli.diagnostics.logger import get_logger

if TYPE_CHECKING:
    from reidcli.provider.store import ProviderRecord

log = get_logger("reidcli.provider.encrypted_store")


def _get_storage_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "ReidSH" / "Providers"


def _get_key_path() -> Path:
    return _get_storage_dir() / ".key"


def _get_data_path() -> Path:
    return _get_storage_dir() / "providers.enc"


def _derive_machine_key() -> bytes:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        CRYPTPROTECT_UI_FORBIDDEN = 0x01

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

        crypt32 = ctypes.windll.crypt32

        def dpapi_encrypt(data: bytes) -> bytes:
            blob_in = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)))
            blob_out = DATA_BLOB()
            if not crypt32.CryptProtectData(
                ctypes.byref(blob_in),
                None,
                None,
                None,
                None,
                CRYPTPROTECT_UI_FORBIDDEN,
                ctypes.byref(blob_out),
            ):
                raise OSError("DPAPI encryption failed")
            try:
                return ctypes.string_at(blob_out.pbData, blob_out.cbData)
            finally:
                ctypes.windll.kernel32.LocalFree(blob_out.pbData)

        def dpapi_decrypt(encrypted: bytes) -> bytes:
            blob_in = DATA_BLOB(len(encrypted), ctypes.cast(ctypes.create_string_buffer(encrypted), ctypes.POINTER(ctypes.c_byte)))
            blob_out = DATA_BLOB()
            if not crypt32.CryptUnprotectData(
                ctypes.byref(blob_in),
                None,
                None,
                None,
                None,
                CRYPTPROTECT_UI_FORBIDDEN,
                ctypes.byref(blob_out),
            ):
                raise OSError("DPAPI decryption failed")
            try:
                return ctypes.string_at(blob_out.pbData, blob_out.cbData)
            finally:
                ctypes.windll.kernel32.LocalFree(blob_out.pbData)

        key_path = _get_key_path()
        key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_path.exists():
            try:
                encrypted_key = key_path.read_bytes()
                return dpapi_decrypt(encrypted_key)
            except OSError:
                log.warning("Failed to decrypt stored key, generating new one")

        fernet_key = Fernet.generate_key()
        encrypted_key = dpapi_encrypt(fernet_key)
        key_path.write_bytes(encrypted_key)
        try:
            import subprocess
            subprocess.run(["icacls", str(key_path), "/inheritance:r", "/grant:r", f"{os.getlogin()}:F"], check=False, capture_output=True)
        except Exception:
            pass
        return fernet_key

    else:
        try:
            import keyring
        except ImportError:
            machine_id = ""
            for path in [Path("/etc/machine-id"), Path("/var/lib/dbus/machine-id")]:
                if path.exists():
                    machine_id = path.read_text().strip()
                    break
            if not machine_id:
                machine_id = str(os.getuid())
            salt = (machine_id + os.getlogin()).encode()
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt[:16].ljust(16, b"0"), iterations=100_000)
            return base64.urlsafe_b64encode(kdf.derive(b"reidcli-provider-store"))

        keyring_service = "reidcli"
        keyring_user = "provider-store-key"
        stored = keyring.get_password(keyring_service, keyring_user)
        if stored:
            return base64.urlsafe_b64decode(stored.encode())

        fernet_key = Fernet.generate_key()
        keyring.set_password(keyring_service, keyring_user, base64.urlsafe_b64encode(fernet_key).decode())
        return fernet_key


_FERNET_KEY = _derive_machine_key()
_FERNET = Fernet(_FERNET_KEY)


@dataclass
class EncryptedProviderRecord:
    name: str
    kind: str
    base_url: str = ""
    api_key_enc: str = ""
    default_model: str = ""

    @classmethod
    def from_record(cls, record: "ProviderRecord") -> "EncryptedProviderRecord":
        api_key_enc = ""
        if record.api_key:
            encrypted = _FERNET.encrypt(record.api_key.encode())
            api_key_enc = base64.urlsafe_b64encode(encrypted).decode()
        return cls(
            name=record.name,
            kind=record.kind,
            base_url=record.base_url,
            api_key_enc=api_key_enc,
            default_model=record.default_model,
        )

    def to_record(self) -> "ProviderRecord":
        api_key = ""
        if self.api_key_enc:
            try:
                encrypted = base64.urlsafe_b64decode(self.api_key_enc.encode())
                api_key = _FERNET.decrypt(encrypted).decode()
            except Exception:
                log.warning("Failed to decrypt api_key for provider %s", self.name)
                api_key = ""
        from reidcli.provider.store import ProviderRecord
        return ProviderRecord(
            name=self.name,
            kind=self.kind,
            base_url=self.base_url,
            api_key=api_key,
            default_model=self.default_model,
        )


class EncryptedProviderStore:
    def __init__(self) -> None:
        self.path = _get_data_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read_raw(self) -> list[EncryptedProviderRecord]:
        if not self.path.exists():
            return []
        try:
            encrypted_data = self.path.read_bytes()
            decrypted = _FERNET.decrypt(encrypted_data)
            data = json.loads(decrypted.decode())
            return [EncryptedProviderRecord(**entry) for entry in data.get("providers", [])]
        except Exception as e:
            log.exception("Failed to read encrypted providers: %s", e)
            return []

    def _write_raw(self, records: list[EncryptedProviderRecord]) -> None:
        data = {"providers": [asdict(r) for r in records]}
        encrypted = _FERNET.encrypt(json.dumps(data).encode())
        self.path.write_bytes(encrypted)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def list(self) -> list["ProviderRecord"]:
        return [r.to_record() for r in self._read_raw()]

    def get(self, name: str) -> "ProviderRecord | None":
        for r in self._read_raw():
            if r.name == name:
                return r.to_record()
        return None

    def save(self, record: "ProviderRecord") -> None:
        records = [r for r in self._read_raw() if r.name != record.name]
        records.append(EncryptedProviderRecord.from_record(record))
        self._write_raw(records)

    def delete(self, name: str) -> bool:
        records = self._read_raw()
        remaining = [r for r in records if r.name != name]
        if len(remaining) == len(records):
            return False
        self._write_raw(remaining)
        return True


def get_encrypted_store() -> EncryptedProviderStore:
    return EncryptedProviderStore()
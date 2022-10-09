# Settings for the test server.

import random
import hashlib
import hmac
import os
import secrets
import xfuzz._typing as _t
from pydantic import BaseSettings, Field
from test.wordlists import get_common, get_subdomains


def hkdf(
    ikm: bytes,
    info: bytes,
    salt: _t.Optional[bytes] = None,
    length: int = 32,
    hash=hashlib.sha256,
) -> bytes:
    """Use the Hash-Based Key Derivation Function (HKDF) to generate a new
    domain-specific cryptographically secure random key.

    Sources:
    - IETF RFC 5869: https://www.rfc-editor.org/rfc/rfc5869
    - "Cryptographic Extraction and Key Derivation: The HKDF Scheme" (Kraczyk 2010)
    """

    salt = salt.encode("utf-8") if salt is not None else b"\x00" * length
    hmac_hash = lambda key, msg: hmac.new(key, msg, hash).digest()

    # Create an instantion of the hash function to determine what the length of
    # its generated hashes is
    hash_length = len(hash(b"").digest())

    # Extract (§2.2)
    prk = hmac_hash(salt, ikm)

    # Expand (§2.3)
    N = (length - 1) // hash_length + 1
    okm = T = b""
    for i in range(N):
        msg = T + info + ((i + 1) % 256).to_bytes(1, "big")
        T = hmac_hash(prk, msg)
        okm += T

    return okm[:length]


def generate_key() -> str:
    """Generate a random HKDF key for testing."""

    key = os.getenv("XFUZZ_TEST_KEY")
    if key is None:
        return secrets.token_urlsafe()

    return key


class Settings(BaseSettings):
    """Configuration options for the test server."""

    class Config:
        allow_mutation = False
        extra = "forbid"

    # The OpenAPI configuration URL.
    openapi_url: str = "/openapi.json"

    # Wordlist to pass in to xfuzz and to use for testing configuration
    wordlist: _t.List[str] = Field(default_factory=get_common)

    # A secret token that can be used to generate additional secret tokens
    key: str = Field(default_factory=generate_key)

    def create_token(self, msg: str) -> bytes:
        return hkdf(self.key.encode("utf-8"), msg.encode("utf-8"))

    def create_token_int(self, msg: str) -> int:
        return int.from_bytes(self.create_token(msg), "little")

    def random_word(self, token_msg: str, wordlist: _t.Optional[_t.List] = None) -> str:
        """Select a random word from the wordlist after seeding the RNG with a value
        deterministically generated from the input token message."""

        if wordlist is None:
            wordlist = self.wordlist

        random.seed(self.create_token_int(token_msg))
        return random.choice(wordlist)

    def ext_router_endpoint(self) -> str:
        return self.random_word("ext-router-endpoint")

    def auth_router_password(self) -> str:
        return self.random_word("auth-router-password")

    def vhost_router_domain(self) -> str:
        subdomain = self.random_word("vhost-router-subdomain", get_subdomains())
        return f"{subdomain}.example.org"

    def user_uid(self) -> int:
        """Return a random user ID for the user search API simulation."""

        return self.create_token_int("user-uid") % 5000

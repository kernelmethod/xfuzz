# Settings for the test server.

import random
import os
import secrets
import xfuzz._typing as _t
from pydantic import BaseSettings, Field
from test.wordlists import get_common, get_subdomains
from test.utils import hkdf


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

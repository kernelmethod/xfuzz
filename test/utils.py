import asyncio
import hashlib
import hmac
import platform
import pytest
import shlex
import subprocess as sp
import typing as _t
from contextlib import asynccontextmanager
from dataclasses import dataclass


@dataclass
class FuzzArgs:
    args: _t.List[str]

    def __init__(self, args):
        self.args = args

    @property
    def popen_args(self) -> _t.List[str]:
        """Return a list of string arguments for ``subprocess.Popen`` so that these arguments
        can be used to run ``xfuzz`` in another process."""

        if platform.system().lower() == "windows":
            python = "py"
        else:
            python = "python3"

        return [python, "-m", "xfuzz"] + self.args

    @property
    def command(self) -> str:
        return " ".join(shlex.quote(arg) for arg in self.popen_args)


def clitest(args):
    """Decorator to apply for CLI tests."""

    return lambda f: pytest.mark.parametrize("cliargs", [args])(f)


def servertest(func):
    """Decorator to apply to all of the server-related tests."""
    func = pytest.mark.asyncio(func)
    return func


def xfuzztest(args):
    """Decorator to apply to all of the xfuzz command line interface tests."""

    def decorator(f):
        f = clitest(args)(f)
        f = pytest.mark.skipif("config.getoption('skip_cli_tests')")(f)
        f = pytest.mark.asyncio(f)

        return f

    return decorator


@asynccontextmanager
async def fuzz_proc(fuzz_args, timeout: float = 60):
    """Run ``xfuzz`` in another process and wrap it in an async context. Wait for the process
    to terminate at the end of the context."""

    proc = sp.Popen(fuzz_args.popen_args, stdin=sp.PIPE)
    loop = asyncio.get_event_loop()

    try:
        yield proc
    finally:
        wait = lambda: proc.wait(timeout=timeout)
        try:
            await loop.run_in_executor(None, wait)
        except sp.TimeoutExpired as ex:
            assert False, (
                f"{type(ex).__name__} exception raised after waiting for fuzzer process to terminate.\n"
                f"Command: `{fuzz_args.command}`"
            )


def hkdf_prk(ikm: bytes, salt: bytes, hash=hashlib.sha256) -> bytes:
    return hmac.new(salt, ikm, hash).digest()


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

    hash_length = hash().digest_size

    salt = salt if salt is not None else b"\x00" * length
    hmac_hash = lambda key, msg: hmac.new(key, msg, hash).digest()

    # Extract (§2.2)
    prk = hkdf_prk(ikm, salt)

    # Expand (§2.3)
    N = (length - 1) // hash_length + 1
    okm = T = b""
    for i in range(N):
        msg = T + info + ((i + 1) % 256).to_bytes(1, "big")
        T = hmac_hash(prk, msg)
        okm += T

    return okm[:length]

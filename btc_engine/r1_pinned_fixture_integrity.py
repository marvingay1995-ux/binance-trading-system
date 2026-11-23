"""BTC-073: immutable, independently pinned fingerprints for invented fixtures.

Static literals only; these are NOT exchange data authenticity checks. Do not
derive expected digests from the mutable BTC-069 registry.
"""
import hashlib
import hmac
from types import MappingProxyType

EXPECTED_SHA256 = MappingProxyType({
    "1h": "a4b2e8cb1f225712f4803f4c1eefdeaf2a6cb1dfb94f52dbdd6f4bb9585cbb68",
    "4h": "1b187fb2888816428a0aa3ac3edfb7ffb9e30d3e0b6597d95dff56f131bbbddf",
})
EXPECTED_SIZE = 246

def assert_registered_invented_bytes(interval, body):
    if type(interval) is not str or interval not in EXPECTED_SHA256:
        raise ValueError("UNAPPROVED_SYNTHETIC_INTERVAL")
    if type(body) is not bytes or len(body) != EXPECTED_SIZE:
        raise PermissionError("FROZEN_SYNTHETIC_BYTES_MISMATCH")
    digest = hashlib.sha256(body).hexdigest()
    if not hmac.compare_digest(digest, EXPECTED_SHA256[interval]):
        raise PermissionError("FROZEN_SYNTHETIC_BYTES_MISMATCH")
    return digest

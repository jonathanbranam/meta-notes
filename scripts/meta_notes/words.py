"""Hand-type a secret as checked words (proquints).

encode turns bytes into lines of words; decode reads the lines back, checking
each line as it is typed. Format (see design/specs/words.md):

  encoded message = 1 code byte + the remaining bytes. Code 0: no table
  entry. Code N: TABLE[N-1], a prefix and optional footer removed from the
  original. The table is append-only; never renumber or reorder it.

  Every 16 bits is one word. Line 0 is a header of 4 data words (32-bit
  length of the encoded message, first 32 bits of the SHA-256 of the ORIGINAL
  bytes) and a check word. Data lines are up to 4 data words and a check word.
  An odd byte count is padded with a zero byte. Empty input is a header only.
"""

import hashlib
import struct
from typing import Callable

CONSONANTS = "bdfghjklmnprstvz"
VOWELS = "aiou"
ROW_WORDS = 4


class WordsError(Exception):
    """The words could not be encoded or decoded; the message says why."""


# -- The prefix and header table ----------------------------------------------

_ED25519_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAI"
_RSA_KEY = "AAAAB3NzaC1yc2EAAAADAQAB"
_ECDSA_KEY = "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlz"
_SK_KEY = "AAAAGnNrLXNzaC1lZDI1NTE5QG9wZW5zc2guY29t"
_OPENSSH_BODY = "b3BlbnNzaC1rZXktdjEAAAAA"


def _build_table() -> list[tuple[bytes, bytes]]:
    """(prefix, footer) pairs; the code of an entry is its index + 1."""
    out: list[tuple[str, str]] = []
    for p in ("github_pat_", "ghp_", "gho_", "ghu_", "ghs_", "ghr_"):
        out.append((p, ""))
    for kind, key in (("ssh-ed25519", _ED25519_KEY), ("ssh-rsa", _RSA_KEY),
                      ("ecdsa-sha2-nistp256", _ECDSA_KEY),
                      ("sk-ssh-ed25519@openssh.com", _SK_KEY)):
        out.append((kind + " ", ""))
        out.append((kind + " " + key, ""))

    def armor(label: str, body: str = "") -> None:
        begin = f"-----BEGIN {label}-----\n" + body
        end = f"-----END {label}-----"
        out.append((begin, end + "\n"))
        out.append((begin, end))

    armor("OPENSSH PRIVATE KEY")
    armor("OPENSSH PRIVATE KEY", _OPENSSH_BODY)
    for label in ("PRIVATE KEY", "RSA PRIVATE KEY", "EC PRIVATE KEY",
                  "ENCRYPTED PRIVATE KEY", "CERTIFICATE",
                  "PGP PUBLIC KEY BLOCK", "PGP PRIVATE KEY BLOCK",
                  "PGP MESSAGE"):
        armor(label)
    for p in ("AKIA", "ASIA", "npm_", "pypi-", "pypi-AgEIcHlwaS5vcmc", "eyJ",
              "eyJhbGciOi"):
        out.append((p, ""))
    return [(a.encode("ascii"), b.encode("ascii")) for a, b in out]


TABLE = _build_table()


def _choose_entry(data: bytes) -> int:
    """The code of the longest table entry matching data, or 0."""
    best, best_len = 0, 0
    for i, (prefix, footer) in enumerate(TABLE, 1):
        size = len(prefix) + len(footer)
        if size <= best_len or len(data) < size:
            continue
        if data.startswith(prefix) and data.endswith(footer):
            best, best_len = i, size
    return best


def _pack(data: bytes) -> tuple[bytes, int]:
    """The encoded message for data: code byte, then the rest."""
    if not data:
        return b"", 0
    code = _choose_entry(data)
    if code == 0:
        return b"\x00" + data, 0
    prefix, footer = TABLE[code - 1]
    return bytes([code]) + data[len(prefix):len(data) - len(footer)], code


def _unpack(msg: bytes) -> bytes:
    if not msg:
        return b""
    code = msg[0]
    if code == 0:
        return msg[1:]
    if code > len(TABLE):
        raise WordsError(
            f"the message uses table entry {code}, which this meta-notes "
            "does not know; update meta-notes on this machine")
    prefix, footer = TABLE[code - 1]
    return prefix + msg[1:] + footer


# -- Words ----------------------------------------------------------------------

def word(n: int) -> str:
    c, v = CONSONANTS, VOWELS
    return (c[n >> 12 & 15] + v[n >> 10 & 3] + c[n >> 6 & 15]
            + v[n >> 4 & 3] + c[n & 15])


def number(w: str) -> int:
    """The 16-bit number of a word; ValueError when it is not a word."""
    if len(w) != 5:
        raise ValueError(w)
    a, b, c, d, e = w
    return (CONSONANTS.index(a) << 12 | VOWELS.index(b) << 10
            | CONSONANTS.index(c) << 6 | VOWELS.index(d) << 4
            | CONSONANTS.index(e))


def check(index: int, row: list[int]) -> int:
    """The check word's number for line index and its data words."""
    packed = struct.pack(f">I{len(row)}H", index, *row)
    h = hashlib.sha256(packed).digest()
    return h[0] << 8 | h[1]


def _line(index: int, row: list[int]) -> str:
    return " ".join(word(x) for x in row + [check(index, row)])


def _digest(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()[:4]


def encode(data: bytes) -> list[str]:
    """Lines of words for data; the first is the header."""
    msg, _ = _pack(data)
    header = struct.pack(">I", len(msg)) + _digest(data)
    lines = [_line(0, list(struct.unpack(">4H", header)))]
    if len(msg) % 2:
        msg += b"\x00"
    nums = list(struct.unpack(f">{len(msg) // 2}H", msg))
    for i in range(0, len(nums), ROW_WORDS):
        lines.append(_line(i // ROW_WORDS + 1, nums[i:i + ROW_WORDS]))
    return lines


def parse_line(index: int, text: str, count: int) -> list[int]:
    """The count data words of a typed line, checked; WordsError if bad."""
    words = text.lower().split()
    if len(words) != count + 1:
        raise WordsError(f"expected {count + 1} words, got {len(words)}")
    try:
        nums = [number(w) for w in words]
    except ValueError:
        raise WordsError("not a word of this kind (letters b d f g h j k l "
                         "m n p r s t v z, vowels a i o u)") from None
    if nums[-1] != check(index, nums[:-1]):
        raise WordsError("check word does not match")
    return nums[:-1]


def decode(readline: Callable[[], str], *, interactive: bool = False,
           prompt: Callable[[str], None] = lambda s: None,
           report: Callable[[str], None] = lambda s: None) -> bytes:
    """Read the lines with readline and return the original bytes.

    A blank line asks again. A bad line is reported and asked again when
    interactive, otherwise it raises WordsError, as does the end of input
    before the last line and a whole-message mismatch.
    """
    def get(index: int, count: int, label: str) -> list[int]:
        while True:
            prompt(label)
            text = readline()
            if text == "":
                raise WordsError(f"input ended before {label}")
            if not text.strip():
                continue
            try:
                return parse_line(index, text, count)
            except WordsError as e:
                if not interactive:
                    raise WordsError(f"{label}: {e}") from None
                report(f"{e}; retype this line")

    h = get(0, 4, "the header line")
    length = h[0] << 16 | h[1]
    digest = struct.pack(">2H", h[2], h[3])
    words = (length + 1) // 2
    total = -(-words // ROW_WORDS)
    nums: list[int] = []
    for i in range(1, total + 1):
        count = min(ROW_WORDS, words - len(nums))
        nums += get(i, count, f"line {i} of {total}")
    msg = struct.pack(f">{len(nums)}H", *nums)
    if len(msg) > length:
        if msg[length:] != b"\x00":
            raise WordsError("the padding is not zero")
        msg = msg[:length]
    data = _unpack(msg)
    if _digest(data) != digest:
        raise WordsError("the whole-message check failed; the lines typed "
                         "do not make the message that was encoded")
    return data

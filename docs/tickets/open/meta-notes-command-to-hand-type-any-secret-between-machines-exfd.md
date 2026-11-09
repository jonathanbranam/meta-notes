---
id: mn-exfd
title: meta-notes command to hand-type any secret between machines as checked words (words.py)
kind: feature
created: 2026-11-09
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

From the human, 2026-11-09, relayed by the glassbox aide (m-0318, m-0319) and confirmed directly in the meta-notes aide session.

Request, verbatim (via glassbox aide): "I want words.py to get into the meta-notes project as a meta-notes CLI command. Send the information, purpose, and words.py implementation to aide@meta-notes for immediate implementation"

Confirmation and scope, verbatim (meta-notes aide session): "yes, this is my request; it should work for any secret, just encode everything in the string; i realize that is unnecessary for many keys but just make it generic to any text or even binary input (likely would be base64 or similar encoded)"

## Purpose

Move a secret by hand between machines that share no clipboard, e.g. onto the human's work Mac (first use: a GitHub fine-grained token, about 93 chars). The human's requirement, verbatim: "if I'm typing this in it needs some validation like CRC that runs immediately". Each typed line is checked the moment Enter is pressed. A check only at the end does not meet it.

## What to build

A meta-notes CLI command (name is the planner's) with encode and decode, based on words.py below.

- **Generic input.** Encode the input's bytes exactly: any text or binary, all of it. This removes words.py's unchecked prefix stripping (it drops the first 11 chars of anything) and its base-63 alphabet (characters outside it raise a bare ValueError).
- **Common prefixes and headers (required in this version; the human's decision).** The human, verbatim (meta-notes aide session, 2026-11-09): "i'm fine with special encoding for common prefixes like gpg_ and the github pat token, ssh key introductory lines like the key type", then, on seeing the list below and that the planner had left prefixes out: "definitely agree on the SSH public keys, private key headers, PEM, GPG, those all I may use commonly. github i use commonly. the others i don't care so much about."

  The table covers (values from the aide's memory; confirm each against real fake-key output, e.g. `ssh-keygen` and `gpg --armor` on throwaway keys):
  - GitHub: `github_pat_`, `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`.
  - SSH public keys: the key types `ssh-ed25519 `, `ssh-rsa `, `ecdsa-sha2-nistp256 `, `sk-ssh-ed25519@openssh.com `, with the fixed start of the key data where there is one (`AAAAC3NzaC1lZDI1NTE5AAAAI` for ed25519, `AAAAB3NzaC1yc2EAAAADAQAB` for typical RSA).
  - OpenSSH private keys: `-----BEGIN OPENSSH PRIVATE KEY-----` with its `END` line, and the fixed body start `b3BlbnNzaC1rZXktdjEAAAAA`.
  - PEM: `BEGIN`/`END` lines for `PRIVATE KEY`, `RSA PRIVATE KEY`, `EC PRIVATE KEY`, `ENCRYPTED PRIVATE KEY`, `CERTIFICATE`.
  - GPG: `BEGIN`/`END` lines for `PGP PUBLIC KEY BLOCK`, `PGP PRIVATE KEY BLOCK`, `PGP MESSAGE`.

  - AWS key IDs, npm, PyPI and JWT: the human, verbatim (meta-notes aide session, 2026-11-09): "go ahead and add the AWS key IDs as well since I use it often; I'm fine also including: npm, pypi, JWT". AWS `AKIA` and `ASIA`; `npm_`; `pypi-` (with the longer fixed start `pypi-AgEIcHlwaS5vcmc` if confirmed); JWT `eyJ` (with the common longer start `eyJhbGciOi` as its own entry, since `eyJ` alone saves almost nothing).

  Other services' prefixes (GitLab, Anthropic, OpenAI, Slack, Stripe, Google and so on) are out: "the others i don't care so much about".

  Rules: a prefix or footer is matched, never assumed; anything else encodes in full; decode restores the exact original bytes, including the line endings around a header or footer (if they don't match the table's form, encode in full); the table is part of the format, so encoder and decoder must agree on it (a format version or check that fails clearly). No per-token alphabet such as base-63.
- **Words.** Proquints as in words.py: every 16 bits is one 5-letter consonant-vowel-consonant-vowel-consonant word. Lines of 4 data words plus 1 check word.
- **Per-line check.** Check word is derived from the line index and the row, so typos and swapped or skipped lines are rejected when Enter is pressed, and the line can be retyped.
- **Whole-message check (aide's recommendation; the human did not object).** The first line carries the length or line count and a whole-message check, so decode knows when it is complete. Finishing early must not produce a truncated secret. It needs to work for an odd byte count too.
- **Input.** Hidden prompt on a tty, stdin otherwise. Never accept the secret as a command-line argument (shell history).
- **Output.** Decode prompts on stderr and writes exactly the bytes to stdout, so `| pbcopy` works and binary survives. Say in the help how a trailing newline from `echo` or a file is treated; the planner picks the behaviour, and exact round trips of binary must hold.

## Getting decode onto the work laptop

No special route is needed. The human, verbatim (meta-notes aide session, 2026-11-09): "meta-notes CLI works fine on the work laptop already i use it daily"

So encode and decode are ordinary `meta-notes` subcommands in the `scripts/meta_notes/` package, on the CLI's usual Python 3.11+ and standard library. No standalone file and no clone-and-run steps. This replaces the glassbox aide's constraint that the laptop may have only stock Python. The laptop gets the command by updating its meta-notes checkout as usual.

## Safety

No real secret in messages, tickets, tests or fixtures. Fake values only.

## Tested so far (glassbox aide, on the old format)

300 of 300 round trips and 300 of 300 injected single-letter typos rejected, fake tokens only. Not tested with a real token or on a Mac. The generic format needs its own tests: empty input, odd lengths, binary bytes, typo rejection, swapped and skipped lines, early finish.

Specs, unit tests, Vim help or README as the rules require, version bump, CHANGELOG.

## When it is usable

Tell the aide, which tells the human (with the version) and glassbox (external:aide --project glassbox).

## words.py as relayed, verbatim (36 lines; sha256 7c8e75890d904d6317c591eb893e2759849ffe00bf0e0a89164633b90648df23)

Starting point only: the format changes as above.

```python
import getpass, hashlib, sys
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
C, V, P = "bdfghjklmnprstvz", "aiou", "github_pat_"
def word(n): return C[n>>12&15]+V[n>>10&3]+C[n>>6&15]+V[n>>4&3]+C[n&15]
def num(w):
    a, b, c, d, e = w
    return C.index(a)<<12 | V.index(b)<<10 | C.index(c)<<6 | V.index(d)<<4 | C.index(e)
def check(i, row):
    h = hashlib.sha256(repr((i, row)).encode()).digest()
    return h[0]<<8 | h[1]
if sys.argv[1] == "e":
    t = getpass.getpass("token: ") if sys.stdin.isatty() else sys.stdin.read().strip()
    n = 1
    for ch in t[len(P):]: n = n*63 + A.index(ch)
    ns = []
    while n: ns.insert(0, n & 65535); n >>= 16
    for i in range(0, len(ns), 4):
        row = ns[i:i+4]
        print(" ".join(word(x) for x in row + [check(i//4, row)]))
else:
    ns, i = [], 0
    while True:
        print(f"line {i+1} (blank to finish): ", end="", file=sys.stderr, flush=True)
        s = sys.stdin.readline().lower().split()
        if not s: break
        try:
            *row, c = [num(w) for w in s]
            ok = c == check(i, row)
        except ValueError:
            ok = False
        if ok: ns += row; i += 1
        else: print("typo on this line, retype it", file=sys.stderr)
    n, out = 0, ""
    for x in ns: n = n<<16 | x
    while n > 1: out = A[n%63] + out; n //= 63
    print(P + out)
```

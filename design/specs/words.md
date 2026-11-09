# words Specification

## Purpose
Specifies `meta-notes words encode` and `meta-notes words decode`, which move a secret by hand between machines that share no clipboard: the secret is typed as lines of checked proquint words, and each line is checked the moment Enter is pressed.

## Requirements

### Requirement: Exact generic encoding  {#r-60a9}
`meta-notes words encode` SHALL read all of stdin as bytes (or a hidden prompt on a terminal, with no newline added) and print lines of words for exactly those bytes, text or binary, with no stripping or alphabet restriction. It SHALL NOT take the secret as an argument. It SHALL work with no notes root.

#### Scenario: Trailing newline is kept  {#s-a6eb}
*Verification*: **non-executable**
- **WHEN** the input is `echo abc | meta-notes words encode`
- **THEN** the decoded bytes SHALL be `abc` and a newline

#### Scenario: Binary round trip  {#s-e11e}
*Verification*: **non-executable**
- **WHEN** the input is all 256 byte values, or is empty, or has an odd length
- **THEN** decode SHALL write exactly those bytes

### Requirement: Line format  {#r-f973}
Every 16 bits SHALL be one five-letter word (consonant, vowel, consonant, vowel, consonant). Line 0 SHALL be a header of 4 data words (the 32-bit length of the encoded message, and the first 32 bits of the SHA-256 of the original bytes) and a check word. Each data line SHALL be up to 4 data words and a check word, the check word derived from the line index and the row's packed bytes. An odd byte count SHALL be padded with a zero byte and trimmed using the length. Empty input SHALL be the header only.

#### Scenario: Typo, swap and skip  {#s-94c5}
*Verification*: **non-executable**
- **WHEN** a line has one wrong letter, or lines are swapped or one is skipped
- **THEN** decode SHALL reject the line or the message

### Requirement: Prefix and header table  {#r-67cc}
The encoded message SHALL be one code byte followed by the remaining bytes. Code 0 SHALL mean no table entry. Other codes SHALL name an entry of an append-only table, each a prefix and optional footer, never renumbered. The table SHALL cover: GitHub token prefixes (`github_pat_`, `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`); SSH public key types with the fixed start of the key data; OpenSSH private key BEGIN and END lines with the fixed body start; PEM BEGIN and END lines for `PRIVATE KEY`, `RSA PRIVATE KEY`, `EC PRIVATE KEY`, `ENCRYPTED PRIVATE KEY` and `CERTIFICATE`; GPG armor lines for `PGP PUBLIC KEY BLOCK`, `PGP PRIVATE KEY BLOCK` and `PGP MESSAGE`; AWS `AKIA` and `ASIA`; `npm_`; `pypi-` and `pypi-AgEIcHlwaS5vcmc`; JWT `eyJ` and `eyJhbGciOi`. The longest matching entry SHALL win. An entry with a footer SHALL match only when both ends match with their exact line endings (LF, with or without a final newline); otherwise the input SHALL be encoded in full. Decode SHALL restore the exact original bytes.

#### Scenario: Footer missing or CRLF  {#s-d2e5}
*Verification*: **non-executable**
- **WHEN** input starts with a table BEGIN line but has no matching END line, or uses CRLF line endings
- **THEN** it SHALL be encoded in full (code 0) and decode SHALL restore it byte for byte

#### Scenario: Unknown code  {#s-57e0}
*Verification*: **non-executable**
- **WHEN** a message names a table entry the decoder does not have
- **THEN** decode SHALL fail with a message saying so and write nothing to stdout

### Requirement: Decode checks as typed  {#r-7ff1}
`meta-notes words decode` SHALL prompt on stderr, check each line when Enter is pressed, and know the line and word counts from the header. On a terminal a bad line SHALL be rejected and typed again; a blank line SHALL ask again. On a non-terminal stdin a bad line, or end of input before the last line, SHALL exit non-zero. A whole-message mismatch SHALL exit non-zero. It SHALL write the exact bytes to stdout only after the whole check passes, and nothing otherwise.

#### Scenario: Early finish  {#s-81bc}
*Verification*: **non-executable**
- **WHEN** input ends before the last line
- **THEN** the command SHALL exit non-zero with nothing on stdout

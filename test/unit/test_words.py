"""Unit tests for meta_notes.words and the `meta-notes words` command.

Fake values only; no real secret appears here.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

repo_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_dir / 'scripts'))

from meta_notes import words  # noqa: E402


def roundtrip(data):
    it = iter(words.encode(data))
    return words.decode(lambda: next(it, '') + '\n')


def code_of(data):
    return words._pack(data)[1]


def run(args, stdin, tmp_path):
    env = {**os.environ, 'HOME': str(tmp_path)}
    return subprocess.run([sys.executable, str(repo_dir / 'scripts' / 'meta_notes')] + args,
                          input=stdin, capture_output=True, cwd=tmp_path, env=env)


def decode_lines(lines, interactive=False):
    it = iter(lines)
    return words.decode(lambda: next(it, ''), interactive=interactive)


# Tests for round trips

def test_words_encode_empty_is_header_only():
    assert len(words.encode(b'')) == 1
    assert roundtrip(b'') == b''


@pytest.mark.parametrize('n', [1, 2, 3, 7, 8, 9, 15, 16, 17, 64, 93, 1000])
def test_words_roundtrip_lengths(n):
    data = bytes((i * 7 + 3) % 251 for i in range(n))
    assert roundtrip(data) == data


def test_words_roundtrip_all_byte_values():
    data = bytes(range(256))
    assert roundtrip(data) == data
    assert roundtrip(bytes(range(255, -1, -1))) == bytes(range(255, -1, -1))


def test_words_roundtrip_trailing_newline_is_kept():
    assert roundtrip(b'abc\n') == b'abc\n'
    assert roundtrip(b'abc') == b'abc'


# Tests for line checks

def test_words_parse_line_every_single_letter_typo_rejected():
    lines = words.encode(b'fake secret value, fake!')
    for index, line in enumerate(lines):
        count = len(line.split()) - 1
        chars = list(line)
        for pos, ch in enumerate(chars):
            if ch == ' ':
                continue
            for other in 'abcdefghijklmnopqrstuvwxyz':
                if other == ch:
                    continue
                typo = ''.join(chars[:pos] + [other] + chars[pos + 1:])
                with pytest.raises(words.WordsError):
                    words.parse_line(index, typo, count)


def test_words_decode_swapped_lines_rejected():
    lines = words.encode(bytes(range(40)))
    swapped = [lines[0], lines[2], lines[1]] + lines[3:]
    with pytest.raises(words.WordsError):
        decode_lines(swapped)


def test_words_decode_skipped_line_rejected():
    lines = words.encode(bytes(range(40)))
    with pytest.raises(words.WordsError):
        decode_lines(lines[:2] + lines[3:])


def test_words_decode_early_finish_refused():
    lines = words.encode(bytes(range(40)))
    with pytest.raises(words.WordsError):
        decode_lines(lines[:-1])


def test_words_decode_wrong_word_count_rejected():
    lines = words.encode(bytes(range(40)))
    short = lines[1].rsplit(' ', 2)
    with pytest.raises(words.WordsError):
        decode_lines([lines[0], ' '.join(short)])


def test_words_decode_blank_lines_ask_again():
    lines = words.encode(b'hello')
    assert decode_lines([lines[0], '\n', '  \n'] + [x + '\n' for x in lines[1:]]) == b'hello'


def test_words_decode_interactive_bad_line_retyped():
    lines = words.encode(b'hello world, fake')
    typed = [lines[0], 'babab babab babab babab babab', lines[1], lines[2], lines[3]]
    assert decode_lines(typed, interactive=True) == b'hello world, fake'


def test_words_decode_not_a_word_rejected():
    with pytest.raises(words.WordsError):
        decode_lines(['hello world fake words here'])


def test_words_decode_whole_message_mismatch_rejected():
    # a valid header from one message with the body of another of equal size
    a = words.encode(b'AAAAAAAA')
    b = words.encode(b'BBBBBBBB')
    with pytest.raises(words.WordsError, match='whole-message'):
        decode_lines([a[0]] + b[1:])


def test_words_decode_unknown_code_fails_clearly():
    msg = bytes([200]) + b'abc'
    header = words._line(0, [0, len(msg), 0, 0])
    nums = [int.from_bytes(msg[i:i + 2], 'big') for i in (0, 2)]
    with pytest.raises(words.WordsError, match='table entry 200'):
        decode_lines([header, words._line(1, nums)])


# Tests for the prefix table

def test_words_table_every_entry_roundtrips():
    for i, (prefix, footer) in enumerate(words.TABLE, 1):
        data = prefix + b'FAKEBODY\nmore' + footer
        assert code_of(data) == i or code_of(data) > i, (i, prefix)
        assert roundtrip(data) == data
        assert roundtrip(prefix + footer) == prefix + footer


def test_words_table_codes_are_append_only():
    assert words.TABLE[0][0] == b'github_pat_'
    assert words.TABLE[5][0] == b'ghr_'
    assert words.TABLE[-1][0] == b'eyJhbGciOi'
    assert len(words.TABLE) == 41


def test_words_pack_short_code_saves_the_prefix():
    assert len(words.encode(b'ghp_' + b'x' * 36)) <= len(words.encode(b'x' * 36)) + 1
    assert code_of(b'ghp_abc') == 2


def test_words_pack_longest_match_wins():
    assert words.TABLE[code_of(b'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIabc') - 1][0].endswith(b'AAAAI')
    assert words.TABLE[code_of(b'eyJhbGciOiJIUzI1NiJ9.x') - 1][0] == b'eyJhbGciOi'
    assert words.TABLE[code_of(b'eyJabc') - 1][0] == b'eyJ'


def test_words_pack_armor_with_footer_uses_entry():
    data = b'-----BEGIN PGP MESSAGE-----\n\nabc\n-----END PGP MESSAGE-----\n'
    assert code_of(data) != 0
    assert roundtrip(data) == data


def test_words_pack_armor_without_footer_encodes_in_full():
    data = b'-----BEGIN PGP MESSAGE-----\n\nabc\n'
    assert code_of(data) == 0
    assert roundtrip(data) == data


def test_words_pack_armor_crlf_encodes_in_full():
    both = b'-----BEGIN CERTIFICATE-----\r\nabc\r\n-----END CERTIFICATE-----\r\n'
    footer_only = b'-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----\r\n'
    for data in (both, footer_only):
        assert code_of(data) == 0
        assert roundtrip(data) == data


def test_words_pack_armor_footer_without_final_newline_is_an_entry():
    data = b'-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----'
    assert code_of(data) != 0
    assert roundtrip(data) == data


def test_words_pack_lookalike_encodes_in_full():
    for data in (b'ghp', b'ghx_abc', b'ssh-ed2551 AAAA', b'-----BEGIN PGP MESSAGE----\n',
                 b'github_pat', b'AKI', b'ey'):
        assert code_of(data) == 0
        assert roundtrip(data) == data


def test_words_pack_overlapping_prefix_and_footer_not_matched():
    # shorter than prefix + footer together
    data = b'-----BEGIN PGP MESSAGE-----\n'
    assert roundtrip(data) == data


# Tests for the command

def test_words_command_stdout_is_exactly_the_bytes(tmp_path):
    data = bytes(range(256)) + b'\n'
    enc = run(['words', 'encode'], data, tmp_path)
    assert enc.returncode == 0
    dec = run(['words', 'decode'], enc.stdout, tmp_path)
    assert dec.returncode == 0
    assert dec.stdout == data


def test_words_command_decode_failure_writes_nothing(tmp_path):
    enc = run(['words', 'encode'], b'fake secret', tmp_path).stdout.decode().splitlines()
    for text in ('\n'.join(enc[:-1]) + '\n', '\n'.join([enc[0], enc[1][:-1] + 'z']) + '\n', ''):
        dec = run(['words', 'decode'], text.encode(), tmp_path)
        assert dec.returncode != 0
        assert dec.stdout == b''
        assert dec.stderr


def test_words_command_takes_no_secret_argument(tmp_path):
    result = run(['words', 'encode', 'ghp_FAKE'], b'', tmp_path)
    assert result.returncode != 0
    assert b'ghp_FAKE' not in result.stdout


def test_words_command_works_without_a_notes_root(tmp_path):
    result = run(['words', 'encode'], b'x', tmp_path)
    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == 2

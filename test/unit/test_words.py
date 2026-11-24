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
    return words.decode(lambda: next((x + '\n' for x in it), ''))


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


def stream_of(data):
    return ' '.join(words.encode(data)).split()


def test_words_decode_one_word_per_line():
    ws = stream_of(b'fake secret value')
    assert decode_lines([w + '\n' for w in ws]) == b'fake secret value'


def test_words_decode_all_on_one_line():
    ws = stream_of(b'fake secret value')
    assert decode_lines(['  ' + ' \t '.join(ws) + '  \r\n']) == b'fake secret value'


def test_words_decode_breaks_mid_line():
    lines = words.encode(b'fake secret value')
    ws = ' '.join(lines).split()
    typed = [' '.join(ws[:3]) + '\n', ' '.join(ws[3:11]) + '\n\n', ' '.join(ws[11:]) + '\n']
    assert decode_lines(typed) == b'fake secret value'


def test_words_decode_leftover_words_rejected():
    ws = stream_of(b'hello')
    with pytest.raises(words.WordsError, match='2 more words'):
        decode_lines([' '.join(ws + ['babab', 'babab']) + '\n'])


def test_words_decode_trailing_whitespace_lines_allowed():
    lines = words.encode(b'hello')
    assert decode_lines([x + '\n' for x in lines] + ['\n', '  \n']) == b'hello'


def test_words_decode_interactive_whole_pasted_blob():
    ws = stream_of(b'fake secret value')
    prompts = []
    it = iter([' '.join(ws) + '\n'])
    got = words.decode(lambda: next(it, ''), interactive=True, prompt=prompts.append)
    assert got == b'fake secret value'
    assert prompts == ['the header line']


def test_words_decode_interactive_paste_prompts_only_when_waiting():
    lines = words.encode(b'fake secret value')
    queue = [x + '\n' for x in lines]
    prompts = []
    got = words.decode(lambda: queue.pop(0) if queue else '', interactive=True,
                       prompt=prompts.append, pending=lambda: bool(queue))
    assert got == b'fake secret value'
    assert prompts == []


def test_words_decode_interactive_bad_group_drops_buffer_and_asks_again():
    lines = words.encode(b'fake secret value')
    bad = 'babab babab babab babab babab'
    typed = [lines[0] + '\n', bad + ' ' + lines[2] + '\n', lines[1] + '\n',
             lines[2] + '\n', lines[3] + '\n']
    reports = []
    it = iter(typed)
    got = words.decode(lambda: next(it, ''), interactive=True, report=reports.append)
    assert got == b'fake secret value'
    assert len(reports) == 1 and reports[0].startswith('line 1 of 3')


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
    enc = run(['encode'], data, tmp_path)
    assert enc.returncode == 0
    dec = run(['decode'], enc.stdout, tmp_path)
    assert dec.returncode == 0
    assert dec.stdout == data


def test_words_command_roundtrip_with_explicit_algorithm(tmp_path):
    enc = run(['encode', '-a', 'mn-proquint'], b'fake secret', tmp_path)
    dec = run(['decode', '--algorithm', 'mn-proquint'], enc.stdout, tmp_path)
    assert dec.stdout == b'fake secret'


def test_words_command_text_argument_wins_over_stdin(tmp_path):
    enc = run(['encode', 'fake-arg'], b'fake stdin', tmp_path)
    assert run(['decode'], enc.stdout, tmp_path).stdout == b'fake-arg'


def test_words_command_text_argument_with_empty_open_stdin(tmp_path):
    enc = run(['encode', 'fake-arg'], b'', tmp_path)
    assert enc.returncode == 0
    assert run(['decode'], enc.stdout, tmp_path).stdout == b'fake-arg'


def test_words_command_piped_stdin_without_argument(tmp_path):
    enc = run(['encode'], b'fake stdin', tmp_path)
    assert run(['decode'], enc.stdout, tmp_path).stdout == b'fake stdin'


def test_words_command_quoted_argument_with_spaces_roundtrips(tmp_path):
    enc = run(['encode', 'fake two  words'], b'', tmp_path)
    assert run(['decode'], enc.stdout, tmp_path).stdout == b'fake two  words'


def test_words_command_unknown_algorithm_is_an_error(tmp_path):
    for cmd in ('encode', 'decode'):
        result = run([cmd, '-a', 'nope'], b'x', tmp_path)
        assert result.returncode != 0
        assert result.stdout == b''
        assert b'nope' in result.stderr


def test_words_command_words_subcommand_is_gone(tmp_path):
    for args in (['words', 'encode'], ['words', 'decode'], ['words']):
        result = run(args, b'x', tmp_path)
        assert result.returncode != 0
        assert result.stdout == b''


def test_words_command_decodes_a_line_encoded_by_2_38_0(tmp_path):
    # Output of v2.38.0 `words encode` for b'abc'; the wire format is fixed
    old = 'babab babah ronum dipuz fanuv\nbadod kanog jituj\n'
    assert run(['decode'], old.encode(), tmp_path).stdout == b'abc'


def test_words_command_decode_failure_writes_nothing(tmp_path):
    enc = run(['encode'], b'fake secret', tmp_path).stdout.decode().splitlines()
    for text in ('\n'.join(enc[:-1]) + '\n', '\n'.join([enc[0], enc[1][:-1] + 'z']) + '\n', ''):
        dec = run(['decode'], text.encode(), tmp_path)
        assert dec.returncode != 0
        assert dec.stdout == b''
        assert dec.stderr


def test_words_command_works_without_a_notes_root(tmp_path):
    result = run(['encode'], b'x', tmp_path)
    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == 2


# Tests for labels, read_secret and encode --interactive

import pty
import threading
import termios

from meta_notes import cli


def test_words_label_matches_decode_prompts():
    lines = words.encode(b'fake secret value')
    prompts = []
    it = iter(lines)
    words.decode(lambda: next(it, ''), prompt=prompts.append)
    assert prompts == [words.label(i, len(lines) - 1) for i in range(len(lines))]


def test_words_labelled_format():
    out = words.labelled(words.encode(b'fake secret value'))
    assert out[0].startswith('the header line: ')
    assert out[1].startswith('line 1 of %d: ' % (len(out) - 1))


def secret_via_pty(typed):
    master, slave = pty.openpty()
    before = termios.tcgetattr(slave)
    seen = []

    def terminal():
        # Type once the prompt is shown, so raw mode is already set
        while 'p: ' not in ''.join(seen):
            seen.append(os.read(master, 4096).decode())
        os.write(master, typed)

    t = threading.Thread(target=terminal, daemon=True)
    t.start()
    try:
        result = words.read_secret(slave, 'p: ')
    except KeyboardInterrupt:
        result = KeyboardInterrupt
    t.join(5)
    return result, master, slave, before


def stars_written(master):
    os.set_blocking(master, False)
    try:
        return os.read(master, 4096).decode()
    except BlockingIOError:
        return ''


def test_words_read_secret_typed_shows_stars_and_no_newline():
    secret, master, slave, _ = secret_via_pty(b'fake1\r')
    assert secret == b'fake1'
    assert stars_written(master).count('*') == 5


def test_words_read_secret_pasted_shows_a_star_per_char():
    text = b'x' * 40
    secret, master, _, _ = secret_via_pty(text + b'\n')
    assert secret == text
    assert stars_written(master).count('*') == 40


def test_words_read_secret_backspace_drops_char_and_star():
    secret, master, _, _ = secret_via_pty(b'abc\x7fd\x08e\r')
    assert secret == b'abe'
    out = stars_written(master)
    assert out.count('*') == 5 and out.count('\b \b') == 2


def test_words_read_secret_multibyte_char_is_one_star():
    secret, master, _, _ = secret_via_pty('éa\r'.encode())
    assert secret == '\u00e9a'.encode()
    assert stars_written(master).count('*') == 2


def test_words_read_secret_ctrl_c_aborts_and_restores_mode():
    result, master, slave, before = secret_via_pty(b'ab\x03')
    assert result is KeyboardInterrupt
    assert termios.tcgetattr(slave) == before


def test_words_read_secret_mode_restored_after_enter():
    _, _, slave, before = secret_via_pty(b'ab\r')
    assert termios.tcgetattr(slave) == before


def interactive_run(monkeypatch, capsys, argv, stdin=None, enters=2):
    master, slave = pty.openpty()
    os.write(master, b'\n' * enters)
    monkeypatch.setattr(cli.os, 'open', lambda *a, **k: slave)
    monkeypatch.setattr(cli.os, 'close', lambda fd: None)
    if stdin is not None:
        import io
        monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(stdin)))
    code = cli.main(argv)
    return code, capsys.readouterr()


def test_words_command_interactive_labels_match_decode(monkeypatch, capsys):
    code, cap = interactive_run(monkeypatch, capsys,
                                ['encode', '-i', 'fake secret value'], enters=5)
    assert code == 0
    assert cap.out.splitlines() == words.labelled(words.encode(b'fake secret value'))


def test_words_command_interactive_waits_for_enter_between_lines(monkeypatch, capsys):
    # One Enter for three lines: the second wait finds nothing and stops
    master, slave = pty.openpty()
    os.write(master, b'\n')
    monkeypatch.setattr(cli.os, 'open', lambda *a, **k: slave)
    monkeypatch.setattr(cli.os, 'close', lambda fd: None)
    os.set_blocking(slave, False)
    with pytest.raises(BlockingIOError):
        cli.main(['encode', '-i', 'fake secret value'])
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_words_command_interactive_piped_secret(monkeypatch, capsys):
    code, cap = interactive_run(monkeypatch, capsys, ['encode', '-i'],
                                stdin=b'fake piped', enters=5)
    assert code == 0
    assert cap.out.splitlines() == words.labelled(words.encode(b'fake piped'))


def test_words_command_interactive_without_terminal_is_an_error(tmp_path):
    result = subprocess.run(
        [sys.executable, str(repo_dir / 'scripts' / 'meta_notes'), 'encode', '-i', 'x'],
        capture_output=True, cwd=tmp_path, start_new_session=True,
        env={**os.environ, 'HOME': str(tmp_path)})
    assert result.returncode != 0
    assert result.stdout == b''
    assert b'needs a terminal' in result.stderr


def test_words_command_interactive_with_json_is_an_error(monkeypatch, capsys):
    code, cap = interactive_run(monkeypatch, capsys, ['encode', '-i', '--json', 'x'])
    assert code != 0
    assert '--json' in cap.out


def test_words_command_plain_encode_output_has_no_labels(tmp_path):
    out = run(['encode'], b'fake', tmp_path).stdout.decode().splitlines()
    assert out == words.encode(b'fake')

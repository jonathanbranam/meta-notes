"""
Unit tests for scripts/meta_notes/ui.py and `meta-notes ui`

Uses a stub server script that honours the meta-notes-ui start contract.
"""

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

scripts_dir = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

from meta_notes import cli, ui

pytestmark = pytest.mark.skipif(shutil.which('node') is None,
                                reason='node is not installed')

STUB = r'''
const fs = require('fs'), path = require('path');
const a = process.argv, get = (k) => (a.indexOf(k) < 0 ? undefined : a[a.indexOf(k) + 1]);
if (process.env.STUB_FAIL) { console.error('boom'); process.exit(3); }
const root = get('--root'), host = get('--host') || '127.0.0.1';
const port = Number(get('--port') || 8787);
fs.readFileSync(get('--token-file'));
const dir = path.join(root, '.meta-notes-cache', 'ui');
fs.mkdirSync(dir, { recursive: true });
const file = path.join(dir, 'server.json');
fs.writeFileSync(file, JSON.stringify({ pid: process.pid, host, port,
  url: `http://${host}:${port}/`, version: '0.0.1' }));
const done = () => { try { fs.unlinkSync(file); } catch (e) {} process.exit(0); };
process.on('SIGTERM', done);
setInterval(() => {}, 1000);
'''


@pytest.fixture
def notes_root(tmp_path, monkeypatch):
    root = tmp_path / 'notes'
    root.mkdir()
    clone = tmp_path / 'clone'
    (clone / 'dist' / 'server').mkdir(parents=True)
    (clone / 'dist' / 'server' / 'index.js').write_text(STUB)
    (root / '.meta-notes').write_text(f'[ui]\npath = "{clone}"\nport = 8799\n')
    monkeypatch.delenv('META_NOTES_ROOT', raising=False)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.chdir(root)
    yield root
    ui.stop(str(root))


def run(capsys, *argv):
    code = cli.main([*argv, '--json'])
    return code, json.loads(capsys.readouterr().out)


# Tests for ui start

def test_ui_start_prints_url_with_token_and_makes_token(notes_root, capsys):
    code, out = run(capsys, 'ui', 'start')
    token = (notes_root / '.meta-notes-cache/ui/token').read_text().strip()
    assert code == 0
    assert out['url'] == f'http://127.0.0.1:8799/?token={token}'
    assert out['running'] is True
    assert oct((notes_root / '.meta-notes-cache/ui/token').stat().st_mode & 0o777) == '0o600'


def test_ui_start_host_and_port_options_override_config(notes_root, capsys):
    code, out = run(capsys, 'ui', 'start', '--host', 'localhost', '--port', '8801')
    assert code == 0
    assert out['url'].startswith('http://localhost:8801/')


def test_ui_start_refuses_when_running(notes_root, capsys):
    run(capsys, 'ui', 'start')
    code, out = run(capsys, 'ui', 'start')
    assert code == 1
    assert 'already running' in out['error']


def test_ui_start_without_path_errors(notes_root, capsys):
    (notes_root / '.meta-notes').write_text('')
    code, out = run(capsys, 'ui', 'start')
    assert code == 1
    assert '[ui]' in out['error']


def test_ui_start_without_dist_says_to_build(notes_root, capsys):
    shutil.rmtree(notes_root.parent / 'clone' / 'dist')
    code, out = run(capsys, 'ui', 'start')
    assert code == 1
    assert 'npm run build' in out['error']


def test_ui_start_without_node_errors(notes_root, capsys, monkeypatch):
    monkeypatch.setenv('PATH', '')
    code, out = run(capsys, 'ui', 'start')
    assert code == 1
    assert 'node' in out['error']


def test_ui_start_server_exits_early_errors(notes_root, capsys, monkeypatch):
    monkeypatch.setenv('STUB_FAIL', '1')
    code, out = run(capsys, 'ui', 'start')
    assert code == 1
    assert 'server.log' in out['error']
    assert 'boom' in (notes_root / '.meta-notes-cache/ui/server.log').read_text()


# Tests for ui status, url and stop

def test_ui_status_not_running(notes_root, capsys):
    code, out = run(capsys, 'ui', 'status')
    assert code == 0
    assert out['running'] is False


def test_ui_status_running_has_url_without_token(notes_root, capsys):
    run(capsys, 'ui', 'start')
    code, out = run(capsys, 'ui', 'status')
    assert out['running'] is True
    assert out['url'] == 'http://127.0.0.1:8799/'
    assert out['version'] == '0.0.1'


def test_ui_status_stale_file_is_removed(notes_root, capsys):
    info = notes_root / '.meta-notes-cache/ui/server.json'
    info.parent.mkdir(parents=True)
    info.write_text(json.dumps({'pid': 2 ** 22 + 12345, 'url': 'http://x/'}))
    code, out = run(capsys, 'ui', 'status')
    assert out['running'] is False
    assert not info.exists()


def test_ui_url_fails_when_not_running(notes_root, capsys):
    code, out = run(capsys, 'ui', 'url')
    assert code == 1


def test_ui_url_has_token_when_running(notes_root, capsys):
    run(capsys, 'ui', 'start')
    code, out = run(capsys, 'ui', 'url')
    assert code == 0
    assert '?token=' in out['url']


def test_ui_stop_ends_server_and_removes_file(notes_root, capsys):
    run(capsys, 'ui', 'start')
    code, out = run(capsys, 'ui', 'stop')
    assert out['stopped'] is True
    assert not (notes_root / '.meta-notes-cache/ui/server.json').exists()


def test_ui_stop_when_not_running_succeeds(notes_root, capsys):
    code, out = run(capsys, 'ui', 'stop')
    assert code == 0
    assert out['stopped'] is False


# Tests for ui open

def test_ui_open_starts_and_opens_url(notes_root, capsys, monkeypatch):
    opened = []
    monkeypatch.setattr(ui, 'open_url', opened.append)
    code, out = run(capsys, 'ui', 'open')
    assert code == 0
    assert out['started'] is True
    assert opened == [out['url']]


def test_ui_open_reuses_running_server(notes_root, capsys, monkeypatch):
    monkeypatch.setattr(ui, 'open_url', lambda link: None)
    run(capsys, 'ui', 'start')
    code, out = run(capsys, 'ui', 'open')
    assert out['started'] is False

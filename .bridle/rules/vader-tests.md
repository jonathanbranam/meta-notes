---
id: vader-tests
severity: must
roles: [manager, worker]
---
Vimscript behaviour is tested with vader.vim, in `test/*.vader`, run by
`./run_tests.sh` (or `./run_tests.sh test/<file>.vader` for one file).
`run_tests.sh` starts `vim -es` with a clean runtimepath and loads vader from
`$VADER_PATH` (default `~/.vim/pack/testing/start/vader.vim`). If vader isn't
there, say so; don't install it or change the runner.

A test that touches the file system works in a temporary directory, so it
never reads or writes the repo or the human's notes, and removes it at the
end:

```vim
Execute (Setup - Create temporary test directory):
  let g:test_dir = tempname()
  call mkdir(g:test_dir, 'p')
  let g:original_dir = getcwd()
  execute 'cd' g:test_dir

Execute (Test that writes a file):
  call mkdir('note/path', 'p')
  call writefile(['# Sample Note'], g:test_dir . '/note/path/Filename.md')

Execute (Cleanup):
  execute 'cd' g:original_dir
  call delete(g:test_dir, 'rf')
  unlet g:test_dir
  unlet g:original_dir
```

Create every folder before writing into it. Use `g:test_dir`, which most
tests use (`test/open_note.vader` still calls it `g:test_root`).

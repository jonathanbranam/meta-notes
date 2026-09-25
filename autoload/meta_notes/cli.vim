" cli.vim - Run the meta-notes command line interface
" The CLI implements file operations; the plugin calls it and handles buffers

" Run bin/meta-notes with --json and --root set to Vim's current directory
" Args:
"   args: List of arguments: the subcommand and its arguments
" Returns:
"   The decoded JSON object. Always has 'ok' and 'warnings'; has 'error'
"   when 'ok' is false. If the CLI can't be run or its output isn't JSON,
"   returns {'ok': 0, 'error': <message>, 'warnings': []}.
function! meta_notes#cli#Run(args) abort
  let l:cmd = shellescape(meta_notes#template#GetPluginRoot() . '/bin/meta-notes')
        \ . ' --root ' . shellescape(getcwd()) . ' --json'
  for l:arg in a:args
    let l:cmd .= ' ' . shellescape(l:arg)
  endfor

  let l:output = system(l:cmd)

  try
    let l:result = json_decode(l:output)
  catch
    let l:result = 0
  endtry

  if type(l:result) != v:t_dict || !has_key(l:result, 'ok')
    return {'ok': 0, 'warnings': [],
          \ 'error': 'meta-notes CLI failed: ' . trim(l:output)}
  endif

  return l:result
endfunction

" Echo the warnings from a CLI result
" Args:
"   result: Dictionary returned by meta_notes#cli#Run()
function! meta_notes#cli#ShowWarnings(result) abort
  for l:warning in get(a:result, 'warnings', [])
    echohl WarningMsg
    echo 'Warning: ' . l:warning
    echohl None
  endfor
endfunction

" Get the meta-notes version line from the CLI
" Returns:
"   The line `meta-notes --version` prints, such as
"   'meta-notes 0.1.0 (f20d0de)', or '' if the CLI failed (after echoing
"   the error)
function! meta_notes#cli#Version() abort
  let l:result = meta_notes#cli#Run(['--version'])
  if !l:result.ok
    echohl ErrorMsg
    echo l:result.error
    echohl None
    return ''
  endif

  let l:line = 'meta-notes ' . l:result.version
  if type(get(l:result, 'commit', v:null)) == v:t_string
    let l:line .= ' (' . l:result.commit . (l:result.dirty ? '-dirty' : '') . ')'
  endif
  return l:line
endfunction

" Echo the meta-notes version (for :MetaNotesVersion)
function! meta_notes#cli#ShowVersion() abort
  let l:line = meta_notes#cli#Version()
  if !empty(l:line)
    echo l:line
  endif
endfunction

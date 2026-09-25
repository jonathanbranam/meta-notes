" template.vim - Template helpers for meta_notes
" Templates are rendered by `meta-notes note`; Vim runs the {{% vim %}} blocks
" left in its output

" Store the plugin root directory at script load time
let s:plugin_root = fnamemodify(expand('<sfile>:p:h'), ':h:h')

" Get the plugin root directory
" Returns:
"   Absolute path to the plugin root directory
function! meta_notes#template#GetPluginRoot() abort
  return s:plugin_root
endfunction

" Execute a Python script from the scripts/ directory
" Args:
"   script_name: Name of the script (e.g., 'time_report.py' or 'scripts/time_report.py')
"   args: List of arguments to pass to the script
" Returns:
"   Dictionary with keys:
"     - success: 1 if successful, 0 if error
"     - output: The script output
"     - error: Error message (empty if success)
function! meta_notes#template#ExecutePythonScript(script_name, ...) abort
  " Get plugin root
  let l:plugin_root = meta_notes#template#GetPluginRoot()

  " Normalize script name (remove leading 'scripts/' if present)
  let l:script = substitute(a:script_name, '^scripts/', '', '')

  " Construct full script path
  let l:script_path = l:plugin_root . '/scripts/' . l:script

  " Check if script exists
  if !filereadable(l:script_path)
    return {
          \ 'success': 0,
          \ 'output': '',
          \ 'error': 'Python script not found: ' . l:script_path
          \ }
  endif

  " Build command with arguments
  let l:cmd = 'python3 ' . shellescape(l:script_path)

  " Add any arguments
  if a:0 > 0
    for l:arg in a:1
      let l:cmd .= ' ' . shellescape(l:arg)
    endfor
  endif

  " Execute the script
  let l:output = system(l:cmd)

  " Check for errors
  if v:shell_error != 0
    return {
          \ 'success': 0,
          \ 'output': l:output,
          \ 'error': 'Python script failed with exit code ' . v:shell_error
          \ }
  endif

  return {
        \ 'success': 1,
        \ 'output': l:output,
        \ 'error': ''
        \ }
endfunction

" Run the {{% vim command %}} blocks in rendered note lines
" `meta-notes note` leaves vim blocks in its output for Vim to run.
" Args:
"   lines: List of rendered lines
" Returns:
"   The lines, with each vim block line replaced by its command's output
"   split into lines, or by an error comment if the command failed
function! meta_notes#template#RunVimBlocks(lines) abort
  let l:result = []
  for l:line in a:lines
    let l:matches = matchlist(l:line, '{{%\s*vim\s\+\(.\+\)\s*%}}')
    if empty(l:matches)
      call add(l:result, l:line)
      continue
    endif

    try
      redir => l:output
      silent execute l:matches[1]
      redir END
    catch
      redir END
      let l:output = '<!-- Command failed: ' . l:line . "\n" . 'Error: ' . v:exception . ' -->'
    endtry
    call extend(l:result, split(l:output, "\n", 1))
  endfor
  return l:result
endfunction

" notes.vim - Note management functions for meta_notes
" Handles wiki-style [[links]] and note operations

" Get text within delimiters under the cursor
" Args:
"   open_delim: Opening delimiter string (e.g., '[[', '[', '<', '(', '|')
"   close_delim: Closing delimiter string (e.g., ']]', ']', '>', ')', '|')
" Returns:
"   The text between delimiters if cursor is within them, or empty string if not
" Examples:
"   For "See [[note/path]]" with delimiters '[[' and ']]', returns "note/path"
"   For "Link <http://example.com>" with delimiters '<' and '>', returns "http://example.com"
"   For "Markdown [text](url)" with delimiters '(' and ')', returns "url"
function! meta_notes#notes#GetTextWithinDelimiters(open_delim, close_delim) abort
  let line = getline('.')
  let col = col('.') - 1  " Convert to 0-indexed

  " Escape special regex characters in delimiters for use in patterns
  let open_escaped = escape(a:open_delim, '\.*^$[]~')
  let close_escaped = escape(a:close_delim, '\.*^$[]~')

  " Build pattern to match: open_delim + content + close_delim
  " Use non-greedy matching to capture content
  let pattern = open_escaped . '\(.\{-}\)' . close_escaped

  " Search for all matching patterns on the line
  let start = 0
  while 1
    let match_pos = match(line, pattern, start)
    if match_pos == -1
      break
    endif

    let match_end = matchend(line, pattern, start)

    " Check if cursor is within this match (0-indexed positions)
    if col >= match_pos && col < match_end
      " Extract the content from within delimiters
      let match_text = matchstr(line, pattern, start)
      " Remove delimiters from the matched text
      let content = strpart(match_text, len(a:open_delim), len(match_text) - len(a:open_delim) - len(a:close_delim))
      return content
    endif

    " Move to next potential match
    let start = match_end
  endwhile

  " Cursor is not within any delimited text
  return ''
endfunction

" Get the link text under the cursor (convenience wrapper for wiki-style [[links]])
" Returns the filename/path if cursor is within [[...]], or empty string if not
" Example: For "See [[note/path]]", returns "note/path" if cursor is within brackets
function! meta_notes#notes#GetLinkUnderCursor() abort
  return meta_notes#notes#GetTextWithinDelimiters('[[', ']]')
endfunction

" Open a note from a wiki-style link [[path/to/note]]
" If cursor is within [[...]], opens or creates the note
" If note doesn't exist, creates a new buffer with header template
function! meta_notes#notes#Open() abort
  let path = meta_notes#notes#GetLinkUnderCursor()

  if path == ''
    echoerr 'Cursor is not within a wiki-style link [[...]]'
    return
  endif

  " Create filepath with .md extension
  let filepath = path . '.md'

  " Check if file exists
  if filereadable(filepath)
    " Open existing file
    execute 'edit!' fnameescape(filepath)
  else
    " Create new buffer with header template
    execute 'edit!' fnameescape(filepath)
    call setline(1, ['# ' . path, ''])
    call cursor(3, 1)
  endif
endfunction

" Calculate the Monday of the current week
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Returns:
"   Date string in YYYY-mm-dd format representing the Monday of the week
" Example:
"   For Friday 2026-02-13, returns '2026-02-09' (previous Monday)
"   For Monday 2026-02-09, returns '2026-02-09' (same day)
function! meta_notes#notes#CalculateWeekStart(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Find the plugin root directory (where scripts/ is located)
  " Try to use the current file's directory, or fall back to current working directory
  let l:plugin_root = expand('<sfile>:p:h:h:h')
  if !isdirectory(l:plugin_root . '/scripts')
    let l:plugin_root = getcwd()
  endif

  let l:script_path = l:plugin_root . '/scripts/notes.py'

  let l:python_cmd = printf('python3 -c "import sys; sys.path.insert(0, ''%s''); from datetime import date; from notes import calculate_week_start; print(calculate_week_start(date.fromisoformat(''%s'')).isoformat())"',
        \ l:plugin_root . '/scripts',
        \ l:date_str)

  return trim(system(l:python_cmd))
endfunction

" Calculate the Sunday of the current week
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Returns:
"   Date string in YYYY-mm-dd format representing the Sunday of the week
" Example:
"   For Friday 2026-02-13, returns '2026-02-15' (next Sunday)
"   For Sunday 2026-02-15, returns '2026-02-15' (same day)
function! meta_notes#notes#CalculateWeekEnd(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Find the plugin root directory (where scripts/ is located)
  " Try to use the current file's directory, or fall back to current working directory
  let l:plugin_root = expand('<sfile>:p:h:h:h')
  if !isdirectory(l:plugin_root . '/scripts')
    let l:plugin_root = getcwd()
  endif

  let l:script_path = l:plugin_root . '/scripts/notes.py'

  let l:python_cmd = printf('python3 -c "import sys; sys.path.insert(0, ''%s''); from datetime import date; from notes import calculate_week_end; print(calculate_week_end(date.fromisoformat(''%s'')).isoformat())"',
        \ l:plugin_root . '/scripts',
        \ l:date_str)

  return trim(system(l:python_cmd))
endfunction

" Open the week plan file for the current week
" Week plan files are located at: resource/plan/week/Plan YYYY-mm-dd
" where the date is the Monday of the current week
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in the week of Feb 9-15, 2026, opens 'resource/plan/week/Plan 2026-02-09.md'
function! meta_notes#notes#OpenWeekPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')
  let l:week_start = meta_notes#notes#CalculateWeekStart(l:date_str)

  " Construct the week plan file path
  let l:filepath = 'resource/plan/week/Plan ' . l:week_start . '.md'

  " Check if file exists
  if filereadable(l:filepath)
    " Open existing file
    execute 'edit!' fnameescape(l:filepath)
  else
    " Create new file with header template
    execute 'edit!' fnameescape(l:filepath)
    call setline(1, ['# Week Plan - ' . l:week_start, ''])
    call cursor(3, 1)
  endif
endfunction

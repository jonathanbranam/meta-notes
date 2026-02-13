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

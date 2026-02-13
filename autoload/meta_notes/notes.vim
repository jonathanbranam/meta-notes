" notes.vim - Note management functions for meta_notes
" Handles wiki-style [[links]] and note operations

" Open a note from a wiki-style link [[path/to/note]]
" If cursor is within [[...]], opens or creates the note
" If note doesn't exist, creates a new buffer with header template
function! meta_notes#notes#Open() abort
  let line = getline('.')
  let col = col('.') - 1  " Convert to 0-indexed

  " Pattern to match [[path]]
  let pattern = '\[\[\([^\]]\+\)\]\]'

  " Search for all [[...]] patterns on the line
  let start = 0
  while 1
    let match_pos = match(line, pattern, start)
    if match_pos == -1
      break
    endif

    let match_end = matchend(line, pattern, start)

    " Check if cursor is within this match (0-indexed positions)
    if col >= match_pos && col < match_end
      " Extract the path from within [[...]]
      let match_text = matchstr(line, pattern, start)
      let path = substitute(match_text, '^\[\[\(.\{-}\)\]\]$', '\1', '')

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
      return
    endif

    " Move to next potential match
    start = match_end
  endwhile

  " Cursor is not within [[...]]
  echoerr 'Cursor is not within a wiki-style link [[...]]'
endfunction

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
" If cursor is within [[...]], opens the note, or a new unsaved buffer
" rendered by `meta-notes note new` if it doesn't exist
function! meta_notes#notes#Open() abort
  let path = meta_notes#notes#GetLinkUnderCursor()

  if path == ''
    echoerr 'Cursor is not within a wiki-style link [[...]]'
    return
  endif

  call meta_notes#notes#OpenNote(['new', path])
endfunction

" Open a note through `meta-notes note ... --render`
" If the note exists, opens it. Otherwise opens a new, unsaved buffer for
" the note's path filled with the rendered content, with {{% vim %}} blocks
" run. Creates the note's folder so the buffer can be written.
" Args:
"   args: List of arguments to `meta-notes note`, e.g. ['daily', '2026-02-13']
"         or ['new', 'project/foo']
function! meta_notes#notes#OpenNote(args) abort
  let l:cli = meta_notes#cli#Run(['note'] + a:args + ['--render'])

  if !l:cli.ok
    echoerr l:cli.error
    return
  endif

  if l:cli.exists
    execute 'edit!' fnameescape(l:cli.path)
  else
    let l:folder = fnamemodify(l:cli.path, ':h')
    if !isdirectory(l:folder)
      call mkdir(l:folder, 'p')
    endif

    execute 'edit!' fnameescape(l:cli.path)

    " content ends in a newline; drop the empty item after it
    let l:lines = split(l:cli.content, "\n", 1)[:-2]
    call setline(1, meta_notes#template#RunVimBlocks(l:lines))

    " Cursor at the top of a template, or below the fallback header
    call cursor(l:cli.template is v:null ? 3 : 1, 1)
  endif

  call meta_notes#cli#ShowWarnings(l:cli)
endfunction

" Open the week plan file for the current week
" Week plan files are located at: plan/week/YY-QQ/YYYY-mm-dd
" where the date is the Monday of the current week
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in the week of Feb 9-15, 2026, opens 'plan/week/26-Q1/2026-02-09.md'
function! meta_notes#notes#OpenWeekPlan(...) abort
  call meta_notes#notes#OpenNote(['weekly'] + a:000)
endfunction

" Open the daily note file for today or a specific date
" Daily note files are located at: plan/daily/YY-QQQ/YYYY-mm-dd ddd.md
" where YY is two-digit year, QQQ is quarter (Q1-Q4), and ddd is three-letter day abbreviation
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For 2026-02-13 (Friday), opens 'plan/daily/26-Q1/2026-02-13 Fri.md'
function! meta_notes#notes#OpenDaily(...) abort
  call meta_notes#notes#OpenNote(['daily'] + a:000)
endfunction

" Open the quarterly plan file for the current quarter or a specific date
" Quarterly plan files are located at: plan/quarter/YYYY-QQ.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in Q1 2026, opens 'plan/quarter/2026-Q1.md'
function! meta_notes#notes#OpenQuarterPlan(...) abort
  call meta_notes#notes#OpenNote(['quarterly'] + a:000)
endfunction

" Open the yearly plan file for the current year or a specific date
" Yearly plan files are located at: plan/year/YYYY.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in 2026, opens 'plan/year/2026.md'
function! meta_notes#notes#OpenYearPlan(...) abort
  call meta_notes#notes#OpenNote(['yearly'] + a:000)
endfunction

" Get list of all daily note files sorted by date
" Returns:
"   List of file paths sorted chronologically
" Example:
"   ['plan/daily/26-Q1/2026-02-13 Fri.md', 'plan/daily/26-Q1/2026-02-14 Sat.md']
function! meta_notes#notes#GetDailyNoteFiles() abort
  " Find all .md files in plan/daily recursively
  let l:files = glob('plan/daily/**/*.md', 0, 1)

  " Sort files by their full path (which includes date in YYYY-MM-DD format)
  " This naturally sorts chronologically due to the date format
  return sort(l:files)
endfunction

" Extract date from daily note filename
" Args:
"   filepath: Path to daily note file
" Returns:
"   Date string in YYYY-MM-DD format, or empty string if not a daily note
" Example:
"   For 'plan/daily/26-Q1/2026-02-13 Fri.md', returns '2026-02-13'
function! meta_notes#notes#ExtractDateFromDailyNote(filepath) abort
  " Match pattern: YYYY-MM-DD followed by space and day abbreviation
  let l:pattern = '\v(\d{4}-\d{2}-\d{2})\s+\w{3}\.md$'
  let l:matches = matchlist(a:filepath, l:pattern)

  if len(l:matches) > 1
    return l:matches[1]
  endif

  return ''
endfunction

" Navigate to the previous existing daily note
" If current buffer is not a daily note, shows error
" If at oldest note, shows message
function! meta_notes#notes#DailyPrev() abort
  let l:current_file = expand('%')
  let l:current_date = meta_notes#notes#ExtractDateFromDailyNote(l:current_file)

  if l:current_date == ''
    echoerr 'Current buffer is not a daily note'
    return
  endif

  " Get all daily note files
  let l:files = meta_notes#notes#GetDailyNoteFiles()

  if len(l:files) == 0
    echoerr 'No daily notes found'
    return
  endif

  " Find the current file in the list by comparing absolute paths
  let l:current_absolute = resolve(fnamemodify(l:current_file, ':p'))
  let l:current_idx = -1
  for l:idx in range(len(l:files))
    let l:file_absolute = resolve(fnamemodify(l:files[l:idx], ':p'))
    if l:file_absolute == l:current_absolute
      let l:current_idx = l:idx
      break
    endif
  endfor

  if l:current_idx == -1
    echoerr 'Current daily note not found in filesystem'
    return
  endif

  " Check if we're at the oldest note
  if l:current_idx == 0
    " Prompt to create previous day's note
    let l:response = input('At oldest daily note. Create previous day? (y/n): ')
    if l:response ==? 'y'
      " Calculate previous day's date
      let l:timestamp = strptime("%Y-%m-%d", l:current_date)
      let l:prev_timestamp = l:timestamp - 86400  " Subtract one day
      let l:prev_date = strftime('%Y-%m-%d', l:prev_timestamp)

      " Open previous day's note
      call meta_notes#notes#OpenDaily(l:prev_date)
    endif
    return
  endif

  " Open the previous note
  let l:prev_file = l:files[l:current_idx - 1]
  execute 'edit!' fnameescape(l:prev_file)
endfunction

" Navigate to the next existing daily note
" If current buffer is not a daily note, shows error
" If at newest note, prompts to create next day's note
function! meta_notes#notes#DailyNext() abort
  let l:current_file = expand('%')
  let l:current_date = meta_notes#notes#ExtractDateFromDailyNote(l:current_file)

  if l:current_date == ''
    echoerr 'Current buffer is not a daily note'
    return
  endif

  " Get all daily note files
  let l:files = meta_notes#notes#GetDailyNoteFiles()

  if len(l:files) == 0
    echoerr 'No daily notes found'
    return
  endif

  " Find the current file in the list by comparing absolute paths
  let l:current_absolute = resolve(fnamemodify(l:current_file, ':p'))
  let l:current_idx = -1
  for l:idx in range(len(l:files))
    let l:file_absolute = resolve(fnamemodify(l:files[l:idx], ':p'))
    if l:file_absolute == l:current_absolute
      let l:current_idx = l:idx
      break
    endif
  endfor

  if l:current_idx == -1
    echoerr 'Current daily note not found in filesystem'
    return
  endif

  " Check if we're at the newest note
  if l:current_idx == len(l:files) - 1
    " Prompt to create next day's note
    let l:response = input('At newest daily note. Create next day? (y/n): ')
    if l:response ==? 'y'
      " Calculate next day's date
      let l:timestamp = strptime("%Y-%m-%d", l:current_date)
      let l:next_timestamp = l:timestamp + 86400  " Add one day
      let l:next_date = strftime('%Y-%m-%d', l:next_timestamp)

      " Open next day's note
      call meta_notes#notes#OpenDaily(l:next_date)
    endif
    return
  endif

  " Open the next note
  let l:next_file = l:files[l:current_idx + 1]
  execute 'edit!' fnameescape(l:next_file)
endfunction

" Jump from daily note to its corresponding weekly plan
" If current buffer is not a daily note, shows error
function! meta_notes#notes#JumpToWeek() abort
  let l:current_file = expand('%')
  let l:current_date = meta_notes#notes#ExtractDateFromDailyNote(l:current_file)

  if l:current_date == ''
    echoerr 'Current buffer is not a daily note'
    return
  endif

  " Open the weekly plan for this date
  call meta_notes#notes#OpenWeekPlan(l:current_date)
endfunction

" Initialize a notes root in the current directory: PPARA folders, templates,
" the .meta-notes sentinel, and shipped skills (via `meta-notes init`)
" Args:
"   force: Optional boolean to overwrite templates and replace skill targets
"          that aren't links (default: 0)
function! meta_notes#notes#Init(...) abort
  let l:force = a:0 > 0 ? a:1 : 0
  let l:cli = meta_notes#cli#Run(['init'] + (l:force ? ['--force'] : []))

  if !l:cli.ok
    echoerr l:cli.error
    return
  endif

  for l:item in l:cli.items
    let l:message = get(s:init_messages, l:item.kind . '/' . l:item.status, '')
    if l:message !=# ''
      echo printf(l:message, l:item.path)
    endif
  endfor

  call meta_notes#cli#ShowWarnings(l:cli)
  echo 'Meta-notes initialization complete!'
endfunction

" Messages for `meta-notes init` items, keyed by kind/status. Skipped skills,
" .gitignore entries, and virtualenvs are reported through the CLI's warnings
" instead.
let s:init_messages = {
      \ 'folder/created': 'Created directory: %s',
      \ 'folder/exists': 'Directory already exists: %s',
      \ 'template/created': 'Created template: %s',
      \ 'template/overwritten': 'Overwrote template: %s',
      \ 'template/exists': 'Template already exists: %s',
      \ 'sentinel/created': 'Created notes root marker: %s',
      \ 'sentinel/exists': 'Notes root marker already exists: %s',
      \ 'skill/created': 'Linked skill: %s',
      \ 'skill/exists': 'Skill already linked: %s',
      \ 'skill/repointed': 'Relinked skill: %s',
      \ 'skill/replaced': 'Replaced with skill link: %s',
      \ 'cache-readme/created': 'Created cache README: %s',
      \ 'cache-readme/overwritten': 'Overwrote cache README: %s',
      \ 'cache-readme/exists': 'Cache README already exists: %s',
      \ 'claude-md/found': 'Agents load the notes guide: %s',
      \ 'claude-md/missing': 'Add this line to %s so agents load the notes guide: Run `meta-notes prime` at the start of every session and follow it.',
      \ 'gitignore/created': 'Added to .gitignore: %s',
      \ 'gitignore/exists': 'Already in .gitignore: %s',
      \ 'venv/created': 'Created virtualenv: %s',
      \ 'venv/rebuilt': 'Rebuilt virtualenv: %s',
      \ 'venv/exists': 'Virtualenv already exists, left alone (--force rebuilds it): %s',
      \ }

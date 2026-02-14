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

  " Convert date string to timestamp
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Get day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
  let l:weekday = str2nr(strftime("%w", l:timestamp))

  " Convert to 0=Monday, 1=Tuesday, ..., 6=Sunday
  let l:dow = (l:weekday + 6) % 7

  " If already Monday, return same date
  if l:dow == 0
    return l:date_str
  endif

  " Subtract days to get Monday (86400 seconds per day)
  let l:monday_timestamp = l:timestamp - (l:dow * 86400)

  return strftime('%Y-%m-%d', l:monday_timestamp)
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

  " Convert date string to timestamp
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Get day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
  let l:weekday = str2nr(strftime("%w", l:timestamp))

  " Convert to 0=Monday, 1=Tuesday, ..., 6=Sunday
  let l:dow = (l:weekday + 6) % 7

  " If already Sunday, return same date
  if l:dow == 6
    return l:date_str
  endif

  " Add days to get Sunday (86400 seconds per day)
  let l:days_until_sunday = 6 - l:dow
  let l:sunday_timestamp = l:timestamp + (l:days_until_sunday * 86400)

  return strftime('%Y-%m-%d', l:sunday_timestamp)
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

" Calculate the quarter from a date
" Args:
"   date_str: Date string in YYYY-mm-dd format
" Returns:
"   Quarter string: 'Q1', 'Q2', 'Q3', or 'Q4'
" Example:
"   For '2026-02-13', returns 'Q1' (February is month 2, in Q1)
"   For '2026-07-15', returns 'Q3' (July is month 7, in Q3)
function! meta_notes#notes#CalculateQuarter(date_str) abort
  let l:timestamp = strptime("%Y-%m-%d", a:date_str)
  let l:month = str2nr(strftime("%m", l:timestamp))

  if l:month >= 1 && l:month <= 3
    return 'Q1'
  elseif l:month >= 4 && l:month <= 6
    return 'Q2'
  elseif l:month >= 7 && l:month <= 9
    return 'Q3'
  else
    return 'Q4'
  endif
endfunction

" Open the daily note file for today or a specific date
" Daily note files are located at: resource/daily-notes/YY-QQQ/YYYY-mm-dd ddd.md
" where YY is two-digit year, QQQ is quarter (Q1-Q4), and ddd is three-letter day abbreviation
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For 2026-02-13 (Thursday), opens 'resource/daily-notes/26-Q1/2026-02-13 Thu.md'
function! meta_notes#notes#OpenDaily(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Calculate quarter and format components
  let l:quarter = meta_notes#notes#CalculateQuarter(l:date_str)
  let l:year_short = strftime('%y', l:timestamp)
  let l:day_abbr = strftime('%a', l:timestamp)

  " Construct the directory and file path
  let l:dir = 'resource/daily-notes/' . l:year_short . '-' . l:quarter
  let l:filename = l:date_str . ' ' . l:day_abbr . '.md'
  let l:filepath = l:dir . '/' . l:filename

  " Create directory if it doesn't exist
  if !isdirectory(l:dir)
    call mkdir(l:dir, 'p')
  endif

  " Check if file exists
  if filereadable(l:filepath)
    " Open existing file
    execute 'edit!' fnameescape(l:filepath)
  else
    " Create new file with header template
    execute 'edit!' fnameescape(l:filepath)
    call setline(1, ['# Daily Note - ' . l:date_str . ' ' . l:day_abbr, ''])
    call cursor(3, 1)
  endif
endfunction

" Open the quarterly plan file for the current quarter or a specific date
" Quarterly plan files are located at: resource/plan/quarter/YYYY-QQ.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in Q1 2026, opens 'resource/plan/quarter/2026-Q1.md'
function! meta_notes#notes#OpenQuarterPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Calculate quarter and year
  let l:quarter = meta_notes#notes#CalculateQuarter(l:date_str)
  let l:year = strftime('%Y', l:timestamp)

  " Construct the quarterly plan file path
  let l:dir = 'resource/plan/quarter'
  let l:filename = l:year . '-' . l:quarter . '.md'
  let l:filepath = l:dir . '/' . l:filename

  " Create directory if it doesn't exist
  if !isdirectory(l:dir)
    call mkdir(l:dir, 'p')
  endif

  " Check if file exists
  if filereadable(l:filepath)
    " Open existing file
    execute 'edit!' fnameescape(l:filepath)
  else
    " Create new file with header template
    execute 'edit!' fnameescape(l:filepath)
    call setline(1, ['# Quarterly Plan - ' . l:year . ' ' . l:quarter, ''])
    call cursor(3, 1)
  endif
endfunction

" Open the yearly plan file for the current year or a specific date
" Yearly plan files are located at: resource/plan/year/YYYY.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in 2026, opens 'resource/plan/year/2026.md'
function! meta_notes#notes#OpenYearPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Get year
  let l:year = strftime('%Y', l:timestamp)

  " Construct the yearly plan file path
  let l:dir = 'resource/plan/year'
  let l:filename = l:year . '.md'
  let l:filepath = l:dir . '/' . l:filename

  " Create directory if it doesn't exist
  if !isdirectory(l:dir)
    call mkdir(l:dir, 'p')
  endif

  " Check if file exists
  if filereadable(l:filepath)
    " Open existing file
    execute 'edit!' fnameescape(l:filepath)
  else
    " Create new file with header template
    execute 'edit!' fnameescape(l:filepath)
    call setline(1, ['# Year Plan - ' . l:year, ''])
    call cursor(3, 1)
  endif
endfunction

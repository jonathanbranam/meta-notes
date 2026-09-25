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

" Extract the appropriate date for template context from a filepath
" Args:
"   filepath: Path to the note file
" Returns:
"   Date string in YYYY-MM-DD format appropriate for the note type
" Examples:
"   For 'plan/daily/26-Q1/2026-02-13 Fri.md', returns '2026-02-13'
"   For 'plan/week/26-Q1/2026-02-09.md', returns '2026-02-09' (Monday)
"   For 'plan/quarter/2026-Q1.md', returns '2026-01-01' (first day of quarter)
"   For 'plan/year/2026.md', returns '2026-01-01' (January 1st)
"   For other notes, returns today's date
function! meta_notes#notes#ExtractDateForTemplate(filepath) abort
  " Check for daily note: plan/daily/YY-Q#/YYYY-MM-DD ddd.md
  let l:daily_pattern = '\vplan/daily/\d{2}-Q\d/(\d{4}-\d{2}-\d{2})\s+\w{3}\.md$'
  let l:daily_matches = matchlist(a:filepath, l:daily_pattern)
  if len(l:daily_matches) > 1
    return l:daily_matches[1]
  endif

  " Check for weekly note: plan/week/YY-Q#/YYYY-MM-DD.md or YYYY-MM-DD ddd.md
  let l:weekly_pattern = '\vplan/week/\d{2}-Q\d/(\d{4}-\d{2}-\d{2})(\s+\w{3})?\.md$'
  let l:weekly_matches = matchlist(a:filepath, l:weekly_pattern)
  if len(l:weekly_matches) > 1
    return l:weekly_matches[1]
  endif

  " Check for quarterly note: plan/quarter/YYYY-Q#.md
  let l:quarterly_pattern = '\vplan/quarter/(\d{4})-(Q\d)\.md$'
  let l:quarterly_matches = matchlist(a:filepath, l:quarterly_pattern)
  if len(l:quarterly_matches) > 2
    let l:year = l:quarterly_matches[1]
    let l:quarter = l:quarterly_matches[2]
    " Return first day of the quarter
    let l:month = l:quarter == 'Q1' ? '01' : (l:quarter == 'Q2' ? '04' : (l:quarter == 'Q3' ? '07' : '10'))
    return l:year . '-' . l:month . '-01'
  endif

  " Check for yearly note: plan/year/YYYY.md
  let l:yearly_pattern = '\vplan/year/(\d{4})\.md$'
  let l:yearly_matches = matchlist(a:filepath, l:yearly_pattern)
  if len(l:yearly_matches) > 1
    let l:year = l:yearly_matches[1]
    " Return January 1st
    return l:year . '-01-01'
  endif

  " Default to today's date for non-plan notes
  return strftime('%Y-%m-%d')
endfunction

" Open a note from a wiki-style link [[path/to/note]]
" If cursor is within [[...]], opens or creates the note
" If note doesn't exist, creates a new buffer with template or header
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
    " Create parent directory if it doesn't exist
    let folder = fnamemodify(filepath, ':h')
    if !isdirectory(folder)
      call mkdir(folder, 'p')
    endif

    " Create new buffer with template or header
    execute 'edit!' fnameescape(filepath)

    " Look for template
    let template_path = meta_notes#template#FindTemplate(filepath)
    if template_path != ''
      " Process template with appropriate date for note type
      let date_str = meta_notes#notes#ExtractDateForTemplate(filepath)
      let context = meta_notes#template#CreateContext(date_str, filepath)
      let lines = meta_notes#template#ProcessTemplate(template_path, context)
      call setline(1, lines)
      call cursor(1, 1)
    else
      " Use simple header
      call setline(1, ['# ' . path, ''])
      call cursor(3, 1)
    endif
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
" Week plan files are located at: plan/week/YY-QQ/YYYY-mm-dd
" where the date is the Monday of the current week
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in the week of Feb 9-15, 2026, opens 'plan/week/26-Q1/2026-02-09.md'
function! meta_notes#notes#OpenWeekPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')
  let l:week_start = meta_notes#notes#CalculateWeekStart(l:date_str)

  " Calculate quarter and year components for the folder path
  let l:timestamp = strptime("%Y-%m-%d", l:week_start)
  let l:quarter = meta_notes#notes#CalculateQuarter(l:week_start)
  let l:year_short = strftime('%y', l:timestamp)
  let l:folder = 'plan/week/' . l:year_short . '-' . l:quarter

  " Create directory if it doesn't exist
  if !isdirectory(l:folder)
    call mkdir(l:folder, 'p')
  endif

  " Construct the week plan file path
  let l:filepath = l:folder . '/' . l:week_start . '.md'

  " Check if file exists
  if filereadable(l:filepath)
    " Open existing file
    execute 'edit!' fnameescape(l:filepath)
  else
    " Create new file with template or header
    execute 'edit!' fnameescape(l:filepath)

    " Look for template (folder-specific or standard weekly template)
    let l:template_path = meta_notes#template#FindTemplate(l:filepath, 'weekly')
    if l:template_path != ''
      " Process template
      let l:context = meta_notes#template#CreateContext(l:week_start, l:filepath)
      let l:lines = meta_notes#template#ProcessTemplate(l:template_path, l:context)
      call setline(1, l:lines)
      call cursor(1, 1)
    else
      " Use simple header
      call setline(1, ['# Week Plan - ' . l:week_start, ''])
      call cursor(3, 1)
    endif
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
" Daily note files are located at: plan/daily/YY-QQQ/YYYY-mm-dd ddd.md
" where YY is two-digit year, QQQ is quarter (Q1-Q4), and ddd is three-letter day abbreviation
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For 2026-02-13 (Thursday), opens 'plan/daily/26-Q1/2026-02-13 Thu.md'
function! meta_notes#notes#OpenDaily(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Calculate quarter and format components
  let l:quarter = meta_notes#notes#CalculateQuarter(l:date_str)
  let l:year_short = strftime('%y', l:timestamp)
  let l:day_abbr = strftime('%a', l:timestamp)

  " Construct the directory and file path
  let l:dir = 'plan/daily/' . l:year_short . '-' . l:quarter
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
    " Create new file with template or header
    execute 'edit!' fnameescape(l:filepath)

    " Look for template (folder-specific or standard daily template)
    let l:template_path = meta_notes#template#FindTemplate(l:filepath, 'daily')
    if l:template_path != ''
      " Process template
      let l:context = meta_notes#template#CreateContext(l:date_str, l:filepath)
      let l:lines = meta_notes#template#ProcessTemplate(l:template_path, l:context)
      call setline(1, l:lines)
      call cursor(1, 1)
    else
      " Use simple header
      call setline(1, ['# Daily Note - ' . l:date_str . ' ' . l:day_abbr, ''])
      call cursor(3, 1)
    endif
  endif
endfunction

" Open the quarterly plan file for the current quarter or a specific date
" Quarterly plan files are located at: plan/quarter/YYYY-QQ.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in Q1 2026, opens 'plan/quarter/2026-Q1.md'
function! meta_notes#notes#OpenQuarterPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Calculate quarter and year
  let l:quarter = meta_notes#notes#CalculateQuarter(l:date_str)
  let l:year = strftime('%Y', l:timestamp)

  " Construct the quarterly plan file path
  let l:dir = 'plan/quarter'
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
    " Create new file with template or header
    execute 'edit!' fnameescape(l:filepath)

    " Look for template (folder-specific or standard quarterly template)
    let l:template_path = meta_notes#template#FindTemplate(l:filepath, 'quarterly')
    if l:template_path != ''
      " Process template with the first day of the quarter as the date
      let l:quarter_start = l:year . '-' . (l:quarter == 'Q1' ? '01' : (l:quarter == 'Q2' ? '04' : (l:quarter == 'Q3' ? '07' : '10'))) . '-01'
      let l:context = meta_notes#template#CreateContext(l:quarter_start, l:filepath)
      let l:lines = meta_notes#template#ProcessTemplate(l:template_path, l:context)
      call setline(1, l:lines)
      call cursor(1, 1)
    else
      " Use simple header
      call setline(1, ['# Quarterly Plan - ' . l:year . ' ' . l:quarter, ''])
      call cursor(3, 1)
    endif
  endif
endfunction

" Open the yearly plan file for the current year or a specific date
" Yearly plan files are located at: plan/year/YYYY.md
" Args:
"   date_str: Optional date string in YYYY-mm-dd format (defaults to today)
" Example:
"   For any day in 2026, opens 'plan/year/2026.md'
function! meta_notes#notes#OpenYearPlan(...) abort
  let l:date_str = a:0 > 0 ? a:1 : strftime('%Y-%m-%d')

  " Convert date string to timestamp for formatting
  let l:timestamp = strptime("%Y-%m-%d", l:date_str)

  " Get year
  let l:year = strftime('%Y', l:timestamp)

  " Construct the yearly plan file path
  let l:dir = 'plan/year'
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
    " Create new file with template or header
    execute 'edit!' fnameescape(l:filepath)

    " Look for template (folder-specific or standard yearly template)
    let l:template_path = meta_notes#template#FindTemplate(l:filepath, 'yearly')
    if l:template_path != ''
      " Process template with January 1st as the date
      let l:year_start = l:year . '-01-01'
      let l:context = meta_notes#template#CreateContext(l:year_start, l:filepath)
      let l:lines = meta_notes#template#ProcessTemplate(l:template_path, l:context)
      call setline(1, l:lines)
      call cursor(1, 1)
    else
      " Use simple header
      call setline(1, ['# Year Plan - ' . l:year, ''])
      call cursor(3, 1)
    endif
  endif
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

" Messages for `meta-notes init` items, keyed by kind/status. Skipped skills
" are reported through the CLI's warnings instead.
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
      \ }

" time_tracking.vim - Time tracking functions for meta_notes
" Provides time tracking report generation and commands

" Check if current buffer is a daily note
" Returns 1 if in daily note, 0 otherwise
function! meta_notes#time_tracking#IsInDailyNote() abort
  let l:filepath = expand('%:p')
  " Daily notes are in plan/daily/ directory
  return l:filepath =~# 'plan/daily/.*\.md$'
endfunction

" Generate and display time tracking report
" Only works when editing a daily note file
function! meta_notes#time_tracking#ShowReport() abort
  " Check if we're in a daily note
  if !meta_notes#time_tracking#IsInDailyNote()
    echoerr 'TimeReport command is only available in daily notes'
    return
  endif

  " Get current file path
  let l:filepath = expand('%:p')

  " Check if file has been saved
  if !filereadable(l:filepath)
    echoerr 'Please save the file before generating a time report'
    return
  endif

  " Execute the Python script
  let l:result = meta_notes#template#ExecutePythonScript('time_report.py', [l:filepath])

  " Check for errors
  if !l:result.success
    echoerr 'Error generating time report: ' . l:result.error
    if !empty(l:result.output)
      echoerr l:result.output
    endif
    return
  endif

  let l:output = l:result.output

  " Create a new split window for the report
  " Check if a time report buffer already exists
  let l:report_bufnr = bufnr('Time Report')

  if l:report_bufnr != -1
    " Buffer exists, switch to it
    let l:report_winnr = bufwinnr(l:report_bufnr)
    if l:report_winnr != -1
      " Window is already visible, jump to it
      execute l:report_winnr . 'wincmd w'
    else
      " Buffer exists but window is not visible, open it
      execute 'sbuffer ' . l:report_bufnr
    endif
  else
    " Create new buffer
    execute 'new Time Report'
  endif

  " Set buffer options
  setlocal buftype=nofile
  setlocal bufhidden=hide
  setlocal noswapfile
  setlocal nomodified
  setlocal readonly
  setlocal filetype=markdown

  " Clear buffer and insert report
  setlocal noreadonly
  setlocal modifiable
  silent %delete _
  silent put =l:output
  silent 1delete _

  " Set as readonly again
  setlocal nomodified
  setlocal readonly
  setlocal nomodifiable

  " Position cursor at the top
  normal! gg
endfunction

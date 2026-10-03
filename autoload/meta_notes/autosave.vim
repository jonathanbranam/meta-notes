" autosave.vim - Autosave and autoreload for notes buffers
" Applies only to buffers whose file is under a notes root (the nearest
" directory holding a .meta-notes file). Everything is off by default; see
" :help meta-notes-autosave.

let s:save_timers = {}
let s:watchers = {}
let s:check_timer = -1
let s:warned_no_watcher = 0

" Settings, read each time so changes take effect without a restart
function! s:Autosave() abort
  return get(g:, 'meta_notes_autosave', 0)
endfunction

function! s:Autoreload() abort
  return get(g:, 'meta_notes_autoreload', 0)
endfunction

function! s:Delay() abort
  return get(g:, 'meta_notes_autosave_delay', 1000)
endfunction

function! s:Interval() abort
  return get(g:, 'meta_notes_checktime_interval', 0)
endfunction

" Find the notes root for a file, as the CLI does: the nearest directory
" with a .meta-notes file, stopping after $HOME.
" Returns: the root directory, or '' when the file isn't in a notes root
function! meta_notes#autosave#FindRoot(file) abort
  if a:file ==# ''
    return ''
  endif
  let l:dir = fnamemodify(a:file, ':p:h')
  let l:home = substitute(fnamemodify($HOME, ':p'), '/\+$', '', '')
  while 1
    if filereadable(l:dir . '/.meta-notes')
      return l:dir
    endif
    let l:parent = fnamemodify(l:dir, ':h')
    if l:dir ==# l:home || l:parent ==# l:dir
      return ''
    endif
    let l:dir = l:parent
  endwhile
endfunction

" Does the buffer belong to a notes root?
function! meta_notes#autosave#IsNotesBuffer(buf) abort
  return getbufvar(a:buf, 'meta_notes_root', '') !=# ''
endfunction

" What Vim last read or wrote, to compare against the disk
function! s:DiskStamp(buf) abort
  let l:file = fnamemodify(bufname(a:buf), ':p')
  return getftime(l:file) . ':' . getfsize(l:file)
endfunction

function! s:StoreStamp(buf) abort
  call setbufvar(a:buf, 'meta_notes_stamp', s:DiskStamp(a:buf))
endfunction

function! s:Name(buf) abort
  return fnamemodify(bufname(a:buf), ':t')
endfunction

function! s:Message(text, warn) abort
  if a:warn
    echohl WarningMsg
  endif
  echomsg 'meta-notes: ' . a:text
  echohl None
endfunction

function! s:InInsert() abort
  return mode() =~# '^[iRc]'
endfunction

" Attach to a buffer: find its notes root, and set up the buffer-local
" options and autocmds when autosave or autoreload is on.
" Args:
"   buf: buffer number
"   refresh_stamp: 1 to record the file's current state as what Vim read
function! meta_notes#autosave#Attach(buf, refresh_stamp) abort
  if !bufexists(a:buf) || getbufvar(a:buf, '&buftype') !=# ''
    return
  endif
  if getbufvar(a:buf, 'meta_notes_root', v:null) is v:null
    call setbufvar(a:buf, 'meta_notes_root',
          \ meta_notes#autosave#FindRoot(bufname(a:buf)))
  endif
  if !meta_notes#autosave#IsNotesBuffer(a:buf)
    return
  endif
  if a:refresh_stamp || getbufvar(a:buf, 'meta_notes_stamp', '') ==# ''
    call s:StoreStamp(a:buf)
  endif
  let l:active = s:Autosave() || s:Autoreload()
  call s:SetBufferAutocmds(a:buf, l:active)
  if s:Autoreload()
    call setbufvar(a:buf, '&autoread', 1)
    call s:StartWatcher(getbufvar(a:buf, 'meta_notes_root'))
    call s:StartTimer()
  else
    if bufnr('%') == a:buf
      " Back to the global value
      setlocal autoread<
    endif
  endif
endfunction

function! s:SetBufferAutocmds(buf, active) abort
  let l:cur = bufnr('%')
  if l:cur != a:buf
    " Buffer-local autocmds belong to the current buffer; do it on entry
    return
  endif
  augroup meta_notes_buffer
    autocmd! * <buffer>
    if a:active
      autocmd FileChangedShell <buffer> call meta_notes#autosave#OnChangedShell()
      autocmd FileChangedShellPost <buffer> call meta_notes#autosave#OnChangedShellPost()
    endif
  augroup END
endfunction

" Re-apply settings to every loaded buffer, the watchers and the timer
function! meta_notes#autosave#Refresh() abort
  for l:info in getbufinfo({'bufloaded': 1})
    call setbufvar(l:info.bufnr, 'meta_notes_root', v:null)
  endfor
  call s:StopWatchers()
  call s:StopTimer()
  " Buffer-local autocmds are set for each buffer when it's entered
  for l:info in getbufinfo({'bufloaded': 1})
    call meta_notes#autosave#Attach(l:info.bufnr, 0)
  endfor
  call s:StartTimer()
endfunction

" Event handlers called from plugin/meta_notes.vim

" Turn GitGutter off for the whole session when Vim starts inside a notes
" root. Once, at VimEnter, so the signs stay off in every buffer.
function! meta_notes#autosave#OnVimEnter() abort
  if !get(g:, 'meta_notes_disable_gitgutter', 1)
        \ || !exists(':GitGutterDisable')
    return
  endif
  if meta_notes#autosave#FindRoot(getcwd()) !=# ''
    GitGutterDisable
  endif
endfunction

function! meta_notes#autosave#OnBufRead() abort
  if s:Autosave() || s:Autoreload()
    call meta_notes#autosave#Attach(bufnr('%'), 1)
  endif
endfunction

function! meta_notes#autosave#OnBufEnter() abort
  if s:Autosave() || s:Autoreload() || exists('b:meta_notes_root')
    call meta_notes#autosave#Attach(bufnr('%'), 0)
  endif
endfunction

function! meta_notes#autosave#OnFocusGained() abort
  if s:Autoreload()
    call s:CheckAll()
  endif
endfunction

function! meta_notes#autosave#OnTextChanged() abort
  if s:Autosave() && meta_notes#autosave#IsNotesBuffer('%')
    call s:Schedule(bufnr('%'))
  endif
endfunction

function! meta_notes#autosave#OnInsertLeave() abort
  if !meta_notes#autosave#IsNotesBuffer('%')
    return
  endif
  if getbufvar('%', 'meta_notes_pending', 0)
    call s:Resolve(bufnr('%'))
  endif
  if s:Autosave()
    call s:Schedule(bufnr('%'))
  endif
endfunction

function! meta_notes#autosave#OnWritten() abort
  if meta_notes#autosave#IsNotesBuffer('%')
    call s:StoreStamp(bufnr('%'))
    call s:ClearConflict(bufnr('%'))
  elseif s:Autosave() || s:Autoreload()
    call meta_notes#autosave#Attach(bufnr('%'), 1)
  endif
endfunction

" Noticing changes

" Run :checktime on a notes buffer, unless in insert mode
function! s:Check(buf) abort
  if !s:Autoreload() || !bufloaded(a:buf) || !meta_notes#autosave#IsNotesBuffer(a:buf)
    return
  endif
  if s:InInsert()
    call setbufvar(a:buf, 'meta_notes_pending', 1)
    return
  endif
  silent! execute 'checktime' a:buf
endfunction

function! s:CheckAll() abort
  for l:info in getbufinfo({'bufloaded': 1})
    call s:Check(l:info.bufnr)
  endfor
endfunction

" After insert mode: act on a change that arrived while typing
function! s:Resolve(buf) abort
  call setbufvar(a:buf, 'meta_notes_pending', 0)
  if s:DiskStamp(a:buf) ==# getbufvar(a:buf, 'meta_notes_stamp', '')
    return
  endif
  if getbufvar(a:buf, '&modified')
    call s:Conflict(a:buf)
  elseif s:Autoreload()
    silent! edit
    call s:Notice(a:buf)
  endif
endfunction

" Store the new stamp now, but show the message from a timer: the reload
" is usually inside `silent! checktime`, which swallows :echomsg.
function! s:Notice(buf) abort
  call s:StoreStamp(a:buf)
  call timer_start(0, function('s:NoticeLater', [a:buf]))
endfunction

function! s:NoticeLater(buf, timer) abort
  call s:Message('reloaded ' . s:Name(a:buf)
        \ . ' (changed on disk; u to undo)', 0)
endfunction

" FileChangedShell, set per notes buffer. Decides what Vim does when the
" file changed on disk.
function! meta_notes#autosave#OnChangedShell() abort
  let l:buf = bufnr('%')
  let l:reason = v:fcs_reason
  if !s:Autosave() && !s:Autoreload()
    let v:fcs_choice = 'ask'
  elseif l:reason ==# 'conflict'
    let v:fcs_choice = ''
    call timer_start(0, function('s:ConflictLater', [l:buf]))
  elseif l:reason ==# 'changed'
    if s:Autoreload() && !s:InInsert()
      let v:fcs_choice = 'reload'
    elseif s:Autoreload()
      let v:fcs_choice = ''
      call setbufvar(l:buf, 'meta_notes_pending', 1)
    else
      let v:fcs_choice = 'ask'
    endif
  elseif l:reason ==# 'deleted'
    let v:fcs_choice = ''
    call s:Message(s:Name(l:buf) . ' was deleted on disk', 1)
  else
    " mode, time: the contents are the same
    let v:fcs_choice = ''
    call s:StoreStamp(l:buf)
  endif
endfunction

function! s:ConflictLater(buf, timer) abort
  call s:Conflict(a:buf)
endfunction

" FileChangedShellPost: Vim reloaded the buffer. With 'autoread' and an
" unmodified buffer Vim skips FileChangedShell, so v:fcs_reason is empty
" here; only mode and time changes (no reload) are left out.
function! meta_notes#autosave#OnChangedShellPost() abort
  if v:fcs_reason !~# '^\(mode\|time\)$' && s:Autoreload()
    call s:Notice(bufnr('%'))
  endif
endfunction

" Autosave

function! s:Schedule(buf) abort
  if has_key(s:save_timers, a:buf)
    call timer_stop(s:save_timers[a:buf])
  endif
  let s:save_timers[a:buf] = timer_start(s:Delay(),
        \ function('s:SaveTimer', [a:buf]))
endfunction

function! s:SaveTimer(buf, timer) abort
  if has_key(s:save_timers, a:buf) && s:save_timers[a:buf] == a:timer
    call remove(s:save_timers, a:buf)
  endif
  if bufnr('%') != a:buf || mode() !~# '^n'
    " Only the current buffer in normal mode; try again later
    if bufnr('%') == a:buf && bufloaded(a:buf)
      call s:Schedule(a:buf)
    endif
    return
  endif
  call meta_notes#autosave#Save(a:buf)
endfunction

" Save a notes buffer if it's safe to: it has unsaved edits, the file on
" disk is what Vim last read, and there's no pending conflict. Never forces
" a write.
" Returns: 1 when the buffer was written, 0 otherwise
function! meta_notes#autosave#Save(buf) abort
  if !s:Autosave() || !bufloaded(a:buf)
        \ || !meta_notes#autosave#IsNotesBuffer(a:buf)
        \ || getbufvar(a:buf, 'meta_notes_conflict', 0)
        \ || !getbufvar(a:buf, '&modified')
        \ || getbufvar(a:buf, '&readonly')
        \ || !getbufvar(a:buf, '&modifiable')
    return 0
  endif
  if s:Autoreload()
    silent! execute 'checktime' a:buf
    if getbufvar(a:buf, 'meta_notes_conflict', 0) || !getbufvar(a:buf, '&modified')
      return 0
    endif
  endif
  if s:DiskStamp(a:buf) !=# getbufvar(a:buf, 'meta_notes_stamp', '')
    call s:Conflict(a:buf)
    return 0
  endif
  try
    if bufnr('%') == a:buf
      silent update
    else
      call s:Message('not saving ' . s:Name(a:buf) . ': not the current buffer', 0)
      return 0
    endif
  catch
    call s:Message('autosave of ' . s:Name(a:buf) . ' failed: '
          \ . substitute(v:exception, '^Vim\((\w\+)\)\?:', '', ''), 1)
    return 0
  endtry
  return 1
endfunction

" Conflicts: unsaved edits and the file changed on disk

function! s:Conflict(buf) abort
  if !bufloaded(a:buf) || getbufvar(a:buf, 'meta_notes_conflict', 0)
    return
  endif
  call setbufvar(a:buf, 'meta_notes_conflict', 1)
  call s:Message(s:Name(a:buf) . ' changed on disk and has unsaved edits;'
        \ . ' autosave paused. Resolve, then :w', 1)
  if get(g:, 'meta_notes_conflict_diff', 1) && bufnr('%') == a:buf
    call s:OpenDiff(a:buf)
  endif
endfunction

" Open a scratch split with the file as it is on disk and diff it
function! s:OpenDiff(buf) abort
  let l:file = fnamemodify(bufname(a:buf), ':p')
  if !filereadable(l:file)
    return
  endif
  let l:ft = &filetype
  let l:orig_win = win_getid()
  vertical new
  setlocal buftype=nofile bufhidden=wipe noswapfile
  let &l:filetype = l:ft
  silent! file `='meta-notes://disk/' . fnamemodify(l:file, ':t')`
  silent! execute 'read ++edit' fnameescape(l:file)
  silent! 1delete _
  setlocal nomodifiable
  let l:scratch = bufnr('%')
  diffthis
  call win_gotoid(l:orig_win)
  diffthis
  call setbufvar(a:buf, 'meta_notes_diff', l:scratch)
  call setbufvar(l:scratch, 'meta_notes_diff_of', a:buf)
  augroup meta_notes_diff
    execute 'autocmd BufWipeout <buffer=' . l:scratch . '> call meta_notes#autosave#DiffClosed(' . a:buf . ')'
  augroup END
endfunction

" The scratch buffer went away: turn diff mode off in the notes buffer
function! meta_notes#autosave#DiffClosed(buf) abort
  call setbufvar(a:buf, 'meta_notes_diff', 0)
  let l:cur = win_getid()
  for l:win in win_findbuf(a:buf)
    if win_gotoid(l:win)
      diffoff
    endif
  endfor
  call win_gotoid(l:cur)
endfunction

" A successful write ends the conflict: autosave resumes, the diff closes
function! s:ClearConflict(buf) abort
  if !getbufvar(a:buf, 'meta_notes_conflict', 0)
    return
  endif
  call setbufvar(a:buf, 'meta_notes_conflict', 0)
  let l:scratch = getbufvar(a:buf, 'meta_notes_diff', 0)
  if l:scratch && bufexists(l:scratch)
    silent! execute 'bwipeout' l:scratch
  endif
endfunction

" File watcher job

" The watcher command for a root, or [] when no watcher is installed
function! meta_notes#autosave#WatcherCommand(root) abort
  let l:fswatch = executable('fswatch')
  let l:inotify = executable('inotifywait')
  let l:prefer_fswatch = has('mac') || has('osx') || has('macunix')
  if l:fswatch && (l:prefer_fswatch || !l:inotify)
    return ['fswatch', '-r', '-l', '0.2',
          \ '-e', '/\.git/', '-e', '/\.venv/', '-e', '/\.meta-notes-cache/',
          \ a:root]
  elseif l:inotify
    return ['inotifywait', '-m', '-r', '-q',
          \ '-e', 'close_write,moved_to,create,delete',
          \ '--format', '%w%f',
          \ '--exclude', '(^|/)(\.git|\.venv|\.meta-notes-cache)(/|$)',
          \ a:root]
  endif
  return []
endfunction

function! s:StartWatcher(root) abort
  if !get(g:, 'meta_notes_watch', 1) || !has('job') || has_key(s:watchers, a:root)
    return
  endif
  let l:cmd = meta_notes#autosave#WatcherCommand(a:root)
  if empty(l:cmd)
    if !s:warned_no_watcher
      let s:warned_no_watcher = 1
      call s:Message('no file watcher (fswatch or inotifywait) found; '
            \ . (s:Interval() > 0 ? 'using the timer' : 'set g:meta_notes_checktime_interval to poll'), 1)
    endif
    return
  endif
  try
    let s:watchers[a:root] = job_start(l:cmd, {
          \ 'out_mode': 'nl',
          \ 'out_cb': function('s:WatcherOutput'),
          \ 'err_io': 'null',
          \ 'stoponexit': 'term'})
  catch
    call s:Message('could not start ' . l:cmd[0] . ': ' . v:exception, 1)
  endtry
endfunction

function! s:StopWatchers() abort
  for l:job in values(s:watchers)
    silent! call job_stop(l:job)
  endfor
  let s:watchers = {}
endfunction

function! meta_notes#autosave#StopWatchers() abort
  call s:StopWatchers()
  call s:StopTimer()
endfunction

" A path changed: check its buffer, if it's loaded
function! s:WatcherOutput(channel, line) abort
  let l:path = resolve(a:line)
  for l:info in getbufinfo({'bufloaded': 1})
    if l:info.name !=# '' && resolve(fnamemodify(l:info.name, ':p')) ==# l:path
      call s:Check(l:info.bufnr)
    endif
  endfor
endfunction

" Timer

function! s:StartTimer() abort
  if s:check_timer == -1 && s:Autoreload() && s:Interval() > 0 && has('timers')
    let s:check_timer = timer_start(s:Interval(), function('s:Tick'),
          \ {'repeat': -1})
  endif
endfunction

function! s:StopTimer() abort
  if s:check_timer != -1
    call timer_stop(s:check_timer)
    let s:check_timer = -1
  endif
endfunction

function! s:Tick(timer) abort
  call s:CheckAll()
endfunction

" Commands

" Set, toggle or read a setting for :MetaNotesAutosave / :MetaNotesAutoreload
function! s:SetOption(name, arg) abort
  let l:cur = get(g:, a:name, 0)
  if a:arg ==# 'on'
    let g:{a:name} = 1
  elseif a:arg ==# 'off'
    let g:{a:name} = 0
  elseif a:arg ==# '' || a:arg ==# 'toggle'
    let g:{a:name} = !l:cur
  else
    echoerr 'Usage: expected on, off or toggle'
    return
  endif
  call meta_notes#autosave#Refresh()
  call meta_notes#autosave#Status()
endfunction

function! meta_notes#autosave#SetAutosave(arg) abort
  call s:SetOption('meta_notes_autosave', a:arg)
endfunction

function! meta_notes#autosave#SetAutoreload(arg) abort
  call s:SetOption('meta_notes_autoreload', a:arg)
endfunction

function! meta_notes#autosave#Complete(lead, line, pos) abort
  return join(['on', 'off', 'toggle'], "\n")
endfunction

" State as a list of lines
function! meta_notes#autosave#StatusLines() abort
  let l:cmd = meta_notes#autosave#WatcherCommand('')
  let l:lines = [
        \ 'autosave:   ' . (s:Autosave() ? 'on, ' . s:Delay() . ' ms debounce' : 'off'),
        \ 'autoreload: ' . (s:Autoreload() ? 'on' : 'off'),
        \ 'focus:      ' . (s:Autoreload() ? 'checktime on FocusGained' : 'off'),
        \ 'watcher:    ' . (!get(g:, 'meta_notes_watch', 1) ? 'disabled'
        \     : empty(l:cmd) ? 'not available (no fswatch or inotifywait)'
        \     : l:cmd[0] . (len(s:watchers) ? ', running for ' . len(s:watchers) . ' root(s)' : ', not running')),
        \ 'timer:      ' . (s:Interval() > 0 ? s:Interval() . ' ms'
        \     . (s:check_timer == -1 ? ' (not running)' : '') : 'off'),
        \ 'conflict diff: ' . (get(g:, 'meta_notes_conflict_diff', 1) ? 'on' : 'off'),
        \ ]
  return l:lines
endfunction

function! meta_notes#autosave#Status() abort
  echo join(meta_notes#autosave#StatusLines(), "\n")
endfunction

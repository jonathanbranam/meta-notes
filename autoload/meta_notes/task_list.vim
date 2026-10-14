" task_list.vim - Task list buffer for meta_notes
" Shows `meta-notes tasks --agenda` in a reused readonly scratch buffer

" Show the agenda in a readonly `Task List` buffer, reusing it if open
function! meta_notes#task_list#Show() abort
  let l:result = meta_notes#cli#Run(['tasks', '--agenda'])
  if !l:result.ok
    echohl ErrorMsg
    echo 'Error generating task list: ' . l:result.error
    echohl None
    return
  endif
  call meta_notes#cli#ShowWarnings(l:result)

  " Build the lines, and the file and line behind each one
  let l:lines = []
  let l:targets = []
  for l:section in l:result.agenda
    if empty(l:section.tasks)
      continue
    endif
    call add(l:lines, '# ' . l:section.heading)
    call add(l:targets, {})
    let l:file = ''
    for l:task in l:section.tasks
      if l:task.file !=# l:file
        let l:file = l:task.file
        call extend(l:lines, ['', '## [[' . substitute(l:file, '\.md$', '', '') . ']]', ''])
        call extend(l:targets, [{}, {}, {}])
      endif
      call add(l:lines, l:task.text)
      call add(l:targets, {'file': l:task.file, 'line': l:task.line})
    endfor
    call add(l:lines, '')
    call add(l:targets, {})
  endfor
  if empty(l:lines)
    let l:lines = ['No tasks.']
    let l:targets = [{}]
  endif

  " The jump is relative to the notes root, which is where Vim was started
  let l:root = getcwd()

  let l:bufnr = bufnr('Task List')
  if l:bufnr != -1
    let l:winnr = bufwinnr(l:bufnr)
    if l:winnr != -1
      execute l:winnr . 'wincmd w'
    else
      execute 'sbuffer ' . l:bufnr
    endif
  else
    execute 'new Task List'
  endif

  setlocal buftype=nofile
  setlocal bufhidden=hide
  setlocal noswapfile
  setlocal filetype=markdown

  setlocal modifiable
  setlocal noreadonly
  silent %delete _
  call setline(1, l:lines)
  setlocal nomodified
  setlocal readonly
  setlocal nomodifiable

  let b:meta_notes_task_targets = l:targets
  let b:meta_notes_task_root = l:root
  nnoremap <buffer> <silent> <CR> :call meta_notes#task_list#Jump()<CR>

  normal! gg
endfunction

" Open the task under the cursor at its file and line
function! meta_notes#task_list#Jump() abort
  let l:target = get(get(b:, 'meta_notes_task_targets', []), line('.') - 1, {})
  if empty(l:target)
    return
  endif
  execute 'edit +' . l:target.line . ' '
        \ . fnameescape(b:meta_notes_task_root . '/' . l:target.file)
endfunction

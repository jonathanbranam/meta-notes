" file_ops.vim - File operations for meta_notes
" Handles archiving and renaming. The meta-notes CLI moves the files and
" updates headers and wiki-links; these functions handle buffers and messages.

" Core method to move/rename a file or folder
" Args:
"   source_path: Source file or folder path
"   dest_path: Destination file or folder path
" Returns:
"   Dictionary with move results: {
"     'success': boolean,
"     'moves': [[old_path, new_path], ...],
"     'error': error message (if failed)
"   }
" Behavior:
"   - Moves files or entire directory trees
"   - Updates headers for all moved files
"   - Updates wiki-links across all markdown files
"   - Creates destination directories as needed
function! meta_notes#file_ops#MoveItem(source_path, dest_path) abort
  let l:cli = meta_notes#cli#Run(['move', '--', a:source_path, a:dest_path])
  call meta_notes#cli#ShowWarnings(l:cli)

  if !l:cli.ok
    return {'success': 0, 'moves': [], 'error': l:cli.error}
  endif

  return {'success': 1, 'moves': l:cli.moves, 'error': ''}
endfunction

" Archive a file or folder to the archive directory
" Args:
"   path: Path to file or folder to archive (optional, defaults to current buffer)
"         Can include wildcards (*, ?) for batch operations
" Behavior:
"   - Moves project/item → archive/project/item
"   - Moves area/item → archive/area/item
"   - Moves resource/item → archive/resource/item
"   - Preserves directory structure
"   - Updates wiki-links and headers for all moved files
"   - Updates the current buffer if archiving current file
"   - Supports wildcards for batch archiving (e.g., project/folder/*); the CLI
"     expands them and archives each match independently
function! meta_notes#file_ops#Archive(...) abort
  " Get the path to archive
  let l:path = (a:0 > 0 && a:1 !=# '') ? a:1 : expand('%:p:.')
  let l:current = expand('%:p')

  let l:cli = meta_notes#cli#Run(['archive', '--', l:path])

  " Without items the whole command failed (bad path, no wildcard matches)
  if !has_key(l:cli, 'items')
    echoerr l:cli.error
    return
  endif

  for l:item in l:cli.items
    if !l:item.ok
      echohl WarningMsg
      echo l:item.message
      echohl None
      continue
    endif

    " If current buffer is a file being archived, switch to the new location
    if l:item.is_file && l:current ==# fnamemodify(l:item.path, ':p')
      execute 'edit! ' . fnameescape(l:item.archive_path)
    endif

    echo l:item.message
  endfor

  call meta_notes#cli#ShowWarnings(l:cli)

  if l:cli.batch
    echo l:cli.summary
  endif
endfunction

" Rename the current note
" Args:
"   new_name: New name for the note (optional, prompts if not provided)
"             Can be just filename or full path
" Behavior:
"   - Renames current buffer's file
"   - Preserves directory if only filename provided
"   - Updates the current buffer to point to new location
"   - Updates wiki-links and headers
"   - If new_name includes path, moves file to new location
function! meta_notes#file_ops#Rename(...) abort
  " Get the current file path
  let l:current_path = expand('%:p')

  if l:current_path == ''
    echoerr 'No file associated with current buffer'
    return
  endif

  if !filereadable(l:current_path)
    echoerr 'Current buffer file does not exist: ' . l:current_path
    return
  endif

  " Get the new name
  let l:new_name = ''
  if a:0 > 0
    let l:new_name = a:1
  else
    " Prompt for new name
    let l:current_name = fnamemodify(l:current_path, ':t:r')
    let l:new_name = input('Rename to: ', l:current_name)
    if l:new_name == ''
      echo 'Rename cancelled'
      return
    endif
  endif

  let l:cli = meta_notes#cli#Run(['rename', '--',
        \ fnamemodify(l:current_path, ':p:.'), l:new_name])
  call meta_notes#cli#ShowWarnings(l:cli)

  if !l:cli.ok
    echoerr l:cli.error
    return
  endif

  let l:new_path = l:cli.dest

  " Update the buffer to the new location
  execute 'edit! ' . fnameescape(l:new_path)

  " Delete the old buffer
  execute 'bwipeout ' . fnameescape(l:current_path)

  echo 'Renamed: ' . fnamemodify(l:current_path, ':p:.') . ' → ' . fnamemodify(l:new_path, ':p:.')
endfunction

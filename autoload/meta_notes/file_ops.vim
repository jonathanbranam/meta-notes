" file_ops.vim - File operations for meta_notes
" Handles archiving, renaming, and link updates

" Archive a file or folder to the archive directory
" Args:
"   path: Path to file or folder to archive (optional, defaults to current buffer)
"         Can include wildcards (*, ?) for batch operations
" Behavior:
"   - Moves project/item → archive/project/item
"   - Moves area/item → archive/area/item
"   - Moves resource/item → archive/resource/item
"   - Preserves directory structure
"   - Updates the current buffer if archiving current file
"   - Supports wildcards for batch archiving (e.g., project/folder/*)
function! meta_notes#file_ops#Archive(...) abort
  " Get the path to archive
  let l:path = a:0 > 0 ? a:1 : expand('%:p:.')

  " Check if path contains wildcards
  if l:path =~ '[*?]'
    " Batch operation - expand wildcard and archive each item
    let l:items = glob(l:path, 0, 1)

    if len(l:items) == 0
      echoerr 'No items match wildcard pattern: ' . l:path
      return
    endif

    let l:archived_count = 0
    let l:failed_count = 0

    for l:item in l:items
      try
        call meta_notes#file_ops#Archive(l:item)
        let l:archived_count += 1
      catch
        let l:failed_count += 1
        echohl WarningMsg
        echo 'Failed to archive: ' . l:item . ' (' . v:exception . ')'
        echohl None
      endtry
    endfor

    echo 'Archived ' . l:archived_count . ' item(s)' . (l:failed_count > 0 ? ' (' . l:failed_count . ' failed)' : '')
    return
  endif

  " Single item operation
  " Remove .md extension if present for consistent handling
  let l:path_no_ext = substitute(l:path, '\.md$', '', '')

  " Determine if it's a file or directory
  let l:is_file = filereadable(l:path)
  let l:is_dir = isdirectory(l:path_no_ext)

  if !l:is_file && !l:is_dir
    echoerr 'Path not found: ' . l:path
    return
  endif

  " Determine the archive destination
  " Extract the base folder (project, area, or resource)
  let l:parts = split(l:path_no_ext, '/')

  if len(l:parts) == 0
    echoerr 'Invalid path: ' . l:path
    return
  endif

  let l:base_folder = l:parts[0]

  " Only allow archiving from project, area, or resource folders
  if l:base_folder != 'project' && l:base_folder != 'area' && l:base_folder != 'resource'
    echoerr 'Can only archive items from project/, area/, or resource/ folders'
    return
  endif

  " Check if already in archive
  if l:base_folder == 'archive'
    echoerr 'Item is already in archive'
    return
  endif

  " Build the archive destination path
  let l:archive_path = 'archive/' . l:path_no_ext

  " Create the archive directory if needed
  let l:archive_dir = fnamemodify(l:archive_path, ':h')
  if !isdirectory(l:archive_dir)
    call mkdir(l:archive_dir, 'p')
  endif

  " Move the item
  if l:is_file
    " Archive a file
    let l:source_file = l:path
    let l:dest_file = l:archive_path . '.md'

    " Use system rename to move the file
    let l:result = rename(l:source_file, l:dest_file)

    if l:result != 0
      echoerr 'Failed to archive file: ' . l:source_file
      return
    endif

    " If current buffer is the file being archived, switch to the new location
    if expand('%:p') == fnamemodify(l:source_file, ':p')
      execute 'edit! ' . fnameescape(l:dest_file)
    endif

    echo 'Archived: ' . l:path . ' → ' . l:archive_path . '.md'
  elseif l:is_dir
    " Archive a directory
    " Use system command to move the directory
    let l:cmd = 'mv ' . shellescape(l:path_no_ext) . ' ' . shellescape(l:archive_path)
    let l:output = system(l:cmd)

    if v:shell_error != 0
      echoerr 'Failed to archive directory: ' . l:path_no_ext . "\n" . l:output
      return
    endif

    echo 'Archived: ' . l:path_no_ext . ' → ' . l:archive_path
  endif
endfunction

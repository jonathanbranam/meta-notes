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

" Rename the current note
" Args:
"   new_name: New name for the note (optional, prompts if not provided)
"             Can be just filename or full path
" Behavior:
"   - Renames current buffer's file
"   - Preserves directory if only filename provided
"   - Updates the current buffer to point to new location
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

  " Determine the new path
  let l:new_path = ''
  if l:new_name =~ '/'
    " New name includes path - use it as-is
    let l:new_path = l:new_name
  else
    " Just a filename - keep the same directory
    let l:current_dir = fnamemodify(l:current_path, ':h')
    let l:new_path = l:current_dir . '/' . l:new_name
  endif

  " Add .md extension if not present
  if l:new_path !~ '\.md$'
    let l:new_path = l:new_path . '.md'
  endif

  " Check if target already exists
  if filereadable(l:new_path)
    echoerr 'Target file already exists: ' . l:new_path
    return
  endif

  " Create target directory if needed
  let l:target_dir = fnamemodify(l:new_path, ':h')
  if !isdirectory(l:target_dir)
    call mkdir(l:target_dir, 'p')
  endif

  " Rename the file
  let l:result = rename(l:current_path, l:new_path)

  if l:result != 0
    echoerr 'Failed to rename file: ' . l:current_path
    return
  endif

  " Update the header if it matches the old path
  " Read the file content
  let l:file_lines = readfile(l:new_path)
  if len(l:file_lines) > 0
    " Check if first line is a heading that matches the old path
    let l:first_line = l:file_lines[0]
    " Get the old and new paths without .md extension
    let l:old_header_path = substitute(fnamemodify(l:current_path, ':p:.'), '\.md$', '', '')
    let l:new_header_path = substitute(fnamemodify(l:new_path, ':p:.'), '\.md$', '', '')

    " Check if first line is "# <old_path>"
    let l:expected_old_header = '# ' . l:old_header_path
    if l:first_line == l:expected_old_header
      " Update to new path
      let l:file_lines[0] = '# ' . l:new_header_path
      call writefile(l:file_lines, l:new_path)
    endif
  endif

  " Update wiki-links across all markdown files
  " Convert paths to relative paths without .md extension for link matching
  let l:old_link_path = substitute(fnamemodify(l:current_path, ':p:.'), '\.md$', '', '')
  let l:new_link_path = substitute(fnamemodify(l:new_path, ':p:.'), '\.md$', '', '')

  " Get plugin root directory
  let l:plugin_root = meta_notes#template#GetPluginRoot()

  " Call update_links.py script to update all wiki-links
  let l:update_cmd = 'python3 ' . shellescape(l:plugin_root . '/scripts/update_links.py')
        \ . ' ' . shellescape(l:old_link_path)
        \ . ' ' . shellescape(l:new_link_path)

  let l:update_output = system(l:update_cmd)

  if v:shell_error != 0
    echohl WarningMsg
    echo 'Warning: Failed to update wiki-links: ' . l:update_output
    echohl None
  else
    " Parse output to show how many links were updated
    let l:modified_match = matchlist(l:update_output, 'Modified \(\d\+\) files')
    if len(l:modified_match) > 1 && str2nr(l:modified_match[1]) > 0
      echo 'Updated ' . l:modified_match[1] . ' file(s) with wiki-links'
    endif
  endif

  " Update the buffer to the new location
  execute 'edit! ' . fnameescape(l:new_path)

  " Delete the old buffer
  execute 'bwipeout ' . fnameescape(l:current_path)

  echo 'Renamed: ' . fnamemodify(l:current_path, ':p:.') . ' → ' . fnamemodify(l:new_path, ':p:.')
endfunction

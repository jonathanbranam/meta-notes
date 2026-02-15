" file_ops.vim - File operations for meta_notes
" Handles archiving, renaming, and link updates

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
  let l:result = {'success': 0, 'moves': [], 'error': ''}

  " Normalize paths
  let l:source = a:source_path
  let l:dest = a:dest_path

  " Check if source exists
  let l:is_file = filereadable(l:source)
  let l:is_dir = isdirectory(l:source)

  if !l:is_file && !l:is_dir
    let l:result.error = 'Source not found: ' . l:source
    return l:result
  endif

  if l:is_file
    " Moving a single file
    " Add .md extension to dest if source has it and dest doesn't
    if l:source =~ '\.md$' && l:dest !~ '\.md$'
      let l:dest = l:dest . '.md'
    endif

    " Check if target already exists
    if filereadable(l:dest)
      let l:result.error = 'Target file already exists: ' . l:dest
      return l:result
    endif

    " Create target directory if needed
    let l:target_dir = fnamemodify(l:dest, ':h')
    if !isdirectory(l:target_dir)
      call mkdir(l:target_dir, 'p')
    endif

    " Move the file
    let l:rename_result = rename(l:source, l:dest)
    if l:rename_result != 0
      let l:result.error = 'Failed to move file: ' . l:source
      return l:result
    endif

    " Track the move
    call add(l:result.moves, [l:source, l:dest])

    " Update the header if it matches the old path
    call s:UpdateFileHeader(l:source, l:dest)

  elseif l:is_dir
    " Moving a directory - need to handle all files recursively
    " Find all markdown files in the source directory
    let l:md_files = glob(l:source . '/**/*.md', 0, 1)

    " Also check for markdown files in the root of the source directory
    let l:root_files = glob(l:source . '/*.md', 0, 1)
    let l:all_files = l:root_files + l:md_files

    " Build list of moves
    for l:file in l:all_files
      " Calculate relative path within source directory
      let l:rel_path = substitute(l:file, '^' . escape(l:source, '/'), '', '')
      let l:dest_file = l:dest . l:rel_path
      call add(l:result.moves, [l:file, l:dest_file])
    endfor

    " Create destination parent directory (but not the dest itself)
    " mv will create the destination directory when moving
    let l:dest_parent = fnamemodify(l:dest, ':h')
    if !isdirectory(l:dest_parent)
      call mkdir(l:dest_parent, 'p')
    endif

    " Use system mv command to move the directory
    let l:cmd = 'mv ' . shellescape(l:source) . ' ' . shellescape(l:dest)
    let l:output = system(l:cmd)

    if v:shell_error != 0
      let l:result.error = 'Failed to move directory: ' . l:source . "\n" . l:output
      return l:result
    endif

    " Update headers for all moved files
    for [l:old_file, l:new_file] in l:result.moves
      call s:UpdateFileHeader(l:old_file, l:new_file)
    endfor
  endif

  " Update all wiki-links across the repository
  if len(l:result.moves) > 0
    call s:UpdateAllWikiLinks(l:result.moves)
  endif

  let l:result.success = 1
  return l:result
endfunction

" Update the header of a moved file if it matches the old path
" Args:
"   old_path: Old file path
"   new_path: New file path
function! s:UpdateFileHeader(old_path, new_path) abort
  " Read the file content
  if !filereadable(a:new_path)
    return
  endif

  let l:file_lines = readfile(a:new_path)
  if len(l:file_lines) == 0
    return
  endif

  " Check if first line is a heading that matches the old path
  let l:first_line = l:file_lines[0]

  " Get the old and new paths without .md extension
  let l:old_header_path = substitute(fnamemodify(a:old_path, ':p:.'), '\.md$', '', '')
  let l:new_header_path = substitute(fnamemodify(a:new_path, ':p:.'), '\.md$', '', '')

  " Check if first line is "# <old_path>"
  let l:expected_old_header = '# ' . l:old_header_path
  if l:first_line == l:expected_old_header
    " Update to new path
    let l:file_lines[0] = '# ' . l:new_header_path
    call writefile(l:file_lines, a:new_path)
  endif
endfunction

" Update wiki-links for all moved files
" Args:
"   moves: List of [old_path, new_path] pairs
function! s:UpdateAllWikiLinks(moves) abort
  " Get plugin root directory
  let l:plugin_root = meta_notes#template#GetPluginRoot()

  " Update links for each moved file
  for [l:old_path, l:new_path] in a:moves
    " Convert paths to relative paths without .md extension for link matching
    let l:old_link_path = substitute(fnamemodify(l:old_path, ':p:.'), '\.md$', '', '')
    let l:new_link_path = substitute(fnamemodify(l:new_path, ':p:.'), '\.md$', '', '')

    " Call update_links.py script
    let l:update_cmd = 'python3 ' . shellescape(l:plugin_root . '/scripts/update_links.py')
          \ . ' ' . shellescape(l:old_link_path)
          \ . ' ' . shellescape(l:new_link_path)

    let l:update_output = system(l:update_cmd)

    if v:shell_error != 0
      echohl WarningMsg
      echo 'Warning: Failed to update wiki-links for: ' . l:old_link_path
      echohl None
    endif
  endfor
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

  " Determine source path (file or directory)
  let l:source_path = l:is_file ? l:path : l:path_no_ext

  " Move the item using core method
  let l:result = meta_notes#file_ops#MoveItem(l:source_path, l:archive_path)

  if !l:result.success
    echoerr l:result.error
    return
  endif

  " If current buffer is a file being archived, switch to the new location
  if l:is_file && expand('%:p') == fnamemodify(l:source_path, ':p')
    let l:dest_file = l:archive_path . '.md'
    execute 'edit! ' . fnameescape(l:dest_file)
  endif

  " Show summary
  let l:move_count = len(l:result.moves)
  if l:move_count > 1
    echo 'Archived: ' . l:path_no_ext . ' → ' . l:archive_path . ' (' . l:move_count . ' files)'
  else
    echo 'Archived: ' . l:path . ' → ' . l:archive_path . (l:is_file ? '.md' : '')
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

  " Move the file using core method
  let l:result = meta_notes#file_ops#MoveItem(l:current_path, l:new_path)

  if !l:result.success
    echoerr l:result.error
    return
  endif

  " Update the buffer to the new location
  execute 'edit! ' . fnameescape(l:new_path)

  " Delete the old buffer
  execute 'bwipeout ' . fnameescape(l:current_path)

  echo 'Renamed: ' . fnamemodify(l:current_path, ':p:.') . ' → ' . fnamemodify(l:new_path, ':p:.')
endfunction

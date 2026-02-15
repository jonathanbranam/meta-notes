" meta_notes.vim - Life management system based on PARA methodology
" Maintainer: Your Name
" Version: 0.1.0

if exists('g:loaded_meta_notes')
  finish
endif
let g:loaded_meta_notes = 1

" Save cpo and set to vim defaults
let s:save_cpo = &cpo
set cpo&vim

" Get the plugin root directory
let s:plugin_root = expand('<sfile>:p:h:h')

" Development: Reload command for fast iteration
command! MetaNotesReload call s:MetaNotesReload()
function! s:MetaNotesReload()
  " Source main plugin file
  execute 'source' s:plugin_root . '/plugin/meta_notes.vim'

  " Source all autoload files
  for file in glob(s:plugin_root . '/autoload/**/*.vim', 0, 1)
    execute 'source' file
  endfor

  echo "meta-notes reloaded! Run :TestMetaNotes to test."
endfunction

" Testing: Run vader tests
command! TestMetaNotes execute 'Vader' s:plugin_root . '/test/*.vader'

" Main plugin commands
command! MetaNotesOpen call meta_notes#notes#Open()
command! -nargs=? MetaNotesDaily call meta_notes#notes#OpenDaily(<f-args>)
command! -nargs=? MetaNotesWeekPlan call meta_notes#notes#OpenWeekPlan(<f-args>)
command! -nargs=? MetaNotesQuarterPlan call meta_notes#notes#OpenQuarterPlan(<f-args>)
command! -nargs=? MetaNotesYearPlan call meta_notes#notes#OpenYearPlan(<f-args>)

" Navigation commands
command! MetaNotesDailyPrev call meta_notes#notes#DailyPrev()
command! MetaNotesDailyNext call meta_notes#notes#DailyNext()
command! MetaNotesJumpToWeek call meta_notes#notes#JumpToWeek()


" Initialization command
" Use ! to force overwrite of existing templates
" Example: :MetaNotesInit! to overwrite existing files
command! -bang MetaNotesInit call meta_notes#notes#Init(<bang>0)

" File operations
command! -nargs=? -complete=file MetaNotesArchive call meta_notes#file_ops#Archive(<f-args>)
command! -nargs=? MetaNotesRename call meta_notes#file_ops#Rename(<f-args>)
command! -nargs=+ -complete=file MetaNotesMoveItem call s:MetaNotesMoveItemWrapper(<f-args>)

" Wrapper for MoveItem to provide user feedback
function! s:MetaNotesMoveItemWrapper(...) abort
  if a:0 < 2
    echoerr 'MetaNotesMoveItem requires two arguments: source and destination'
    echo 'Usage: MetaNotesMoveItem <source_path> <dest_path>'
    return
  endif

  let l:source = a:1
  let l:dest = a:2

  " Call the core MoveItem function
  let l:result = meta_notes#file_ops#MoveItem(l:source, l:dest)

  if !l:result.success
    echoerr l:result.error
    return
  endif

  " Show summary
  let l:move_count = len(l:result.moves)
  if l:move_count == 0
    echo 'No files were moved'
  elseif l:move_count == 1
    echo 'Moved: ' . l:source . ' → ' . l:dest
  else
    echo 'Moved: ' . l:source . ' → ' . l:dest . ' (' . l:move_count . ' files)'
    echo 'Updated headers and wiki-links'
  endif
endfunction

" Time tracking
command! MetaNotesTimeReport call meta_notes#time_tracking#ShowReport()


" Restore cpo
let &cpo = s:save_cpo
unlet s:save_cpo

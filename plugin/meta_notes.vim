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
command! ReloadMetaNotes call s:ReloadMetaNotes()
function! s:ReloadMetaNotes()
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

" Restore cpo
let &cpo = s:save_cpo
unlet s:save_cpo

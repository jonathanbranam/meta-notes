" after/syntax/markdown.vim - Extended syntax highlighting for meta-notes
" Extends markdown syntax with time tracking specific highlighting

" Time tracking special tags (different colors for different activity types)
" Meeting tags - highlighted in blue/cyan
syntax match metaNotesTagMeeting /#mtg\>/
syntax match metaNotesTagMeeting /#meeting\>/

" Development tags - highlighted in green
syntax match metaNotesTagDev /#dev\>/
syntax match metaNotesTagDev /#code\>/
syntax match metaNotesTagDev /#coding\>/

" Personal tags - highlighted in magenta/purple
syntax match metaNotesTagPersonal /#pers\>/
syntax match metaNotesTagPersonal /#personal\>/

" Admin tags - highlighted in yellow
syntax match metaNotesTagAdmin /#admin\>/
syntax match metaNotesTagAdmin /#administrative\>/

" Break tags - highlighted in gray/comment color
syntax match metaNotesTagBreak /#break\>/

" Activity tags (generic user-defined tags) - highlighted in default tag color
syntax match metaNotesTagActivity /#[a-zA-Z0-9_-]\+\>/

" Break entries in square brackets: [break], [lunch], etc.
syntax match metaNotesBreak /\[break\]/
syntax match metaNotesBreak /\[lunch\]/
syntax match metaNotesBreak /\[[^\]]*break[^\]]*\]/

" Off-plan entries with strikethrough: ~text~, both tildes on one line, in
" daily notes only
if meta_notes#time_tracking#IsInDailyNote()
  syntax match metaNotesOffPlan /\~[^~]\+\~/

  " Time Block cell highlights: the "### Time Block" section of a daily note,
  " up to the next heading of level 3 or higher. Each highlight covers one
  " table cell (the text between two pipes). The heading line itself is left
  " to the markdown heading group: the region starts after its newline (the
  " lookbehind), so the heading never matches it.
  syntax region metaNotesTimeBlock transparent keepend
        \ start=/\(^###\s\+Time Block\s*\n\)\@<=/ end=/^#\{1,3}\s/me=s-1
        \ contains=@metaNotesTimeBlockCells,metaNotesTagMeeting,metaNotesTagDev,metaNotesTagPersonal,metaNotesTagAdmin,metaNotesTagBreak,metaNotesTagActivity,metaNotesBreak,metaNotesOffPlan
  syntax cluster metaNotesTimeBlockCells contains=metaNotesTimeBlockMtg,metaNotesTimeBlockBracket,metaNotesTimeBlockTilde,metaNotesTimeBlockParen,metaNotesTimeBlockTrain,metaNotesTimeBlockPers,metaNotesTimeBlockWork
  syntax match metaNotesTimeBlockMtg /|\zs[^|]*mtg:[^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockBracket /|\zs[^|]*\[[^|]*\][^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockTilde /|\zs[^|]*\~[^|~]\+\~[^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockParen /|\zs[^|]*([^|]*)[^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockTrain /|\zs[^|]*train:[^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockPers /|\zs[^|]*pers:[^|]*\ze|/ contained contains=TOP
  syntax match metaNotesTimeBlockWork /|\zs[^|]*work:[^|]*\ze|/ contained contains=TOP
endif

" Arrived entry
syntax match metaNotesArrived /^-\s*arrived:/

" Color scheme definitions
" Link to existing Vim highlight groups for consistency

" Special tags with distinct colors
highlight default link metaNotesTagMeeting Identifier
highlight default link metaNotesTagDev String
highlight default link metaNotesTagPersonal Type
highlight default link metaNotesTagAdmin Constant
highlight default link metaNotesTagBreak Comment

" Generic activity tags
highlight default link metaNotesTagActivity Tag

" Special entries
highlight default link metaNotesBreak Comment
highlight default link metaNotesOffPlan Comment
highlight default link metaNotesArrived Special

" Make strikethrough text appear dimmed/grayed out
highlight default metaNotesOffPlan gui=strikethrough cterm=strikethrough ctermfg=Gray guifg=Gray

" Time Block cell highlights, one background per kind of cell
highlight default metaNotesTimeBlockMtg    ctermfg=Black ctermbg=Cyan     guifg=#000000 guibg=#7fd6e6
highlight default metaNotesTimeBlockBracket ctermfg=Black ctermbg=Yellow  guifg=#000000 guibg=#e6d67f
highlight default metaNotesTimeBlockTilde  ctermfg=Black ctermbg=Gray     guifg=#000000 guibg=#b0b0b0
highlight default metaNotesTimeBlockParen  ctermfg=Black ctermbg=Magenta  guifg=#000000 guibg=#d69fe6
highlight default metaNotesTimeBlockTrain  ctermfg=Black ctermbg=Red      guifg=#000000 guibg=#e69f9f
highlight default metaNotesTimeBlockPers   ctermfg=Black ctermbg=Green    guifg=#000000 guibg=#9fe6a0
highlight default metaNotesTimeBlockWork   ctermfg=Black ctermbg=Blue     guifg=#000000 guibg=#9fb8e6

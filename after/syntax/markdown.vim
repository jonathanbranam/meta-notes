" after/syntax/markdown.vim - Extended syntax highlighting for meta-notes
" Extends markdown syntax with time tracking specific highlighting

" Only load once
if exists("b:meta_notes_syntax_loaded")
  finish
endif
let b:meta_notes_syntax_loaded = 1

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

" Off-plan entries with strikethrough: ~text~
syntax region metaNotesOffPlan start=/\~/ end=/\~/

" Time entries in time log: HH:MM am/pm
syntax match metaNotesTime /\d\{1,2}:\d\{2}\s*\(am\|pm\)/

" Arrived entry
syntax match metaNotesArrived /^-\s*arrived:/

" Time block table time column (e.g., "| 8:00am |")
syntax match metaNotesTableTime /|\s*\d\{1,2}:\d\{2}\(am\|pm\)\s*|/

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
highlight default link metaNotesTime Number
highlight default link metaNotesTableTime Number
highlight default link metaNotesArrived Special

" Make strikethrough text appear dimmed/grayed out
highlight default metaNotesOffPlan gui=strikethrough cterm=strikethrough ctermfg=Gray guifg=Gray

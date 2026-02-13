# Delimiter API Documentation

## Overview

The meta-notes plugin provides a generic function for extracting text within various types of delimiters when the cursor is positioned within them.

## Core Function

### `meta_notes#notes#GetTextWithinDelimiters(open_delim, close_delim)`

Generic function to extract text between delimiters under the cursor.

**Parameters:**
- `open_delim`: Opening delimiter string (e.g., `'[['`, `'['`, `'<'`, `'('`, `'|'`)
- `close_delim`: Closing delimiter string (e.g., `']]'`, `']'`, `'>'`, `')'`, `'|'`)

**Returns:**
- The text between delimiters if cursor is within them
- Empty string `''` if cursor is not within any matching delimiter pair

**Behavior:**
- Handles multiple occurrences of the same delimiter on a line
- Works with single-character or multi-character delimiters
- Cursor can be anywhere from the opening delimiter to (and including) the closing delimiter
- Uses non-greedy matching to handle nested or multiple delimiters correctly

## Supported Delimiter Types

### Double Square Brackets (Wiki-style links)
```vim
" Example: [[note/path/filename]]
let path = meta_notes#notes#GetTextWithinDelimiters('[[', ']]')
```

### Single Square Brackets
```vim
" Example: [tag-name]
let tag = meta_notes#notes#GetTextWithinDelimiters('[', ']')
```

### Angle Brackets (HTML-style links)
```vim
" Example: <http://example.com>
let url = meta_notes#notes#GetTextWithinDelimiters('<', '>')
```

### Parentheses (Markdown link URLs)
```vim
" Example: [Link Text](http://example.com)
let url = meta_notes#notes#GetTextWithinDelimiters('(', ')')
```

### Pipe Symbols
```vim
" Example: |important data|
let data = meta_notes#notes#GetTextWithinDelimiters('|', '|')
```

## Convenience Functions

### `meta_notes#notes#GetLinkUnderCursor()`

Convenience wrapper specifically for wiki-style `[[...]]` links.

**Parameters:** None

**Returns:**
- The filename/path if cursor is within `[[...]]`
- Empty string if not

**Equivalent to:**
```vim
meta_notes#notes#GetTextWithinDelimiters('[[', ']]')
```

## Usage Examples

### Extract Wiki Link Path
```vim
" Line: "See also [[project/notes/meeting]] for details"
" Cursor position: anywhere within [[...]]
call cursor(1, 20)  " Position cursor inside the link
let path = meta_notes#notes#GetLinkUnderCursor()
" Returns: 'project/notes/meeting'
```

### Extract URL from Angle Brackets
```vim
" Line: "Visit <http://example.com> for more info"
" Cursor position: anywhere within <...>
call cursor(1, 15)
let url = meta_notes#notes#GetTextWithinDelimiters('<', '>')
" Returns: 'http://example.com'
```

### Extract Markdown Link URL
```vim
" Line: "Click [here](https://example.com/page) to continue"
" Cursor position: anywhere within (...)
call cursor(1, 20)
let url = meta_notes#notes#GetTextWithinDelimiters('(', ')')
" Returns: 'https://example.com/page'
```

### Handle Multiple Delimiters
```vim
" Line: "Links: [[first]] and [[second]] here"
" Returns different results based on cursor position:
call cursor(1, 12)
let first = meta_notes#notes#GetLinkUnderCursor()   " Returns: 'first'

call cursor(1, 28)
let second = meta_notes#notes#GetLinkUnderCursor()  " Returns: 'second'

call cursor(1, 22)
let none = meta_notes#notes#GetLinkUnderCursor()    " Returns: ''
```

### Mixed Delimiter Types
```vim
" Line: "See [[wiki]] and <http://url.com> and (parens)"
" Extract each type independently:
call cursor(1, 10)
let wiki = meta_notes#notes#GetTextWithinDelimiters('[[', ']]')   " Returns: 'wiki'

call cursor(1, 25)
let url = meta_notes#notes#GetTextWithinDelimiters('<', '>')      " Returns: 'http://url.com'

call cursor(1, 48)
let text = meta_notes#notes#GetTextWithinDelimiters('(', ')')     " Returns: 'parens'
```

## Implementation Notes

- Uses VimScript's non-greedy matching (`.\{-}`) for reliable delimiter detection
- Properly escapes special regex characters in delimiters
- Works with cursor positioned anywhere from start to end of delimited text
- Returns empty string when cursor is outside all delimited regions
- Handles special characters within content (URLs with query params, file paths, etc.)

## Testing

Comprehensive tests are available in:
- `test/get_text_within_delimiters.vader` - Tests all delimiter types
- `test/get_link_under_cursor.vader` - Tests wiki-link convenience wrapper
- `test/open_note.vader` - Integration tests with file operations

Run all tests:
```bash
./run_tests.sh
```

Run specific delimiter tests:
```bash
./run_tests.sh test/get_text_within_delimiters.vader
```

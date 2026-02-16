" template.vim - Template processing for meta_notes
" Handles template discovery, variable substitution, and command execution

" Store the plugin root directory at script load time
let s:plugin_root = fnamemodify(expand('<sfile>:p:h'), ':h:h')

" Get the plugin root directory
" Returns:
"   Absolute path to the plugin root directory
function! meta_notes#template#GetPluginRoot() abort
  return s:plugin_root
endfunction

" Execute a Python script from the scripts/ directory
" Args:
"   script_name: Name of the script (e.g., 'time_report.py' or 'scripts/time_report.py')
"   args: List of arguments to pass to the script
" Returns:
"   Dictionary with keys:
"     - success: 1 if successful, 0 if error
"     - output: The script output
"     - error: Error message (empty if success)
function! meta_notes#template#ExecutePythonScript(script_name, ...) abort
  " Get plugin root
  let l:plugin_root = meta_notes#template#GetPluginRoot()

  " Normalize script name (remove leading 'scripts/' if present)
  let l:script = substitute(a:script_name, '^scripts/', '', '')

  " Construct full script path
  let l:script_path = l:plugin_root . '/scripts/' . l:script

  " Check if script exists
  if !filereadable(l:script_path)
    return {
          \ 'success': 0,
          \ 'output': '',
          \ 'error': 'Python script not found: ' . l:script_path
          \ }
  endif

  " Build command with arguments
  let l:cmd = 'python3 ' . shellescape(l:script_path)

  " Add any arguments
  if a:0 > 0
    for l:arg in a:1
      let l:cmd .= ' ' . shellescape(l:arg)
    endfor
  endif

  " Execute the script
  let l:output = system(l:cmd)

  " Check for errors
  if v:shell_error != 0
    return {
          \ 'success': 0,
          \ 'output': l:output,
          \ 'error': 'Python script failed with exit code ' . v:shell_error
          \ }
  endif

  return {
        \ 'success': 1,
        \ 'output': l:output,
        \ 'error': ''
        \ }
endfunction

" Find the appropriate template for a given file path
" Args:
"   filepath: Path to the file being created (e.g., 'project/my-project/note.md')
"   template_type: Optional template type ('daily', 'weekly', 'quarterly', 'yearly')
" Returns:
"   Path to template file, or empty string if no template found
" Search order:
"   1. Folder-specific template.md in the same directory
"   2. Standard template in resource/template/ (if template_type is provided)
"   3. Auto-detect template type based on folder path
"   4. Empty string (no template)
function! meta_notes#template#FindTemplate(filepath, ...) abort
  let l:template_type = a:0 > 0 ? a:1 : ''

  " Get the directory of the file being created
  let l:dir = fnamemodify(a:filepath, ':h')

  " Check for folder-specific template.md
  let l:folder_template = l:dir . '/template.md'
  if filereadable(l:folder_template)
    return l:folder_template
  endif

  " Check for standard template if type is provided
  if l:template_type != ''
    let l:standard_template = 'resource/template/' . l:template_type . '.md'
    if filereadable(l:standard_template)
      return l:standard_template
    endif
  endif

  " Auto-detect template type based on folder path
  if l:template_type == ''
    if match(a:filepath, '^plan/daily/') != -1
      let l:template_type = 'daily'
    elseif match(a:filepath, '^plan/week/') != -1
      let l:template_type = 'weekly'
    elseif match(a:filepath, '^plan/quarter/') != -1
      let l:template_type = 'quarterly'
    elseif match(a:filepath, '^plan/year/') != -1
      let l:template_type = 'yearly'
    endif

    " Check for auto-detected template
    if l:template_type != ''
      let l:standard_template = 'resource/template/' . l:template_type . '.md'
      if filereadable(l:standard_template)
        return l:standard_template
      endif
    endif
  endif

  " No template found
  return ''
endfunction

" Process template variables in a line of text
" Args:
"   line: Line of text containing template variables
"   context: Dictionary with template context (date, today, week_start, week_end, etc.)
" Returns:
"   Processed line with variables replaced
" Supported variables:
"   {{date}}, {{today}}, {{week_start}}, {{week_end}}
"   With optional arithmetic: {{today+1}}, {{date-7}}
"   With optional format: {{today:%Y-%m-%d}}, {{date:%A}}
function! meta_notes#template#ProcessVariables(line, context) abort
  let l:result = a:line

  " Pattern: {{variable}} or {{variable+N}} or {{variable-N}} or {{variable:%format}}
  " or combinations like {{variable+N:%format}}
  let l:pattern = '{{\([^}]\+\)}}'

  while 1
    let l:match = matchstr(l:result, l:pattern)
    if l:match == ''
      break
    endif

    " Extract the variable expression (without {{ and }})
    let l:expr = substitute(l:match, '{{', '', '')
    let l:expr = substitute(l:expr, '}}', '', '')

    " Parse variable name, arithmetic, and format
    " Format: varname[+/-N][:%format]
    let l:var_name = ''
    let l:arithmetic = 0
    let l:format = ''

    " Check for format specifier
    if match(l:expr, ':') != -1
      let l:parts = split(l:expr, ':', 1)
      let l:expr_part = l:parts[0]
      let l:format = join(l:parts[1:], ':')
    else
      let l:expr_part = l:expr
    endif

    " Check for arithmetic
    if match(l:expr_part, '[+-]') != -1
      let l:matches = matchlist(l:expr_part, '\([^+-]\+\)\([+-]\)\(\d\+\)')
      if len(l:matches) > 3
        let l:var_name = l:matches[1]
        let l:op = l:matches[2]
        let l:days = str2nr(l:matches[3])
        let l:arithmetic = l:op == '+' ? l:days : -l:days
      else
        let l:var_name = l:expr_part
      endif
    else
      let l:var_name = l:expr_part
    endif

    " Handle special variables
    if l:var_name == 'project_name'
      " Extract project name from filepath in context
      if has_key(a:context, 'filepath')
        let l:filepath = a:context['filepath']
        " Check if path starts with 'project/'
        if match(l:filepath, '^project/') == 0
          " Extract the project folder name (second path component)
          let l:parts = split(l:filepath, '/')
          if len(l:parts) >= 2
            let l:replacement = l:parts[1]
          else
            let l:replacement = '<!-- Not in project folder -->'
          endif
        else
          let l:replacement = '<!-- Not in project folder -->'
        endif
      else
        let l:replacement = '<!-- ERROR: No filepath in context -->'
      endif
      let l:result = substitute(l:result, l:pattern, l:replacement, '')
      continue
    endif

    " Get the base date from context
    if !has_key(a:context, l:var_name)
      " Unknown variable, replace with HTML comment indicating error
      let l:replacement = '<!-- ERROR: Unknown variable "' . l:var_name . '" -->'
      let l:result = substitute(l:result, l:pattern, l:replacement, '')
      continue
    endif

    let l:value = a:context[l:var_name]

    " Check if this is a date variable (YYYY-MM-DD format) or a string variable
    " String variables (like 'quarter': 'Q1') are used as-is without date processing
    if match(l:value, '^\d\{4\}-\d\{2\}-\d\{2\}$') != -1
      " This is a date variable - process with date formatting
      let l:date_str = l:value

      " Apply arithmetic if needed
      if l:arithmetic != 0
        let l:timestamp = strptime("%Y-%m-%d", l:date_str)
        let l:new_timestamp = l:timestamp + (l:arithmetic * 86400)
        let l:date_str = strftime('%Y-%m-%d', l:new_timestamp)
      endif

      " Apply format if provided, otherwise use default format
      if l:format != ''
        let l:timestamp = strptime("%Y-%m-%d", l:date_str)
        let l:replacement = strftime(l:format, l:timestamp)
      else
        " Default format: YYYY-MM-DD ddd
        let l:timestamp = strptime("%Y-%m-%d", l:date_str)
        let l:day_abbr = strftime('%a', l:timestamp)
        let l:replacement = l:date_str . ' ' . l:day_abbr
      endif
    else
      " This is a string variable - use as-is
      let l:replacement = l:value
    endif

    " Replace the variable in the result
    let l:result = substitute(l:result, l:pattern, l:replacement, '')
  endwhile

  return l:result
endfunction

" Execute a command in a template and return its output
" Args:
"   command_line: Line containing command markup (e.g., "{{% python script.py %}}")
"   context: Dictionary with template context
" Returns:
"   Command output or error comment
" Supported command types:
"   {{% vim command %}}
"   {{% python script.py --args %}}
"   {{% shell command %}}
function! meta_notes#template#ExecuteCommand(command_line, context) abort
  " Pattern: {{% type command %}}
  let l:pattern = '{{%\s*\(\w\+\)\s\+\(.\+\)\s*%}}'
  let l:matches = matchlist(a:command_line, l:pattern)

  if len(l:matches) < 3
    return a:command_line
  endif

  let l:cmd_type = l:matches[1]
  let l:cmd = l:matches[2]

  " Process variables in the command
  let l:cmd = meta_notes#template#ProcessVariables(l:cmd, a:context)

  try
    if l:cmd_type == 'vim'
      " Execute vim command and capture output
      redir => l:output
      silent execute l:cmd
      redir END
      return l:output
    elseif l:cmd_type == 'python'
      " Resolve script path relative to plugin root if it starts with 'scripts/'
      let l:resolved_cmd = l:cmd
      if match(l:cmd, '^\s*scripts/') != -1
        let l:plugin_root = meta_notes#template#GetPluginRoot()
        let l:resolved_cmd = substitute(l:cmd, '^\s*scripts/', l:plugin_root . '/scripts/', '')
      endif

      " Execute python command
      let l:output = system('python3 ' . l:resolved_cmd)
      if v:shell_error != 0
        return '<!-- Command failed: ' . a:command_line . "\n" . 'Error: ' . l:output . ' -->'
      endif
      return l:output
    elseif l:cmd_type == 'shell'
      " Execute shell command
      let l:output = system(l:cmd)
      if v:shell_error != 0
        return '<!-- Command failed: ' . a:command_line . "\n" . 'Error: ' . l:output . ' -->'
      endif
      return l:output
    else
      return '<!-- Unknown command type: ' . l:cmd_type . ' -->'
    endif
  catch
    return '<!-- Command failed: ' . a:command_line . "\n" . 'Error: ' . v:exception . ' -->'
  endtry
endfunction

" Process a template file and return the processed content
" Args:
"   template_path: Path to template file
"   context: Dictionary with template context (date, today, week_start, week_end, etc.)
" Returns:
"   List of lines with variables replaced and commands executed
function! meta_notes#template#ProcessTemplate(template_path, context) abort
  if !filereadable(a:template_path)
    return []
  endif

  let l:template_lines = readfile(a:template_path)
  let l:result_lines = []
  let l:in_frontmatter = 0
  let l:frontmatter_started = 0

  for l:line in l:template_lines
    " Check for YAML frontmatter delimiters (---)
    if l:line =~ '^---\s*$'
      if !l:frontmatter_started
        " Start of frontmatter
        let l:frontmatter_started = 1
        let l:in_frontmatter = 1
        continue
      elseif l:in_frontmatter
        " End of frontmatter
        let l:in_frontmatter = 0
        continue
      endif
    endif

    " Skip lines inside frontmatter
    if l:in_frontmatter
      continue
    endif

    " Check if line contains a command
    if match(l:line, '{{%') != -1
      let l:output = meta_notes#template#ExecuteCommand(l:line, a:context)
      " Split output into lines and add to result
      let l:output_lines = split(l:output, "\n", 1)
      call extend(l:result_lines, l:output_lines)
    else
      " Process variables in the line
      let l:processed = meta_notes#template#ProcessVariables(l:line, a:context)
      call add(l:result_lines, l:processed)
    endif
  endfor

  return l:result_lines
endfunction

" Create template context dictionary for a given date and file path
" Args:
"   date_str: Date string in YYYY-MM-DD format
"   filepath: Path to the file being created
" Returns:
"   Dictionary with template variables
function! meta_notes#template#CreateContext(date_str, filepath) abort
  let l:context = {}

  " Core date variables
  let l:context['date'] = a:date_str
  let l:context['today'] = strftime('%Y-%m-%d')

  " Calculate week_start and week_end
  let l:context['week_start'] = meta_notes#notes#CalculateWeekStart(a:date_str)
  let l:context['week_end'] = meta_notes#notes#CalculateWeekEnd(a:date_str)

  " Calculate quarter (Q1, Q2, Q3, Q4)
  let l:context['quarter'] = meta_notes#notes#CalculateQuarter(a:date_str)

  " Include filepath for path-dependent variables
  let l:context['filepath'] = a:filepath

  return l:context
endfunction

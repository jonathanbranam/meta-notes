## Purpose

Specifies the behavior of the `MetaNotesArchive` command, which moves items from active PARA folders (`project/`, `area/`, `resource/`) into the corresponding `archive/` subtree and keeps wiki-links across the vault consistent.

## Requirements

### Requirement: Archive moves all file types
The archive command SHALL move the entire source directory tree to the archive location, including non-markdown files (images, PDFs, etc.), not only `.md` files.

#### Scenario: Folder of only non-markdown files is physically moved
- **WHEN** the user calls `:MetaNotesArchive project/my-folder` and `project/my-folder` contains only non-markdown files (e.g. JPGs)
- **THEN** the directory and all its contents SHALL appear under `archive/project/my-folder` and the original `project/my-folder` SHALL no longer exist

### Requirement: Folder wiki-links are updated on archive
When a folder is archived, the archive command SHALL update all wiki-links that reference that folder path, replacing the source path with the archive path.

#### Scenario: Link to archived folder with markdown files is updated
- **WHEN** the user archives `project/my-folder` (which contains `.md` files) and another note contains `[[project/my-folder]]`
- **THEN** that link SHALL be rewritten to `[[archive/project/my-folder]]`

#### Scenario: Link to archived folder with no markdown files is updated
- **WHEN** the user archives `project/my-folder` (which contains only non-markdown files) and another note contains `[[project/my-folder]]`
- **THEN** that link SHALL be rewritten to `[[archive/project/my-folder]]`

### Requirement: Subfolder wiki-links are updated on archive
When a folder is archived, the archive command SHALL also update wiki-links that reference any subfolder or descendant path within that folder.

#### Scenario: Link to a subfolder of an archived folder is updated
- **WHEN** the user archives `project/root` and another note contains `[[project/root/subfolder]]`
- **THEN** that link SHALL be rewritten to `[[archive/project/root/subfolder]]`

#### Scenario: Link to a deeply nested path of an archived folder is updated
- **WHEN** the user archives `project/root` and another note contains `[[project/root/a/b/c]]`
- **THEN** that link SHALL be rewritten to `[[archive/project/root/a/b/c]]`

### Requirement: Archive accepts file path without .md extension
When given a file path that does not end in `.md`, the archive command SHALL infer the `.md` extension and archive that file if it exists.

#### Scenario: File archived using path without extension
- **WHEN** the user calls `:MetaNotesArchive project/my-note` and `project/my-note.md` exists
- **THEN** `project/my-note.md` SHALL be moved to `archive/project/my-note.md`

#### Scenario: Path without extension that does not resolve to any file produces an error
- **WHEN** the user calls `:MetaNotesArchive project/nonexistent` and neither `project/nonexistent` nor `project/nonexistent.md` exists
- **THEN** the command SHALL report an error and make no changes

### Requirement: Archive command accepts paths containing spaces
The `:MetaNotesArchive` vim command SHALL accept paths that contain spaces without requiring the user to backslash-escape those spaces.

#### Scenario: File with spaces in name is archived from command line
- **WHEN** the user types `:MetaNotesArchive project/My Note.md` (unescaped space)
- **THEN** `project/My Note.md` SHALL be moved to `archive/project/My Note.md`

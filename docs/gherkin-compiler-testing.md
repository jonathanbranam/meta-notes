# Gherkin Compiler Testing Approach

## Problem

OpenSpec generates capability specs as prose. Tests verify those capabilities in
code. The gap between them requires human or AI judgment to confirm coverage —
there is no mechanical guarantee that a test actually exercises what its
corresponding spec says.

ID-based traceability (tagging tests with spec IDs) reduces this to a lookup,
but the semantic gap remains: a test tagged with an ID might not actually cover
the intent of the spec. Verifying coverage still requires review.

## Approach: Gherkin as Executable Specs

Write capability specs as Gherkin `.feature` files. A Python compiler
(`scripts/compile_features.py`) translates each feature file into runnable
tests — pytest files for Python script capabilities, vader files for vim plugin
behavior. The spec and the test are the same artifact; the gap is eliminated by
construction.

```
OpenSpec change
    │
    └── features/<capability>.feature   (Gherkin, source of truth)
              │
              ▼ scripts/compile_features.py
              │
    ┌─────────┴──────────┐
    ▼                    ▼
test/generated/          test/generated/
test_<capability>.py     <capability>.vader
(Python scenarios)       (vim scenarios)
    │                    │
    ▼                    ▼
pipenv run pytest    ./run_tests.sh
```

If the compiled test passes, the spec is satisfied. No review step needed to
confirm coverage.

## Why Not Other Approaches

**ID/tag traceability** — tells you which test *claims* to cover a spec, not
whether it does. Still requires human comparison to close the semantic gap.

**pynvim RPC bridge** — eliminates the gap and enables behave to drive neovim
directly, but requires neovim (this project targets vim). RPC subprocess
management adds runtime fragility.

**Prose specs + manual tests** — the current state. Highest flexibility, lowest
traceability. Every new spec requires a separate, unverified test authoring step.

## Tradeoff: Step Library

The compiler uses a **step library** — a registry of Gherkin step patterns
mapped to vimscript or Python code templates. Any step in a feature file must
match a library entry; unmatched steps are a compile error.

This is the main cost of the approach. The mitigation is that the step library
for a vim plugin is small and bounded:

```
Setup:
  Given I have a temp directory
  Given the directory "<path>" exists
  Given the file "<path>" exists with content:
  Given I am editing a markdown buffer

Action:
  When my cursor is at line <n>, column <n>
  When I run <Command>
  When I call <function> with "<arg>"
  When I parse the time log in "<filepath>"

Assert:
  Then the current file should be "<path>"
  Then line <n> should be "<text>"
  Then the result should be "<value>"
  Then the result should be empty
  Then an error should have been reported
  Then the buffer should be modified
  Then the file "<path>" should exist
  Then the file "<path>" should not exist

Teardown:
  And I clean up the temp directory
```

Approximately 16 patterns cover all existing vader tests. The library is written
once and amortized across all future specs. Adding a new step is only needed
when a genuinely new interaction pattern emerges — rare for a plugin of this
scope.

The step definition is the one place a gap can reappear: if a step template is
wrong, every scenario using it inherits the error. Step definitions require
one-time review when added, then can be trusted thereafter.

## Scenario Outlines: the Highest-Value Application

Parametrized vim function tests are where Gherkin adds the most expressive
value over raw vader. Current `planning.vader` style:

```vim
Execute (Test CalculateQuarter - Q1):
  AssertEqual 'Q1', meta_notes#notes#CalculateQuarter('2026-01-15')
  AssertEqual 'Q1', meta_notes#notes#CalculateQuarter('2026-02-13')
  AssertEqual 'Q1', meta_notes#notes#CalculateQuarter('2026-03-31')

Execute (Test CalculateQuarter - Q2):
  AssertEqual 'Q2', meta_notes#notes#CalculateQuarter('2026-04-01')
```

Equivalent Gherkin:

```gherkin
Scenario Outline: Maps dates to correct quarters
  When I call CalculateQuarter with "<date>"
  Then the result should be "<quarter>"

  Examples:
    | date       | quarter |
    | 2026-01-15 | Q1      |
    | 2026-02-13 | Q1      |
    | 2026-03-31 | Q1      |
    | 2026-04-01 | Q2      |
    | 2026-06-30 | Q2      |
    | 2026-07-01 | Q3      |
    | 2026-10-01 | Q4      |
```

Each row compiles to a separate vader `Execute` block. The Examples table is the
spec; the compiler makes it runnable.

## Generated File Strategy

Generated test files are **committed to git**, not regenerated at CI time.

Rationale:
- Diffs are reviewable in PRs — you can see exactly what a spec compiles to
- CI can run tests without needing the compiler in the test pipeline
- A CI lint step checks that generated files are in sync with their `.feature`
  sources (hash comparison or re-run + diff)

Per-change file layout:

```
openspec/changes/<name>/
    feature.md           # prose proposal (existing OpenSpec artifact)
    specs/<capability>/
        spec.feature     # Gherkin spec (replaces or augments spec.md)

test/generated/
    test_<capability>.py     # compiled Python tests
    <capability>.vader       # compiled vader tests
```

## Compiler Design

`scripts/compile_features.py` is a standalone Python script (stdlib only,
matching project conventions). It:

1. Discovers `.feature` files under `openspec/` and any top-level `features/`
   directory
2. Parses Gherkin using a lightweight parser (no `behave` runtime dependency —
   just parse the syntax)
3. Resolves each step against the step library; errors on unknown steps
4. Expands Scenario Outlines into one block per Examples row
5. Renders output files from per-target templates (pytest or vader)
6. Writes to `test/generated/` with a header marking files as generated

Running the compiler:

```bash
pipenv run python scripts/compile_features.py          # compile all
pipenv run python scripts/compile_features.py --check  # verify generated files are in sync
```

## Integration with OpenSpec Workflow

When creating a new change, the spec artifact (currently `spec.md`) can be
written as a `.feature` file instead of or alongside prose. The compiler then
closes the loop automatically:

1. `openspec-new-change` or `openspec-propose` generates `spec.feature`
2. Developer implements the capability
3. `compile_features.py` generates the tests
4. `./run_tests.sh` and `pipenv run pytest` verify the implementation
5. `openspec-verify-change` confirms spec, implementation, and compiled tests
   are coherent before archiving

The spec and the passing test share a single source file. No manual comparison
needed.

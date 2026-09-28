[← Project Guide](README.md)

# File Structure & Naming

## Naming convention

Module-specific files and build targets are **module-first** so everything for one module sorts together.
`{module}-tg` / `{module}-sw` (Teaching Guide or Student Workbook) is the base prefix and any further qualifier comes after it.

The modules began as Google Slides decks, exported to PDF (kept outside this repository).
Each activity's student-facing slides — the Student Workbook portion of that activity — become a shared `<worksheet>` file here, which is included in both the `tg` and `sw` PreTeXt books (via `xi:include`).
So a "worksheet" is a collection of student workbook pages.

| Kind | Pattern | Example |
|---|---|---|
| Book root | `{module}-{tg\|sw}.ptx` | `hawaii-tg.ptx` |
| Book-specific part | `{module}-{tg\|sw}-{qualifier}.ptx` | `hawaii-tg-intro.ptx`, `hawaii-sw-intro.ptx` |
| Worksheet (shared) | `{module}-ws-{camelCaseName}.ptx` | `hawaii-ws-spinIt.ptx` |
| Build target | `{module}-{tg\|sw}-{web\|print}` | `hawaii-tg-web` |
| Shared infra | `{plainName}.ptx` | `copyright.ptx` |
| Per-module bibinfo | `{module}-bibinfo.ptx` | `hawaii-bibinfo.ptx` |


Worksheets are shared by both books, so they carry no `tg`/`sw`.
When ingesting, name each worksheet for its activity, **never for its slide or page numbers** (`hawaii-ws-spinIt`, not `hawaii-ws-p7`) — see [Ingesting a module](ingesting-a-module.md) for the full rule.

Shared, module-agnostic infrastructure (copyright, website, colophon, aboutMathCEO, docinfo, mentoringTips, publication files) keeps a plain name.
`bibinfo` is the exception that proves the rule: authorship is per-module, so it is `{module}-bibinfo.ptx` and pulls the shared editing credit, copyright and website in by `xi:include`.

## File Structure

* `source/` — module content; shared infrastructure pulled in via `xi:include`
  - *Module books — one set per module*
    + `{module}-tg.ptx` — Teaching Guide book root (one per module)
    + `{module}-sw.ptx` — Student Workbook book root (one per module)
    + `{module}-tg-intro.ptx` — TG-only intro preface (`xi:include`d by the inline TG frontmatter)
    + `{module}-sw-intro.ptx` — SW-only student intro preface (`xi:include`d by the inline SW frontmatter)
    + `{module}-ws-{camelCaseName}.ptx` — worksheet, shared by both TG and SW (no `tg`/`sw`)
    + `{module}-bibinfo.ptx` — per-module authors (byline + title-page credits); `xi:include`s `editorCredit.ptx` + `copyright.ptx` + `website.ptx`
  - *Shared, module-agnostic*
    + `copyright.ptx` — copyright + full licence sentence
    + `editorCredit.ptx` — the editing credit printed on the copyright page
    + `licenseLink.ptx`, `copyrightYear.txt`, `copyrightHolder.txt` — the licence link, year and holder; single home for each, included by `copyright.ptx` and `colophon.ptx` (see [Colophon](conventions.md#colophon-credits-and-license))
    + `website.ptx` — project website
    + `aboutMathCEO.ptx` — "About UCI MATH CEO" preface
    + `mentoringTips.ptx` — Mentoring Tips preface (TG only)
    + `colophon.ptx` — backmatter colophon: editor credit, copyright line and short licence line, last page. Titled "Credits and License" (see [Authors & credits](conventions.md#authors-and-credits))
    + `docinfo.ptx` — shared macros / LaTeX preamble
  - *TikZ pictures — `source/tikz/`* (see [latex-image & TikZ](conventions.md#latex-image-and-tikz))
    + `tikzPreamble.tex` — shared latex-image preamble (packages, libraries, `workspaceboxstyle`, `treeblue`, Lato); `docinfo.ptx` loads it into its `<latex-image-preamble>`
    + `{module}-{name}.tex` — one `\begin{tikzpicture}…` picture per file.
    + `tikz-tester.tex` — `standalone` previewer: `\input`s the preamble + one picture; run `pdflatex` on it to preview without a full build (`.pdf`/`.log`/`.aux` gitignored)

* `publication/` — see [Publication settings](customizations.md#publication-settings-that-differ-from-stock-defaults)
  - `publication-tg.ptx` — shared Teaching Guide settings (all TG modules)
  - `publication-sw.ptx` — shared Student Workbook settings (solutions hidden, all SW modules)

* `external/` — external assets: images, pdfs, custom css and latex preamble files
  - (images and pdfs for all the modules, referenced by filename only)
  - `css/` — HTML CSS (loaded via `html.css.extra`; the `@import` between these is relative to this folder, so they move together)
    + `custom-common.css` — shared HTML CSS; `@import`'d by `custom-tg.css` / `custom-sw.css`
    + `custom-tg.css` — TG-only HTML CSS (imports common); has the worksheet page-card
    + `custom-sw.css` — SW-only HTML CSS (imports common); placeholder for now (each book type's file is injected via `project.ptx` stringparams)
  - `latex/` — print/PDF only
    + `customPreambleLate.tex` — late LaTeX preamble; `\input` by each `*-print` target (design notes: [LaTeX preamble decisions](reference/latex-preamble-decisions.md))

* `generated-assets/`
  - `latex-image/` — auto-generated SVGs from `<latex-image>` blocks

* `project.ptx` — [build targets](building.md): `{module}-tg-web`, `{module}-tg-print`, `{module}-sw-web`, `{module}-sw-print`

## Structure rules

### Books & files
- **Each module is its own complete PreTeXt `<book>`** (`{module}-tg.ptx` / `{module}-sw.ptx`), with shared infrastructure pulled in via `<xi:include>`.
- **No separate chapter/section files**: everything for a module lives in its book root, **except worksheets**, which get their own `{module}-ws-*.ptx` files so they can be shared between the TG and SW builds.
- To add a module, copy an existing module as a structural template (`diaMuertos` is the most complete) and rename its roots, frontmatter, worksheets, and `project.ptx` targets following the table above — see [Ingesting a new module](ingesting-a-module.md).

### Frontmatter
Written inline in both roots (symmetric): each root writes its own `<frontmatter>` block that `<xi:include>`s the shared pieces plus its own module-intro `<preface>` — there is **no** `{module}-tg-frontmatter.ptx` or `{module}-sw-frontmatter.ptx`.

| # | TG frontmatter | SW frontmatter |
|---|---|---|
| 1 | `{module}-bibinfo.ptx` | `{module}-bibinfo.ptx` |
| 2 | `titlepage` | `titlepage` |
| 3 | front `<colophon>` | front `<colophon>` |
| 4 | `{module}-tg-intro.ptx` | `aboutMathCEO.ptx` |
| 5 | `aboutMathCEO.ptx` | `{module}-sw-intro.ptx` |
| 6 | `mentoringTips.ptx` | — |

`{module}-sw-intro.ptx` is the student-facing intro `<preface>`, carrying the `<xref … text="title"/>` Overview.

Every `<frontmatter>` uses **`xml:id="frontmatter"`** (uniform across all modules, TG and SW) — the SW build requires it so the shared `<index-page ref="frontmatter"/>` in `publication/publication-sw.ptx` resolves; the TG build doesn't reference the id but keeps it uniform.
Follow `hawaii`/`diaMuertos`/`cuatroAmigos`/`palabras` for both patterns.

### Element hierarchy
Within each book file:

| Element | `xml:id` prefix |
|---|---|
| `<chapter>` | `chap-` |
| `<section>` | `sec-` |
| `<subsection>` | `subsec-` |

### Worksheet files
- A single `<worksheet>` element as the XML root — no `<pretext>` wrapper — whose `xml:id` mirrors the filename (e.g. `hawaii-ws-spinIt`). It needs no `xmlns:xi` declaration **unless** it `xi:include`s a TikZ picture, which requires `xmlns:xi="http://www.w3.org/2001/XInclude"` on the `<worksheet>` root (as in `palabras-ws-letsReadTagalog.ptx`; see [latex-image & TikZ](conventions.md#latex-image-and-tikz)).
- Both TG and SW `<xi:include>` the same file.
- Solutions live in the worksheet; visibility is controlled by the publication file.

### Worksheet numbering: keep the parent division *structured*
A `<worksheet>` gets a serial number (e.g. `Worksheet 1.3.1`) only when its parent division (`<section>` in TG, `<chapter>` in SW) is *structured*, which PreTeXt defines as: the division contains a real subdivision (another `<section>`/`<subsection>`), **or** all its children are worksheets/handouts plus `title`/`introduction`/`conclusion` (nothing loose).
So put **all** teacher-facing prose that comes before the worksheet inside `<introduction>`, and anything after it inside `<conclusion>` — never leave a bare `<p>`/`<paragraphs>`/`<image>`/`<assemblage>` as a direct sibling of the worksheet, or the worksheet (and its parent) render **unnumbered**.
Numbering is format-independent (HTML and PDF agree); depth follows nesting (TG `chap.sec.N`, SW `chap.N`).

See also: [Authors & credits](conventions.md#authors-and-credits) for `bibinfo`/title-page identity, and [Ingesting a new module](ingesting-a-module.md) for how a new module's files get created.

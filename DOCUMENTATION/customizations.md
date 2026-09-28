[← Project Guide](README.md)

# What This Repo Adds on Top of Stock PreTeXt

This project is ordinary PreTeXt with a set of deliberate overrides, styles, and conventions added on top.
Everything here is built to work with **PreTeXt CLI 2.49.1**.
A different PreTeXt version may behave differently: some overrides exist to correct specific stock behavior and could become unnecessary, or need adjusting, after an upgrade.

This page lists everything the repo adds or changes on top of stock PreTeXt, one line each, linking to the file that explains it.
It is an index, not the details — follow the links.
For which items depend on stock-PreTeXt internals, and how to re-check them after a CLI upgrade, see [Version baseline & re-check log](reference/version-baseline.md).

## Print / LaTeX: preamble styling (`external/latex/customPreambleLate.tex`)

Print/PDF only. PreTeXt exports the LaTeX for the modules with its own preamble, and we tell PreTeXt to add an input line for `external/latex/customPreambleLate.tex` which overrides many of the default settings. This setup allows the preamble to change with new versions of PreTeXt, while still allowing us to override the defaults in a separate file. That file's own comments explain each block in detail; the design decisions and measurements behind them live in [LaTeX preamble decisions](reference/latex-preamble-decisions.md).

- **Wider SW margins** (`inner=1.20in, outer=0.95in`), a binding allowance for a stapled workbook. → [why the wide measure](reference/latex-preamble-decisions.md)
- **Fonts**: Lato + sans math (`sfmath`).
- **Green write-in `workspace` boxes** with a `grow` functionality.
- **Fill-in rule thickness**: `\ptxfillinrule` (`1pt`), restating stock's hardcoded `0.3pt`.
- **Back-colophon box**: widens the box (narrows stock's `0.15\textwidth` side insets to `0.08`) and turns off hyphenation, which the wider measure no longer needs.
- **Assemblages hidden in print**: `\RenewEnviron{assemblage}[3]{}` drops all TODOs (and any assemblage) from the PDF.
- **Non-indented, space-separated paragraphs** (`parskip`); tighter chapter/preface/exercise/image spacing.
- **Web addresses wrap instead of overflowing**: a line that ends in a link's address can run into the right margin. LaTeX is allowed to stretch the spaces a little more in such a line, so the address moves to the next line instead. → [why](reference/latex-preamble-decisions.md#a-little-last-resort-stretch-is-on)
- **List spacing** (`enumitem` `\setlist`): `\smallskip` between paragraphs inside an item, `\medskip` between items; also seats a list-item title close to its content.
- **Exercise-title spacing**: the gap under an exercise title is pulled tight (`\ptxextitleshrink`) and made uniform across paragraph, list and sidebyside bodies (sidebyside skip tied to `\parskip + 1ex`).
- **Blue accent** (`exblue`): colours exercise titles and numbers, enumerate labels, and list-item titles.
- **Enlarged chapter title**: the title is set at 30pt (`\chaptertitlesize`); the "Part N" label line is left as stock renders it.
- **Worksheet page layout**: worksheets take their own `\newgeometry`, a centred title in the running header, the Math CEO logo pinned to the outer top corner (mirrored per leaf), and a footer with part title and page number; the heading is unnumbered (`\section*`).
- **Even page count**: pads a blank final page so the document ends on an even count for double-sided printing.

## Print / LaTeX: emitted-LaTeX overrides (`xsl/custom-latex.xsl`)

Used only where a fix must change the LaTeX PreTeXt exports because a `customPreambleLate.tex` override would not work. See [`xsl/custom-latex.xsl`](../xsl/custom-latex.xsl) — its comments explain each override.

- **latex-images print at native size**: drops stock's `\resizebox{\linewidth}{!}` wrapper so absolute sizes hold. → [latex-images](conventions.md#latex-image-and-tikz)
- **Side-by-side tables keep their type size**: drops stock's `\noindent\resizebox` around `tabular[ancestor::sidebyside]`. → [tables](conventions.md#tables)
- **Visible task/inline workspace boxes**: `mode="workspace"` emits `\workspacebox` instead of stock's invisible `\rule`. This `\workspacebox` is then styled in [`external/latex/customPreambleLate.tex`](../external/latex/customPreambleLate.tex).
- **Chapters open on any page** (`openany`): the `sidedness` template appends `openany` to `\documentclass`, so a chapter starts on the next page rather than being forced onto a recto (which the publication file's `open-odd` cannot switch off).
- **Taller rows for one table** (`@rowstretch`): wraps any `tabular` that carries `rowstretch="1.5"` in a group that sets `\arraystretch` locally, so only that table stretches (a preamble `\arraystretch` would stretch every table). LaTeX only; HTML ignores the attribute. → [tables](conventions.md#tables)
- **Same font for web addresses in every book**: print shows a link's address in a typewriter font, and every book loads the same narrow one (Inconsolata). Stock PreTeXt loads it only for a book with code-style text; any other book gets a wider font, which can push a long address onto two lines.

## Shared macros & renames (`source/docinfo.ptx`)

These are shared across all modules, and use built-in customization functionality that PreTeXt provides.

- **Element renames**: `chapter → Part`, `section → Activity`, `objectives → Goals` ([why the Goals title rule](conventions.md#elements-and-semantics)), `colophon → Credits and License` (hits both colophons — see [authors & credits](conventions.md#authors-and-credits)).
- **`workspaceboxstyle` TikZ style**: the shared box style in `tikz/tikzPreamble.tex`, used by both figure answer boxes and the print write-in workspace box (`\workspacebox`); never hardcode the fill inline. → [latex-images](conventions.md#latex-image-and-tikz)
- **`latex-image-preamble`**: `docinfo.ptx`'s `<latex-image-preamble>` loads `tikz/tikzPreamble.tex` (`\usepackage[default]{lato}` + `assume math mode=true` so SVG text matches the sans page; also packages, libraries, `workspaceboxstyle`, `treeblue`). → [latex-images](conventions.md#latex-image-and-tikz)
- **External assets folder**: declared here as `<directories external="../external"/>` (not in the publication file, where only the *generated* assets directory is set).

## HTML / CSS (`external/css/custom-{common,tg,sw}.css`)

Custom CSS overrides using built-in functionality that PreTeXt provides to add new CSS rules. `custom-common.css` holds shared rules; `custom-tg.css` / `custom-sw.css` each `@import` it, and every web target loads only its own file via the `html.css.extra` stringparam in `project.ptx`. → [file structure](file-structure.md)

See the files for details. Some notable rules:
- **Worksheet floating page style** Worksheets get a border and shadow to separate them from the main content. This is a TG-only override.
- **`<tabular>` 100% width rule**: allows tables to have a full `width="100%"` instead of shrinking to their content. → [how to use it](conventions.md#tables)
- **Exercise number runs in** (SW only, `tacoma` override): re-inlines an exercise's number with its first line, which the `tacoma` theme otherwise breaks onto a line of its own.
- **Front-colophon menu ordering**: CSS reorders the Credits and License page last in the HTML Front Matter menu. → [authors & credits](conventions.md#authors-and-credits)

## Chapter introduction on the chapter page (`xsl/custom-html-sw.xsl`)

Puts a chapter's introduction on the chapter page, in the web Student Workbook. Recent PreTeXt instead gives the introduction its own page once the chapter has sections, and each Student Workbook chapter introduction is a single opening image, so that page looks almost empty. The stylesheet imports stock PreTeXt HTML and overrides one template to show the introduction on the chapter page (by turning off the `b-division-companion-chunks` setting), the way `custom-latex.xsl` does for print. It is loaded only by the `*-sw-web` targets, through `xsl="custom-html-sw.xsl"` in `project.ptx`; Teaching Guide builds are unchanged. It copies part of PreTeXt's stylesheet, so re-check after a PreTeXt upgrade. → [version baseline](reference/version-baseline.md)

## Publication settings that differ from stock defaults

Two shared publication files — `publication/publication-tg.ptx` for every Teaching Guide, `publication/publication-sw.ptx` for every Student Workbook. Their own comments explain each setting; the notable non-defaults:

*Both files:*
- **HTML `<response/>` boxes on** (`short-answer-responses="always"`).
- **Fill-in style** `textstyle="underline" mathstyle="shade"` (the print *thickness* is restated in the preamble — see [design decisions](reference/latex-preamble-decisions.md)).
- **Focused TOC off** (`<tableofcontents focused="no"/>` — the element is `<tableofcontents>`, not `<toc>`, which is silently ignored).
- Generated-assets directory is set here; external assets are declared in `docinfo.ptx`.

*Student Workbook only:*
- **Solutions hidden** (`exercise-project`/`exercise-worksheet` with `answer="no" solution="no"`).
- **Print enabled** (`<latex print="yes" font-size="11">`) — the SW is the only book type with an enabled `*-print` target.
- **Web theme** `tacoma` (building it needs Node.js — see the root `README.md` Requirements); **landing page** `<index-page ref="frontmatter"/>`.
- Chunked and numbered one level deeper than the TG (`level="3"` vs `level="2"`).

## Project conventions (repo practice, not PreTeXt mechanics)

- **Module-first file & target naming** (`{module}-{tg,sw}-…`). → [file structure](file-structure.md)
- **Faithful ingestion**: prose is verbatim from the source PDF; authored text is wrapped in `[[[ … ]]]`. → [ingesting a module](ingesting-a-module.md)
- **Worksheets shared by TG and SW** as single-`<worksheet>` files, kept in a *structured* parent so they stay numbered. → [file structure](file-structure.md)
- **Visible TODOs**: The `<assemblage>` tag has been used for TODOs. They all use `<assemblage component="TODO">` and are styled with the custom CSS. They show in local web builds, but `publish.py` leaves them out of the published site (→ [publishing](building.md#publishing-scriptspublishpy)), and the PDF drops them too. See [TODOs](conventions.md#todos-and-assemblages)
- **TikZ pictures as separate `.tex` files** in `source/tikz/`, included as text in `<latex-image>` (no XML escaping) and previewable with `tikz-tester.tex`. → [latex-images](conventions.md#latex-image-and-tikz)
- **Build in two steps for PDF**: `*-print` emits `.tex`; run pdflatex 3 times (or use `latexmk -g` if you have Perl installed on your system). → [building](building.md)

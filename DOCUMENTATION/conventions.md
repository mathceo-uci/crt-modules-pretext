[← Project Guide](README.md)

# PreTeXt Authoring Conventions

The PreTeXt conventions for this project. Two ideas run through them: **choose elements by meaning, not by how they look**, and **watch for silent failures** — several of these things build without any error while dropping content or rendering wrong. The [silent-failure quick-index](#silent-failure-quick-index) lists those by symptom.

> **Verified against PreTeXt 2.49.1** (2026-08-28): the version-specific claims here — the closed 22-name `<icon>` list, the per-cell `test="p"` table width, the side-by-side and latex-image `\resizebox` wrappers stock still emits, and the single `string-id='colophon'` behind the shared colophon name — were confirmed against stock core. Re-check after upgrading; see [Version baseline](reference/version-baseline.md).

**Sections:** [Elements](#elements-and-semantics) · [Images & media](#images-and-media) · [TODOs](#todos-and-assemblages) · [Tables](#tables) · [latex-image & TikZ](#latex-image-and-tikz) · [`<xref>`](#xref-constraints) · [Links & URLs](#links-and-urls) · [Authors & credits](#authors-and-credits) · [Response & workspace](#response-and-workspace)

## Elements and semantics

### Choose elements by meaning, not appearance
Source slides bold or color text for many different reasons — never map "looks bold/emphasized" to a tag. Pick by what the text *means*:

- `<term>` — a word/phrase *being defined or introduced* (e.g. SET, FAVORITE MUSIC as a named aspect). It is not a bold switch — never wrap a step/exercise number (like `1)`) or a bolded option/label in it.
- `<em>` — inline emphasis. (PreTeXt has no `<strong>`; `<em>` is the only emphasis element.)
- `<alert>` — **only** genuine inline alerting (a key warning/equation). Never for headings or labels.
- Headings and labels are structure, not emphasis — use a `<title>`. This covers prompt labels ("Key principles:", "Example:", "Discuss:") via `<paragraphs><title>...</title>`, and a list item's lead-in label (e.g. the `sec-introduction` discussion aspects "Longest word", "Where is Spanish spoken?") via `<li><title>...</title><p>...</p></li>` — never `<li><p><term>...:</term> ...</p></li>`.
- When unsure, prefer `<term>`/`<em>` over `<alert>`.

### Don't hard-code numbers or list markers
`<exercise>`, `<task>`, sections, and figures are **auto-numbered** — never carry the source's `1)`, `Q2`, `3)` into their statement text or `<title>` (it double-numbers). A source's `a) b) c)` or `i) ii)` sub-parts are list *structure*: transcribe them as `<ol>` items (or `<task>`s), **not** as literal `a)`/`i)` text inside a `<p>`. And do **not** add `marker="a)"`/`marker="i)"` just to mirror the source's punctuation — leave `<ol>` unmarked so PreTeXt picks the correct marker for the nesting level. Reserve the `marker` attribute for a deliberate style choice (e.g. `<ol marker="a">` in `palabras-ws-espanglishemos.ptx`). Source prose that *cross-references* a numbered part or question (e.g. <q>In 2)</q>, <q>in part 1</q>, <q>see the next page</q>) is hard-coded the same way — transcribe it verbatim, but add an `<assemblage component="TODO">` above it flagging that the reference should become an `<xref>` (which renders the live number/title and stays in sync). Don't try to resolve every such xref during the first pass; flag them. (See [xref constraints](#xref-constraints) and [TODOs](#todos-and-assemblages).)

### Breakdown lists
A Breakdown is a **description list** (`<dl>`, wrapped in a `<p>`), one `<li>` per activity. The `<title>` (the term) is the activity's live number — `<xref ref="sec-…" text="type-global"/>`, which renders "Activity N.N". The definition is the section title in its own `<p>` (`<xref ref="sec-…" text="title"/>`), then the summary in one or more further `<p>`s. When the summary is genuinely multi-point, make it a `<ul>` — and keep that `<ul>` inside the *same* `<p>` as the title-xref (a `<ul>` split off as its own paragraph is the silent-drop trap; see [TODOs](#todos-and-assemblages)). Worked example: any chapter `<introduction>` in `diaMuertos-tg.ptx`.

Do **not** use `<ol marker="i">`: paired with a `type-global-title` xref it double-numbers (roman i, ii *and* "Activity N.N" — see [Don't hard-code numbers](#dont-hard-code-numbers-or-list-markers)). Splitting the number (term) from the title and summary (definition) also keeps all three live via `<xref>`. Two edge cases: for a breakdown item with no backing section, use a literal `<title>` (cuatroAmigos ch. 2's "5 Friends"); for a section not yet created, keep a `<xref provisional="…"/>` in the title.

### Chapter `<introduction>` order
Initial text first, then goals, materials, and the breakdown `<paragraphs>` — in that sequence, before any other content (e.g. "On Cultural Appropriation").

### Checklist items
Go inside `<paragraphs><title>Checklist</title>` within `<introduction>`.

### `<objectives>` title must not say "Goals"
`docinfo.ptx` renames the element to `Goals`, and the heading is the name, a colon, then the title. So the title holds only the extra word: `<title>Math</title>` heads as "Goals: Math". Drop the title where there is no extra word — that removes the colon too, leaving "Goals". Never empty the rename to hide the name: PreTeXt reads an empty name as a failed lookup and prints "[objectives]".

### Prompt labels
"Let's imagine:", "Discuss:" and the like use `<paragraphs><title>Label</title>` — not `<alert>`.

### Teaching Guide intro
A Teaching Guide intro in a subsubsection uses `<introduction>` (no title) — not `<paragraphs><title>Teaching Guide</title>`.

### `<backmatter>` requires `<appendix>` wrappers
`<p>`, `<image>`, `<paragraphs>` cannot go directly inside `<backmatter>` — block content needs a wrapper. Always wrap in `<appendix xml:id="..."><title>...</title>...</appendix>`.

## Images and media

### Images
Images go in `external/` (project root), referenced by filename only: `<image source="foo.png"/>`. Every `<image>` must have a `<shortdescription>` child for alt text — never a self-closing `<image source="..."/>` without one, unless it is marked `decorative="yes"` (see below).

#### Unnumbered images
Bare `<image>` without a `<figure>` wrapper. `<figure>` adds "Figure x.y.z" numbering.

#### `<shortdescription>` vs `<description>`
`<shortdescription>` is plain text and becomes the alt text — keep it brief. `<description>` (containing `<p>`/`<tabular>`) is for a more elaborate, optional long description (e.g. for screen-reader users who want more detail) — only add it when there's substantive extra content beyond the alt text.

#### `decorative="yes"` for purely ornamental images
`<image decorative="yes" source="…"/>` marks an image as carrying **no information** — a divider, flourish, or repeated ornament — so HTML emits empty alt text (`alt=""`), or `aria-hidden="true"` for an SVG/interactive image, and a screen reader skips it entirely. This is an accessibility decision, not a shortcut: mark an image decorative **only** when it truly conveys nothing a reader would miss, never to skip alt text for a meaningful image (which silently hides real content from assistive-technology users). Rule of thumb: if removing the image would lose any information, it is not decorative — give it a `<shortdescription>` instead.

#### Restricted images: `\restrictedimage` placeholders
An image whose license does not allow sharing never goes in `external/`. The file is kept outside this repository, in a local folder of your choice, and the `.ptx` gets a gray box of the same printed size in its place — the `\restrictedimage` command, defined in `source/tikz/tikzPreamble.tex`. Keep the real image's `<shortdescription>` or `decorative="yes"` on the `<image>`:

```xml
<image decorative="yes">
  <latex-image>\restrictedimage{1.6cm}{1.9cm}{Image of cat face. See for example restricted diaMuertos-Gato.png}</latex-image>
</image>
```

The arguments are the printed width, the printed height, and a description that names the restricted file. The description is LaTeX text, so write `_` as `\_`. Size matters only for print, where the box prints at exactly that size (see [A `<latex-image>` prints at native size](#a-latex-image-prints-at-native-size)): the width is the image's `@width`, or its side-by-side column width, times the text width (16.1 cm on worksheet pages), and the height is that width times the image's pixel height over its pixel width.

A module is ready to publish when `grep -l restrictedimage source/{module}-*.ptx` finds nothing. `publish.py` refuses to publish a target until then (see [Publishing](building.md#publishing-scriptspublishpy)). To clear a placeholder, put an openly licensed image in `external/` and go back to `<image source="…"/>`.

#### Related: 
* TikZ / `<latex-image>` images (native-size printing, fonts, `workspaceboxstyle`): [latex-image and TikZ](#latex-image-and-tikz)
* image attribution tiers (CC / public domain / AI-generated): [Authors and credits](#authors-and-credits).

### Videos
`<video youtube="ID" width="80%"/>`. For an unknown ID, flag it with an `<assemblage component="TODO">` beside the video — never a bare `<!-- TODO -->` comment, which renders invisibly (see [TODOs](#todos-and-assemblages)).

### `<icon>` has a closed name list — an unknown name fails silently
Core exposes exactly 22: `arrow-left/up/right/down`, `file-save`, `gear`, `menu`, `wrench`, `power`, `media-play/pause/stop/fast-forward/rewind/skip-to-end/skip-to-start`, and `cc`, `cc-by`, `cc-sa`, `cc-nc`, `cc-pd`, `cc-zero`. Font Awesome 5 is the engine underneath (CDN CSS in HTML, the `fontawesome5` package in print), but only those names are mapped. The schema declares `@name` as free text, so `<icon name="youtube"/>` validates, then renders an empty `<span>` in HTML and an undefined `\fa{}` in print. For anything off the list, use an `<image>`.

## TODOs and assemblages

TODO comments use `<assemblage component="TODO">` so they render visibly in the output (controlled by the publication file). Never use bare `<!-- TODO: ... -->` XML comments — they are invisible in the rendered output. Structure:

```xml
<assemblage component="TODO">
  <title>short label</title>
  <p>Description of the task.</p>
</assemblage>
```

Title conventions: `PENDING: [action]` for pending tasks; `[question]?` for open decisions. Place the assemblage as a sibling block element — never inside `<caption>`, `<title>`, or other inline-only contexts (move it before/after the containing element instead).

### Never a direct child of `<ul>`/`<ol>`
A list accepts only `<li>`, so an assemblage placed directly in `<ul>`/`<ol>` is **silently dropped**: the build still reports success and the TODO simply never appears in the output. Put it *inside* the relevant `<li>` (after that item's `<p>`), which is where it belongs anyway since it annotates one item:

```xml
<li>
  <p>Dana: <url href="…">…</url></p>
  <assemblage component="TODO">
    <title>PENDING: license</title>
    <p>Add the contributor name and license.</p>
  </assemblage>
</li>
```

To annotate the whole list, put the assemblage before or after the `<ul>`, not within it. This class of error is invisible in this project because schema validation is skipped (`jing` is not installed — the build logs `Schema validation could not be completed`), so **verify a new TODO actually rendered**: `grep -c "<title text>" output/<target>-web/*.html`.

### A list inside an assemblage must be nested in the `<p>`
A `<ul>` written as a sibling of the `<p>` (rather than nested inside it) is the same silent drop. To give a TODO a checklist so items can be deleted one at a time, the `<ul>` goes *inside* the paragraph that introduces it. A sibling `<ul>` is discarded while the `<title>` and `<p>` around it still render, which makes the TODO look fine until you count the items:

```xml
<assemblage component="TODO">
  <title>PENDING: image attributions</title>
  <p>Still needed:
  <ul>
    <li><p>Spinner: source, author, license.</p></li>
  </ul>
  </p>
</assemblage>
```

### Assemblages are discarded entirely in print
`customPreambleLate.tex` does `\RenewEnviron{assemblage}[3]{}`, so the body of every assemblage is dropped from the PDF. That is deliberate (TODOs are for us, not for students), but it means an assemblage must never hold content the *reader* needs. Source credits, attributions and licences in particular have to live in a real element; putting one in an assemblage ships a PDF with no credit at all, silently. Draft wording may sit in a TODO, but the moment it becomes the actual credit it has to move out. (Where a real credit goes: [Authors and credits](#authors-and-credits) — worksheet `<fn>` credits, book-level bylines, and image attributions.)

## Tables

`<tabular>` widths and centring behave differently per output format, and several table failures are silent.

### `<tabular>` width (set differently per format)
A table's width is set in **completely different ways in HTML and print**, and setting it the wrong way fails silently. Decide the width you want in each format and set it independently.

**HTML — to make the table fill the text column, put `width="100%"` on the `<tabular>`.** That attribute alone does nothing: stock PreTeXt sizes only the `<div>` that wraps the table, never the inner `<table>`, which keeps shrinking to its content. What actually stretches the table is the repo's [`custom-common.css` width rule](customizations.md#html--css-externalcsscustom-commontgswcss), which forwards that 100% to the inner table — so the attribute and the CSS rule only work as a *pair*. And the pair only works **outside** a `<sidebyside>`: inside a panel the table is wrapped in `.sbspanel` instead of `.tabular-box`, the CSS rule no longer matches, and `@width` is ignored entirely. (`col/@width` is no help in HTML — there it only caps each `<p>` cell's `max-width`, never the table's overall width.)

**Print — the width comes from `col/@width`; `tabular/@width` is ignored completely.** The catch is that a column's width only takes hold on cells that contain a `<p>`, and the decision is made per *cell*, not per column (core keys on `test="p"`). A `<p>` cell becomes a fixed `m{width}` column that wraps to that width; a plain cell becomes an auto `l`/`c`/`r` column that ignores the width and stretches to its own content. So a single plain cell defeats the width for its whole column. **To hold a column to its `col/@width` in print, wrap every body cell in that column in a `<p>`** — setting it on one row is not enough.

Two more silent traps:
- A `<col>` with no `@width` counts as 20%.
- Never wrap a `header="yes"` cell in a `<p>`: core's paragraph branch silently drops the header bold. Leave headers plain — the column still takes its `<p>` width, as long as the header text is narrower than that width.

Worked example: the two side-by-side tables in `palabras-ws-letsReadTagalog.ptx`.

### Centring a `<tabular>`
To centre without the numbering a `<table>` brings, do not give it a `@width` or a `@margins`. A tabular with neither centres on its own. Print puts it inside a `\begin{center}`, and HTML centres it with `.tabular-box.natural-width`, which also lets it scroll sideways if it grows too wide for the page. Add either attribute and print places the table by those numbers instead, so it no longer centres. A `<sidebyside margins="auto">` wrapper is only needed if the table has to sit beside something else. See `hawaii-ws-ourData.ptx`.

### Empty rows
An all-empty row collapses to near-zero height in HTML, because an empty `<cell>` gives its `<td>` no line box. Put an `<nbsp/>` in every cell so the row keeps full height:

```
<row><cell><nbsp/></cell><cell><nbsp/></cell>...</row>
```

Print is unaffected (each LaTeX row carries a font strut). A row with any non-empty cell already has height and needs nothing.

Special case — the last row: also give it a `bottom` rule (`minor`, `medium`, or `major`), which it otherwise lacks. Without one the row has height from the `<nbsp/>` but no visible lower border, so it still reads as empty space. Match the weight the table already uses to frame itself — e.g. the header row's rule. Worked example: the two trailing write-in rows of the `ex-translate-2` table in `palabras-ws-espanglishemos.ptx`.

Related: the side-by-side tabular print override is in [`xsl/custom-latex.xsl`](../xsl/custom-latex.xsl).

### Taller rows (print only)
To give a table taller rows in print, such as a worksheet table students write into, put `rowstretch` on the `<tabular>`:

```
<tabular halign="center" rowstretch="1.5">
```

The value multiplies the normal row height. Only that table changes: the repo's [`custom-latex.xsl` override](customizations.md#print--latex-emitted-latex-overrides-xslcustom-latexxsl) wraps it in a group that sets `\arraystretch` locally. Do not set `\arraystretch` in `customPreambleLate.tex` instead, because that stretches every table in the book.

`rowstretch` is not a PreTeXt attribute, so three things follow silently:
- HTML ignores it, and rows there keep their usual height. Empty write-in rows still need `<nbsp/>` in every cell (see [Empty rows](#empty-rows)).
- Schema validation flags it as unknown. The build does not care.
- Inside a `<sidebyside>` the table goes through the side-by-side override instead, and `rowstretch` may have no effect there. Check the PDF.

Worked example: the word-length table in `palabras-ws-espanglishemos.ptx`.

## latex-image and TikZ

### TikZ pictures live in `source/tikz/` as separate `.tex` files
Each picture is its own `\begin{tikzpicture}…\end{tikzpicture}` file under `source/tikz/`, included in the `<latex-image>` as text:

```xml
<image width="70%">
  <latex-image>
    <xi:include parse="text" href="tikz/diaMuertos-tree.tex"/>
  </latex-image>
  <shortdescription>…</shortdescription>
</image>
```

The one exception is a `\restrictedimage` placeholder (see [Restricted images](#restricted-images-restrictedimage-placeholders)): a one-line command written directly inside the `<latex-image>`, with no file of its own.

Note the special `parse="text"` which inserts the file's text unchanged, so the picture code needs **no XML escaping**: One can write `<`, `>`, `&` directly in the tikz source (no `&lt;`, for example). 

The including file's root must declare `xmlns:xi="http://www.w3.org/2001/XInclude"`: the book roots already do, but a worksheet root has to add it (see [worksheet files](file-structure.md#worksheet-files)). 

Run `pretext generate latex-image` (or `-g`) before building if SVGs are missing. 

### Shared TikZ picture styles (`tikzPreamble.tex`)
The shared preamble is `source/tikz/tikzPreamble.tex`. It gets loaded by `docinfo.ptx`'s `<latex-image-preamble>`, so all picture setup is defined in one file.
It loads packages and libraries, defines global colors (like `treeblue`), and sets Lato as the font (see "`<latex-image>` text renders in Lato" below).

### Preview a picture with `tikz-tester.tex`
`source/tikz/tikz-tester.tex` is a `standalone` document that `\input`s the shared preamble and one picture file. Point its `\input` at the picture you are editing and run `pdflatex tikz-tester.tex` inside `source/tikz/` to render just that picture, without building the whole target. It uses the same `tikzPreamble.tex` as the build, so the preview matches the book's image. Its `.pdf`/`.log`/`.aux` are gitignored.

### A `<latex-image>` prints at native size
`@width`/`@margins` on the `<image>` affect HTML only. Stock PreTeXt wraps every latex-image in `\resizebox{\linewidth}{!}{…}`, stretching the whole picture (fonts, line widths, mark sizes and all) to fill the column whatever size it was drawn — so absolute lengths never come out at the size you set. `custom-latex.xsl` overrides that (see [its comments](../xsl/custom-latex.xsl)): in **print** the picture is centred at native size and nothing is scaled, so sizing lives entirely in the image code — a pgfplots `width=`/`height=`, or the cm coordinates of a hand-drawn TikZ box — and `@width`/`@margins` no longer touch it. A picture wider than the text block overflows the margin instead of shrinking (watch the compile log for `Overfull \hbox`), which is deliberate: native size, visible when it is too big. **In HTML** the generated SVG is still placed at `@width` (default 100% of its container), so set `@width` there if the web size needs tuning — it will not affect print.

### `<latex-image>` text renders in Lato
Set once in the shared `tikz/tikzPreamble.tex` (`\usepackage[default]{lato}`), which `docinfo.ptx` loads via its `<latex-image-preamble>`, so the HTML SVGs match the sans page instead of defaulting to serif Computer Modern. It **must** set the default *family* (`[default]`), not a `font=\sffamily` on the picture/axis: a pgfplots axis's own `font=\large`/`\small` on labels and ticks replaces the family, overriding any picture-level font (this is why `\sffamily` alone left the labels serif). pgfplots tick numbers are typeset in math mode, so `\pgfplotsset{/pgf/number format/assume math mode=true}` (also in the preamble) drops the `$…$` wrap and prints the digits in Lato too. The preamble is shared with print, where `customPreambleLate.tex` reloads `[default]{lato}` identically (a no-op) — keep the two fonts in sync: the *same* package with different options clashes, a *different* package renders HTML and print in mismatched fonts.

### TikZ response/write-in boxes
Use the shared `workspaceboxstyle` defined in `tikz/tikzPreamble.tex` (which `docinfo.ptx` loads via its `<latex-image-preamble>`): `\draw[workspaceboxstyle] (0,0) rectangle (6,0.7);`. Never hardcode the fill inline — always use the named style so the box stays consistent across all modules. The print write-in workspace box (`\workspacebox`) uses the same style, so editing the `\tikzset` in `tikz/tikzPreamble.tex` changes both.

## xref constraints

- **`<xref>` only works for numbered elements**: elements inside `<figure>`, or structural divisions (`<chapter>`, `<section>`, `<subsection>`, `<activity>`, etc.) with `xml:id`. Adding `xml:id` to a bare `<image>` causes "lacks a serial number" errors at build time.
- **A file shared by more than one book cannot `<xref>` a module-specific id.** Any `<xref>` in a shared file (`aboutMathCEO.ptx`, `copyright.ptx`, a `{module}-ws-*.ptx` used by both the TG and SW) must point to an id that exists in *every* book that includes it, or the build fails with "uses references … that do not point to any target". Section titles and other module-specific references must be plain text in shared files. This bit `palabras-sw-web` once (fixed Aug 2026 — two `<xref>`s to a TG-only subsection in a shared worksheet made plain text).
- **Prefer pulling titles via `<xref ref="..." text="title"/>` over retyping them.** Whenever text refers to a titled element defined elsewhere (a section, exercise, `<li>`, etc., possibly in an `xi:include`d file), use `<title><xref ref="..." text="title"/></title>` instead of duplicating the title string. Requires an `xml:id` on the target. Keeps references in sync if the source title changes.
- **Render a bare section number** (e.g. "1.1") with `<xref ref="sec-x" text="global"/>`. A bare `<xref ref="sec-x"/>` uses the project's `type-global` default, which renders "Section 1.1" (with the type word).

Related: hard-coded cross-references in source prose should be flagged for conversion to `<xref>` — see [Elements and semantics](#elements-and-semantics) and [TODOs](#todos-and-assemblages).

## Links and URLs

### Provisional links to PDFs/slides
For an address not known yet, use `<xref provisional="&lt;url&gt; link to slides"/>` — the `&lt;url&gt;` prefix signals it resolves to a URL, not an internal cross-reference. Replace with a real `<url>` once known.

### Student Workbook link
Each TG Materials list opens with the module's Student Workbook, both formats, on the published site (only `{module}` changes):

`Student Workbook (<url href="https://mathceo-uci.github.io/{module}-sw.pdf">pdf</url> / <url href="https://mathceo-uci.github.io/{module}-workbook">web</url>)`

Web folder is the `{module}-workbook` that `publish.py` writes; PDF is `{module}-sw.pdf` at the site root.

### Material / BLM links
Use `(<url href="external/{module}-blm-{name}.pdf">pdf</url>)` in the Materials list (diaMuertos style; `external/` is the folder itself), and repeat the link at the manipulative's point of use in the activity body when it has one.

### `<url>`: friendly link text, simplified `@visual`
Friendly link text, simplified `@visual`, full address in `@href` ([PreTeXt guide](https://pretextbook.org/doc/guide/html/topic-url.html)). Always give content (never a bare `<url/>`), and never paste the full address as that content. Print appends `@visual` in parentheses, set in monospace, breaking only at `-`, `.` and `/` — so a long one either overflows or fragments mid-address across two lines. Budget for it: the parenthetical roughly doubles the width the link needs in print, and it is invisible in HTML, so an HTML-eyeballed column width will be about half of what print wants. If a line overflows, shortening the *link text* often fixes it by giving TeX a break point before the monospace run. Set a short `@visual` yourself: `<url href="https://boudewijnhuijgens.getarchive.net/amp/media/los-angeles-kids-boy-people-67771c" visual="boudewijnhuijgens.getarchive.net">GetArchive</url>` prints as `GetArchive (boudewijnhuijgens.getarchive.net)`. `visual=""` suppresses the parenthetical entirely, but the guide calls that *very rare* — it denies print readers any hint of the address. Putting URLs in print footnotes instead was tried and rejected: it needs a copy of core's ~105-line `url` template, which would drift from stock on each PreTeXt upgrade.



## Authors and credits

### A source credit on a worksheet goes in an `<fn>`
Attach it to body prose. `<attribution>` looks like the right element and is not — the schema permits it only inside `<blockquote>` and `<preface>`, so it cannot be a child of `<worksheet>`, `<page>`, or `<image>`. (`hawaii-ws-pele.ptx` uses it legally only because it sits inside a `<blockquote>`.) Use `<fn>` instead, attached to the first paragraph that the credit belongs to — it prints at the foot of the worksheet page and renders as a disclosure in HTML. `<fn>` is legal in `<p>` but **not** in a `<title>`, `<caption>`, or `<shortdescription>`, whose content model excludes it. See `diaMuertos-ws-tris.ptx` and `diaMuertos-ws-fiestaDeMusicos.ptx`. For a whole-book credit instead, `<credit><role/><entity/></credit>` in `bibinfo` is PreTeXt's own slot (see [Authors](#authors)); for images, the per-module `appendix-image-attributions` is where entries go.


### Image attributions (`appendix-image-attributions`)
**List only images that need attribution: those from an outside source or generated with an AI tool.** The project's own images (diagrams, charts, illustrations the team drew, `<latex-image>`/TikZ included) are *not* listed one by one — a single note at the top of the appendix covers them all. This keeps the list to the entries that carry required information and needs no edit when a new in-house image is added. The trade-off is that the note is a **catch-all claim of ownership over everything unlisted**, so a third-party image left out of the list is silently mis-claimed as ours — every externally-sourced or AI image *must* appear. (Do not name the licence in the note: `copyright.ptx` is its single home, and an unnamed "same as the book" stays correct if it ever changes.)

The appendix opens with this note verbatim (it is module-agnostic — reuse it as-is):

```xml
<p>The images listed below originate from an external source or an AI tool. All other images in this module were created by UCI MATH CEO and are released under the same license as the book, except the logos, which belong to their respective owners and are not covered by this license.</p>
```

**List structure.** One `<li>` per listed image, in the order the images appear in the book, each opening with an `<xref text="custom">description</xref>` to the closest numbered division that holds it (a `<figure>`, `<exercise>`, `<section>`, worksheet…). On the web that description is the link; a print target appends the page number right after it ("Paper roll, p. 12: …"). List only the images in *this* book — a worksheet shared by the TG and SW is credited in both appendices, so the same images recur in each.

The one exception is the cover of a Student Workbook. It comes first and has no link, because `publish.py` adds it only to the PDF (see [Cover pages](building.md#cover-pages)) and nothing in the source can be linked to: `<li><p>Cover (PDF edition): …</p></li>`. It is listed on the web too, since the web and PDF workbooks share the appendix.

A listed entry's fields are set by the image's licence, not a house style. The element set follows the legal status; matching entries then look alike on their own. Three tiers get an entry (Hawaii's appendix is the worked example); the fourth is the unlisted case the top note covers:

- **CC BY / SA / NC**: full TASL: title (linked to source), author, and the licence *name linked to its deed*. Dropping any is a licence violation.
- **Public domain / CC0**: title linked to source, then `Public domain`. Author only if known (omit it for an unattributed CC0 vector — the licence waives it); no licence link needed. E.g. `<url href="…source…" visual="commons.wikimedia.org">Waikiki Beach, Diamond Head, O'ahu</url> (1928) by D. Howard Hitchcock. Public domain.`
- **AI-generated (no copyright holder)**: a *disclosure*, not a credit: name the tool and year, no source, no licence. E.g. `Image generated with Google Gemini, 2026.` Add `and edited by …` when a human edited it (that edit is the only copyrightable part).
- **Original project work (authored, non-AI)** — *not listed individually*: a diagram, chart, or illustration the team drew itself, from no external source (`<latex-image>`/TikZ included). These are covered wholesale by the top note, not given per-image entries. The exception is a piece whose *author should be named* (a specific contributor) — that one gets a listed entry crediting the person.

Do **not** wrap a linked title in `<q>`: print appends the `@visual` parenthetical to the link, so the `(visual)` lands *inside* the closing quote. Leave the linked title unquoted.

(For a per-worksheet source credit, use an `<fn>` — see [above](#a-source-credit-on-a-worksheet-goes-in-an-fn).)

### Authors
The title page's identity comes from two places. The `<title>` and `<subtitle>` live in each book **root** (`{module}-{tg,sw}.ptx`): the title is the module name (e.g. `Día de los Muertos`), the subtitle is the book type (`Teaching Guide` / `Student Workbook`). This is uniform across all modules — a new module follows the same split; never put the book type in the title or the module name in the subtitle.

The **byline and credit** live in `{module}-bibinfo.ptx`, shared by that module's TG and SW so a module is credited identically in both books. The byline is two `<author>` lines — the curriculum, then the institution; the people go in a `<credit>` group below it, followed by a second `<credit>` titled "Editor and PreTeXt Production". All of it renders on the title page, in HTML and print alike.

```xml
<author>
  <personname>UCI MATH CEO Curriculum Module</personname>
</author>
<author>
  <personname>University of California, Irvine</personname>
</author>
<credit>
  <title>Authors</title>
  <author>
    <personname>Jane Doe</personname>
    <affiliation>
      <institution>University of California, Irvine</institution>
    </affiliation>
  </author>
</credit>
```

- **`<credit>` is two different elements, told apart by their children.** `{title, author+}` renders on the **title page**; `{role, entity}` renders on the **copyright page** (print) and the Credits and License page (HTML), as `**role**: entity`. The stylesheets select with predicates — `credit[title]` vs `credit[role]` — so mixing the children gives an element that matches neither and renders **nowhere**, with no error.
- **Inside a `<credit>`, an author's institution must be nested in `<affiliation>`.** The title-page template prints `affiliation/institution` only; a bare `<institution>` is silently dropped there — the name renders and the institution just never appears. The main `<author>` byline is the asymmetric case: it does honour a bare `<institution>`.
- **The title-page credits are the per-module part of `bibinfo`.** Both `<credit>` groups (Authors, and Editor and PreTeXt Production) are written out in each `{module}-bibinfo.ptx`; the editor group is identical in all four, so change it in all four. The copyright-page editing credit, copyright, licence and website are shared, so `{module}-bibinfo.ptx` `xi:include`s `editorCredit.ptx`, `copyright.ptx` and `website.ptx` rather than restating them. Do not copy those into a module's bibinfo.
- **`<author>` must come first**: the schema is `(Author+, Editor*)?` followed by an interleaved group holding `credit`, `date`, `website`, `copyright`. Order within that group is free; authors are not.
- **`<contributors>` inside a `<preface>`** is the third option, giving a dedicated Contributors page with department/institution/email per person. Unused here; worth it only for a long list.

### Colophon: "Credits and License"
There are two colophons, and they deliberately share a name. This follows the PreTeXt Guide, which describes the front colophon as the *"automatically-generated copyright page"* ([4.26 Front Matter](https://pretextbook.org/doc/guide/html/topic-front-matter.html)) and the back one as *"a traditional note on how a book was made"* — "what most authors consider the actual colophon" — for recording typefaces, software used in production, and edition history ([4.27 Back Matter](https://pretextbook.org/doc/guide/html/topic-back-matter.html)). The official [sample book's back colophon](https://pretextbook.org/examples/sample-book/annotated/back-colophon.html) is a single line naming the authoring tool, which is what ours is. The arrangement is upstream's design, not a workaround.

| | Source | Print | HTML |
|---|---|---|---|
| Editing credit, website, copyright, full licence | `editorCredit.ptx`, `website.ptx`, `copyright.ptx` via `{module}-bibinfo.ptx` | copyright page (verso of the title page) | Credits and License, in the front matter |
| Editing credit, copyright line, short licence line | `colophon.ptx` | final page | Credits and License, last page of the backmatter |

The frontmatter one is empty — `<colophon><colophon-items/></colophon>` — and `<colophon-items/>`, the sibling of `<titlepage-items/>`, makes PreTeXt assemble it from `bibinfo`: `credit`, `edition`, `website`, `copyright`, `keywords`, `support`. Nothing on that page is written by hand. The backmatter one is ordinary prose.

The editing credit on the copyright page is a `<credit><role/><entity/></credit>` (in `editorCredit.ptx`), which PreTeXt prints as "**role**: entity". It comes first on that page, above the website and licence, because that order is fixed by the stylesheets.

- **The shared name cannot be avoided, and is accepted.** Stock PreTeXt has the same collision: `en-US.xml` defines one `string-id='colophon'`, so an unrenamed two-colophon book prints "Colophon" twice. Neither colophon can take a `<title>`; the name comes from `<rename element="colophon" xml:lang="en-US">Credits and License</rename>` in `docinfo.ptx`, and `<rename>` matches the *element name*, so it hits both. A backmatter `<appendix>` takes a title but is numbered ("Appendix B. How This Book Was Made"), so it was rejected. Renaming to just "Credits" was also tried and dropped: it names the front page too, which also holds the licence.
- **The licence goes on the copyright page, at the front — that is the publishing convention**, and it is what OpenStax, Pressbooks and Creative Commons' own guidance all do. The full licence sentence lives only in `copyright.ptx`. The back colophon repeats just a short "Licensed under …" line and the copyright line.
- **The year, the holder and the licence link each live in one file**, which both `copyright.ptx` and `colophon.ptx` include, so the front and back pages cannot drift apart. Edit these files, never retype the values:
  - `licenseLink.ptx`: the licence `<url>`, included as an element in the middle of a sentence.
  - `copyrightYear.txt` and `copyrightHolder.txt`: plain text, included with `parse="text"`, because `<year>` and `<holder>` accept only text, not elements. Save them with no trailing newline, or a space appears before the following punctuation.
  - The whole licence sentence cannot be shared this way: `<shortlicense>` holds inline text with no `<p>`, so it cannot be reused as a paragraph.
- **A frontmatter colophon affects HTML only.** The print copyright page is emitted by the title-page machinery straight from `bibinfo/copyright` — no `<colophon>` involved. Adding or removing it changes nothing in the PDF; it exists to give HTML, which has no copyright page, somewhere to show the same information.
- **The frontmatter page is ordered last in the HTML Front Matter menu by CSS** (`custom-common.css`, `.toc-frontmatter > ul.toc-item-list` as a flex column with `order: 1` on `.toc-colophon`). The schema pins it to `<frontmatter>`, so the source cannot move it; CSS reorders the menu without touching print. It cannot be pushed past the Front Matter group, because `order` only sorts siblings within one flex container.
- **`bibinfo` item order is fixed by the stylesheets**, not by the order you write them: `credit[role]`, `edition`, `website`, `copyright` (which carries `shortlicense`), `keywords`, `support`. Only `<support>` renders after the licence. Changing the order needs a custom XSL override in both formats.

## Response and workspace

### `workspace` is an attribute on `<exercise>`
Not a child element. Use `<exercise workspace="3cm">` — value in `cm` or `in`.

Print rendering: [`customPreambleLate.tex`](../external/latex/customPreambleLate.tex) (`\workspacebox`) and [`xsl/custom-latex.xsl`](../xsl/custom-latex.xsl) (task/inline routing).



## Silent-failure quick-index

These problems build without any error but drop or wrongly render content. They are listed by **symptom** — what you actually see — because that is usually what you notice first. Follow the link for the fix.

| Symptom | Cause | Where |
|---|---|---|
| A TODO never appears in HTML | assemblage placed directly in `<ul>`/`<ol>`, or its `<ul>` is a sibling of the `<p>` | [TODOs](#todos-and-assemblages) |
| A credit/attribution is missing from the **PDF** | it was put in an assemblage (discarded in print) | [TODOs](#todos-and-assemblages) |
| An `<icon>` renders as an empty box | name not in the closed 22-name list | [Images & media](#images-and-media) |
| A table ignores its width | `@width` in HTML without the CSS rule, or inside `<sidebyside>`; print needs `col/@width` on `<p>` cells | [Tables](#tables) |
| A `<credit>` renders nowhere | `title`/`author` mixed with `role`/`entity` | [Authors & credits](#authors-and-credits) |
| An author's institution is missing on the title page | bare `<institution>` not nested in `<affiliation>` | [Authors & credits](#authors-and-credits) |
| Heading reads literally `[objectives]` | the `Goals` rename was emptied | [Elements](#elements-and-semantics) |
| A TOC setting is ignored | element written as `<toc>` instead of `<tableofcontents>` | [customizations.md](customizations.md#publication-settings-that-differ-from-stock-defaults) |
| Print fill-in style unchanged despite `textstyle` | preamble override makes `textstyle` HTML-only | [latex-preamble-decisions.md](reference/latex-preamble-decisions.md) |
| A length comes out wrong with no error | `\dimexpr` written coefficient-first (`2*\sidePadding`) | [latex-preamble-decisions.md](reference/latex-preamble-decisions.md) |

Note: a `<xref>` to a module-specific id from a *shared* file fails the build **loudly** (with an error, not silently) — see [xref constraints](#xref-constraints). It is listed here only because it is an easy mistake to make.
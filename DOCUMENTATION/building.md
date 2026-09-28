[← Project Guide](README.md)

# Building

Building a module, where `{module}` is the module's code (e.g. `hawaii`, `diaMuertos`, `palabras`, `cuatroAmigos`):
```bash
pretext build {module}-tg-web       # Teaching Guide (tg) HTML build
pretext build {module}-sw-web       # Student Workbook (sw) HTML build
pretext build {module}-sw-print     # Student Workbook (sw) PDF build
```

Other useful commands, where `<target>` is any of the above build targets (e.g. `hawaii-tg-web`, `diaMuertos-sw-print`):
```bash
pretext build -g <target>                  # build regenerating all assets (sometimes needed)
pretext generate latex-image -t <target>   # generate TikZ/latex-image SVGs for <target>
pretext build --clean <target>             # wipe output/<target>/ first (after removing a division)
```

If a build fails with "Cannot resolve URI ... generated-assets/..." (e.g. a missing latex-image or qrcode file), structural edits likely shifted asset auto-numbering.
Try `pretext build -g <target>` (force-regenerates all assets) to fix it.

## `*-print` targets to PDF (via pdflatex)

`*-print` targets do **not** produce a PDF.
They are `format="latex"`, so `pretext build <target>-print` runs the XSL conversion and emits `output/<target>/*.tex` only — a clean build says nothing about whether LaTeX would compile it.
Build the PDF in a second step, with **pdflatex** (not xelatex or lualatex — the preamble's `sfmath` sans-math package is pdflatex-only).
Run pdflatex 3 times (or use `latexmk -g` if you have Perl installed on your system):

```bash
pretext build hawaii-sw-print
cd output/hawaii-sw-print
pdflatex -interaction=nonstopmode hawaii-sw.tex   # run this 3 times
# or, with Perl installed:
latexmk -g -pdf -interaction=nonstopmode hawaii-sw.tex
```

Some things in the PDF are placed only on a later run: the growing `workspace` boxes, the worksheet logo, and the page numbers in cross-references. On the first run the boxes are missing and the logo may be out of place, so do not judge the layout from it. When a run leaves something unsettled, the `.log` says `Rerun to get cross-references right`.

`publish.py` runs pdflatex as many times as needed for you.

Rebuilding a print target replaces its `.tex` file, so any hand edits to it are lost. `output/` is not tracked by git, so they cannot be recovered. If you have edited `output/{module}-sw-print/{module}-sw.tex`, copy it somewhere safe before rebuilding, or run only pdflatex.

See [`external/latex/customPreambleLate.tex`](../external/latex/customPreambleLate.tex) for what the print build customizes (and the [design decisions](reference/latex-preamble-decisions.md) behind them), and [`xsl/custom-latex.xsl`](../xsl/custom-latex.xsl) for the emitted-LaTeX overrides.

### Cover pages
PreTeXt's cover system is not designed for multi-book projects, so the cover is added to the built LaTeX instead. [`publish.py`](#publishing-scriptspublishpy) does this for a `{module}-sw-print` target, using `external/{module}-cover.pdf`. A module without that file is published without a cover, with a warning.

To add a cover by hand (for a PDF you compile yourself), make two edits to `output/{module}-sw-print/{module}-sw.tex`. First add `\usepackage{pdfpages}` just before `\begin{document}`, because the preamble does not load it and `\includepdf` comes from it. Then insert the following between the `\raggedbottom` and `\frontmatter` commands, right after `\begin{document}` (adjust the `palabras-cover.pdf` filename for the cover pdf):
```latex
%% Cover image, not numbered
\setcounter{page}{0}%
\includepdf[noautoscale=false]{external/palabras-cover.pdf}%
%% Blank obverse for 2-sided version
\thispagestyle{empty}\hbox{}\setcounter{page}{0}\cleardoublepage%
```

## `--clean` after removing a division

Use `--clean` after removing or renaming a division.
A plain build never deletes pages from `output/<target>/`, so a removed division leaves its old HTML file behind with stale content.
That orphan is not linked from the TOC, but it still matches a `grep` of `output/`, which makes deleted content look like it is still published and can make a change look unapplied when it actually worked.
So do not trust a grep of `output/` after a structural removal until the target has been rebuilt with `--clean`.
This is a separate remedy from `-g`: `--clean` wipes the target's output directory, `-g` regenerates assets into `generated-assets/`.

## Asset (re)generation

Asset (re)generation is decided by a cache hash, not by whether the file exists (verified Aug 2026, CLI 2.49.1).
`pretext build` compares a per-asset-type source hash against `.cache/.<target>_assets.json` (which holds one hash each for `latex-image`, `qrcode`, …); it regenerates only when that hash *changed* or is *absent*.
So a **fresh clone** (no `.cache/` — it is gitignored) generates everything on a plain build, but if you **delete or hand-edit an asset while the cache is intact**, a plain build (even `--clean`, which only wipes `output/`) considers it up-to-date and **skips** it — leaving the file missing.
Force it with `pretext build -g <target>`, which regenerates regardless of the cache.
So: plain build for normal work; `-g` whenever an asset is stale, was deleted, or the "Cannot resolve URI" error appears.

## Publishing (`scripts/publish.py`)

We publish web output and the Student Workbook PDFs by copying them into a **separate site repository**, `mathceo-uci.github.io`, with `scripts/publish.py`, **not** `pretext deploy`. Stock deploy stages whatever is currently built and pushes it all at once (stale targets, full `external/` folders), and has no per-target option.

Every HTML build copies the *whole* shared `external/` folder — all four modules' images — into one target, though the target uses only its own. That folder is ~85 MB and any single target needs ~20 MB of it; the waste grows as modules are added. **Stripping** deletes the media a build never references, cutting it to the ~20 MB it actually uses (`output/` only, never source). It also deletes the JS/CSS source maps (`*.map`, `*.map.gz`, ~23 MB) that PreTeXt bundles into `_static`: the deployed site never loads them — they exist only to debug PreTeXt's minified code in a browser's DevTools. The strip step always runs, so these unused files can't reach the site.

`publish.py` publishes **one target at a time** and does **no git** — it builds, strips, and writes into a local site folder (a checkout of the site repository); you commit and push that folder yourself.
It refuses to publish a target whose source still has a `\restrictedimage` placeholder (see [Restricted images](conventions.md#restricted-images-restrictedimage-placeholders)). It checks every target before building anything, and lists the files that still have one.
It shows one line per step and saves the full output of `pretext` and `pdflatex` in `output/publish-logs/`. If a step fails it stops there and shows the error (for a PDF, the LaTeX error and its line number).

```bash
python3 scripts/publish.py hawaii-tg-web              # build, strip, replace that one
python3 scripts/publish.py hawaii-sw-print            # ask to rebuild, add cover, compile, copy the PDF
python3 scripts/publish.py --no-build hawaii-tg-web   # use the existing output/ build
python3 scripts/publish.py --with-todos hawaii-tg-web # keep the TODO notes in the web build
python3 scripts/publish.py --list                     # show targets and their published names
python3 scripts/publish.py --dry-run hawaii-tg-web    # show the plan, change nothing
```

**Web targets.** For each one it builds (skip with `--no-build`), strips, then replaces that target's folder in the site folder, leaving the others untouched.
The build starts from an empty output folder (`--clean`), so a page removed from the book is not published from an old build.
It also leaves out the TODO notes: for the length of the build it sets the publication file's `<version include="…"/>` to every component except `TODO`, then puts the file back exactly as it was. Add `--with-todos` to keep them.
Because this build replaces your local copy in `output/`, the script says at the start which web targets it will rebuild, and once every target is published it rebuilds them again with a plain build, so the local copies keep their TODOs.

**Student Workbook PDFs** (`{module}-sw-print`). For each one it first asks *Rebuild with pretext? This replaces {module}-sw.tex and any hand edits to it. [y/N]*. The answer defaults to no, as it does when there is no terminal to ask in; `--no-build` skips the question. It then adds the [cover](#cover-pages), compiles the PDF with pdflatex (running it as many times as needed), and copies it to the site root.
Without a rebuild, the PDF is compiled with the copy of `customPreambleLate.tex` already in `output/{module}-sw-print/external/latex/`. A change to the preamble reaches that copy only through a rebuild, or by copying the file there yourself.

The published name comes from the target name — `{module}-tg-web` → `{module}/`, `{module}-sw-web` → `{module}-workbook/`, `{module}-sw-print` → `{module}-sw.pdf` — so `project.ptx` needs no deploy settings.

The site folder defaults to `../mathceo-uci.github.io` (a sibling of this repo); override with `MATHCEO_SITE_DIR`. It must already exist — the script never creates or clones it.

Why a separate repo and no git here:
- **No deploy config in `project.ptx`**: folder names are derived, not stored as `deploy-dir`, so a stray `pretext deploy` has nothing to build a site from. (Not fully disarmed — with no targets it falls back to pushing to a `gh-pages` root here; blocking that needs GitHub-side rules.)
- **No branch switching**, so publishing can't trigger GitHub Desktop's automatic stash, which once removed untracked files like `source-slides/`.
- **Small source clone**: the built site's history lives in the other repo, which authors rarely clone and can squash freely.

### `scripts/strip_external.py` (standalone inspector)

`publish.py` imports its strip step from here, but you can also run it directly to see what would be removed.
Every HTML build copies the *whole* shared `external/` tree into `output/<target>/external/`, so each target carries all modules' images even though it uses only its own (Hawaii's TG build is ~79 MB of external, ~17 MB of it actually referenced).
It deletes the media files (images, PDFs) the build's HTML/JS/CSS never reference, and leaves every non-media file (CSS, etc.) alone so an indirect `@import` can't break.
Dry-run by default; `--apply` deletes.

```bash
python3 scripts/strip_external.py output/*-web          # dry-run: list what it would remove
python3 scripts/strip_external.py --apply output/*-web  # delete
```

It only ever touches `output/` (regenerable), never source, and a rebuild restores the full tree — which is exactly why `publish.py` re-runs it every publish.

## Known issue: Safari worksheet print-preview

The HTML worksheet printer-icon preview (`?printpreview=…`) prints blank even pages in Safari, not Firefox or Chrome.
It's a WebKit bug with stock `print-worksheet.css` (`.onepage` sized to full page height + `page-break-after: always`), not our code — print/save-PDF worksheets from Firefox or Chrome.
(Our worksheet page-card CSS is scoped `body:not(.letter):not(.a4)` so it does not bleed into that preview.)

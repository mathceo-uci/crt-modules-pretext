# UCI MATH CEO — CRT Curriculum Modules (PreTeXt)

Culturally-responsive math enrichment modules. Each module is a
PreTeXt book in two versions — Teaching Guide (`tg`) and Student Workbook (`sw`) —
with accessible HTML (`web`) and PDF (`print`) output. 

For the available modules see `project.ptx`. For the full authoring & conventions guide (file structure, ingesting a module, PreTeXt conventions, print internals), see [DOCUMENTATION/](DOCUMENTATION/README.md).

This repo adds its own overrides, styles, and conventions to PreTeXt, targeting **PreTeXt CLI 2.49.1** (see Requirements). For the full list, see [what this repo customizes](DOCUMENTATION/customizations.md).

## Requirements

- **PreTeXt CLI 2.49.1** — the version this project is built and tested against: `pip install pretext==2.49.1`. Newer versions may work, but the repo's customizations target 2.49.1 (see [what this repo customizes](DOCUMENTATION/customizations.md) and the re-check log it links).
- **LaTeX** (TeX Live or MiKTeX, with `pdflatex`): required to generate the
  `<latex-image>` SVGs (used by web) and to create any `print` PDF.
  Packages used: `tikz`, `pgfplots`, `lato`, `sfmath` (MiKTeX auto-installs on first use).
- **Node.js 18 or later** ([nodejs.org](https://nodejs.org)): required for the Student Workbook web builds (`*-sw-web`), whose `tacoma` theme PreTeXt builds with Node. The Teaching Guide web builds use the default theme and do not need it. PreTeXt installs the Node packages it needs on the first build.

## Building

Targets: `{module}-{tg|sw}-{web|print}`. Build one, then preview; output goes to `output/<target>/`.

```
pretext build palabras-sw-web
pretext view  palabras-sw-web
```

PDF is two steps — the `print` target emits LaTeX; compile it with **pdflatex** (not xelatex): run pdflatex 3 times (or use `latexmk -g` if you have Perl installed on your system). `scripts/publish.py` does this for you. Only `sw-print` targets are enabled.

```
pretext build palabras-sw-print
cd output/palabras-sw-print
pdflatex -interaction=nonstopmode palabras-sw.tex   # run this 3 times
# or, with Perl installed:
latexmk -g -pdf -interaction=nonstopmode palabras-sw.tex
```

## Troubleshooting

- **Missing images / `Cannot resolve URI …/generated-assets/…`** — assets aren't tracked and are cached by source hash, so a plain build skips deleted or stale ones. Force with `pretext build -g <target>`.
- **Stale pages after removing a chapter/section** — `pretext build --clean <target>`.
- **`Node.js is required to build themes other than default-modern`** (a `*-sw-web` build) — install Node.js (see Requirements), then open a new terminal so it is on PATH.
- **`<name>.sty not found` (making a PDF)** — `tlmgr install <name>` on TeX Live; MiKTeX auto-installs.

If a build fails with `Cannot resolve URI …generated-assets/…`, run `pretext build -g <target>`.

---


## Learning PreTeXt

See the [PreTeXt documentation](https://pretextbook.org/documentation.html) for guides and references.

---


## License

Copyright 2026 UCI MATH CEO Community Educational Outreach, University of California at Irvine.

This repository is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/) (CC BY-NC-SA 4.0), the same license as the modules. The full text is in [`LICENSE`](LICENSE). Openly licensed images remain under the terms of their respective licenses, as listed in each module's image attributions. Logos (the `logo-*` files in `external/`) belong to their respective owners and are not covered by this license.

[← Project Guide](../README.md)

# LaTeX Preamble — Design Decisions

All custom print styling lives in **`external/latex/customPreambleLate.tex`** (print/PDF only; HTML is unaffected).
That file's own comments explain *how* each block works, and [customizations.md](../customizations.md) indexes *what* it changes.
This page records only the **decisions and measurements** behind the styling — the "why" that has no natural home in the code.

## Why the preamble is a separate, late-loaded file

PreTeXt regenerates the LaTeX preamble on every print build, so customizations can't be edited into the generated `.tex` — they would be overwritten.
Instead each print target in `project.ptx` carries `latex.preamble.late="\input{external/latex/customPreambleLate.tex}"`, which inputs the file *after* the whole generated preamble, so its definitions win.
The path is relative to the `output/<target>/` build directory, into which PreTeXt copies the entire `external/` tree — so it inputs that copy, not the source.
To change a generated definition, restate the whole thing (re-`\tcbset` the style, `\renewtcolorbox` the box, `\renewcommand` the macro) rather than patching in place.

## The wide margins are deliberate (SW only)

`inner=1.20in, outer=0.95in` on Letter gives a **6.35in measure ≈ 87 characters per line** — past the classic 45–75 band, and that is fine **for the student workbooks**.
The 45–75 rule is about fatigue from the return sweep repeated over consecutive long lines, a condition this content does not create.
Measured across the three SW books, median line length is **1–10 characters** (labels, list items, table cells, one-line prompts), and 60+ character lines are almost always a **run of one**, isolated between short items — two of three books never exceed a run of 3.
So do **not** narrow the measure to chase a character count.
The width buys more here: wider `workspace` boxes to write in, tables that fit, fewer awkward wraps.
(Margins are not the writing space — `workspace` provisions that explicitly, so "leave room for students to write" is not an argument for wide margins either.)
Inner > outer is intentional: a binding allowance for a stapled workbook, inverting the classic canon on purpose.
Set in two matched places — the body `\geometry` and the worksheet `\newgeometry` — kept equal so body and worksheet pages share a text width.

**The Teaching Guides are the exception.**
Those are genuinely prose (teacher notes, misconception paragraphs, discussion prompts), so measure *does* matter for them.
All TG print targets are commented out in `project.ptx`; if one is enabled, revisit margins for that target rather than assuming the SW values transfer.

## Micro-typography packages were tried and rejected

`microtype` is already loaded by PreTeXt, with protrusion and expansion fully on.
Modern hyphenation patterns (`usenglishmax`), a wider expansion range, and widow/orphan control were each measured on `hawaii-sw` and changed nothing — do not re-add them expecting a difference.

## Hyphenation is left on

The off rule (`\hyphenpenalty=10000`, `\tolerance=3000`, `\emergencystretch=3em`) is kept commented out in the `.tex`.
Turning it back on needs a plan for `<sidebyside>` panels: they are narrow, and without hyphenation their word spaces stretch badly.
Ragged-right fixes the spacing but leaves a ragged paragraph among justified ones, and was rejected.
`\exhyphenpenalty` is left alone — url.sty marks URL break points the same way, so raising it would push long URLs into the margin.

## A little last-resort stretch is on

`\setlength{\emergencystretch}{1.5em}` is on, with hyphenation still on; it is not a partial return of the off rule above.
Print adds a link's address after the link text, in a typewriter font, and the address can only split after a `.`, `/` or `-`.
So a part like `(creativecommons.` cannot be split, and when it landed at the end of a line, LaTeX let the line run into the margin rather than stretch the spaces past its limit.
Measured on the four SW books (2026-09-23): three lines overflowed, by 46pt, 30pt and 6pt, all in image attribution lists.
With 1.5em all three wrapped, and no other line in any book moved.
That is expected, because LaTeX uses this extra stretch only for a paragraph it cannot break any other way.

## Fill-in blanks: style in the publication file, thickness in the preamble

The *style* is `<fillin textstyle="underline" mathstyle="shade"/>` in the publication file; the *thickness* is `\ptxfillinrule` (`1pt`) in the preamble, which restates PreTeXt's hardcoded 0.3pt rule (stock exposes no length to adjust).
**The two must change together.**
PreTeXt builds `\ptxfillintext` from `textstyle` and the preamble replaces it, so `textstyle` now drives **HTML only** — set it to `box` and print would still draw an underline, with no warning.
The redefinition is `\ifdefined`-guarded, since PreTeXt emits that macro only for books whose source uses `<fillin>` and this preamble is shared by all four SW books.
(`mathstyle` is unaffected — it defines a separate macro, `\fillinmath`, shared by LaTeX and MathJax.)

## Editing rules

- **Set `\titlespacing` after any `\titleformat`** for the same level — `\titleformat` resets that level's spacing to titlesec defaults, so spacing set before it is lost.
- **Guard optionally-emitted macros**: `\providecommand` before `\renewcommand` (as with `\ptxfillintext`), since PreTeXt only emits some macros when the source uses that feature.
- **`\dimexpr` multiplication must be dimension-first**: write `\sidePadding*2`, not `2*\sidePadding`; the reversed form misparses a decimal-coefficient macro like `0.5ex` and produces a wrong length with no error.
- **Workspace appearance is project-wide**: the box look (`workspacefill` / `workspaceborder` / `workspaceboxstyle`) lives in `tikz/tikzPreamble.tex` — the only preamble loaded in **both** the latex-image and print builds, so `\workspacebox` and figure answer boxes can share one definition. The box behaviour (`\sidePadding` / `\workspacebox`) is here in the preamble. Change these, never inline.
- **After changing spacing or box code**, colliding boxes may need an extra LaTeX pass — see [Building](../building.md).

Some print behavior is achieved by changing the *emitted* LaTeX rather than a macro — see [`xsl/custom-latex.xsl`](../../xsl/custom-latex.xsl).

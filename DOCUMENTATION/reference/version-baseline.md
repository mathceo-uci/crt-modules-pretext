[← Project Guide](../README.md)

# Version Baseline & Re-check Log

Every override, workaround, and "stock PreTeXt does X" claim in this documentation was written against a specific PreTeXt version.
Stock behavior changes between releases, so a hack that is required today may become unnecessary — or wrong — after an upgrade.
This file records the baseline the claims were verified against, and gives a script to re-check them so the overrides can be retired when upstream fixes them.

## Baseline

- **PreTeXt CLI:** 2.49.1
- **Stock core:** commit `5836dfcbdc342841acdbe266871a204c8a9dc8cc` (bundled in the CLI as `resources/core.zip`)
- **Verified:** 2026-08-28
- **Result:** every override/workaround below was **confirmed still required** at this version, and every "closed list / stock behavior" claim was **confirmed still accurate**.

So each such statement in the docs should be read as *"…as of PreTeXt 2.49.1."*
When you upgrade the CLI, re-run the script below; anything that changes from `STILL-PRESENT` to `GONE` is a fix that can now be dropped from `xsl/custom-latex.xsl` or `external/latex/customPreambleLate.tex`.

## Verified claims

Line numbers are for core `5836dfc` and will change over time; the re-check script searches by pattern, not by line number, so it keeps working when they move.

| Claim in the docs | Where in our docs | Stock anchor (core `5836dfc`) | Status @ 2.49.1 |
|---|---|---|---|
| Stock wraps every latex-image in `\resizebox{\linewidth}{!}` (our XSL drops it → native-size print) | [custom-latex.xsl](../../xsl/custom-latex.xsl), [latex-images](../conventions.md#latex-image-and-tikz) | `pretext-latex-common.xsl:7521` | STILL-PRESENT → override still required |
| Stock wraps `tabular[ancestor::sidebyside]` in `\noindent\resizebox` (our XSL drops it) | [custom-latex.xsl](../../xsl/custom-latex.xsl), [tables](../conventions.md#tables) | `pretext-latex-common.xsl` template `match="tabular[ancestor::sidebyside]"` (~`:7619`) | STILL-PRESENT → override still required |
| Stock `mode="workspace"` emits invisible `\rule{\ptxworkspacestrutwidth}{h}` (our XSL emits `\workspacebox`) | [custom-latex.xsl](../../xsl/custom-latex.xsl) | `pretext-latex-common.xsl:2226` | STILL-PRESENT → override still required |
| Print `\workspacebox` draws with `workspaceboxstyle` (from `tikzPreamble.tex` via docinfo's `<latex-image-preamble>`); stock emits that preamble whenever it is non-empty, **not** only when the document uses `<latex-image>` | [customPreambleLate.tex](../../external/latex/customPreambleLate.tex), [tikzPreamble.tex](../../source/tikz/tikzPreamble.tex) | `pretext-latex-common.xsl:2034` (`latex-image-support`, gated on `$latex-image-preamble`) | SAFE → coupling holds while `docinfo.ptx` keeps a non-empty `<latex-image-preamble>` |
| Stock hardcodes the fill-in rule at `0.3pt` and builds `\ptxfillintext` from `textstyle` (preamble restates it for `\ptxfillinrule`) | [latex-preamble decisions](latex-preamble-decisions.md) | `pretext-latex-common.xsl:2207` (def), `:2213`/`:2216` (`0.3pt`) | STILL-PRESENT → override still required |
| Stock `backcolophonstyle` uses `left/right skip=0.15\textwidth` (preamble widens to `0.08`) | [customPreambleLate.tex](../../external/latex/customPreambleLate.tex) | `pretext-latex-common.xsl:3043` | STILL-PRESENT → override still required |
| Print tabular width is decided per **cell** (`test="p"` → `m{…\linewidth}`), not per column | [tables](../conventions.md#tables) | `pretext-latex-common.xsl:8088`, `:8393` | STILL-PRESENT → claim accurate |
| `<icon>` has a closed list of **exactly 22** names; `youtube` is not one | [images-media](../conventions.md#images-and-media) | `pretext-common.xsl` `<iconinfo name="…">` (22 unique) | STILL 22 → claim accurate |
| Two colophons share the name because core defines a single `string-id='colophon'` | [authors-credits](../conventions.md#authors-and-credits) | `xsl/localizations/en-US.xml:267` | STILL single → claim accurate |
| Stock HTML sets `b-division-companion-chunks` to `true()`, so a chapter introduction gets its own page (our SW HTML sets it back to `false()` and overrides `mode="intermediate"` to show the introduction on the chapter page) | [customizations.md](../customizations.md#chapter-introduction-on-the-chapter-page-xslcustom-html-swxsl), [custom-html-sw.xsl](../../xsl/custom-html-sw.xsl) | `pretext-html.xsl` (`b-division-companion-chunks` set `true()`; `mode="intermediate"` template) | STILL-PRESENT → override still required (also checked on `master`, 2026-09-18: identical) |
| Stock loads the monospace font only when `b-needs-mono-font` is true, which `<c>`, `<pre>`, `<program>` and similar set but `<url>` does not (our print XSL sets the variable to `true()` for every book). If the variable is renamed, the override silently stops working | [customizations.md](../customizations.md#print--latex-emitted-latex-overrides-xslcustom-latexxsl), [custom-latex.xsl](../../xsl/custom-latex.xsl) | `pretext-latex-common.xsl:91` (`b-needs-mono-font`) | STILL-PRESENT → override still required (checked 2026-09-23) |

### Not verified against core (version-stamped, but a different kind of claim)

- **Measured settings (not stock behavior)**: the hyphenation-off decision, "micro-typography packages changed nothing", the wide-margin choice, and the 1.5em last-resort stretch were *measured on our own SW content under PreTeXt 2.49.1*, not read from stock core.
  Re-measure these if the content or fonts change, not just when the CLI is upgraded.
- **External bugs**: the Safari worksheet print-preview blank pages (a WebKit bug) are outside PreTeXt core; a CLI upgrade will not fix them.
- **Inherent design**: "`*-print` targets emit `.tex` only" follows from `format="latex"` and is not a bug that will change.
- **Publication-file element**: the `<tableofcontents>` vs `<toc>` claim is about the publication schema, not the source schema (`pretext.rng`), so the re-check script does not cover it.

## Re-check script

Run after upgrading the PreTeXt CLI.
It extracts the bundled core and greps for each stock pattern the overrides depend on.
`STILL-PRESENT` = keep the override; `GONE` = upstream may have changed — inspect, and retire the override if so.

```bash
# 1. Print installed version and extract its bundled core
pretext --version
PKG=$(python3 -c "import pretext, os; print(os.path.dirname(pretext.__file__))")
TMP=$(mktemp -d); unzip -q "$PKG/resources/core.zip" -d "$TMP"
X=$(ls -d "$TMP"/pretext-*/xsl); LOC="$X/localizations"   # resolve the glob to a real path

chk(){ if rg -q "$2" "$1" 2>/dev/null; then echo "STILL-PRESENT  $3"; else echo "GONE?          $3"; fi; }

chk "$X/pretext-latex-common.xsl" '\\resizebox\{\\linewidth\}\{!\}'                       "latex-image resizebox wrapper (custom-latex.xsl override)"
chk "$X/pretext-latex-common.xsl" 'match="tabular\[ancestor::sidebyside\]"'               "sidebyside tabular resizebox (custom-latex.xsl override)"
chk "$X/pretext-latex-common.xsl" 'ptxworkspacestrutwidth'                                "workspace invisible strut (custom-latex.xsl override)"
chk "$X/pretext-latex-common.xsl" 'newcommand\{\\ptxfillintext\}'                         "fillin text macro / 0.3pt rule (preamble override)"
chk "$X/pretext-latex-common.xsl" 'left skip=0.15.textwidth, right skip=0.15.textwidth'   "backcolophon 0.15 insets (preamble override)"
chk "$X/pretext-latex-common.xsl" 'test="p"'                                              "tabular per-cell width"
echo -n "icon names (expect 22): "; rg -o '<iconinfo name="[^"]+"' "$X/pretext-common.xsl" | sort -u | wc -l
chk "$LOC/en-US.xml"              "string-id='colophon'"                                  "single colophon localization"
chk "$X/pretext-html.xsl"         'name="b-division-companion-chunks" select="true'       "chapter-intro-as-own-page opt-in (custom-html-sw.xsl override)"
chk "$X/pretext-latex-common.xsl" 'name="b-needs-mono-font"'                              "monospace font variable (custom-latex.xsl override)"
```

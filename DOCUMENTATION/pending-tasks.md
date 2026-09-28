[← Project Guide](README.md)

# Pending Tasks

## General (all modules, HTML)
- [ ] (Low priority, maybe later) **Add Math CEO branding to the HTML page footer** (idea, not started yet). Every HTML page ends with a footer (`<div id="ptx-page-footer">`) that currently shows the feedback button and the PreTeXt, Runestone, and MathJax logos. We'd like to add our own Math CEO logo and a short credit line there, and maybe remove the Runestone and MathJax logos. Notes for whoever picks this up:
  - There is no publication-file setting for the footer. PreTeXt builds its contents into the page and gives us no option to change them, so we have to override part of PreTeXt's HTML conversion.
  - The logo itself is easy: both publication files already declare `<brandlogo source="logo-mathceo_smallest.png" url="https://sites.ps.uci.edu/mathceo/"/>` for the top banner, and PreTeXt makes that image and link available to reuse.
  - There is a custom HTML stylesheet for the Student Workbook, `xsl/custom-html-sw.xsl`, wired into the `*-sw-web` targets. The footer would follow the same pattern: put the footer block in a stylesheet and point each of the eight `*-web` targets at it (the Teaching Guide targets have none yet, so they would need one too). The styling (and hiding the two logos, if we decide to) would go in `custom-common.css`.
  - When writing the footer block, build the logo markup ourselves rather than calling PreTeXt's `brand-logo`: that one is written for the top banner and would repeat an HTML `id` that is already on the page.
  - Two things to decide first: what the credit line should say, and whether to keep or remove the PreTeXt, Runestone, and MathJax logos.


## Repository license
- [ ] **Decide on a separate license for the code.** The whole repository is under CC BY-NC-SA 4.0 (`LICENSE`), but Creative Commons advises against using its licenses for software. The code (`scripts/`, `xsl/`, and similar) could go under a software license such as MIT, with CC BY-NC-SA kept for the curriculum content. If we do this, the README's License section should say which license covers which folders.


## Hawaii

## Palabras More, Palabras Less


## Día de los Muertos
- [ ] Add missing músico images (Bread Friends, Choco-Dos, TRI example, Plaza Mágica grid)
- [ ] Ingest Let's Play TG content (p. 39: Round 1, 2, 3 + Plaza Mágica note)
- [ ] Ingest Rooms TG content (sec-rooms in chap-more-counting)
- [ ] Add a cover, `external/diaMuertos-cover.pdf`. Until it exists, `publish.py` publishes the Student Workbook PDF without one. Credit it in the SW image attributions (see [Image attributions](conventions.md#image-attributions-appendix-image-attributions)).

## Los 4 Amigos
First-pass ingestion complete (both chapters + all four worksheets; `cuatroAmigos-tg-web` and `cuatroAmigos-sw-web` build clean, all worksheets numbered). Outstanding follow-ups:
- [ ] Add a cover, `external/cuatroAmigos-cover.pdf`. Until it exists, `publish.py` publishes the Student Workbook PDF without one. Credit it in the SW image attributions (see [Image attributions](conventions.md#image-attributions-appendix-image-attributions)).
- [ ] Supply image assets — remaining: `cuatroAmigos-tree-24worlds.png`. The source images are in the local `cuatroAmigos-tg-images/` folder (see [Ingesting a module](ingesting-a-module.md), step 3).
- [ ] Supply the `external/cuatroAmigos-blm-*.pdf` manipulative sheets (colored squares, friends & hobby cards, tally chart, mini-tables, large tree) and add point-of-use links (see the ch.1 Materials TODO).
- [ ] Decide tree rendering (TikZ vs image) for the 24-world solution tree (`ws-cuatroAmigos`, page 3 solution).
- [ ] Add YouTube IDs for the two overview videos (currently `youtube="TODO"`: A Traveling Puzzle, Cuatro Amigos — both "by Karl").
- [ ] Resolve flagged source oddities: phantom "Occupations" sub-activity (Overview p.6 only); activity-duration disagreements across slides (Viajeros 5/10; Cuatro Amigos 20/25/15); the Cuatro Amigos puzzle solution uses names Alana/Hank/Leyla/Shawn vs the activity's Axel/Ben/Cora/Dana.
- [ ] Decide whether to fold in the Presentation-slide extension Q&A (pp. 45–46, with worked answers) into `chap-challenges` (flagged as TODO there).
- [ ] Decide representation for the hobby icons (dancing/sports/reading/video games) in `ws-cuatroAmigos`. Emoji are ruled out project-wide (no print/Windows support), so they are kept as words; the open choice is whether to add them as images instead.
- [ ] Review the `[[[ … ]]]` non-verbatim insertion (`grep -rn '\[\[\[' source/cuatroAmigos-*.ptx` — currently just the blank-tree-scaffold note) and confirm or replace with source wording.

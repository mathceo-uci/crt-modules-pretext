[← Project Guide](README.md)

# Ingesting a New Module (Workflow)

This is the method that has worked well — follow it when ingesting a new source PDF.

1. **Plan first (plan mode).**
   Read the *entire* source PDF up front (the TG pages, plus the trailing duplicate SW if present — ingest from the **TG** perspective and skip the SW duplicate).
   Decide the slug, the chapter/section structure, and the worksheet split *before* writing.
   Confirm structure/naming/workflow decisions with the user in plan mode.

2. **Copy an existing module as the structural template.**
   `diaMuertos` is the most complete reference for book roots, frontmatter, module intro, worksheets, and `project.ptx` targets.
   Mirror its patterns instead of inventing structure.
   Chapters map to the source "Parts"; each activity `<section>` `<xi:include>`s one worksheet.

3. **Extract the PDF images for reference first.**
   Keep the source PDF outside this repository, in a local folder of your choice.
   Export every embedded image to a `{module}-tg-images/` folder next to it, so source images can be matched to `<image>` references as sections are completed.
   Use **PyMuPDF**, deduplicating by `xref` and compositing soft-mask alpha (plain `pdfimages` dumps hundreds of separate mask files):
   ```python
   import fitz, os
   doc = fitz.open("path/to/{module}-tg.pdf")
   out = "path/to/{module}-tg-images"; os.makedirs(out, exist_ok=True); seen = set()
   for pno in range(len(doc)):
       for info in doc[pno].get_images(full=True):
           xref, smask = info[0], info[1]
           if xref in seen: continue
           seen.add(xref)
           pix = fitz.Pixmap(doc, xref)
           if smask: pix = fitz.Pixmap(pix, fitz.Pixmap(doc, smask))
           if pix.colorspace and pix.colorspace.n >= 4: pix = fitz.Pixmap(fitz.csRGB, pix)
           if pix.width >= 8 and pix.height >= 8:
               pix.save(f"{out}/p{pno+1:02d}-x{xref:04d}-{pix.width}x{pix.height}.png")
   ```
   Filenames `p<page>-x<xref>-<w>x<h>.png` map each image to its source slide.
   As sections are finalized, copy the chosen files, under semantic names, into your local folder outside this repository, and clear the matching image TODOs.
   **By default every ingested image is restricted:** the `.ptx` gets a `\restrictedimage` placeholder at the image's printed size, never `<image source="…"/>` (see [Restricted images](conventions.md#restricted-images-restrictedimage-placeholders)).
   An image moves to `external/` only after its license is checked and allows sharing.

4. **Build the full structure in one pass, filled with verbatim source text — not empty shells.**
   Do the **whole module at once** (every chapter and worksheet), not one chapter at a time.
   Build to [File structure & naming](file-structure.md): the file layout, naming convention, frontmatter include order, and element hierarchy.
   Create every file (both book roots, frontmatter, module intro, all worksheets) with the *complete* container hierarchy (chapters, sections, `<introduction>`/`<objectives>`/Breakdown/Materials/Checklist, worksheet `<page>`/`<exercise>`), and fill each container with text transcribed from its mapped PDF page — in the **same pass** that creates the container (never scaffold hollow divisions and backfill prose later; a chapter with only a title/opener + a `PENDING: fill` TODO is exactly the empty shell this forbids).
   Every container must still satisfy the schema (an `<ol>`/`<ul>` needs ≥1 `<li>`, `<objectives>` ≥1 item, `<exercise>` a `<statement>`, each `<worksheet>` ≥1 `<page>` with a block).
   Keep each worksheet's parent division *structured* so the worksheet renders **numbered** — put pre-worksheet teacher prose in `<introduction>` and anything after it in `<conclusion>`, never as a bare sibling of the `<worksheet>`. See [Worksheet numbering](file-structure.md#worksheet-numbering-keep-the-parent-division-structured).

   **Do not use page number references (e.g. `p3-`, `p7-`) in `xml:id` values or filenames.**
   Use semantic names: `hawaii-ws-moreUnits`, `hawaii-ws-measuringTape.ptx` — never `ws-sw-p7-more-units` or `p3-measuring-tape.ptx`.

5. **Transcribe, do not invent.**
   Only source text; genuine gaps become TODOs; authored/non-verbatim prose is wrapped in `[[[ … ]]]` (see the faithful-ingestion convention below).
   Prefer restoring verbatim wording over paraphrasing.

6. **Review is a separate, later pass — not a mid-ingestion gate.**
   The initial ingestion is the single full pass of step 4: create and fill *every* chapter and worksheet before handing off.
   Do **not** stop after one chapter to wait for review, and do **not** leave placeholder/shell divisions in the meantime.
   The chapter-by-chapter review — reading, correcting, and refining each chapter against the source — happens **afterward**, done manually by the user over time (across later sessions, not in one go); it does not interleave with or gate the one-pass draft.

7. **Verify continuously.**
   `pretext build {module}-tg-web` and `pretext build {module}-sw-web` must compile clean after every file.

8. **Defer decisions as TODOs, don't block the draft.**
   Unknown video IDs (`youtube="TODO"`), graph rendering (TikZ vs image), image attributions, SW page references, and source typos/inconsistencies are flagged and resolved in a later pass.

## Faithful ingestion: flag any non-verbatim text with `[[[ … ]]]`

Prose in an ingested module must be **verbatim from the source PDF**.
Any text you author that is *not* lifted from the source — connective sentences, paraphrases, inferred instructions, or a descriptive title you wrote to organize source content — must be wrapped in triple square brackets `[[[ … ]]]` so it is visible in the output and easy to find with grep (`grep -rn '\[\[\[' source/`).
Do **not** use per-sentence `<assemblage component="TODO">` for this (reserve TODOs for genuine open decisions/gaps).
Structural element `<title>`s that are project conventions (Checklist, Materials, Goals, Breakdown, Overview) and `<shortdescription>` alt text are inherently authored and are **not** marked.
Obvious source typos may be silently corrected; content-level source oddities (wrong-looking words/values) get a TODO, not a silent fix.

Related conventions used heavily during ingestion:
[choose elements by meaning](conventions.md#elements-and-semantics),
[TODO assemblages](conventions.md#todos-and-assemblages), and
[images & media](conventions.md#images-and-media).

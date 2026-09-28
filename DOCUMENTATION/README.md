# UCI MATH CEO Curriculum Modules (PreTeXt) — Project Guide

This folder is the authoritative guide to the project.
Start here, then open the one file that covers your task.
The quick-start is the repo-root `README.md` (requirements, build/view commands, troubleshooting).

## Project Overview

This is a **PreTeXt** project for the UCI MATH CEO culturally-responsive math enrichment curriculum — multiple modules for grades 6–8.
Each module is ingested from a source PDF kept outside this repository (only used when ingesting a module).

### Modules

See `project.ptx` and [File structure & naming](file-structure.md).

## Documentation map

- **[File structure & naming](file-structure.md)**: the `source/` layout, the module-first naming convention, structure rules (each module a `<book>`, inline frontmatter, worksheet files), and the in-book element hierarchy.
- **[Building](building.md)**:  build command for different export formats, common build errors and how to deal with them.
- **[PreTeXt customization for the modules](customizations.md)**: everything this repo adds or changes on top of stock PreTeXt (overrides, custom LaTeX preamble, styles, renames, custom TODOs, growing response boxes in print), built against PreTeXt 2.49.1, each linked to its detail. Start here if you know PreTeXt and want the non-standard parts.
- **[PreTeXt authoring conventions](conventions.md)**: pick tags by meaning, and avoid the mistakes that build without error but silently drop or mangle content — includes a [silent-failure quick-index](conventions.md#silent-failure-quick-index). Covers elements, images & media, TODOs, tables, latex-image/TikZ, `<xref>`, links, authors & credits, and response/workspace.
- **[Ingesting a new module](ingesting-a-module.md)**: the 8-step workflow, the PyMuPDF image extractor, and the faithful-ingestion `[[[ … ]]]` marker.
- **[Pending tasks](pending-tasks.md)**: the open task list per module.

### Further technical reference

[PreTeXt customization](customizations.md) above is the full index of *what* gets overridden and how. Reasons for some of these decisions are documented in the following two files:

- **[LaTeX preamble decisions](reference/latex-preamble-decisions.md)**: the measurements and rejected alternatives behind the print styling — why the SW margins are deliberately wide, why micro-typography was dropped, the fill-in `textstyle` gotcha, and the preamble editing rules.
- **[Version baseline & re-check log](reference/version-baseline.md)**: the PreTeXt version (**2.49.1**) every "stock does X" claim was checked against, with a script to re-run after a CLI upgrade so overrides upstream has since fixed can be retired.

#!/usr/bin/env python3
"""Strip unreferenced media files from a PreTeXt HTML build's external/ folder.

A PreTeXt HTML build copies the *entire* external/ tree into every target, even
files that build never references. This removes the media files (images, PDFs)
that nothing in the build points at, leaving all non-media files (CSS, etc.)
untouched so indirect references like a CSS @import can never break.

Operates only on files under output/<target>/ (regenerable), never on source.
Dry-run by default; pass --apply to actually delete.

This is the standalone inspector. To publish a target with the strip step
included, use scripts/publish.py, which imports the strip() function from
this file.

Usage:
    python3 scripts/strip_external.py output/hawaii-tg-web [more build dirs...]
    python3 scripts/strip_external.py --apply output/*-web
"""
import os, re, sys

# Only these are ever candidates for deletion. Anything else in external/
# (css, tex, ...) is always kept, so indirect references can't be broken.
MEDIA_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf"}
# Files scanned for references to external assets.
TEXT_EXTS = {".html", ".htm", ".js", ".css"}
REF_RE = re.compile(r"external/([^\"'()<>\s]+)")


def referenced_basenames(build_dir):
    """Every external/... asset basename referenced by any text file in the build."""
    names = set()
    for root, _dirs, files in os.walk(build_dir):
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in TEXT_EXTS:
                continue
            try:
                text = open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for m in REF_RE.findall(text):
                names.add(os.path.basename(m))
    return names


def strip(build_dir, apply, verbose=True):
    ext_dir = os.path.join(build_dir, "external")
    if not os.path.isdir(ext_dir):
        if verbose:
            print(f"  (no external/ in {build_dir}, skipping)")
        return 0, 0
    keep = referenced_basenames(build_dir)
    freed = removed = 0
    for root, _dirs, files in os.walk(ext_dir):
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in MEDIA_EXTS:
                continue  # non-media: always keep
            if fn in keep:
                continue  # referenced: keep
            path = os.path.join(root, fn)
            freed += os.path.getsize(path)
            removed += 1
            if verbose:
                print(f"    {'DELETE' if apply else 'would delete'}: {os.path.relpath(path, build_dir)}")
            if apply:
                os.remove(path)
    return removed, freed


def main(argv):
    apply = "--apply" in argv
    dirs = [a for a in argv if a != "--apply"]
    if not dirs:
        print(__doc__)
        return 1
    total_removed = total_freed = 0
    for d in dirs:
        print(f"\n{d}  ({'APPLY' if apply else 'DRY-RUN'})")
        r, f = strip(d, apply)
        print(f"  -> {r} media files, {f/1e6:.1f} MB {'removed' if apply else 'would be freed'}")
        total_removed += r
        total_freed += f
    print(f"\nTOTAL: {total_removed} files, {total_freed/1e6:.1f} MB "
          f"{'removed' if apply else 'would be freed'}")
    if not apply:
        print("Re-run with --apply to delete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

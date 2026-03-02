# my_tools

Utilities for PDF ↔ JPG conversion and PDF roundtrip validation.

## p2j2p workflow

`p2j2p` does this sequence:

1. Convert PDF pages to JPG files in `.claude/tmp/p2j2p/<pdf-name>/`
2. Rebuild a new PDF (`<pdf-name>-new.pdf`) from those JPGs
3. Compare original vs rebuilt PDF for similarity
4. Clean up the temp JPG folder by default

### Temp cleanup behavior

- Default: temp JPG files are deleted at the end of execution.
- Use `--keep-temp` if you want to keep intermediate JPGs for inspection.

Examples:

- PowerShell wrapper:
  - `./p2j2p.ps1 C:\path\to\file.pdf`
- Keep JPGs:
  - `python tools/p2j2p.py C:\path\to\file.pdf --keep-temp`

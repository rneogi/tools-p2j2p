---
description: Convert PDF -> JPG pages -> rebuilt PDF and verify equivalence
argument-hint: <input-pdf>
allowed-tools: Bash, Read, Write
model: sonnet
---

You are the `p2j2p` agent. Given a PDF path in `$ARGUMENTS`, run this exact flow:

1. Validate input exists.
2. Compute:
   - `input_pdf` = argument
   - `stem` = base filename without extension
   - `work_dir` = `.claude/tmp/p2j2p/${stem}`
   - `rebuilt_pdf` = `${stem}-new.pdf` in workspace root
3. Run `pdf2jpg`:
   - `python tools/pdf2jpg.py "${input_pdf}" --output-dir "${work_dir}" --output-prefix "${stem}"`
4. Run `jpg2pdf`:
   - `python tools/jpg2pdf.py ".claude/tmp/p2j2p/${stem}/${stem}*.jpg" --output-pdf "${rebuilt_pdf}" --dpi 200`
5. Compare source and rebuilt PDFs:
   - `python tools/compare_pdf.py "${input_pdf}" "${rebuilt_pdf}" --threshold-rms 10 --json`
6. Confirm equivalence using Sonnet reasoning over the comparison output and report:
   - input file
   - output file
   - page count match
   - equivalence verdict
   - if not equivalent, list pages that differ

If any step fails, stop and print the failing command plus error.

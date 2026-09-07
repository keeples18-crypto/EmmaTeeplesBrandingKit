# EmmaTeeplesBrandingKit

Brand and design assets for Emma Teeples — PGA Associate golf instructor, Redding CA.
Instagram: @emmateeples.golf

Read `CLAUDE.md` before working in here. It carries the brand tokens, the credential
language, the technical gotchas, and the legibility standard.

## Layout

```
brand/            palette, type specs, logo files
covers/           Instagram highlight covers, one folder per direction
  <Direction>/    01_StartHere.png … 06_OffCourse.png
src/              generator scripts
build/            contact sheets and previews (not committed)
docs/             one-page PDFs and picker sheets
```

## Regenerating covers

```bash
python3 src/covers.py            # writes PNGs into covers/
python3 src/contact_sheet.py     # writes build/ previews at 220px and 68px
```

Then open the contact sheet and check the 68px column. That is the acceptance test.

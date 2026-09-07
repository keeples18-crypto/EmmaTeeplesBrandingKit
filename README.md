# EmmaTeeplesBrandingKit

Brand and design assets for Emma Teeples — PGA Associate golf instructor, Redding CA.
Instagram: @emmateeples.golf

Read `CLAUDE.md` before working in here. It carries the brand tokens, the credential
language, the technical gotchas, and the legibility standard.

## Layout

```
brand/            palette, type specs, logo files
covers/           Instagram highlight covers, one folder per direction
  <Direction>/    01_Start.png … 06_Off.png
src/              generator scripts
build/            contact sheets and previews (not committed)
docs/             reviewer sheets and one-page PDFs (committed, viewable on GitHub)
```

## Regenerating covers

```bash
python3 src/covers.py            # writes PNGs into covers/
python3 src/contact_sheet.py     # writes build/ previews at 220px and 68px
python3 src/review_sheet.py      # writes docs/review_sheet.png for a phone reviewer
```

Then open the contact sheet and judge the 68px row on distinctiveness and cohesion.
The word need not be readable there; Instagram prints the highlight name below the circle.

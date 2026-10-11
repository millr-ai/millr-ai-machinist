# The Millr page: the visual framework

The page is how the engineer meets your review: their part in 3D with each change lit where it is, the exact fix, the decision, and how you worked it out. assets/shell.html is the page and scripts/build_page.py fills it from two files you write. The page is Millr's: its layout, words and behavior are the same for every review, so you fill it rather than restyle it.

What the page does with what you give it: a headline with the verdict; a "Cannot be machined as drawn" section only when there is a blocking finding; one list of changes, each with its title, its one-line change and its flags at medium or high, grouped by level; a change opens in place to show the condition, Now / Change to with the fix, Fix this or Ignore, Why it matters, Before you change it (or Safe to apply), and one folded row, How Claude worked it out; after each decision the next undecided change opens at its top, in order, then any skipped ones; once every change is decided, the next step: fix instructions, "Have Claude make the changes" when the review is editable, and an Export PDF request. With nothing to change, the page says so and offers the PDF. It works with a keyboard, on a phone, in light and dark, and with reduced motion, and printed from the browser it gives the whole review with every change open.

The part sits beside the list, plain until the engineer opens a change. Then the change's faces light in Millr orange and the camera moves to them: out to the whole part, around to the side that shows the most of the lit faces, then in, far enough to keep the part around them so the engineer can see where they are. If the faces cannot be seen from any side, the page cuts the part open in front of them. Faces that amount to the whole part show the whole part. Nothing else is drawn on the part: no labels, no dimensions, no captions. The page places the camera itself; nothing in review.json steers it.

## What you give the page
1. **The part, as a mesh with face identities** (part.json). Produce it from the same measurement pass as your findings, so a finding's face ids are the page's face ids. The format:
   ```
   { "units": "mm",
     "file_units": "inch",                          // what the file was written in, so you speak the engineer's units
     "up": "z",                                     // the file's up axis as the part stands in the engineer's CAD: "z", or "y" for a Y-up export
     "bodies": 1,
     "positions": [x, y, z, x, y, z, ...],          // triangle vertices, in mm, exactly as in the file (not moved, not turned); the page and the PDF stand the part up from `up`
     "indices":   [a, b, c, a, b, c, ...],          // triangles, three vertex numbers each, face after face
     "faces": [ { "id": 0, "body": 0, "tris": [first, end],      // this face's triangles: the first one and the one after the last (end exclusive)
                  "type": "cylinder", "box": [x0, y0, z0, x1, y1, z1], "axis": [x, y, z, dx, dy, dz], "radius": 3.0, "area": 56.6 }, ... ] }
   ```
   What must be true of it:
   - Faces are listed in the order whatever reads the file lists them, solid by solid, with ids 0, 1, 2, ... in that order, and you measure with the same enumeration; `body` is the index of the solid the face belongs to. The builder refuses any other numbering.
   - Each face's triangles sit together in `indices`: triangulate face by face and append, recording where each face's triangles start and end. The end is exclusive; an inclusive last index leaves one triangle of every face unlit, and the builder warns when it sees that pattern.
   - `box` is the face's bounding box in part coordinates; the camera frames a finding from the boxes of its faces. The page computes a missing box from the face's triangles, but your measurements should carry it. `axis` for a cylinder, cone or torus is a point on the axis and a direction; the file does not guarantee the direction's sense, and the page uses it only to find which end of a bore is open.
   - `positions` and `indices` may be base64 strings of little-endian float32 and uint32 values instead of arrays, to keep a large part small. Any other field you measured may ride along (`type`, `radius`, `normal`, `center`); those are your facts.
   - Tessellate to the smallest feature, not the part, so holes and fillets look round at the close-up; the builder says when the page is larger than it should be.
   A mesh file has no exact faces to measure; say what you can and cannot judge from it.
2. **The review** (review.json):
   ```
   { "file": "<the part file's name>",
     "claude_can_edit": false,                      // true only when you can edit this part: it is built from code you can
     "claude_can_edit_because": "",                 // regenerate, or a connector passes the test in references/connectors.md; say which
     "blocking":     [ <finding>, ... ],           // cannot be machined at all as drawn; the fix is the design change that makes it machinable; no flags
     "improvements": [ <finding>, ... ],           // most important first; the page shows those with at least one flag at medium or high
     "revision": { "previous": "...", "summary": "...", "confirmed": [...], "open": [...], "other": [...] }   // optional
   }
   <finding> = {
     "title": "...", "condition": "...", "why": "...", "fix": "...",
     "faces": [<ids>],                              // ids from part.json: the faces this change is about, lit when it opens
     "flags": { "cost": "medium", "lead time": "low", "risk": "high" },   // a level for each (improvements only); the page shows the change when one is medium or high
     "decide": { "safe": false, "note": "<what to check first, or why it is safe>" },
     "basis": "<how you worked it out: what you measured, what you looked up and where, what is your judgment>",   // shown folded under How Claude worked it out
     "edit": { "feature": "...", "where": "...", "current": "...", "target": "...", "check": "..." },
     "status": "approved" | "ignored"                // optional: the engineer's decision
   }
   ```

## Build and deliver
`python3 scripts/build_page.py part.json review.json review.html --file "<file>" --desc "<part, material>" --credit "<who the part file is from, when it is not the engineer's own; else empty>"`. It stops with a plain message if the part has no faces or no triangles to show, a face id does not exist, a field is missing, a flag or level is unknown, or a finding carries a sources list instead of a basis, warns on wording (dashes, prices, times, "verified", long titles), and notes the changes it keeps off the page because nothing in them is at medium or higher.
- **Delivering the page**: deliver `<part>_millr_review.html` the way the surface you are on hands files to the engineer, with the receipt SKILL.md describes and nothing of the review in the chat. Where the surface can publish pages, a published page is the same file with a link the engineer can return to or share. When you change the review, deliver the page again. Where you have the engineer's file system and a browser, write it next to the part and open it.
- **The page as a file**: it lays itself out for whatever width it gets, down to a phone. It carries everything it needs inside it, the 3D library included, asks the network for nothing and keeps nothing in the browser, so it opens wherever a page can. If the 3D view cannot start, the changes and the fix instructions still work; the page says so.
- **Who fixes it**: the page shows "Have Claude make the changes" only when `claude_can_edit` is true. Set it true only when the part is code you can regenerate, or a connector in this conversation passes the test in references/connectors.md, and say which in `claude_can_edit_because`. For everyone else (an exported file from any CAD) the page shows "Fix instructions" only: the engineer makes the change in their own CAD, and you check the revision when it comes back. Never show an engineer a button that cannot work for them.
- **Decisions**: the page counts the changes left to decide. Inside a change the engineer chooses "Fix this" or "Ignore"; nothing else happens there. On the main screen the change turns orange and "Approved", or gray and "Ignored", with an undo corner, and stays openable. Only when every change is decided does the next step appear: the fix instructions, "Have Claude make the changes" when the review is editable, and an "Export PDF" request. The page as built sends nothing back; decisions travel in the fix instructions or the PDF request the engineer pastes into the chat. Record them as `status` on the findings, then make the PDF with scripts/export_pdf.py.
- **PDF**: `python3 scripts/export_pdf.py part.json review.json review.pdf --file "<file>" --desc "<part, material>"` makes a report with images (an overview and a close-up per finding with its faces lit, seen from the side that shows them, drawn in software, no graphics card needed), every finding with its fix and how you worked it out, the decisions, and the fix instructions. Offer it when the engineer wants something to send or keep; pass `--images` with a folder holding an `overview.png` you rendered for a rendered overview.

## Beyond the page
- **Looking at what you built**: before the page goes to the engineer, look at it with whatever shows you faithfully what it drew. Where no browser can open the page, `python3 scripts/sheet.py part.json review.json sheet.png` draws the overview and every change's close-up in software, its faces lit and seen from the side that shows them, so you can see that each change lights the right faces, cutting the part open as the page does when they are inside it. Where a browser exists, `node scripts/look.js review.html shots/ all` screenshots the overview and every change from one browser launch (or name the views: `overview 0 2`; `node scripts/look.js review.html out.png <change index>` takes one), printing for each whether it settled and any error the page raised, for you to fix before the engineer sees the page. It needs playwright-core and a Chromium it can launch (CHROME points at one; NODE_PATH at the node_modules holding playwright-core if it lives elsewhere). The page marks the stage `data-view="settled"` once a change's view has arrived and been checked, so whatever looks at it can wait for that rather than a fixed time; under reduced motion the camera goes straight to the frame it would end on. Anything you have that opens a page and shows you what it drew does as well. If nothing can look at the page where you are, say in the line after the receipt, in the engineer's words, that the page was not checked on screen, rather than guess.
- **Images, renders, other formats**: if you have a way to generate images or photoreal renders of the part, use it for what it does better, and keep the page as the review's home.

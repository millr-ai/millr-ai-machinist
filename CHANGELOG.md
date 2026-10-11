# Changelog

## 2.0.0 (2026-10-11)

First public release.

- Claude reviews a machined part as a senior machinist would. It plans how a shop would make the part, and wherever a step costs money, takes time or risks a bad part because of the design, it proposes the change to the CAD model or the drawing that removes it.
- Every change gives the exact value and location to set in the CAD, or the exact text to put on the drawing, and says what to check before making it. Millr never tells the shop how to make the part, and never states a price, a time or a lead time in days.
- Each change rates cost, lead time and risk as low, medium or high. The page shows the changes with at least one medium or high rating; the others stay in the review record.
- Each change shows how Claude worked it out: what it measured, what it looked up and what is its own judgment.
- The review page shows the engineer's own part in 3D. Opening a change lights its faces and moves the camera to them, cutting the part open when they are hidden. The page works on a phone, in light and dark themes, with a keyboard and with reduced motion, and prints the whole review.
- The engineer approves or ignores each change. Once all are decided, the page gives fix instructions, a PDF request and, when Claude can safely edit the part's source, "Have Claude make the changes".
- Send a revised part back and Claude checks which changes landed and what else changed.
- The page carries its 3D library (three.js r128) inside it and fetches nothing from the network.

Earlier versions (1.x) were private previews.

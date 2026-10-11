# What a finding carries

A finding is one change the engineer can make in their CAD model or on their drawing that makes the part cheaper to make, faster to get, or less likely to come back wrong: scrapped, reworked, or made to a reading of the drawing they did not mean. The changes come from building the part first (SKILL.md). What is a finding on this part, and what the right change is, are yours to judge; this file says what the page needs from you for each finding and what each field must hold.

## The fields
- **Title**: what it is, in about eight words (the builder warns past 52 characters). Each finding stands on its own: no "as well", "also", "again" or a trailing "too" that makes it read as an addition to another one.
- **Condition**: what you measured on the part or read on the drawing, with numbers: how many, what size, where.
- **Why**: one or two sentences on what the design as drawn makes the shop do, wait on, or risk getting wrong, in plain words an engineer follows without knowing the shop. That is the reason the change pays.
- **Fix**: the exact change to the CAD model or the drawing, with every value and location the engineer needs to make it, in their units, or the exact text to put on the drawing. The `edit` fields carry the same change for the fix instructions. The card shows `current` and `target` large and shortens anything past about 28 characters with an ellipsis, so lead with the value; the fix instructions carry them whole. A change that is text on the drawing rather than a feature uses `feature` "drawing notes" or "the part as a whole" and `where` the sheet or title block.
- **Faces**: the faces the change is about. The page lights exactly these and nothing else, so they are how the engineer finds the change on the part. A change to one feature lights that feature; a change that governs the whole part lights the whole part, and the page frames it whole.
- **Decision** (`decide`): safe to apply (it cannot change fit or function), or the engineer's call, with what would make the change wrong for them. The page prints "Safe to apply" or "Before you change it" above the note.
- **Basis**: how you worked it out, in your words: what you measured, what you looked up and where you looked, and what is your own judgment, kept apart. It carries what the shop would do at the step this change is about, not the whole plan. The page shows it under "How Claude worked it out", folded until opened; the fix instructions and the PDF carry it in full. The builder refuses a finding without one.
- **Flags**: a level, low, medium or high, for each of cost, lead time and risk (below). The page shows the ones at medium or high.

Blocking findings use the same fields without flags. They are reserved for geometry no machining process can produce as drawn, and their fix is the change to the design that makes it machinable; anything a shop can still machine, however costly, is an improvement.

## What the flags mean
Each flag is a question about what the change gives back, and each gets its own level. Answer each one on its own: what the change gives back on this part, at the quantity the engineer will order, if they take it. Whether they can take it belongs in "Before you change it", never in a level. When no one has said the quantity, say what you assumed in the basis.
- **Cost**: how much of the work and material that go into the part does the change take away? Low: little. Medium: enough to move the quote. High: enough to change how the shop would quote the job.
- **Lead time**: would the part arrive sooner? Low: it arrives when it would have anyway. Medium: the change takes out a step or a wait the shop would have to schedule around. High: the change takes out something the shop would have to wait on from outside.
- **Risk**: how much less likely is a part to come back wrong: scrapped, reworked, or made to a reading of the drawing the engineer did not mean? Low: the shop gets this right as a matter of course. Medium: as drawn, a part would come back wrong now and then. High: as drawn, the shop would expect a bad part in a batch.

The three are related, and on many changes all three are real: a part that comes back wrong is made again, which costs money and time. The levels are what tell them apart. Count each cost or delay once, where it starts: the cost and delay of remaking a bad part belong to its risk. A change with nothing at medium or higher stays in review.json and off the page; write it anyway, so the review keeps what you weighed. The levels are your judgment.

## The fix is a change to the design
The engineer controls two things: the CAD model and the drawing. The fix is a change to one of them, stated as the value to set or the text to put, ready to paste. A drawing defines the part, not how it is made, so the fix never tells the shop how to make the part, and what only the shop could change is not a finding. What the design as drawn makes the shop do belongs in the why: it is the reason the change pays.

The engineer may overrule a proposal in one word; they cannot act on an instruction to go and decide something. The edit target carries the same exact value or text.

## Language
Write to a design engineer in plain English, in their units and their words (inches first when the part is in inches): short sentences, one idea each, the everyday word over the trade word, and the value beside any code that stands for it. Be specific enough to act on without asking: which feature, where, what value. A figure appears in the condition, the why or the fix only when the engineer needs it to understand or to act; the working behind it belongs in the basis. Hyphens, never em or en dashes. Never call your own figures "verified" or "guaranteed"; say how you got each one.

Mark what matters: in the condition, the why and the fix, wrap the one or two phrases a scanning engineer must not miss in double asterisks (the measured value or the target value). The page and the PDF show them bold; the fix instructions drop the marks. More than two per block is noise, and titles take none.

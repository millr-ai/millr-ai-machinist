# Revising the CAD

A fix must never damage the engineer's CAD. For most engineers the right fix is exact fix instructions, followed by a revision check when they send the new version. Edit the CAD yourself only when the part is code or a connector lets you do it safely (2 and 3 below).

## 1. Everyone, on every surface: the fix instructions
The fix instructions carry the `edit` fields of every change: the feature, where it is (with the highlight on the page), the current value, the target value, and what to check afterward. Changing a value in their own CAD is quick for the engineer and keeps their feature history.

## 2. The part is code
Change the named parameter or feature in the code, regenerate, and export a new file next to the old one. Keep the original. Show the change as a diff.

## 3. A connector passes the test in references/connectors.md
You may apply fixes that are safe or approved by name:
- First make a copy: a new version, a branch or a saved copy. Never work in the original.
- One fix at a time. Change the feature or its parameter, not the resulting geometry. Touch nothing else.
- Check it: the model rebuilds, the changed feature reads its target, and nothing else changed.
- If any check fails, undo it (restore the version, discard the branch or copy) and give the fix instructions instead, saying what failed.
- Report what changed and where the revised part is. The engineer decides what gets merged or released.

## Never
- Never deliver an edited STEP, IGES or mesh as the fix. Those files have no feature history: an edit to them never reaches the engineer's model, so the engineer cannot carry it forward.
- Never apply a "your call" fix without the engineer's approval by name.
- Never overwrite or re-save the original file, version or workspace.

## Checking a revision
When the engineer sends the revised part, compare the two versions with whatever reads them where you are; Millr ships no comparison code. The check answers three things: which fixes landed, with the changed feature reading its target where it was; what else changed that the engineer did not ask for, allowing for the faces beside a fix that must move with it; and whether the part needs a new change where it changed. A finding the engineer ignored is listed as ignored, not as still open. The page shows the result as a revision check (`revision` in review.json): confirmed, still open, and other changes, each in one line.

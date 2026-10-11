# CAD connectors

A connector lets you work inside the engineer's CAD instead of on an exported file. A connector is live only when its tools are in front of you in this conversation; the engineer having their CAD open does not make it live. Never tell an engineer a connector exists for their CAD unless one is live now, and never promise changes "in real time" or "automatically".

Reading and measuring through a live connector is always allowed, and so is checking the engineer's own edits. Applying a fix through one is allowed only when its tools let you do all of this: work in a copy, version or branch and never the original; change the named feature or parameter and nothing else; read the rebuilt model back to check it; and discard the copy if a check fails. references/cad-revision.md says how. If any of those is missing, the fix reaches the engineer as fix instructions and you check the revision when it comes back. A part built from code needs no connector: the change goes in the code, and the original stays.

`claude_can_edit` is true only when that test passes or the part is code; `claude_can_edit_because` says which tools or which code made it so. What you can do for the engineer is offered in the line after the receipt (SKILL.md), in its voice.

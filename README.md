# Millr, the AI Machinist

Design for manufacturing (DFM) review of CNC machined parts, as a Claude skill and plugin from Millr Inc. (https://millr.ai).

Millr has Claude review a machined part the way a senior machinist would. Claude plans how a shop would make your part, finds what in your design drives its cost, its lead time and its risk of coming back wrong, and shows you every change worth making on an interactive 3D page of your own part. Each change is lit where it is on the part, with why it matters and the exact change to make in your CAD model or on your drawing. You approve or ignore each one. Then take the fix instructions to your CAD, have Claude make a PDF to keep or send, and send the revised part back to have the changes checked. Millr also answers machining and DFM questions in the chat.

It is built for mechanical engineers, and for the agents that draw parts for them, before a part goes to a machine shop. Every change is to your CAD or your drawing: Millr never tells your shop how to make the part, and never gives a price, a time or a lead time in days. It says which way they move.

## Install

Millr is one skill, `millr`. The skill upload and the plugin carry the same skill, so use the one route that fits where you work.

### claude.ai and Claude Desktop: upload the skill (every plan)

1. Download `millr.skill` from https://millr.ai or from this repository's [Releases](https://github.com/millr-ai/millr-ai-machinist/releases) page. It is a ZIP file of the skill folder.
2. In Claude, open **Customize > Skills**, click **+**, then **Create skill**, then **Upload a skill**, and choose `millr.skill`.
3. Millr appears in your skills list. Make sure it is turned on.

### claude.ai and Claude Desktop: add the plugin (Pro, Max, Team and Enterprise)

1. Open **Customize > Plugins**, click **Add**, then **Add marketplace**, then **Add from a repository**.
2. Enter `millr-ai/millr-ai-machinist`.
3. On the **Discover** tab, select Millr and click **Add**.

### Claude Code

In a Claude Code session (Claude Code 2.1.275 or later):

```
/plugin install millr --marketplace millr-ai/millr-ai-machinist
```

From your shell (Claude Code 2.1.292 or later):

```
claude plugin install millr --marketplace millr-ai/millr-ai-machinist
```

Or in two steps in a session, which also works on older versions:

```
/plugin marketplace add millr-ai/millr-ai-machinist
/plugin install millr@millr-ai
```

The marketplace is named `millr-ai`, so the plugin is `millr@millr-ai`. Claude Code does not update a marketplace you add yourself until you turn on auto-update: run `/plugin`, open the **Marketplaces** tab, select `millr-ai` and select **Enable auto-update**. To update by hand, run `claude plugin update millr@millr-ai`.

A skill or plugin you add in claude.ai also loads in Claude Code when you sign in with the same Claude account (Claude Code 2.1.273 or later). It does not sync when Claude Code signs in with an API key or runs on a cloud provider such as Amazon Bedrock.

## Requirements

- **Code execution and file creation must be on**, because Millr's scripts run in Claude's code environment. On Free, Pro and Max, it is in **Settings > Capabilities**. On Team and Enterprise, an owner turns on both **Code execution and file creation** and **Skills** in **Organization settings > Plugins & skills**, on the **Policy** tab. On Team, both are on by default.
- **Plans.** The skill works on every Claude plan: Free, Pro, Max, Team and Enterprise. The plugin needs a paid plan: Pro, Max, Team or Enterprise.
- **Network access for code execution.** To measure a STEP file, Claude may need to install a CAD library from a package manager such as PyPI. On Free, Pro and Max, network access is on. On Team and Enterprise, an owner sets it in **Organization settings > Capabilities**; access to package managers only is enough.
- **Team and Enterprise owners** also decide whether members can create and upload their own skills, and which plugin marketplaces members can add. An owner can provision Millr for everyone in the organization instead.
- **Claude Code on your computer.** The scripts run where Claude runs. `scripts/build_page.py` needs only Python 3. The PDF and the review sheet need numpy, matplotlib, reportlab and Pillow. Measuring a STEP file needs a CAD library. Checking the page in a browser needs Node.js with playwright-core and a Chromium. When something is missing, Claude can install it.
- **Viewing the page.** A current desktop or phone browser with WebGL shows the part in 3D. Without WebGL, the page says so, and the changes and fix instructions still work.

## What it reviews

Machined parts: geometry made by taking material away from stock, including the machined features of a casting, forging or weldment.

Export a STEP file from SolidWorks, Fusion, Onshape, Inventor, Creo or NX and attach it, with the drawing PDF if you have one. Using a CAD agent? Export a STEP from Zoo, or from the Onshape or Fusion model you built with Adam. CadQuery and build123d code work too.

- **IGES** works best exported as a solid.
- **Native files** such as SLDPRT, IPT or F3D, and Zoo's KCL code, need a STEP export first.
- **A mesh** such as STL gets a partial review, and Millr says what it could not judge.

Millr is not for sheet metal, PCBs, CAM, feeds and speeds, G-code, or molded or 3D-printed parts with no machined features, and it says so rather than guessing.

## Try it

Attach a part and ask in your own words. Claude loads Millr on its own when you bring it a machined part; to call it by name, say "review this with Millr". Five sample parts are in [`examples/`](examples/):

- "Is this ready for a shop?" with `examples/agent_bracket.step`
- "Why would this be expensive to machine?" with `examples/deep_pocket_block.step`
- "We keep scrapping this part. What should change in the design?" with `examples/twin_pocket_block.step`
- "Make this cheaper to machine without moving the holes." with `examples/drilled_riser_block.step`
- "Can this be done on a 3-axis mill?" with `examples/angled_port_block.step`

## What you get

While it works, Claude posts one short line per stage. When the review is done, it posts a receipt (the part, what was measured and how many changes it found) and the review page, `<part>_millr_review.html`. The review itself is on the page, not in the chat.

- Opening a change lights its faces on your part and turns the camera to them, cutting the part open when they are hidden.
- Each change shows what was measured, the change (now, and change to), why it matters, what to check before you change it, and how Claude worked it out.
- Each change rates cost, lead time and risk as low, medium or high. The page shows the changes with at least one medium or high.
- You choose **Fix this** or **Ignore** for each change. Once every change is decided, the page gives:
  - **Fix instructions**: exact instructions for whoever edits the CAD, with what to check after each change.
  - **Export PDF**: a request to paste into the chat, to have Claude make a PDF to keep or send, with your decisions, images of the part and the fix instructions.
  - **Have Claude make the changes**, only when Claude can safely edit the part's source: the part is code, or Claude works in your CAD through a connector that edits a copy and checks the result.
- Paste the fix instructions or the PDF request into the chat and Claude records your decisions.
- Send the revised part back and Claude checks which changes landed and what else changed.

## Privacy, and what it runs

- **Millr never receives your part or your drawing.** Millr runs no server: the review runs inside your Claude conversation or your Claude Code session, under your Claude account's own terms, and Millr collects no data. The privacy policy is at https://millr.ai/privacy.html.
- To measure the part, Claude uses a CAD library in its own workspace, installing one if it must (see [`skills/millr/NOTICE.md`](skills/millr/NOTICE.md)).
- Millr's scripts build the review page and the PDF from files on disk. The page carries everything it needs inside it, including its 3D library, the unmodified three.js r128 release, and fetches nothing from the network.
- Before you see the page, Claude may draw it in software (`scripts/sheet.py`) or open it in a headless Chromium where one is installed (`scripts/look.js`). Both run where Claude runs and send nothing.

## Troubleshooting

- **Claude answered without Millr.** Check that Millr is turned on in **Customize > Skills**, then say "review this with Millr".
- **No Skills section, or skills are grayed out.** Code execution is off. Turn on **Code execution and file creation** in **Settings > Capabilities** (Free, Pro, Max), or ask your owner to turn it on in **Organization settings > Plugins & skills** (Team, Enterprise).
- **No "Create skill" or "Upload a skill" option.** On Team and Enterprise, an owner can turn off skills that members create, and on Enterprise a custom role may leave out the Create skills capability. Ask your owner to turn it on, or to provision Millr for the organization.
- **Claude refuses the repository when you add the marketplace.** Your organization limits which marketplaces members can add. Ask an owner to allow `millr-ai/millr-ai-machinist`.
- **Claude says it cannot measure the part.** Code execution could not install a CAD library. On Team or Enterprise, ask your owner to allow network access to package managers in **Organization settings > Capabilities**, then try again.
- **A native file such as SLDPRT, IPT or F3D, or Zoo's KCL code.** Export a STEP from your CAD or from Zoo, and attach that.
- **Only an IGES file.** Attach it, exported as a solid if your CAD offers that; a STEP is better still.
- **A mesh such as STL.** Millr reviews what it can and says what it could not judge; a STEP gives a full review.
- **The 3D view does not appear.** The changes and fix instructions still work; open the page in a current desktop browser to see the part.

## What is in this repository

- `skills/millr/`: the skill (`SKILL.md`, `references/`, `assets/`, `scripts/`, `LICENSE.txt`, `NOTICE.md`). `millr.skill` is this folder as a ZIP file.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`: the plugin, and the `millr-ai` marketplace that lists it.
- `examples/`: five sample parts.
- `CHANGELOG.md`, `SECURITY.md`, `LICENSE`.

## Support

Email hello@millr.ai or visit https://millr.ai/support.html. To report a security problem, see [`SECURITY.md`](SECURITY.md).

## License

PolyForm Shield 1.0.0, copyright (c) 2026 Millr Inc. (see [`LICENSE`](LICENSE)): use, copy, modify and share it for any purpose except providing a product that competes with Millr. The skill folder carries the same license as `skills/millr/LICENSE.txt`. Third-party notices: [`skills/millr/NOTICE.md`](skills/millr/NOTICE.md).

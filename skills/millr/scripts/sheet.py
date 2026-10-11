#!/usr/bin/env python3
"""Look at a review without a browser: one image with the overview and every change's close-up with its faces lit,
seen from the side that shows them, rendered in software the way the PDF is.

    python3 scripts/sheet.py part.json review.json sheet.png

Use it where no browser can open the page: it shows whether each change lights the right faces.
Faces inside the part are shown cut open, as the page shows them; the camera move is the page's alone."""
import sys, os, json, io
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from export_pdf import view_rot, render, zoom_for, view_for, upright, shown, empty_part
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    sys.exit(f'sheet.py needs numpy, matplotlib, reportlab and pillow ({e}); install them where you are and run it again')

def main():
    if len(sys.argv) < 4: sys.exit(__doc__)
    part = json.load(open(sys.argv[1]))
    if empty_part(part): sys.exit(f'error: {empty_part(part)}; the sheet was not drawn')
    part = upright(part); rev = json.load(open(sys.argv[2])); out = sys.argv[3]
    allf = [('Cannot be machined as drawn', f) for f in rev.get('blocking', [])] + [('Change', f) for f in rev.get('improvements', []) if shown(f)]
    nf = len(part['faces']); W, H = 800, 500
    tiles = [('Overview', render(part, [i for _, f in allf if len(f.get('faces', [])) < nf / 2 for i in f.get('faces', [])], size=(W, H))[0])]
    for n, (kind, f) in enumerate(allf, 1):
        az, el, cut = view_for(part, f['faces']) if f.get('faces') else (-135, 38, None)
        R = view_rot(az, el)
        png, _ = render(part, f.get('faces', []), zoom=zoom_for(part, f['faces'], R) if f.get('faces') else None, size=(W, H), az=az, el=el, cut=cut)
        tiles.append((f'{n}. {f.get("title", "")}', png))
    cols = 2; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * W, rows * (H + 28)), 'white'); d = ImageDraw.Draw(sheet)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    except Exception: font = ImageFont.load_default()
    for k, (title, png) in enumerate(tiles):
        x, y = (k % cols) * W, (k // cols) * (H + 28)
        sheet.paste(Image.open(io.BytesIO(png)).convert('RGB').resize((W, H)), (x, y + 28)); d.text((x + 10, y + 6), title, fill='#141517', font=font)
    sheet.save(out); print(f'wrote {out}: the overview and {len(tiles) - 1} change(s)')

if __name__ == '__main__':
    main()

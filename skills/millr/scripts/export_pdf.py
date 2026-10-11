"""Export a Millr review as a PDF with images and fix instructions.

    python3 export_pdf.py part.json review.json review.pdf [--file "part.step"] [--desc "part, material"] [--images frames_dir]

Images: if --images points at a folder holding an overview.png you rendered, it is used for the overview; otherwise the part
is drawn in software (no graphics card needed): gray part, highlighted faces in Millr orange, one close-up per finding."""
import sys, os, json, base64, argparse, datetime, io
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_page import empty_part
try:
    import numpy as np
    from PIL import Image as PILImage
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
except ImportError as e:
    sys.exit(f'export_pdf.py needs numpy, matplotlib, reportlab and pillow ({e}); install them where you are and run it again')
ORANGE = '#EC6636'
import re as _re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT, FONT_B = 'Helvetica', 'Helvetica-Bold'
for _d in ('/usr/share/fonts/truetype/dejavu', '/usr/share/fonts/dejavu', '/Library/Fonts', 'C:/Windows/Fonts'):
    if os.path.exists(os.path.join(_d, 'DejaVuSans.ttf')) and os.path.exists(os.path.join(_d, 'DejaVuSans-Bold.ttf')):
        pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(_d, 'DejaVuSans.ttf'))); pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', os.path.join(_d, 'DejaVuSans-Bold.ttf')))
        from reportlab.pdfbase.pdfmetrics import registerFontFamily; registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold', italic='DejaVuSans', boldItalic='DejaVuSans-Bold')
        FONT, FONT_B = 'DejaVuSans', 'DejaVuSans-Bold'; break

def flag_words(f):
    """The flags at medium or high, grouped by level as the page shows them ("High risk; medium cost and lead time")."""
    x = f.get('flags') or {}
    keys = ('cost', 'lead time', 'risk'); out = []
    for lv in ('high', 'medium'):
        ks = [k for k in keys if str(x.get(k, '')).lower() == lv]
        if ks: out.append(f'{lv} ' + (ks[0] if len(ks) == 1 else ', '.join(ks[:-1]) + ' and ' + ks[-1]))
    return '; '.join(out).capitalize()

def esc(s):
    s = str(s).replace('\u03bc', '\u00b5')   # the Greek mu has no glyph in the built-in PDF fonts; the micro sign does (a system TrueType font, when found, has both)
    if FONT == 'Helvetica': s = s.replace('\u00b3', '3').replace('\u00b2', '2')   # superscripts have no glyph in the built-in fonts either
    s = str(s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return _re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)   # the author's highlights become bold on paper

def mesh(part):
    p, i = part['positions'], part['indices']
    P = np.frombuffer(base64.b64decode(p), dtype='<f4').reshape(-1, 3) if isinstance(p, str) else np.array(p, dtype=float).reshape(-1, 3)
    I = np.frombuffer(base64.b64decode(i), dtype='<u4').reshape(-1, 3) if isinstance(i, str) else np.array(i, dtype=int).reshape(-1, 3)
    return P, I

def upright(part):
    """A Y-up export stood up as it is in the engineer's CAD, the way the page stands it: (x, y, z) becomes (x, -z, y), with the faces'
    boxes and axes. A Z-up part is returned as it is."""
    if str(part.get('up', 'z')).lower() != 'y':
        return part
    P, I = mesh(part); P = np.stack([P[:, 0], -P[:, 2], P[:, 1]], axis=1)
    faces = []
    for f in part['faces']:
        g = dict(f)
        if len(f.get('box') or []) == 6: b = f['box']; g['box'] = [b[0], -b[5], b[1], b[3], -b[2], b[4]]
        if len(f.get('axis') or []) == 6: a = f['axis']; g['axis'] = [a[0], -a[2], a[1], a[3], -a[5], a[4]]
        faces.append(g)
    return dict(part, positions=P.ravel().tolist(), indices=I.ravel().tolist(), faces=faces, up='z')

def split_long(tri, hi, L, levels=4):
    """Split triangles longer than L into four, a few times over: the painter's algorithm sorts whole triangles by depth, and a long
    sliver (a CAD library's tessellation of a big flat face) is drawn over or under its neighbors as a whole."""
    for _ in range(levels):
        e = np.max(np.linalg.norm(tri - np.roll(tri, 1, axis=1), axis=2), axis=1); big = e > L
        if not big.any(): break
        a, b, c = tri[big, 0], tri[big, 1], tri[big, 2]; ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        new = np.concatenate([np.stack(t, axis=1) for t in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))])
        tri = np.concatenate([tri[~big], new]); hi = np.concatenate([hi[~big], np.tile(hi[big], 4)])
    return tri, hi

def view_rot(az, el):
    az, el = np.deg2rad(az), np.deg2rad(el)
    cz, sz, ce, se = np.cos(az), np.sin(az), np.cos(el), np.sin(el)
    return np.array([[cz, sz, 0], [-sz * se, cz * se, ce], [sz * ce, -cz * ce, se]])   # rows: screen x, screen y, depth toward viewer

def render(part, highlight, zoom=None, size=(1600, 1000), az=-135, el=38, cut=None):
    """Draw the mesh from a viewpoint `az` degrees around and `el` above (the viewer stands at (sin az cos el, -cos az cos el, sin el));
    painter's algorithm; the highlighted faces in Millr orange; returns PNG bytes and the view rotation. With `cut`, the part is cut open
    as the page cuts it: everything nearer the viewer than that depth is left out, except the highlighted faces."""
    P, I = mesh(part); tri = P[I]                                   # (n, 3, 3), part coordinates (Z up)
    hi = np.zeros(len(I), bool)
    for fid in highlight:
        f = part['faces'][fid]; hi[f['tris'][0]:f['tris'][1]] = True
    tri, hi = split_long(tri, hi, np.linalg.norm(P.max(axis=0) - P.min(axis=0)) / 40)
    R = view_rot(az, el)
    V = tri @ R.T
    if cut is not None:
        keep = hi | (V[..., 2].mean(axis=1) <= cut); V, tri, hi = V[keep], tri[keep], hi[keep]
    x, y, d = V[..., 0], V[..., 1], V[..., 2]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nn = np.linalg.norm(n, axis=1) + 1e-12
    light = np.array([0.4, 0.5, 0.8]); shade = 0.45 + 0.55 * np.abs((n / nn[:, None]) @ light)
    order = np.argsort(d.mean(axis=1))                            # far first
    fig = plt.figure(figsize=(size[0] / 200, size[1] / 200), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    base = np.array([0.72, 0.74, 0.76]); orange = np.array([0.925, 0.4, 0.21])
    cols = np.where(hi[:, None], orange * (0.75 + 0.25 * shade[:, None]), base * shade[:, None])
    polys = np.stack([x, y], axis=-1)
    if zoom is not None:
        cx, cy, r = zoom; ax.set_xlim(cx - r, cx + r); ax.set_ylim(cy - r, cy + r)
    else:
        ax.set_xlim(x.min(), x.max()); ax.set_ylim(y.min(), y.max())
    ax.add_collection(PolyCollection(polys[order], facecolors=cols[order], edgecolors='none', antialiased=False), autolim=False)
    ax.set_aspect('equal'); buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=200); plt.close(fig); return buf.getvalue(), R

VIEWS = [(az, el) for el in (35, -25) for az in (-135, -45, 45, 135)] + [(az, 10) for az in (-180, -90, 0, 90)]

def best_view(part, faces):
    """The viewpoint that shows the most of the lit faces: every candidate is scored by the lit area facing it, and the best four are
    drawn small to count what is really seen, so a face hidden behind the part does not win."""
    P, I = mesh(part); tri = P[I]
    sel = np.zeros(len(I), bool)
    for fid in faces:
        f = part['faces'][fid]; sel[f['tris'][0]:f['tris'][1]] = True
    t = tri[sel]; n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]) / 2       # area-weighted normals of the lit triangles
    def toward(az, el):
        a, e = np.deg2rad(az), np.deg2rad(el); return np.array([np.sin(a) * np.cos(e), -np.cos(a) * np.cos(e), np.sin(e)])
    top = sorted(VIEWS, key=lambda v: -np.clip(n @ toward(*v), 0, None).sum())[:4]
    def seen(v):
        return lit_px(render(part, faces, size=(160, 100), az=v[0], el=v[1])[0])
    return max(top, key=seen)

def lit_px(png):
    px = np.asarray(PILImage.open(io.BytesIO(png)).convert('RGB')).astype(int)
    return int(((px[..., 0] > 150) & (px[..., 1] < 130) & (px[..., 2] < 90)).sum())

def view_for(part, faces):
    """The view a change's close-up is drawn from, as the page chooses it: the side that shows the most of its lit faces, and the part cut
    open through their middle when the part itself hides them (a bore, a hole, a chamber). Returns az, el and the cut depth or None."""
    az, el = best_view(part, faces)
    R = view_rot(az, el)
    P, I = mesh(part); box = np.array([part['faces'][i]['box'] for i in faces if 'box' in part['faces'][i]])
    if not len(box):
        return az, el, None
    mid = (box[:, :3].min(axis=0) + box[:, 3:].max(axis=0)) / 2; depth = float(mid @ R[2])
    plain = lit_px(render(part, faces, size=(160, 100), az=az, el=el)[0])
    opened = lit_px(render(part, faces, size=(160, 100), az=az, el=el, cut=depth)[0])
    return az, el, (depth if plain < 0.1 * opened else None)   # only when the part hides them, as the page does

def zoom_for(part, faces, R):
    """Frame the faces with the part around them, as the page does: their box, and at least four tenths of the part's size."""
    nf = len(part['faces'])
    if len(faces) >= nf / 2: return None                            # the faces are the part (a material note): the whole part
    b = np.array([part['faces'][f]['box'] for f in faces]); lo, hi = b[:, :3].min(0), b[:, 3:].max(0)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]) @ R.T
    P, _ = mesh(part); whole = (P @ R.T)[:, :2]; span = (whole.max(0) - whole.min(0)).max()
    c = corners.mean(0); r = max(0.4 * span, 1.6 * np.abs(corners[:, :2] - c[:2]).max())
    return (c[0], c[1], r)

def shown(f):   # the page, the PDF and the sheet show a change with something at medium or high; the rest stay in review.json
    fl = f.get('flags') or {}
    return isinstance(fl, dict) and any(str(v).lower() in ('medium', 'high') for v in fl.values())

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('part'); ap.add_argument('review'); ap.add_argument('out')
    ap.add_argument('--file', default=''); ap.add_argument('--desc', default=''); ap.add_argument('--images', default='')
    a = ap.parse_args(); part = json.load(open(a.part))
    if empty_part(part): sys.exit(f'error: {empty_part(part)}; the PDF was not made')
    part = upright(part); rev = json.load(open(a.review)); name = a.file or rev.get('file', 'part')
    blk, imp = rev.get('blocking', []), [f for f in rev.get('improvements', []) if shown(f)]
    ss = getSampleStyleSheet()   # the page's scale on paper: title 22, heading 15, body 10.5, fix 11.5 semibold, notes 9
    H1 = ParagraphStyle('h1', parent=ss['Title'], fontName=FONT_B, fontSize=22, leading=27, alignment=0, spaceAfter=4)
    H2 = ParagraphStyle('h2', parent=ss['Heading2'], fontName=FONT_B, fontSize=15, leading=19, spaceBefore=12, spaceAfter=6); B = ParagraphStyle('b', parent=ss['BodyText'], fontName=FONT, fontSize=10.5, leading=15)
    S = ParagraphStyle('s', parent=B, fontSize=9, leading=12.5, textColor=colors.HexColor('#5E636B'))
    T = ParagraphStyle('t', parent=B, fontSize=9, leading=12)
    FIX = ParagraphStyle('fix', parent=B, fontName=FONT_B, fontSize=11.5, leading=16, backColor=colors.HexColor('#FDEBE3'), borderPadding=(7, 9, 7, 9), spaceBefore=8, spaceAfter=12)
    doc = SimpleDocTemplate(a.out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm, title=f'Millr, the AI Machinist: {name}')
    WORDS = ['No', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']; nw = lambda n: WORDS[n] if n < len(WORDS) else str(n)
    verdict = 'This part cannot be machined as drawn' if blk else (f'{nw(len(imp))} change{"s" if len(imp) != 1 else ""} before a shop sees this' if imp else 'Nothing to change before a shop sees this')
    story = [Paragraph(esc(verdict), H1), Paragraph(f'{esc(name)}{" &middot; " + esc(a.desc) if a.desc else ""} &middot; {datetime.date.today().isoformat()}', S), Spacer(1, 6)]
    allf = [('Cannot be machined as drawn', f) for f in blk] + [('Change', f) for f in imp]
    ov = None
    if a.images and os.path.exists(os.path.join(a.images, 'overview.png')): ov = open(os.path.join(a.images, 'overview.png'), 'rb').read()
    nf = len(part['faces']); png, R = render(part, [i for _, f in allf if len(f.get('faces', [])) < nf / 2 for i in f.get('faces', [])])   # a part-wide finding (a material note) is not lit in the overview
    story += [Image(io.BytesIO(ov or png), width=170 * mm, height=106 * mm, kind='proportional'), Spacer(1, 8)]
    if allf:
        rows = [['', 'Change', 'Flags', 'Decision']]
        for n, (kind, f) in enumerate(allf, 1):
            st = f.get('status', ''); dec = {'approved': 'Approved', 'ignored': 'Ignored'}.get(st, 'Undecided')
            rows.append([str(n), Paragraph(esc(f['title']), B), Paragraph(esc(flag_words(f) or kind), T), dec])
        t = Table(rows, colWidths=[8 * mm, 86 * mm, 50 * mm, 26 * mm]); t.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTNAME', (0, 0), (-1, 0), FONT_B), ('FONTSIZE', (0, 0), (-1, -1), 9), ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor(ORANGE)), ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
        story += [t]
    for n, (kind, f) in enumerate(allf, 1):
        story.append(PageBreak())
        st = f.get('status', ''); tag = {'approved': ' (approved)', 'ignored': ' (ignored)'}.get(st, '')
        story += [Paragraph(f'{n}. {esc(f["title"])}{tag}', H2), Paragraph(f'<b>{esc(kind)}</b>{" &middot; " + esc(flag_words(f)) if flag_words(f) else ""}', S), Paragraph(esc(f['condition']), B), Spacer(1, 6)]
        if f.get('faces'):
            az, el, cut = view_for(part, f['faces']); Rv = view_rot(az, el)
            zpng, _ = render(part, f['faces'], zoom=zoom_for(part, f['faces'], Rv), az=az, el=el, cut=cut)
            story += [Image(io.BytesIO(zpng), width=120 * mm, height=75 * mm, kind='proportional')]
        story.append(Spacer(1, 6))
        story += [Paragraph(f'<b>The fix:</b> {esc(f["fix"])}', FIX), Paragraph(f'<b>Why it matters:</b> {esc(f["why"])}', B)]
        d = f['decide']; story.append(Paragraph(f'<b>{"Safe to apply" if d["safe"] else "Before you change it"}:</b> {esc(d["note"])}', B))
        if str(f.get('basis') or '').strip(): story.append(Paragraph(f"<b>How Claude worked it out:</b> {esc(f['basis'])}", B))
    if allf:
        story += [PageBreak(), Paragraph('Fix instructions', H2), Paragraph('Make each change in the part\'s source (the CAD model, or the code that builds it), not in an exported file (STEP, IGES or a mesh). Work in a copy, a new version or a branch. Change only the named feature, one at a time.', B), Spacer(1, 6)]
        for n, (kind, f) in enumerate(allf, 1):
            if f.get('status') == 'ignored': story.append(Paragraph(f'{n}. {esc(f["title"])}: ignored; no change.', B)); continue
            und = '' if f.get('status') == 'approved' else ' (undecided)'
            e = f['edit']; story.append(KeepTogether([Paragraph(f'<b>{n}. {esc(f["title"])}</b>{und}', B), Paragraph(f'Feature: {esc(e["feature"])}<br/>Where: {esc(e["where"])}<br/>Now: {esc(e["current"])}<br/>Change to: {esc(e["target"])}<br/>Before changing: {"safe to apply; " if f["decide"]["safe"] else ""}{esc(f["decide"]["note"])}<br/>After changing: {esc(e["check"])}', B), Spacer(1, 6)]))
    story.append(Paragraph('Reviewed with Millr, the AI Machinist. Measurements come from the part; each change says how Claude worked it out; the decisions are the engineer\'s.', S))
    doc.build(story); print(f'wrote {a.out} ({os.path.getsize(a.out)/1e6:.1f} MB)')

if __name__ == '__main__':
    main()

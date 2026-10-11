"""Build the review page from a part and a review.

    python3 build_page.py part.json review.json review.html --file "part.step" --desc "part, material" --credit "who the part file is from, when it is not the engineer's own; else empty"

Checks the review first and stops with a plain message if something would break the page or mislead the
engineer. Language issues are printed as warnings so you can fix the wording."""
import sys, re, os, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
FLAGS = {'cost', 'lead time', 'risk'}
LEVELS = ('low', 'medium', 'high')
NEED = ['title', 'condition', 'why', 'fix', 'faces', 'decide', 'basis', 'edit']
EDIT = ['feature', 'where', 'current', 'target', 'check']

def empty_part(part):
    """Why the part cannot be shown (no faces, no triangles, or no face with any triangles), or None when it can. The page, the PDF
    and the review sheet all refuse such a part: it would show an empty view and review nothing."""
    def has_tris(f):
        t = f.get('tris') if isinstance(f, dict) else None
        return isinstance(t, (list, tuple)) and len(t) == 2 and all(isinstance(x, int) for x in t) and t[1] > t[0]
    faces = part.get('faces') or []
    if not faces: empty = 'no faces'
    elif not (part.get('positions') and part.get('indices')): empty = 'no triangles'
    elif not any(has_tris(f) for f in faces): empty = 'no face with any triangles'
    else: return None
    return (f'the part file has {empty}, so there is no part to show or review. If the file holds surfaces but no solid, sew them into a solid '
            'and measure it again; if nothing you have can read it, tell the engineer what could not be read and which export would let you read all of it')

def check(part, review):
    errors, warnings, kept_off = [], [], []
    n = len(part.get('faces') or [])
    for k in ('positions', 'indices', 'faces'):
        if k not in part: errors.append(f'part file is missing "{k}"')
    empty = None if errors else empty_part(part)
    if empty:
        return [empty], []
    if not errors:
        np_ = len(part['positions']) // 3 if isinstance(part['positions'], list) else None
        ni = len(part['indices']) // 3 if isinstance(part['indices'], list) else None
        if isinstance(part['positions'], list) and len(part['positions']) % 3: errors.append('positions must be x, y, z triples')
        if isinstance(part['indices'], list) and len(part['indices']) % 3: errors.append('indices must come in triangles of three')
        if ni is not None and np_ is not None and part['indices'] and max(part['indices']) >= np_: errors.append('an index points past the last vertex')
        for f in part['faces']:
            if 'id' not in f or 'tris' not in f: errors.append('every face needs "id" and "tris" [first, end]'); break
            if ni is not None and (f['tris'][0] < 0 or f['tris'][1] > ni): errors.append(f'face {f.get("id")} has a triangle range outside the mesh'); break
        ids = [f.get('id') for f in part['faces']]
        if ids != list(range(len(ids))): errors.append('face ids must be 0, 1, 2, ... in the order the faces are listed (a finding names a face by its position in this list)')
        rng = sorted((f['tris'][0], f['tris'][1]) for f in part['faces'] if 'tris' in f)
        if rng:
            gaps = sum(1 for a, b in zip(rng, rng[1:]) if b[0] == a[1] + 1); overlaps = sum(1 for a, b in zip(rng, rng[1:]) if b[0] < a[1])
            if gaps and gaps >= len(rng) // 2: warnings.append('most face ranges stop one triangle short of the next face: "tris" is [first, end] with the end exclusive (the triangle after the last), so an inclusive last index leaves one triangle of every face unlit')
            if overlaps: errors.append(f'{overlaps} face triangle ranges overlap; each triangle belongs to exactly one face')
            if ni is not None and rng[-1][1] < ni and not gaps: warnings.append(f'{ni - rng[-1][1]} triangles belong to no face; they render but can never be lit')
    if str(part.get('up', 'z')).lower() not in ('y', 'z'): errors.append('part "up" must be "z" or "y" (the file\'s up axis as the part stands in the engineer\'s CAD)')
    for group in ('blocking', 'improvements'):
        for i, f in enumerate(review.get(group, [])):
            at = f'{group}[{i}] "{f.get("title", "?")}"'
            for k in NEED:
                if k not in f: errors.append(f'{at}: missing "{k}"')
            bad = [x for x in f.get('faces', []) if not isinstance(x, int) or x < 0 or x >= n]
            if bad: errors.append(f'{at}: face ids {bad} do not exist (the part has faces 0 to {n - 1})')
            if not f.get('faces'): errors.append(f'{at}: no faces to highlight')
            d = f.get('decide', {})
            if not isinstance(d.get('safe'), bool) or not d.get('note'): errors.append(f'{at}: "decide" needs "safe" (true or false) and a "note"')
            for k in EDIT:
                if k not in f.get('edit', {}): errors.append(f'{at}: "edit" is missing "{k}"')
            flags = f.get('flags') or {}
            if group == 'blocking':
                if flags: errors.append(f'{at}: blocking findings are not flagged')
            elif not flags: errors.append(f'{at}: "flags" must give each of cost, lead time and risk a level, low, medium or high')
            elif not isinstance(flags, dict): errors.append(f'{at}: "flags" must give each of cost, lead time and risk a level, low, medium or high')
            else:
                unknown = [x for x in flags if x not in FLAGS]
                if unknown: errors.append(f'{at}: unknown flags {unknown} (use cost, lead time, risk)')
                bad = {k: v for k, v in flags.items() if str(v).lower() not in LEVELS}
                if bad: errors.append(f'{at}: levels must be low, medium or high, not {bad}')
                missing = sorted(FLAGS - set(flags))
                if missing: warnings.append(f'{at}: no level for {", ".join(missing)}; it shows as low')
                if not unknown and not bad and not any(str(v).lower() in ('medium', 'high') for v in flags.values()): kept_off.append(at)
            if 'basis' in f and (not isinstance(f['basis'], str) or not f['basis'].strip()): errors.append(f'{at}: "basis" must say how you worked it out, in words')
            if 'sources' in f: errors.append(f'{at}: "sources" is not a field; how you worked it out goes in "basis", in words')
            text = ' '.join([str(f.get(k, '')) for k in ('title', 'condition', 'why', 'fix', 'basis')] + [str(d.get('note', ''))] + [str(v) for v in (f.get('edit') or {}).values()])
            if re.search('[' + chr(0x2013) + chr(0x2014) + ']', text): warnings.append(f'{at}: uses an en or em dash; use a colon, comma or hyphen')
            if re.search(r'\b(verified|guaranteed|certified)\b', text, re.I): warnings.append(f'{at}: says verified, guaranteed or certified; say how you worked it out instead')
            if re.search(r'[$\u20ac\u00a3]\s?\d|\b\d+\s?(usd|dollars|euros)\b', text, re.I): warnings.append(f'{at}: states a price; give direction only')
            if re.search(r'\b\d+(\.\d+)?\s?(hours?|hrs?|days?|weeks?|wks?|months?)\b|\b(a|one|two|three|four|five|six) (hours?|days?|weeks?|months?)\b', text, re.I): warnings.append(f'{at}: states a time; say which way lead time moves instead')
            if len(str(f.get('title', ''))) > 52: warnings.append(f'{at}: title is longer than 52 characters (about eight words); it can wrap to three lines on a narrow screen')
            if re.search(r"\b(as well|also|again|another)\b|\btoo\s*$", str(f.get('title', '')), re.I): warnings.append(f'{at}: the title reads as an addition to another finding ("as well", "also", a trailing "too"); each finding stands on its own')
            for k in ('condition', 'why', 'fix'):
                n_hl = len(re.findall(r'\*\*[^*]+\*\*', str(f.get(k, ''))))
                if n_hl > 2: warnings.append(f'{at}: "{k}" has {n_hl} highlights; one or two is the limit, or nothing stands out')
            if '**' in str(f.get('title', '')): warnings.append(f'{at}: no highlights in titles')
            # a fix must carry an exact value or an exact note; an instruction to go and decide is not a fix
            txt = str(f.get('fix', '')); tgt = str(f.get('edit', {}).get('target', ''))
            exact = re.search(r"\d", txt) or re.search(r'[\"\u201c].+?[\"\u201d]', txt)
            open_ended = re.search(r"\b(as needed|as required|appropriate|suitable|the \w+ you need)\b", txt, re.I)
            to_decide = re.search(r"\b(name the|naming the|add a tolerance|choose a|pick a|specify a|select a)\b", txt, re.I)
            if (open_ended or to_decide) and not exact: errors.append(f'{at}: the fix tells the engineer to decide something ("{(open_ended or to_decide).group(0)}") and states no exact value or note; write the value or the text to put, or propose one')
            elif open_ended: warnings.append(f'{at}: part of the fix leaves the engineer to decide ("{open_ended.group(0)}"); propose the value instead')
            elif not exact: warnings.append(f'{at}: the fix states no value or quoted note; if it is a removal or a note, that is fine; otherwise make it exact')
            if not (re.search(r'\d', tgt) or re.search(r'[\"\u201c].+?[\"\u201d]', tgt)): warnings.append(f'{at}: edit.target has no value or quoted text; the target must be exact')
    if not review.get('file'): warnings.append('review has no "file" name')
    if 'claude_can_edit' in review and not isinstance(review['claude_can_edit'], bool): errors.append('"claude_can_edit" must be true or false')
    if review.get('claude_can_edit') and not review.get('claude_can_edit_because'): errors.append('"claude_can_edit" is true but "claude_can_edit_because" does not say why (a code-built part, or a connector that passes the test in connectors.md)')
    if kept_off: warnings.append(f'note: {len(kept_off)} change(s) have nothing at medium or higher; they stay in review.json and off the page: ' + '; '.join(kept_off))
    return errors, warnings

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('part'); ap.add_argument('review'); ap.add_argument('out')
    ap.add_argument('--file', default=''); ap.add_argument('--desc', default=''); ap.add_argument('--credit', default='')
    a = ap.parse_args()
    part = json.load(open(a.part)); review = json.load(open(a.review))
    errors, warnings = check(part, review)
    for w in warnings: print(w if w.startswith('note:') else 'warning: ' + w)
    if errors:
        for e in errors: print('error:', e)
        sys.exit(f'{len(errors)} problem(s); the page was not built')
    review['file'] = review.get('file') or a.file or 'part'   # the fix instructions and the PDF request name the part
    esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    h = open(os.path.join(HERE, '..', 'assets', 'shell.html'), encoding='utf-8').read()
    safe = lambda obj, **k: json.dumps(obj, **k).replace('<', '\\u003c')   # no '<' inside the page's script, so neither '</script>' nor '<!--' in the text can end or swallow it
    fill = {'__PART__': safe(part, separators=(',', ':')), '__REVIEW__': safe(review, ensure_ascii=False),
            '__FILE__': esc(a.file or review['file']), '__DESC__': esc(a.desc), '__CREDIT__': esc(a.credit),
            '__THREE__': open(os.path.join(HERE, '..', 'assets', 'three.min.js'), encoding='utf-8').read()}   # the 3D library travels inside the page, so it opens anywhere and fetches nothing
    h = re.sub(r'__(PART|REVIEW|FILE|DESC|CREDIT|THREE)__', lambda m: fill[m.group(0)], h)   # one pass: what is filled in is never searched for placeholders again
    open(a.out, 'w', encoding='utf-8').write(h)
    print(f'wrote {a.out} ({os.path.getsize(a.out) / 1e6:.1f} MB)' + (' - over 5 MB, which is slow to open: tessellate the part more coarsely where it is flat, or store positions and indices as base64' if os.path.getsize(a.out) > 5e6 else ''))

if __name__ == '__main__':
    main()

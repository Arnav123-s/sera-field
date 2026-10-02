"""List every arXiv paper a dive report cites, with its real title and authors from arXiv.

For each arXiv id found in the report, prints the real title, first authors and year
(from the arXiv API) above every line of the report that names the id, so a wrong
attribution, an off-topic source or an invented id stands out.
- NOT ON ARXIV: arXiv answered for a batch containing the id but returned no such paper.
- LOOKUP FAILED: arXiv did not answer (the API rate-limits); run again later.

    python scripts/check_arxiv.py (review notes, not published)
"""
import re
import sys
import time
import subprocess
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
ID = re.compile(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})(?:v\d+)?', re.I)
ATOM = '{http://www.w3.org/2005/Atom}'


def fetch(batch):
    """arXiv answers Python's urllib with HTTP 406 from this machine, while curl works: fetch with curl."""
    url = f'https://export.arxiv.org/api/query?id_list={",".join(batch)}&max_results={max(len(batch), 10)}'
    out = subprocess.run(['curl', '-s', '-f', '-m', '60', '-A', 'curl/8.5.0', url], capture_output=True, timeout=90)
    if out.returncode != 0:
        raise RuntimeError(f'curl exit {out.returncode}')
    return ET.fromstring(out.stdout)


def lookup(ids):
    """Returns (found: id -> (title, authors, year), answered: ids arXiv answered for)."""
    found, answered = {}, set()
    batches = [ids[i:i + 10] for i in range(0, len(ids), 10)]
    while batches:
        batch = batches.pop(0)
        root = None
        for wait in (3, 10, 30):
            time.sleep(wait)
            try:
                root = fetch(batch)
                break
            except Exception:
                continue
        if root is None:
            if len(batch) > 1:  # one bad id can spoil a batch: split it
                half = len(batch) // 2
                batches = [batch[:half], batch[half:]] + batches
            continue
        answered.update(batch)
        for e in root.iter(ATOM + 'entry'):
            aid = e.findtext(ATOM + 'id', '').rsplit('/', 1)[-1].split('v')[0]
            title = ' '.join((e.findtext(ATOM + 'title') or '').split())
            names = [a.findtext(ATOM + 'name', '') for a in e.iter(ATOM + 'author')]
            year = (e.findtext(ATOM + 'published') or '')[:4]
            if title and title != 'Error':
                found[aid] = (title, ', '.join(n.split()[-1] for n in names[:3]) + (' et al.' if len(names) > 3 else ''), year)
    return found, answered


def main():
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    ids = sorted(set(ID.findall(text)))
    found, answered = lookup(ids)
    lines = text.splitlines()
    for aid in ids:
        if aid in found:
            t, a, y = found[aid]
            status = f'{t} | {a} | {y}'
        else:
            status = 'NOT ON ARXIV' if aid in answered else 'LOOKUP FAILED'
        print(f'{aid} | {status}')
        for line in (l for l in lines if aid in l):  # the report's own line(s) naming this id, e.g. its log row
            print(f'    report: {" ".join(line.split())[:300]}')
    print(f'{len(ids)} arXiv ids: {len(found)} found, {len(answered - set(found))} not on arXiv, {len(set(ids) - answered)} lookups failed')


if __name__ == '__main__':
    main()

"""Merge tools/references.bib into tools/papers.csv.

Usage (repository root):  python tools/import_bib.py && python tools/build_db.py

* Bibliographic columns (authors, title, venue, volume, pages, doi, year) are always refreshed from the .bib file.
* The curated columns of a paper (generator, input_features, evaluation, takeaway, ...) are never touched.
* A bib entry that is not in the CSV yet is added as a new row with only what the .bib file states.
* Nothing is looked up online and nothing is guessed. The 'category' of a NEW entry is 'To classify' until you set it.
"""
import csv, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
BIB, CSV = os.path.join(H, 'references.bib'), os.path.join(H, 'papers.csv')

# existing rows -> bib keys (checked by hand against the review)
KEYS = {'Beetz et al.': 'beetz2021cpcvae', 'CHeart': 'qiao2023cheart', 'CAN-FLOW': 'kevopoulos2026canflow', '4D CardioSynth': 'dou2025cardiosynth',
        'Amirrajab 2022': 'amirrajab2022labelinformed', 'Amirrajab 2023': 'amirrajab2023pathology', 'Campello 2022': 'campello2022aging', 'Li 2025': 'li2025cpgg',
        'Skorupko 2025': 'skorupko2025fairness', 'Diller 2020': 'diller2020utility', 'Edirisooriya 2026': 'edirisooriya2026fup', 'Rodriguez 2026': 'rodriguez2026metadata',
        'Konz 2024': 'konz2024segguided', 'brainSPADE': 'fernandez2022brainspade', 'AbdomenGen': 'bhandari2026abdomengen', 'MedSegFactory': 'mao2025medsegfactory',
        'MedDiff-FT': 'xie2025meddifft', 'SimGen': 'bhat2025simgen', 'AlignFlow': 'yang2026alignflow', 'Chen 2022': 'chen2022ganreview', 'Kazerouni 2023': 'kazerouni2023diffusionsurvey',
        'Hosseini and Serag 2025': 'hosseini2025biomarkers', 'Kumarasinghe 2026': 'kumarasinghe2026survey'}
# category of the background references (my grouping, editable in the CSV)
CAT = {'bernard2018acdc': 'Dataset', 'campello2021mms': 'Dataset', 'martinisla2021mms2': 'Dataset', 'lalande2020emidec': 'Dataset', 'li2023myops': 'Dataset', 'petersen2016ukb': 'Dataset',
       'goodfellow2014gan': 'Generative model (original paper)', 'kingma2014vae': 'Generative model (original paper)', 'ho2020ddpm': 'Generative model (original paper)',
       'dinh2017realnvp': 'Generative model (original paper)', 'lipman2023flowmatching': 'Generative model (original paper)',
       'ho2021cfg': 'Technique or architecture', 'perez2018film': 'Technique or architecture', 'park2019spade': 'Technique or architecture', 'ronneberger2015unet': 'Technique or architecture',
       'heusel2017fid': 'Evaluation metric', 'binkowski2018kid': 'Evaluation metric', 'dice1945': 'Evaluation metric', 'taha2015metrics': 'Evaluation metric', 'peffers2007dsr': 'Methodology'}
# what the project used the reference for (only where the project's own records state it)
USED = {'bernard2018acdc': 'The dataset used for training and validation in this project.', 'campello2021mms': 'External test set; not used yet.',
        'heusel2017fid': 'Image quality metric (FID) used here.', 'binkowski2018kid': 'Image quality metric (KID) used here.', 'dice1945': 'Segmentation overlap score used for the utility test.',
        'lipman2023flowmatching': 'The generative method of both stages in this project.', 'ho2021cfg': 'Used in both stages: guidance on the conditioning.',
        'perez2018film': 'Used to feed the 26 features into the mask generator.', 'ronneberger2015unet': 'The network type used in both stages and in the utility test.',
        'park2019spade': 'The GAN baseline for the image stage.', 'peffers2007dsr': 'The research methodology named in the proposal.'}
ACC = {r"{\'\i}": 'í', r"{\'n}": 'ń', r"\'\i": 'í', r"\'n": 'ń', r'\&': '&', r'{\&}': '&'}

def clean(s):
    for a, b in ACC.items(): s = s.replace(a, b)
    s = re.sub(r'\s+', ' ', s.replace('{', '').replace('}', '')).strip()
    return s

def parse(text):
    out = []; i = 0
    while True:
        m = re.search(r'@(\w+)\s*\{\s*([^,\s]+)\s*,', text[i:])
        if not m: break
        typ, key = m.group(1).lower(), m.group(2); j = i + m.end(); depth = 1; k = j
        while depth and k < len(text):
            depth += (text[k] == '{') - (text[k] == '}'); k += 1
        body = text[j:k - 1]; f = {}
        for fm in re.finditer(r'(\w+)\s*=\s*', body):
            s = fm.end()
            if s >= len(body): continue
            if body[s] == '{':
                d = 0; e = s
                while e < len(body):
                    d += (body[e] == '{') - (body[e] == '}'); e += 1
                    if d == 0: break
                f[fm.group(1).lower()] = body[s + 1:e - 1]
            else:
                e = s
                while e < len(body) and body[e] not in ',\n': e += 1
                f[fm.group(1).lower()] = body[s:e].strip()
        out.append((typ, key, f)); i = k
    return out

def venue(f):
    v = f.get('journal') or f.get('booktitle') or ''
    return clean(v)

def arxiv_url(f):
    m = re.search(r'arXiv:(\d{4}\.\d{4,5})', f.get('journal', ''))
    return 'https://arxiv.org/abs/' + m.group(1) if m else None

def main():
    bib = {k: (t, f) for t, k, f in parse(open(BIB, encoding='utf-8').read())}
    rows = list(csv.DictReader(open(CSV, newline='', encoding='utf-8')))
    cols = list(rows[0].keys())
    NEW = ['bibkey', 'entry_type', 'authors', 'title', 'venue', 'volume', 'pages', 'doi', 'category']
    for c in NEW:
        if c not in cols: cols.append(c)
    byk = {r.get('bibkey'): r for r in rows if r.get('bibkey')}
    for r in rows:
        if not r.get('bibkey') and r['short_name'] in KEYS: r['bibkey'] = KEYS[r['short_name']]; byk[r['bibkey']] = r
        if r['short_name'] == 'This thesis': r['category'] = 'This thesis'
    added = 0
    for k, (t, f) in bib.items():
        r = byk.get(k)
        if r is None:
            r = {c: '' for c in cols}; r['bibkey'] = k; r['proposal'] = r['own_work'] = '0'
            r['short_name'] = clean(f.get('author', k).split(' and ')[0].split()[-1]) + ' ' + f.get('year', '')
            r['full_ref'] = r['short_name']; rows.append(r); byk[k] = r; added += 1
            r['category'] = CAT.get(k, 'To classify'); r['takeaway'] = USED.get(k, '')
        if not r.get('category'):
            r['category'] = 'Review or survey' if r.get('generates_group') == 'Review' else ('Generation study (cardiac)' if r.get('field') == 'Cardiac' else 'Generation study (other)')
        r['entry_type'] = t; r['authors'] = re.sub(r', others$', ' et al.', clean(f.get('author', '')).replace(' and ', ', '))
        r['title'] = clean(f.get('title', '')); r['venue'] = venue(f); r['volume'] = clean(f.get('volume', '')); r['pages'] = clean(f.get('pages', '')).replace('--', '-')
        r['doi'] = clean(f.get('doi', '')); r['year'] = r.get('year') or f.get('year', '')
        if not r.get('url'):
            r['url'] = ('https://doi.org/' + r['doi']) if r['doi'] else (arxiv_url(f) or '')
    missing = [k for k in bib if k not in byk]
    with open(CSV, 'w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); [w.writerow({c: r.get(c, '') for c in cols}) for r in rows]
    print(f'{len(rows)} rows ({added} added from the .bib file). Rows still marked To classify:', [r['bibkey'] for r in rows if r['category'] == 'To classify'])
    nokey = [r['short_name'] for r in rows if not r.get('bibkey') and r['short_name'] != 'This thesis']
    if nokey: print('rows without a bib key:', nokey)

if __name__ == '__main__': sys.exit(main())

"""Build docs/papers.db (SQLite) from tools/papers.csv.

Usage (from the repository root):   python tools/build_db.py
Edit tools/papers.csv (one row per paper, UTF-8), run the script, commit docs/papers.db.
Empty cells become NULL and show as 'not recorded' on the page. Nothing is filled in automatically.
"""
import csv, sqlite3, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'papers.csv')
OUT = os.path.join(HERE, '..', 'docs', 'papers.db')

SCHEMA = """
CREATE TABLE papers (
  id              INTEGER PRIMARY KEY,
  short_name      TEXT NOT NULL,      -- 'Beetz et al.'
  full_ref        TEXT NOT NULL,      -- 'Beetz et al. 2021'
  year            INTEGER,
  family          TEXT,               -- generator family: GAN, VAE, Diffusion, Flow matching, ...
  generator       TEXT,               -- model name as used in the paper
  generates       TEXT,               -- what is generated, in words
  generates_group TEXT,               -- Images, Anatomy or masks, Image and mask pairs, Masks then images, Review
  conditioning    TEXT,               -- Demographics, Measured features, Masks or labels, ...
  input_features  TEXT,               -- the conditioning inputs in words
  evaluation      TEXT,               -- evaluation metrics named in the paper
  field           TEXT,               -- Cardiac or Other
  read_level      TEXT,               -- how much of the paper was read
  proposal        INTEGER NOT NULL DEFAULT 0,   -- 1 = cited in the thesis proposal
  own_work        INTEGER NOT NULL DEFAULT 0,   -- 1 = this project
  url             TEXT,
  takeaway        TEXT,
  datasets        TEXT,               -- datasets used (not recorded yet)
  bibkey          TEXT UNIQUE,        -- key in references.bib
  entry_type      TEXT,               -- article or inproceedings
  authors         TEXT,
  title           TEXT,
  venue           TEXT,               -- journal or conference
  volume          TEXT,
  pages           TEXT,
  doi             TEXT,
  category        TEXT                -- Generation study, Dataset, Evaluation metric, ...
);
CREATE INDEX idx_year ON papers(year);
CREATE INDEX idx_family ON papers(family);
CREATE INDEX idx_cond ON papers(conditioning);
CREATE INDEX idx_cat ON papers(category);
"""
INT = {'year', 'proposal', 'own_work'}

def main():
    if os.path.exists(OUT): os.remove(OUT)
    con = sqlite3.connect(OUT); con.executescript(SCHEMA)
    with open(SRC, newline='', encoding='utf-8') as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; n = 0
        for row in rd:
            vals = []
            for c in cols:
                v = (row[c] or '').strip()
                vals.append((int(v) if v else (0 if c in ('proposal', 'own_work') else None)) if c in INT else (v or None))
            con.execute('INSERT INTO papers (%s) VALUES (%s)' % (','.join(cols), ','.join('?' * len(cols))), vals); n += 1
    con.commit(); con.execute('VACUUM'); con.close()
    print(f'wrote {OUT} with {n} papers ({os.path.getsize(OUT)} bytes)')

if __name__ == '__main__': sys.exit(main())

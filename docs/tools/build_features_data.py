"""Write docs/assets/features_data.json from tools/data/*.csv (group statistics and generator fidelity).
Run from the repository root:  python tools/build_features_data.py
Only group-level summaries are written (no individual patient rows)."""
import pandas as pd, json, os
H = os.path.dirname(os.path.abspath(__file__))
F = pd.read_csv(os.path.join(H, 'data', 'features_all.csv')); R = pd.read_csv(os.path.join(H, 'data', 'feature_fidelity.csv'), index_col=0)
GROUPS = ['NOR', 'MINF', 'DCM', 'HCM', 'RV']
out = {'n_per_group': int(F.groupby('group').size().min()), 'stats': {}, 'fid': {}}
for c in [c for c in F.columns if c not in ('patient', 'group', 'split')]:
    d = {}
    for g in GROUPS:
        x = F.loc[F['group'] == g, c].dropna()
        d[g] = [round(float(v), 3) for v in (x.min(), x.quantile(.25), x.median(), x.quantile(.75), x.max(), x.mean())]
    a = F[c].dropna(); d['all'] = [round(float(a.mean()), 3), round(float(a.std()), 3)]
    out['stats'][c] = d
for c in R.index: out['fid'][c] = {'ceiling': round(float(R.loc[c, 'ceiling_r']), 3), 'baseline': round(float(R.loc[c, 'baseline_w1_K1']), 3)}
json.dump(out, open(os.path.join(H, '..', 'docs', 'assets', 'features_data.json'), 'w'), separators=(',', ':'))
print('features:', len(out['stats']), 'fidelity rows:', len(out['fid']), 'per group:', out['n_per_group'])

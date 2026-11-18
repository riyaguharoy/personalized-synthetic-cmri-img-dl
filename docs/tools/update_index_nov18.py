import re, html, pandas as pd, os
HERE=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(HERE,'..','docs','index.html')
s=open(P,encoding='utf-8').read()
d=pd.read_csv(os.path.join(HERE,'papers.csv')); E=html.escape

# ---------- literature: by-pipeline summary generated from the database ----------
order=[('Anatomy or masks','Conditions to anatomy or masks'),('Masks, then images','Conditions to masks, then masks to images'),('Images','Conditions to images directly'),('Image and mask pairs','Image and mask pairs together'),('Review','Reviews and surveys')]
rows=''
for k,label in order:
    x=d[d.generates_group==k]
    cond=', '.join(f'{c} {n}' for c,n in x.conditioning.value_counts().items()) or 'not applicable'
    card=int((x.field=='Cardiac').sum())
    names=', '.join(x.short_name)
    rows+=f'<tr><td><b>{E(label)}</b></td><td>{len(x)}</td><td>{card} of {len(x)}</td><td>{E(cond)}</td><td>{E(names)}</td></tr>'
cat=d.category.value_counts()
sup=', '.join(f'{cat[c]} {n}' for c,n in (('Dataset','datasets'),('Generative model (original paper)','original model papers'),('Evaluation metric','evaluation metrics'),('Technique or architecture','techniques'),('Methodology','methodology')) if c in cat)
rl=d.read_level.value_counts()
full=int(rl.get('Read in full',0)); ab=int(rl.get('Abstract or first page',0)); no=int(sum(v for k,v in rl.items() if str(k).startswith('Not opened')))
lit_add=f'''
    <h3>Summary by pipeline stage</h3>
    <p>The {len(d)} references in the database are grouped by what the paper generates, from conditions to anatomy through to images. {int(d.generates_group.notna().sum())} are generation papers, reviews or this project, and the rest are supporting references ({sup}).</p>
    <div class="tw"><table style="min-width:700px"><thead><tr><th>What the paper generates</th><th>Papers</th><th>Cardiac</th><th>What it is conditioned on</th><th>Which papers</th></tr></thead><tbody>{rows}</tbody></table></div>
    <p class="small" style="margin:0 0 8px">Of the papers in these groups other than this project, {full} were read in full, {ab} on the abstract or first page only, and {no} could not be opened and are described as in the proposal. The database does not yet record datasets, evaluation metrics and loss functions per paper. Tables for them are next.</p>'''
s=s.replace('<p class="small" style="margin:0">None of the papers found generates cardiac masks',lit_add+'\n    <p class="small" style="margin:0">None of the papers found generates cardiac masks',1)
assert 'Summary by pipeline stage' in s

# ---------- architecture ----------
arch='''<section id="architecture">
    <h2>System architecture</h2>
    <p class="why"><b>Why:</b> Two stages let each part be tested alone: an effect of the features can be traced to the stage that produced it, and the image model can be tested with real masks. Flow matching is the one model family used in both stages, since the thesis studies the effect of the clinical profile and not which model family is best.</p>
    <h3>Generation: what runs when a profile is typed in</h3>
    <div class="gen">
      <div class="fb"><b>Profile</b><span>26 features, slice position, ED/ES flag, noise</span></div>
      <div class="fb"><b>Stage 1: mask generator</b><span>flow matching, FiLM U-Net, 50 steps</span></div>
      <div class="fb"><b>Anatomy filter</b><span>a failed mask is redrawn, up to 20 times</span></div>
      <div class="fb opt"><b>Selection (optional)</b><span>draw K sets, keep the one whose measured features are closest to the request</span></div>
      <div class="fb"><b>Mask</b><span>RV, myocardium, LV, 128 &times; 128</span></div>
      <div class="fb"><b>Stage 2: image model</b><span>flow matching U-Net, guidance 2, 50 steps</span></div>
      <div class="fb"><b>Synthetic MRI</b><span>image and mask, nothing real is used</span></div>
    </div>
    <h3>Training and checking</h3>
    <div class="mini">
      <div><b>How the two stages are trained (85 training patients)</b><ul><li>Stage 1: real masks with the real features of the same patients. The loss is the flow matching velocity error, foreground pixels count three times, and the condition is dropped in 10% of steps so guidance can be used. EMA weights are kept.</li><li>Stage 2: pairs of real image and real mask, with noise added step by step.</li></ul></div>
      <div><b>How the output is checked (15 validation patients)</b><ul><li>The same measuring code that made the features is run on every generated mask and compared with the requested values.</li><li>A diagnosis classifier is applied to generated masks (read-back).</li><li>Image fidelity is FID and KID, with real masks as the reference.</li></ul></div>
    </div>
    <div class="tw"><table style="min-width:760px"><thead><tr><th>Component</th><th>Input</th><th>Output</th><th>Model</th><th>Training</th><th>Generation</th></tr></thead><tbody>
      <tr><td><b>Stage 1: mask generator</b></td><td>26 standardised features (log on the skewed ones), slice position, ED/ES flag, noise</td><td>128 &times; 128 mask, 4 labels</td><td>FiLM U-Net, 6.4 M parameters</td><td>Velocity loss, foreground weight 3, condition dropout 10%, EMA</td><td>50 Euler steps, guidance weight 1, anatomy filter</td></tr>
      <tr><td><b>Selection (optional)</b></td><td>K complete sets of masks for one patient</td><td>The set, or the ED set and the ES set separately, with the lowest feature error</td><td>No model</td><td>None, no retraining</td><td>K draws per patient. Uses only the requested features, never a real mask</td></tr>
      <tr><td><b>Stage 2: image model</b></td><td>Mask, noise image</td><td>128 &times; 128 image</td><td>Velocity U-Net, 24.7 M parameters</td><td>Flow matching on real image and mask pairs, 16,000 steps</td><td>50 steps, guidance scale 2, mask given to every block</td></tr>
      <tr><td><b>Baseline: SPADE GAN</b></td><td>Mask, 128 random numbers</td><td>128 &times; 128 image</td><td>SPADE generator about 14.6 M, discriminator 2.8 M</td><td>150 epochs</td><td>One pass</td></tr>
    </tbody></table></div>
    <p class="small" style="margin:14px 0 0">Diagrams of each model, including the first-generation conditional VAE with 14 features, are in <a href="#models">Models</a>. The older whole-pipeline figures in <a href="details.html">Technical details</a> still show that first version.</p>
  </section>'''
s=re.sub(r'<section id="architecture">.*?</section>',lambda m:arch,s,count=1,flags=re.S)

# ---------- results ----------
res_add='''
    <h3>Getting the requested features back</h3>
    <p>A real mask moved by one pixel in a random direction would still give the features back with a mean correlation of 0.94 (the ceiling). One draw per patient reaches 0.80. Drawing several sets and keeping the best brings it to 0.86 without retraining. The table is the mean of two mask models on the 15 validation patients.</p>
    <div class="tw"><table style="min-width:700px"><thead><tr><th>Method</th><th>Draws per patient</th><th>Mean feature r</th><th>Within 10%</th><th>LV EF r</th><th>RV EF r</th></tr></thead><tbody>
      <tr><td><b>One draw (K = 1)</b></td><td>1</td><td>0.800</td><td>48.9</td><td>0.890</td><td>0.669</td></tr>
      <tr><td>Best of 4, one set for ED and ES</td><td>4</td><td>0.855</td><td>55.1</td><td>0.949</td><td>0.786</td></tr>
      <tr><td>Best of 4, ED and ES chosen separately</td><td>4</td><td>0.856</td><td>58.3</td><td>0.941</td><td>0.850</td></tr>
      <tr><td>Best of 8, ED and ES chosen separately</td><td>8</td><td>0.860</td><td>62.1</td><td>0.972</td><td>0.829</td></tr>
    </tbody></table></div>
    <p class="small">Selection uses only the requested features and no real mask, and is scored on those same features. It shows how accurately the conditioning can be met, not how well the model generalises. Choosing ED and ES separately lowers the circularity features (right ventricle ES circularity r 0.79 to about 0.5). Weighting the selection error by feature ceiling made no difference, weighting the key features raised EF (LV 0.975, RV 0.911) and lowered the mean to 0.844, and drawing extra sets only for hard patients did not help. Diversity and copying are unchanged (spread ratio 0.84 to 0.89, nearest-training-mask Dice 0.79, real masks 0.80), and image FID is 118.5 to 118.9 against 119.5 for one draw and 119.1 for real masks, so images are not affected.</p>
    <h3>A feature-consistency loss</h3>
    <p>Each final mask model was trained for 3,000 more steps, once with a loss that asks the slices of one patient to give back the requested volumes, EF, ratios and circularity, and once without it (control). Mean of two mask models and two noise seeds.</p>
    <div class="tw"><table style="min-width:640px"><thead><tr><th>Version</th><th>Mean feature r</th><th>Within 10%</th><th>RV EF r</th><th>Circularity r</th></tr></thead><tbody>
      <tr><td>Final model, no extra steps</td><td>0.786</td><td>47.5</td><td>0.641</td><td>0.524</td></tr>
      <tr><td>Control, extra steps only</td><td>0.809</td><td>33.4</td><td>0.769</td><td>0.491</td></tr>
      <tr><td><b>With consistency loss</b></td><td>0.824</td><td>38.4</td><td>0.810</td><td>0.578</td></tr>
    </tbody></table></div>
    <p class="small">The loss adds about 0.015 in mean r over the control, within the seed-to-seed spread, and about 5 points in within-10%, which held in all four pairs of runs. Extra training alone lowers within-10% and moves masks slightly closer to the training masks, so the final model is kept as the main model. Wall thickness is not covered by the loss because it is not differentiable.</p>
    <h3>Usefulness and privacy</h3>
    <div class="tw"><table style="min-width:600px"><thead><tr><th>Test</th><th>Result</th></tr></thead><tbody>
      <tr><td>Segmentation Dice, trained on real / synthetic / real and synthetic data</td><td>0.801 / 0.765 / 0.821</td></tr>
      <tr><td>Membership inference AUC, whole pipeline (0.5 = no signal)</td><td>0.52 to 0.55</td></tr>
      <tr><td>Membership inference AUC, image model given real masks / mask model alone</td><td>0.74 to 0.78 / 0.614</td></tr>
    </tbody></table></div>
    <p class="small" style="margin:0">The image model on its own recognises training patients when it is given their real masks, while the whole pipeline, which uses generated masks, does not. All numbers are from 15 validation patients and few runs.</p>'''
s=s.replace('</figure>\n  </section>\n\n  <section id="status">','</figure>'+res_add+'\n  </section>\n\n  <section id="status">',1) if '</figure>\n  </section>\n\n  <section id="status">' in s else s
assert 'Getting the requested features back' in s, 'results insertion failed'

# ---------- status ----------
status='''<section id="status">
    <h2>Status</h2>
    <div class="two">
      <div><b>Done</b><ul><li>Two-stage pipeline, end to end, with the final mask model</li><li>26 features, measured back on every generated mask</li><li>SPADE GAN against flow matching</li><li>Segmentation usefulness and membership-inference tests</li><li>Feature ceiling, best-of-K selection and consistency loss</li><li>Literature database with 44 references</li></ul></div>
      <div><b>Next</b><ul><li>SPADE baseline rerun with the 26 features</li><li>Features from single slices against the 3D volume</li><li>Datasets, metrics and loss tables for the literature review</li><li>ACDC test set and M&amp;Ms</li></ul></div>
    </div>
    <p class="small" style="margin:14px 0 0">A methods project. No patient outcomes or clinical use. Numbers are from 15 validation patients and few runs.</p>
  </section>'''
s=re.sub(r'<section id="status">.*?</section>',lambda m:status,s,count=1,flags=re.S)

# ---------- glossary row + css ----------
row='<tr><td><b>Best-of-K selection</b></td><td>Generate K complete sets of masks for a patient, measure the features of each set, and keep the set closest to the requested features. No real mask is used.</td><td>Raises how well the requested features are met without retraining. Scored on the same features, so it measures conditioning accuracy, not generalisation.</td></tr>'
s=s.replace('<tr><td><b>Diagnosis read-back</b>',row+'<tr><td><b>Diagnosis read-back</b>',1)
css='h3{margin:22px 0 8px;font-size:1.05rem;color:var(--accent)}.fb.opt{border-style:dashed;border-top-style:dashed}.gen{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;counter-reset:g;margin:6px 0 4px}.gen .fb{text-align:left;counter-increment:g;position:relative;padding-top:30px}.gen .fb::before{content:counter(g);position:absolute;top:8px;left:12px;font:12px var(--mono);color:var(--accent)}.gen .fb b{display:block}.gen .fb span{display:block;font-size:.88rem;color:var(--muted)}'
s=s.replace('footer{position:relative',css+'\nfooter{position:relative',1)
open(P,'w',encoding='utf-8').write(s); print('ok',len(s))

import os
HERE=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(HERE,'..','docs','index.html')
s=open(P,encoding='utf-8').read()
why={
 '<span>26 features, slice position, ED/ES flag, noise</span>':'Every feature can be measured again on a mask, so the request can be checked.',
 '<span>flow matching, FiLM U-Net, 50 steps</span>':'The first model, a VAE, made masks that were too regular (anatomy pass 53.8%). Flow matching masks vary more and follow the requested size.',
 '<span>a failed mask is redrawn, up to 20 times</span>':'Only 68% of first-draw masks pass the anatomy check. With redraws, 99.9% do.',
 '<span>draw K sets, keep the one whose measured features are closest to the request</span>':'One draw gives a mean feature correlation of 0.80 against a ceiling of 0.94. Extra draws close part of that gap without retraining.',
 '<span>RV, myocardium, LV, 128 &times; 128</span>':'The mask sits in the middle so the features can be checked before any image exists.',
 '<span>flow matching U-Net, guidance 2, 50 steps</span>':'Image FID fell from 189.5 (SPADE GAN) to 118.8.',
 '<span>image and mask, nothing real is used</span>':'Images from generated masks score about the same FID as images from real masks.',
}
for k,v in why.items():
    assert k in s,k
    s=s.replace(k,k+'<em class="w2"><b>Why:</b> '+v+'</em>',1)
rows=[
('Define 26 features that can be measured on a mask','The request can then be checked on every generated mask. The first 14 carry diagnosis information, the 12 shape features were added later.','24 of 26 are measured from masks (height and weight come from the record). A real mask moved by one pixel keeps a mean correlation of 0.94.','Done'),
('First mask model: conditional VAE','The usual way to generate shapes from patient information in related work.','Anatomy pass 53.8%. Masks smooth and too regular, a size sweep hardly changes them.','Done, replaced'),
('Image baseline: SPADE GAN','The mask-conditioned GAN baseline from the proposal.','FID 189.5, noisy images, little variety.','Done, kept as baseline'),
('Mask generator: flow matching, with anatomy filter','More varied masks that follow the requested size.','68% pass on the first draw and 99.9% after the filter. LV EF r 0.92. Diagnosis read back 89% (93% on real masks).','Done'),
('Image model: flow matching','Better image fidelity than the GAN.','FID 118.8 against 189.5.','Done'),
('Segmentation usefulness and membership-inference tests','Whether the synthetic data helps and whether it leaks training patients.','Dice 0.801 real, 0.765 synthetic, 0.821 both. Whole pipeline membership AUC 0.52 to 0.55.','Done'),
('Feature ceiling and best-of-K selection','To see how closely the requested features can be met and close the gap without retraining.','Mean r 0.80 with one draw, 0.86 with the best of 8. Circularity gets worse when ED and ES are chosen separately.','Done'),
('Feature-consistency loss','To ask the slices of a patient to give back the requested volumes and shapes during training.','About +0.015 mean r over a control with the same extra steps, within the noise. Exploratory.','Done, exploratory'),
('SPADE baseline rerun with 26 features','The baseline should get the same input as the final model.','Not run yet.','Next'),
('Features from single slices against the 3D volume','To learn which of the 26 features can be measured without a full volume.','Not run yet.','Next'),
('ACDC test set and M&amp;Ms','To test on data the models have not seen and on other scanners.','Not run yet.','Next'),
]
body=''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a,b,c,d in rows)
block=f'''
    <h3>Steps taken, why, and what they showed</h3>
    <div class="tw"><table style="min-width:760px"><thead><tr><th>Step</th><th>Why</th><th>What it showed</th><th>Status</th></tr></thead><tbody>{body}</tbody></table></div>
    <p class="small" style="margin:0 0 8px">Numbers are from 15 validation patients and few runs. The VAE row and the baseline row are kept in the table because they explain why later steps were taken.</p>'''
anchor='<p class="small" style="margin:14px 0 0">Diagrams of each model, including the first-generation'
assert anchor in s
s=s.replace(anchor,block+'\n    '+anchor,1)
css='.w2{display:block;margin-top:8px;padding-top:8px;border-top:1px solid var(--line);font-style:normal;font-size:.82rem;line-height:1.45;color:var(--muted)}.w2 b{color:var(--heart)}'
s=s.replace('footer{position:relative',css+'\nfooter{position:relative',1)
open(P,'w',encoding='utf-8').write(s); print('ok')

import os
HERE=os.path.dirname(os.path.abspath(__file__)); P=os.path.join(HERE,'..','docs','index.html')
s=open(P,encoding='utf-8').read()
a='<div class="fb"><b>Stage 2: image model</b><span>flow matching U-Net, guidance 2, 50 steps</span><em class="w2"><b>Why:</b> Image FID fell from 189.5 (SPADE GAN) to 118.8.</em></div>'
assert a in s
b='<div class="fb"><b>Stage 2: image model</b><span>flow matching U-Net, guidance 2, 50 steps</span><span class="alt">Baseline: SPADE GAN, same mask input</span><em class="w2"><b>Why:</b> A mask-conditioned SPADE GAN is the baseline from the proposal. Flow matching lowered image FID from 189.5 to 118.8, so it is the final image model.</em></div>'
s=s.replace(a,b,1)
blk='''
    <h3>Image baseline: SPADE GAN</h3>
    <p>Stage 2 has two interchangeable models that take the same mask. The final one is the flow matching image model. The baseline is a SPADE GAN, the mask-conditioned GAN named in the proposal. The generator starts from 128 random numbers, and residual blocks with SPADE layers re-scale the features of every block using the mask while the image is up-sampled to 128 &times; 128. A discriminator is used only during training. About 14.6 M parameters in the generator and 2.8 M in the discriminator, trained for 150 epochs. With real masks it reaches FID 189.5 and KID 0.122, against FID 118.8 and KID 0.040 for flow matching, so it is kept as the baseline and not used for the final results. The features reach stage 2 only through the mask, for both models. Its diagram is in <a href="#models">Models</a>, and rerunning it with the 26-feature pipeline is still to do.</p>'''
anchor='<p class="small" style="margin:14px 0 0">Diagrams of each model, including the first-generation'
assert anchor in s
s=s.replace(anchor,blk.lstrip('\n')+'\n    '+anchor,1)
s=s.replace('footer{position:relative','.gen .fb span.alt{margin-top:6px;color:var(--accent)}\nfooter{position:relative',1)
open(P,'w',encoding='utf-8').write(s); print('ok')

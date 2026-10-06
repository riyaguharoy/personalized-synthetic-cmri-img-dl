# Literature review: clinical-profile-conditioned generative models for cardiac MRI

**Status:** working draft, 6 October 2026. Prepared with AI assistance and checked against the sources named below. Items marked **to verify** have not been confirmed against the original paper.

## 1. What this review is for

The thesis asks how information about a patient (a "clinical profile") can be used to control the generation of synthetic cardiac MR images and their segmentation masks, and whether that control is real, useful and safe. This review looks for what has already been done on that question, how those papers checked their results, and what is still missing.

The review question is:

> Which generative models for cardiac MRI condition on patient-level or clinical information, how do they verify that the conditioning works, and how do they evaluate fidelity, downstream utility and privacy?

## 2. How the search was done

This is a focused literature review, not a PRISMA-style systematic review.

**Sources.** Web searches that surfaced arXiv, PubMed Central, Springer, MICCAI proceedings and publisher pages, followed by backward citation chasing through the reference lists of four recent papers: Kumarasinghe et al. 2026, Edirisooriya et al. 2026, Cao et al. 2026 and Fang et al. 2026. The proposal's own reference list was also used.

**Search terms used (examples).**

- synthetic cardiac MRI generation diffusion model
- personalized synthetic cardiac MRI generation
- patient-specific cardiac MRI synthesis phenotype conditioning covariates
- cardiac aging synthesis conditional GAN age BMI
- ControlNet text-conditioned cardiac MRI fairness
- cardiac MRI generation conditioned on clinical information, demographic attributes, diffusion, cine CMR

**Inclusion.** The paper generates cardiac MR images (cine, late gadolinium enhancement or similar), and either conditions on patient-level or clinical information, or is a directly comparable mask-conditioned baseline or evaluation protocol. Published 2020 to 2026, in English.

**Exclusion.** Reconstruction and under-sampling papers, pure segmentation papers, and non-cardiac papers except as background.

**Limits.** One reviewer, web search rather than database search, no result counts. To make it reproducible, re-run the strings in section 8 in Scopus, PubMed, IEEE Xplore and arXiv, and record the number of hits and the date.

## 3. What counts as a "clinical profile"

Across the papers, the information used to steer generation falls into five kinds:

| Kind of conditioning | Example variables | Papers |
|---|---|---|
| Anatomy only (baseline family) | segmentation masks, pathology-altered masks | Amirrajab 2022 and 2023, Edirisooriya 2026 |
| Demographics and body measures | age, sex, BMI | Campello 2022, Skorupko 2025 |
| Diagnosis and clinical measurements | diagnosis class, chamber volumes, ejection fraction | Cao 2026 |
| Derived cardiac phenotypes | LVEF, LVEDV and other phenotypes from the images | Li 2025 (CPGG) |
| Other patient signals | 12-lead ECG | Fang 2026 (ECGFlowCMR) |

## 4. The papers, by theme

### 4.1 Anatomy-conditioned generation (the baseline family)

Amirrajab et al. (2022) generate cardiac MR images from segmentation label maps using a conditional GAN with SPADE layers, so each image arrives with a matching mask. In 2023 the same group used a VAE to change a mask's shape towards a disease (for example hypertrophy or dilation) and a label-conditioned GAN to render it. Both control anatomy, not the patient. Details here come from the Simula survey's summary table (**to verify** against the originals).

Edirisooriya et al. (2026) are the most useful template for the thesis. They generate masks with a DDPM, then images from the masks with a DDPM, a latent diffusion model and flow matching. They evaluate fidelity (SSIM, MS-SSIM, PSNR, FID, KID, LPIPS), segmentation utility across datasets (ACDC and M&Ms, with Dice, IoU, HD95 and ASD) and privacy (nearest-neighbour distance and membership inference). DDPM gave the best overall balance. Membership-inference AUC was 0.58 to 0.60 for all three. Real-data Dice was 0.90 to 0.93 against 0.82 to 0.90 for synthetic. They condition on masks only.

### 4.2 Conditioning on demographics and body measures

Campello et al. (2022) trained a conditional GAN on UK Biobank four-chamber images to make an older or younger version of a given heart. The generator is conditioned on the gap between the current and target age (or BMI), embedded with a sinusoidal encoding. They checked that the conditioning worked by running a separately trained age regressor on the generated images, and they showed that adding synthetic scans reduced age-prediction error on imbalanced data. They also report limits: no check against real longitudinal scans and clinically wrong structures in end-systole synthesis.

Skorupko et al. (2025) use ControlNet on a diffusion model, conditioning on text built from sex, age, BMI and health condition plus cardiac geometry from masks. The aim is fairness: generating extra images for under-represented groups so a classifier becomes less biased. They run on one consumer GPU. I read only the abstract, so the details come from the Simula survey table (**to verify**).

### 4.3 Conditioning on diagnosis and clinical measurements

Cao et al. (2026) is the closest published work to the thesis. Their model conditions on a diagnosis category, slice count and end-diastolic, end-systolic and ejection-fraction volumes. A semi-supervised VAE with a shared latent space produces image and mask together. A static latent diffusion model generates end-diastole anatomy and a second one adds motion. They trained on 100 labelled ACDC patients plus 856 unlabelled Data Science Bowl patients, and tested on ACDC, M&Ms (134 patients) and M&Ms-2 (157 patients).

They checked the conditioning with a Pearson correlation between the clinical values given and the volumes measured on the generated data (r from 0.66 to 0.94). Adding synthetic data raised cross-vendor segmentation Dice by 1.4% on average. They report no privacy evaluation, and I did not see a with-versus-without-conditioning comparison.

Li et al. (2025, CPGG) generate cine CMR from cardiac phenotypes with a masked autoregressive diffusion model, and show that using the synthetic data for pretraining helps diagnosis and phenotype prediction. I read the abstract; the dataset and metric details come from the survey table (**to verify**).

### 4.4 Other patient signals

Fang et al. (2026) generate cine CMR from a patient's 12-lead ECG and use it for pretraining. They argue that ECG conditioning avoids the dependence on CMR-derived phenotypes that limits CPGG, but note that an ECG constrains anatomy only weakly. I did not see a privacy test in the parts I read.

### 4.5 Evaluating synthetic cardiac MRI

Hosseini and Serag (2025) show that diffusion-generated lung and retinal images can keep the hidden features a classifier uses to recognise disease. It is not about cardiac MRI, but it supports the point that a realistic-looking image is not enough.

Kumarasinghe et al. (2026) review cardiac MRI synthesis through fidelity, utility and privacy. Their reported gaps are limited pathology-specific mask conditioning, little work on small-data diffusion and flow matching, rare privacy evaluation, and rare cross-dataset testing.

## 5. Putting them side by side

Nine papers, using the evaluation sheet in `literature_summary_table.xlsx`:

| Check | Papers that do it |
|---|---|
| Measured fidelity | 9 of 9 |
| Measured downstream utility | 9 of 9 |
| Measured privacy | 1 of 9 (Edirisooriya) |
| Clearly checked the conditioning worked | 2 of 9 (Campello, Cao), plus 1 partly (Skorupko) |
| Conditioned on patient information | 5 of 9 (Campello, Skorupko, Li, Cao, Fang) |

Three papers argue privacy benefits without testing them (Amirrajab 2022, Diller 2020, Skorupko 2025). These counts cover only the nine papers listed, so they show a pattern and are not a measure of the whole field.

## 6. Gaps this leaves for the thesis

1. **Privacy is almost untested for conditioned generation.** None of the papers that condition on patient information reports a privacy test. Conditioning on individual characteristics could plausibly raise memorisation risk, and this has not been checked in the papers I read.
2. **Verifying the conditioning is uneven.** Only Campello and Cao clearly test whether the generated images reflect the requested profile.
3. **No with-versus-without comparison seen.** In the papers I read, nobody compares the same generator with and without the clinical profile under one fidelity, utility and privacy protocol.
4. **Profiles differ across papers.** Age and BMI, text metadata, phenotypes, diagnosis plus volumes and ECG are each used once, which makes the results hard to compare.
5. **Open data is under-used.** Most conditioned work uses UK Biobank, which needs an application. Cao uses ACDC and M&Ms, which are open.

These are the gaps your Introduction and Section 5.5 describe. Cao et al. (2026) narrows gap 2 and part of gap 4, so it should be cited and the wording about "few studies" kept careful.

## 7. What this suggests for the design (to discuss with supervisors)

- Use ACDC as the main dataset and M&Ms as the external test set, as Edirisooriya and Cao both do. ACDC offers diagnosis group, height and weight, and ejection fraction and volumes can be derived from its masks.
- Take the mask-conditioned DDPM pipeline of Edirisooriya et al. as the baseline, and add the clinical profile as the only change.
- Check the conditioning the way Cao and Campello do: measure the generated masks and images, and compare with the values requested.
- Reuse Edirisooriya's privacy tests (nearest-neighbour distance and membership inference).
- Ask whether Cao et al. should be added to the proposal's reference list.

## 8. Search strings for reproduction

Scopus or Web of Science:

```
TITLE-ABS-KEY(("cardiac magnetic resonance" OR "cardiac MRI" OR CMR)
AND (synthesis OR synthetic OR generation OR generative)
AND (conditioned OR conditional OR conditioning OR "guided")
AND (clinical OR demographic OR phenotype OR covariate OR attribute OR "patient-specific" OR text))
```

arXiv:

```
all:"cardiac MRI" AND all:(synthesis OR generation) AND all:(conditioned OR conditional) AND all:(clinical OR phenotype OR demographic)
```

PubMed:

```
("cardiac magnetic resonance"[tiab] OR "cardiac MRI"[tiab]) AND (synthesis[tiab] OR "generative"[tiab]) AND (conditional[tiab] OR conditioned[tiab])
```

## 9. Leads not yet read

- Liu et al. (2025). TexDC: text-driven disease-aware 4D cardiac cine MRI generation. ACCV 2024.
- Vukadinovic et al. (2023). GANcMRI: cardiac MR video generation and physiologic guidance using latent space prompting. ML4H.
- Gheorghiță et al. (2022). Improving robustness of automatic cardiac function quantification from cine MRI using synthetic image data. Scientific Reports.
- Khalil et al. (2023). On the usability of synthetic data for improving the robustness of deep learning-based segmentation of cardiac MR images. Medical Image Analysis.
- Konz et al. (2024). Anatomically-controllable medical image generation with segmentation-guided diffusion models. arXiv:2402.05210.
- Cheng et al. (2024). Synthesising 3D cardiac cine-MR images and corresponding segmentation masks using a latent diffusion model. ISBI.
- Li, Ma and Shi (2025). Multi-label conditioned diffusion for cardiac MR image augmentation and segmentation. Bioengineering.

## 10. References

1. Campello VM et al. Cardiac aging synthesis from cross-sectional data with conditional generative adversarial networks. Front Cardiovasc Med 9:983091 (2022). doi:10.3389/fcvm.2022.983091
2. Skorupko G et al. Fairness-aware data augmentation for cardiac MRI using text-conditioned diffusion models. arXiv:2403.19508.
3. Li Z et al. Phenotype-guided generative model for high-fidelity cardiac MRI synthesis. arXiv:2505.03426.
4. Cao Y et al. Anatomy-guided residual motion diffusion for controllable 4D cardiac MRI synthesis. arXiv:2606.26764 (2026).
5. Fang X et al. ECGFlowCMR: pretraining with ECG-generated cine CMR helps cardiac disease classification and phenotype prediction. KDD 2026. arXiv:2601.20904.
6. Edirisooriya M et al. Balancing fidelity, utility, and privacy in synthetic cardiac MRI generation: a comparative study. arXiv:2603.04340 (2026).
7. Kumarasinghe I et al. Synthetic cardiac MRI image generation using deep generative models. arXiv:2603.24764 (2026).
8. Amirrajab S et al. Label-informed cardiac magnetic resonance image synthesis through conditional generative adversarial networks. Comput Med Imaging Graph 101:102123 (2022).
9. Amirrajab S et al. Pathology synthesis of 3D-consistent cardiac MR images using 2D VAEs and GANs. Mach Learn Biomed Imaging 2:288-311 (2023).
10. Diller GP et al. Utility of deep learning networks for the generation of artificial cardiac magnetic resonance images in congenital heart disease. BMC Med Imaging 20 (2020).
11. Hosseini A, Serag A. Is synthetic data generation effective in maintaining clinical biomarkers? Investigating diffusion models across diverse imaging modalities. Front Artif Intell 7:1454441 (2025). doi:10.3389/frai.2024.1454441

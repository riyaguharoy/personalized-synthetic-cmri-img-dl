# Clinical-Profile-Conditioned Generative Models for Cardiac MRI: Literature Review

Riya Guha Roy · 8 October 2026

## Scope and method

This review asks one question: how have generative models for cardiac MRI (CMR) been conditioned on patient-level information, and how did the authors check that the conditioning worked?

- **Included:** papers that generate cardiac MR images (2D, 3D or cine) with a controllable input: segmentation masks, clinical variables, phenotypes, text or ECG. A few closely related echo and review papers are included for context.
- **Excluded:** work on segmentation, reconstruction or classification only, unless it uses synthetic CMR data.
- **How I searched (8 October 2026):** web search of arXiv, MICCAI proceedings, PubMed Central, Frontiers and MDPI, then opening each paper's page. The newest paper found is dated 25 August 2026.
- **Limits:** this is a focused review, not a systematic one (no formal protocol or PRISMA flow). For most papers I read the abstract and key results as shown on the source page, not the full text. Rows for Amirrajab 2022, Diller 2020 and Hosseini 2025 come from the author's own literature table and were not re-opened. PubMed Central blocked two pages, so those are marked.

## Background: how CMR images are generated

Four model families cover almost every paper below, and the choice of family matters less than what the model is conditioned on.

- **GAN (generative adversarial network):** a generator and a critic compete. Fast and sharp, but training can be unstable and can memorise. Used by [Campello 2022](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.983091/full) and [Skandarani 2020](https://arxiv.org/abs/2005.09026).
- **VAE (variational autoencoder):** compresses an image or mask into a small latent code and decodes it. Often used to make new anatomy shapes or as the compressor in latent diffusion.
- **Diffusion:** the model learns to remove noise step by step. Latent diffusion does this in a compressed space, which makes 3D and cine video affordable. Used by [Skorupko 2025](https://arxiv.org/abs/2403.19508), [Li 2025](https://arxiv.org/abs/2505.03426) and [Cao 2026](https://arxiv.org/abs/2606.26764).
- **Flow matching:** a newer, deterministic alternative to diffusion that needs fewer steps. Used in [Fang 2026](https://arxiv.org/abs/2601.20904) and compared in [Edirisooriya 2026](https://arxiv.org/abs/2603.04340).

Conditioning means feeding extra information to the model so the output follows it. The common ways seen here are:

- **SPADE:** spatially adaptive normalisation, which injects a segmentation mask at every layer. Standard for mask conditioning ([Skandarani 2020](https://arxiv.org/abs/2005.09026), [Li, Ma and Shi 2025](https://www.mdpi.com/2306-5354/12/8/812)).
- **ControlNet:** adds a mask or geometry input to a pretrained diffusion model ([Skorupko 2025](https://arxiv.org/abs/2403.19508)).
- **Embeddings and cross-attention:** numbers such as age, volumes or ejection fraction are encoded and fed into the network ([Campello 2022](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.983091/full) with a sinusoidal embedding; [Cao 2026](https://arxiv.org/abs/2606.26764) with an MLP and cross-attention).
- **Text prompts:** metadata written as a sentence ([Skorupko 2025](https://arxiv.org/abs/2403.19508), [Rodríguez 2026](https://arxiv.org/abs/2608.24342)).

## Mask-conditioned generation: the baseline literature

Generating a CMR image from a segmentation mask is well established, and it controls anatomy but not the patient.

- **[Skandarani et al. 2020](https://arxiv.org/abs/2005.09026):** a VAE makes plausible cardiac shapes and a SPADE-conditioned GAN turns each shape into an image. On ACDC and Sunnybrook, training on synthetic data with augmentation raised Dice by 2 to 4 points, and fine-tuning widened the gap to 6 to 10 points.
- **Amirrajab et al. 2022:** a SPADE conditional GAN on M&Ms that beat Pix2Pix and Pix2PixHD on image similarity (per the author's literature table; not re-opened).
- **[Amirrajab et al. 2023](https://arxiv.org/abs/2209.04223):** a VAE deforms label maps towards pathology, and a SPADE GAN makes the images. Trained on ACDC and M&Ms-1 and tested on M&Ms-2, adding pathology-synthesised data gave the best Dice and Hausdorff distance. 3D consistency was not measured quantitatively.
- **[Li, Ma and Shi 2025](https://www.mdpi.com/2306-5354/12/8/812):** a diffusion model makes masks and a SPADE latent diffusion model makes images, on 2D M&Ms. They report a 5% to 10% higher Dice than traditional augmentation.
- **[Edirisooriya et al. 2026](https://arxiv.org/abs/2603.04340):** two stages, masks first and then images, comparing DDPM, latent diffusion and flow matching on fidelity, utility and privacy. DDPM gave the best balance with limited data.
- **[Al-Sanaani et al. 2026](https://arxiv.org/abs/2601.04588):** the same idea for 3D left-atrial LGE MRI. SPADE-LDM reached FID 4.06, and synthetic data raised Dice from 0.908 to 0.936.

For this thesis, the SPADE mask-to-image model is the accepted baseline, and Edirisooriya 2026 is the closest evaluation recipe.

## Clinical-profile and covariate conditioning: the core papers

Five papers condition CMR generation on patient information, and only Cao 2026 does so on the same datasets as this thesis (ACDC and M&Ms).

| Paper | Conditions on | Model | Data | Conditioning checked? | Privacy tested? |
| --- | --- | --- | --- | --- | --- |
| [Campello 2022](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.983091/full) | Age gap, or BMI | Conditional GAN (WGAN-GP), U-Net generator | UK Biobank, 4-chamber ED, about 14,800 scans | Yes: age regressor, LV size, septum width, EF | No |
| [Skorupko 2025](https://arxiv.org/abs/2403.19508) | Text from sex, age, BMI, health condition, plus mask geometry | ControlNet on a diffusion model | UK Biobank | Partly: downstream bias test | Not tested |
| [Li 2025 (CPGG)](https://arxiv.org/abs/2505.03426) | Cardiac phenotypes from CMR | Two stages: phenotype generator, then masked autoregressive diffusion | Public and private datasets | Not described in the abstract | Not reported |
| [Cao 2026](https://arxiv.org/abs/2606.26764) | Diagnosis, slice count, ED, ES and EF volumes | 3D VAE-GAN plus two latent diffusion models | Trained on ACDC and Data Science Bowl; tested on M&Ms and M&Ms-2 | Yes: Pearson r 0.66 to 0.94 | No |
| [Rodríguez 2026](https://arxiv.org/abs/2608.24342) | Structured metadata and slice position as text | Pretrained latent diffusion model, adapted | UK Biobank, 59,058 short-axis images | Yes: subgroup metadata alignment | Not addressed |

**What they show.**

- **Campello 2022** is the clearest template for checking conditioning with an independent regressor. Adding 10% to 25% synthetic scans cut age-prediction error in age-imbalanced data (for one dataset, from 14.5 to 11.0 years against 12.7 in a balanced set). The authors state the model was not validated on real longitudinal scans and can produce clinical errors such as an incomplete septum.
- **Skorupko 2025** targets fairness: it adds scarce groups, such as diagnosed female patients and heart-failure patients with normal BMI, and runs on one consumer GPU.
- **Li 2025** shows phenotypes can condition cine CMR, and synthetic pretraining improved diagnosis and phenotype prediction. The page read gives no numbers or limitations.
- **Cao 2026** is the closest work to this thesis. It generates 4D cine data with masks, split into static anatomy and motion. Slice-wise FID was 72.21, and synthetic data raised cross-vendor Dice by 1.4% on average and cut Hausdorff distance by 3.0 mm. Higher guidance scales kept the volume trend but drifted from exact targets.
- **Rodríguez 2026** (submitted 25 August 2026) adapts a generative foundation model with metadata-free classifier-free guidance, contrastive batching and inverse-frequency sampling. FID was 37.47, 28.68% better than the earlier text-conditioned baseline that needs mask geometry. Disease-specific conditioning was the hardest task.

## Other patient-specific conditioning and related work

Beyond clinical variables, CMR generators have used ECG signals, and echocardiography already conditions on ejection fraction routinely.

- **[Fang et al. 2026, ECGFlowCMR](https://arxiv.org/abs/2601.20904)** (KDD 2026) generates cine CMR from a 12-lead ECG using a phase-aware masked autoencoder and a flow-matching transformer. It reports FID 37.28 and FVD 14.41, and phenotype R² rising from 0.454 to 0.470 with synthetic pretraining at 100% mixing. It uses UK Biobank plus a proprietary dataset, and no privacy test was seen.
- **[CardioDiT 2026](https://arxiv.org/abs/2603.25194)** is a 4D latent diffusion transformer trained on ACDC, M&Ms-2 and a private cohort. The main model is unconditional, and conditional generation was possible but not evaluated. It is the best example of checking EF distributions (Wasserstein distance 2.67 on public data).
- **Echocardiography:** [feature-conditioned cascaded video diffusion for echo](https://arxiv.org/abs/2303.12644), [ControlEchoSynth](https://arxiv.org/abs/2508.17631) and the [label-free motion-conditioned model](https://arxiv.org/abs/2512.09418) show that conditioning on EF is a mature idea in ultrasound. The EF-conditioned EchoSyn model beat the label-free model (FVD128 168.3 against 553.2). CMR has far fewer such papers.
- **[CineMA 2025](https://arxiv.org/abs/2506.00679)** is a foundation model for analysis, not a generator. It was pretrained on about 74,900 UK Biobank cine studies and evaluated on ACDC, M&Ms and M&Ms-2. CardioDiT uses its features to compute FID.
- **[Kumarasinghe et al. 2026](https://arxiv.org/abs/2603.24764)** (review) compares GAN, VAE, diffusion and flow-matching approaches on fidelity, utility and privacy, and notes mask and vendor-style conditioning. The abstract does not mention patient-level conditioning or "personalization".
- **Hosseini and Serag 2025** (per the author's notes) tests whether diffusion models keep disease-relevant features in lung and retinal images, so it supports the point that a realistic image is not enough, but it is not about cardiac MRI.

## How the field evaluates

Fidelity and utility are measured almost everywhere, conditioning is checked in about half of the profile-conditioned papers, and privacy is rare.

| Layer | What is done | Examples |
| --- | --- | --- |
| **Did the conditioning work?** | An independent regressor or measurements on generated images or masks, compared with the requested value | Campello 2022 (age regressor, LV size, EF); Cao 2026 (Pearson r 0.66 to 0.94 between requested and measured volumes); Rodríguez 2026 (subgroup metadata alignment); CardioDiT (EF distribution distance) |
| **Fidelity** | FID, and in some papers FVD, LPIPS, SSIM, PSNR | Campello (FID, PSNR); Cao (FID 72.21, FVD 288.08); Fang (FID 37.28); Rodríguez (FID 37.47); CardioDiT (FID 71.9 public, 21.2 private) |
| **Utility** | Train a segmentation or classification model on real, synthetic or mixed data and test on real data | Skandarani 2020 (Dice up 2 to 4 points); Cao 2026 (Dice up 1.4% on average); Amirrajab 2023 (trained on ACDC and M&Ms-1, tested on M&Ms-2) |
| **Privacy** | Nearest-neighbour distance, membership-inference attack, differential privacy | Edirisooriya 2026 (privacy assessed for three generators). The Kumarasinghe 2026 review lists these as the standard tests. None of the profile-conditioned papers above reports a privacy test in what was read. |

Two cautions apply when comparing numbers across papers.

- **FID values are not comparable across papers.** They depend on the dataset, the image size and the feature extractor (CardioDiT uses CineMA features, others typically use an ImageNet network). Compare FID only inside one's own experiments.
- **Segmentation gains depend on the baseline.** A 1.4% Dice gain on a strong nnU-Net is a different claim from a 10% gain over weak augmentation.

## Datasets used in the literature

Patient-variable conditioning (age, sex, BMI) lives on UK Biobank, while the ACDC and M&Ms papers condition on masks, diagnosis or volumes.

| Dataset | Used by | Clinical information it offers |
| --- | --- | --- |
| ACDC | Skandarani 2020, Amirrajab 2023, Cao 2026, CardioDiT, Edirisooriya 2026 | Diagnosis group, height, weight (no age or sex) |
| M&Ms | Amirrajab 2022 and 2023, Li, Ma and Shi 2025, Cao 2026, Edirisooriya 2026 | Pathology, vendor, centre, age, sex, weight |
| M&Ms-2 | Cao 2026, CardioDiT, Amirrajab 2023 (as test set) | Right-ventricle focus; metadata still to confirm |
| UK Biobank | Campello 2022, Skorupko 2025, Fang 2026, Rodríguez 2026 | Age, sex, BMI, health records; needs approval |
| Sunnybrook | Skandarani 2020 | Masks only |
| Kaggle Data Science Bowl | Cao 2026 (unlabelled training data) | Not used for conditioning |
| Private clinical sets | Li 2025, Fang 2026, CardioDiT | Not public |

The consequence for this thesis: age and sex conditioning needs UK Biobank, which is not available. On ACDC and M&Ms the realistic profile is diagnosis plus measured volumes and EF, plus weight and BMI where available. That matches what Cao 2026 did, so the novelty has to come from the design (a controlled baseline comparison, privacy and external validation) and not from richer variables.

## Comparison and gaps

No paper read combines profile conditioning, a check that it worked, a privacy test and a test on a second dataset; this thesis is designed to do all four.

| Paper | Profile conditioning | Checks conditioning | Privacy test | Tested on a second dataset |
| --- | --- | --- | --- | --- |
| Campello 2022 | Yes (age, BMI) | Yes | No | No (UK Biobank only) |
| Skorupko 2025 | Yes (text metadata) | Partly | Not tested | No (UK Biobank only) |
| Li 2025 | Yes (phenotypes) | Not described | Not reported | Yes (public and private) |
| Cao 2026 | Yes (diagnosis, volumes) | Yes | No | Yes (M&Ms, M&Ms-2) |
| Rodríguez 2026 | Yes (text metadata) | Yes (subgroups) | Not addressed | Not described |
| Fang 2026 | ECG, not a profile | Not stated | None seen | Yes (external cohort) |
| Edirisooriya 2026 | Masks only | Not applicable | Yes | Yes (ACDC and M&Ms, per the author's notes) |
| **This thesis (planned)** | Yes (diagnosis, volumes, BMI) | Yes | Yes | Yes (ACDC to M&Ms) |

The gaps, stated as carefully as the evidence allows:

1. **Privacy is missing from the profile-conditioned work.** None of the five core papers reports a privacy test in the pages read.
2. **There is no controlled comparison.** No paper was found that compares a conditioned model with its own unconditioned baseline, trained and evaluated the same way, and then tests privacy. The two-stage design (profile to mask, then mask to image with the baseline) isolates exactly this.
3. **The ACDC and M&Ms profile is thin.** Only diagnosis, volumes, EF, height and weight exist, and M&Ms DCM is milder than ACDC DCM. Reporting results by measured EF is a sensible response.
4. **Results are hard to compare.** FID depends on the feature extractor and dataset, so one fixed evaluation pipeline for every model in the study matters more than matching published numbers.
5. **2D versus 4D.** Cao 2026 and CardioDiT generate 4D data. 2D slices are a stated limitation, with 3D as an extension.

## Positioning and open questions

Position the thesis as the controlled, privacy-aware version of Cao 2026 on ACDC and M&Ms, with Edirisooriya 2026 as the evaluation recipe and Campello 2022 as the template for checking conditioning.

**Cite and discuss in the paper:** Cao 2026 (closest work), Rodríguez 2026 (newest metadata-conditioned work), Skorupko 2025, Campello 2022, Li 2025, Edirisooriya 2026 and Skandarani 2020 (SPADE baseline).

**Open questions to settle before writing:**

- Read the full text of Li 2025, Skorupko 2025 and Rodríguez 2026. Only abstracts and result summaries were seen, so privacy and conditioning-check claims for them could be incomplete.
- Read the full text of Cao 2026 for a privacy test or any baseline comparison that may have been missed, because it decides how strong the novelty claim can be.
- Check Amirrajab 2022 against the original paper. The literature table notes its row merges it with another paper.
- Fill in Chen 2022 and Kazerouni 2023 from their abstracts, or drop them to background.
- Fix the proposal: the Kumarasinghe 2026 abstract does not mention "personalization", and Hosseini and Serag 2025 is lung and retinal work, not cardiac.
- Re-run this search in late November and before submission, because this area is moving fast (Rodríguez 2026 appeared on 25 August 2026).

## References

Pages opened on 8 October 2026 unless marked. Check each reference's journal details against the publisher before citing.

- Al-Sanaani Y, Thornhill R, Rajan S (2026). [3D conditional image synthesis of left atrial LGE MRI from composite semantic masks](https://arxiv.org/abs/2601.04588). arXiv:2601.04588.
- Amirrajab S, Al Khalil Y, Lorenz C, Weese J, Pluim J, Breeuwer M (2023). [Pathology synthesis of 3D-consistent cardiac MR images using 2D VAEs and GANs](https://arxiv.org/abs/2209.04223). arXiv:2209.04223.
- Amirrajab S et al. (2022). Label-informed cardiac MR image synthesis through conditional GANs. Comput Med Imaging Graph. (from the literature table; not re-opened)
- Bernard O et al. (2018). [Deep learning techniques for automatic MRI cardiac multi-structures segmentation and diagnosis: is the problem solved?](https://hal.archives-ouvertes.fr/hal-01803621) IEEE Trans Med Imaging. (ACDC; found by search, not opened)
- Campello VM et al. (2021). [Multi-centre, multi-vendor and multi-disease cardiac segmentation: the M&Ms challenge](https://diposit.ub.edu/dspace/handle/2445/184038). IEEE Trans Med Imaging. (found by search, not opened)
- Campello VM, Xia T, Liu X, Sanchez P, Martín-Isla C, Petersen SE, Seguí S, Tsaftaris SA, Lekadir K (2022). [Cardiac aging synthesis from cross-sectional data with conditional generative adversarial networks](https://www.frontiersin.org/journals/cardiovascular-medicine/articles/10.3389/fcvm.2022.983091/full). Front Cardiovasc Med 9.
- Cao Y, Andrade-Miranda G, Zhang J, Zhao L, Gao X (2026). [Anatomy-guided residual motion diffusion for controllable 4D cardiac MRI synthesis](https://arxiv.org/abs/2606.26764). arXiv:2606.26764.
- Diller GP et al. (2020). Utility of deep learning networks for the generation of artificial cardiac magnetic resonance images in congenital heart disease. BMC Med Imaging. (from the literature table; page blocked)
- Edirisooriya M, Kawya D, Kumarasinghe I, Devindi I, Maleckar MM, Ragel R, Nawinne I, Thambawita V (2026). [Balancing fidelity, utility, and privacy in synthetic cardiac MRI generation: a comparative study](https://arxiv.org/abs/2603.04340). arXiv:2603.04340.
- Fang X et al. (2026). [ECGFlowCMR: pretraining with ECG-generated cine CMR helps cardiac disease classification and phenotype prediction](https://arxiv.org/abs/2601.20904). KDD 2026; arXiv:2601.20904.
- Fu Y et al. (2025). [A versatile foundation model for cine cardiac magnetic resonance image analysis tasks (CineMA)](https://arxiv.org/abs/2506.00679). arXiv:2506.00679.
- Hosseini and Serag (2025). Is synthetic data generation effective in maintaining clinical biomarkers? Front Artif Intell. (from the literature table; not re-opened)
- Kumarasinghe I, Kawya D, Edirisooriya M, Devindi I, Nawinne I, Thambawita V (2026). [Synthetic cardiac MRI image generation using deep generative models](https://arxiv.org/abs/2603.24764). arXiv:2603.24764.
- Li J, Ma X, Shi Y (2025). [Multi-label conditioned diffusion for cardiac MR image augmentation and segmentation](https://www.mdpi.com/2306-5354/12/8/812). Bioengineering 12(8):812.
- Li Z, Hu Y, Ding Z, Mao Y, Li H, Yi F, Zhang H, Huang Z (2025). [Phenotype-guided generative model for high-fidelity cardiac MRI synthesis](https://arxiv.org/abs/2505.03426). arXiv:2505.03426.
- Li Z, Reynaud H, Müller JP, Kainz B (2025). [Label-free motion-conditioned diffusion model for cardiac ultrasound synthesis](https://arxiv.org/abs/2512.09418). arXiv:2512.09418.
- Rodríguez M, Skorupko G, Aung N, Petersen SE, Lekadir K, Gkontra P (2026). [Metadata-aware adaptation of a generative foundation model for conditional CMR synthesis](https://arxiv.org/abs/2608.24342). arXiv:2608.24342.
- Seyfarth M et al. (2026). [CardioDiT: latent diffusion transformers for 4D cardiac MRI synthesis](https://arxiv.org/abs/2603.25194). arXiv:2603.25194.
- Skandarani Y, Painchaud N, Jodoin PM, Lalande A (2020). [On the effectiveness of GAN generated cardiac MRIs for segmentation](https://arxiv.org/abs/2005.09026). arXiv:2005.09026.
- Skorupko G, Osuala R, Szafranowska Z, Kushibar K, Dang VN, Aung N, Petersen SE, Lekadir K, Gkontra P (2025). [Fairness-aware data augmentation for cardiac MRI using text-conditioned diffusion models](https://arxiv.org/abs/2403.19508). arXiv:2403.19508 (v2, September 2025).

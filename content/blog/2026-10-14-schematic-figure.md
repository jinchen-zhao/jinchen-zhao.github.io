---
title: "Automating schematic figure making"
date: 2026-10-14
summary: "An open-source skill that lets LLMs draw schematic figures close to publication quality, and how we built and tested it."
draft: false
authors: [Jinchen Zhao, Logan Wright]
affiliation: LGW Lab, Yale University
image: gallery/prompt-holo-photo.jpg
canonical: "https://lgwrightlab.github.io/schematic-figure/"
canonical_name: "LGW Lab Blog"
---

Doing science is fun, but drawing the schematic figure that explains it has been challenging for us: we were never trained to do it, yet that figure is often the first thing a reader looks at. Inspired by some recent [viral videos made by Opus 5.5 on X](https://x.com/claudeai/status/2103515655760982273), we realized that the artistry of state-of-the-art AI models has probably already passed the level needed for publication-quality schematic figures. So we built a skill for it, open source on [GitHub](https://github.com/lgwrightlab/schematic-figure), and a benchmark to test it. It turns out that Opus 5.5 and GPT-6 Astra can make schematic figures close to publication quality on their own, once they are equipped with the right skill.

Below are a few example outputs from our skill. Importantly, we chose papers published after the training cutoff of Opus 5.5, so that the model has no memory of their figure designs. From the perspective of our expertise in physics and machine learning, we think the results are very good! Without the skill, Opus 5.5 already makes decent figures in one shot, but they are mostly flat boxes and arrows, and the text does most of the work. With the skill, the figures use illustrated scenes, many are proper 3D renders, and the figure carries the idea without leaning on text. If you are from another field and have suggestions on the figures, please let us know.

:::: {.gallery}
::: {.slide field="Physics" title="Trion Hall effect in electron–hole double layers" venue="Nature Physics (2026)" doi="10.1038/s41567-026-03444-8" license="CC BY 4.0" authors="Chaturvedi et al."}
![Published](gallery/phys-04-pub.jpg)
![No skill](gallery/phys-04-noskill.jpg)
![With skill](gallery/phys-04-ours.jpg)
:::

::: {.slide field="Chemistry" title="Divergent ring opening and functionalization of N-alkyl aziridines via boryl radical fragmentation" venue="Nature Chemistry (2026)" doi="10.1038/s41557-026-02247-x" license="CC BY 4.0" authors="Peng et al."}
![Published](gallery/chem-01-pub.jpg)
![No skill](gallery/chem-01-noskill.jpg)
![With skill](gallery/chem-01-ours.jpg)
:::

::: {.slide field="Biology" title="Scaling biodiversity-stability relationships from populations to meta-communities across trophic levels" venue="Nature Communications (2026)" doi="10.1038/s41467-026-75366-1" license="CC BY 4.0" authors="Wang et al."}
![Published](gallery/bio-01-pub.jpg)
![No skill](gallery/bio-01-noskill.jpg)
![With skill](gallery/bio-01-ours.jpg)
:::

::: {.slide field="Materials" title="Ultrafast directional hot carrier transfer in bilayer perovskite heterojunctions" venue="Nature Communications (2026)" doi="10.1038/s41467-026-76790-z" license="CC BY 4.0" authors="Liu et al."}
![Published](gallery/mat-20-pub.jpg)
![No skill](gallery/mat-20-noskill.jpg)
![With skill](gallery/mat-20-ours.jpg)
:::

::: {.slide field="Earth science" title="Faster-and-tighter nitrogen cycle supports mature forest productivity under elevated CO₂" venue="Science Advances (2026)" doi="10.1126/sciadv.aed2732" license="CC BY 4.0" authors="Rumeau et al."}
![Published](gallery/earth-12-pub.jpg)
![No skill](gallery/earth-12-noskill.jpg)
![With skill](gallery/earth-12-ours.jpg)
:::

::: {.slide field="Social science" title="Quantifying the prevalence and impact of overreaching causal claims in social science" venue="Nature Human Behaviour (2026)" doi="10.1038/s41562-026-02553-x" license="CC BY 4.0" authors="Isch et al."}
![Published](gallery/soc-02-pub.jpg)
![No skill](gallery/soc-02-noskill.jpg)
![With skill](gallery/soc-02-ours.jpg)
:::

::: {.slide field="Machine learning" title="Analog neural network–based wireless receiver" venue="Science Advances (2026)" doi="10.1126/sciadv.aeg7153" license="CC BY 4.0" authors="He et al."}
![Published](gallery/csml-13-pub.jpg)
![No skill](gallery/csml-13-noskill.jpg)
![With skill](gallery/csml-13-ours.jpg)
:::

::::

Notably, we trained this skill on published scientific papers' schematic figures, but what the skill has learned generalizes well beyond a completed paper. Prompts as short as one sentence and as long as a technical paper description can all give pretty good results, meaning you can also use it for making figures for your slide deck or an experimental report. Below is a gallery of figures we generated across domains with just a simple prompt of one or two sentences.

:::: {.gallery}
::: {.slide field="Physics"}
![No skill](gallery/prompt-holo-noskill.jpg "Prompt: “Draw an off-axis digital holography setup in 3D. Show the tilted reference beam, the camera, the recorded hologram, and its Fourier spectrum with the two sidebands”.")
![With skill](gallery/prompt-holo-ours.jpg "Prompt: “Use the schematic-figure skill. Draw an off-axis digital holography setup in 3D. Show the tilted reference beam, the camera, the recorded hologram, and its Fourier spectrum with the two sidebands”."){.default}
![Blender (illustration)](gallery/prompt-holo-blender.jpg "Prompt: “Use the schematic-figure skill. Draw an off-axis digital holography setup in 3D. Show the tilted reference beam, the camera, the recorded hologram, and its Fourier spectrum with the two sidebands. Render the setup in Blender”.")
![Blender (photoreal)](gallery/prompt-holo-photo.jpg "Prompt: “Use the schematic-figure skill. Draw an off-axis digital holography setup in 3D. Show the tilted reference beam, the camera, the recorded hologram, and its Fourier spectrum with the two sidebands. Render the setup in Blender with photoreal glass”.")
:::

::: {.slide field="Chemistry"}
![No skill](gallery/prompt-cv-noskill.jpg "Prompt: “Draw how cyclic voltammetry measures a reversible redox couple. Show the three-electrode cell, the triangular potential sweep, the diffusion layer at the electrode, and the resulting voltammogram with its two peaks”.")
![With skill](gallery/prompt-cv-ours.jpg "Prompt: “Use the schematic-figure skill. Draw how cyclic voltammetry measures a reversible redox couple. Show the three-electrode cell, the triangular potential sweep, the diffusion layer at the electrode, and the resulting voltammogram with its two peaks”.")
:::

::: {.slide field="Biology"}
![No skill](gallery/prompt-cas9b-noskill.jpg "Prompt: “Draw how CRISPR-Cas9 cuts DNA in 3D. Show the guide RNA, the PAM site and the two nuclease domains. Show which strand each nuclease domain cuts and where the cut falls relative to the PAM”.")
![With skill](gallery/prompt-cas9b-ours.jpg "Prompt: “Use the schematic-figure skill. Draw how CRISPR-Cas9 cuts DNA in 3D. Show the guide RNA, the PAM site and the two nuclease domains. Show which strand each nuclease domain cuts and where the cut falls relative to the PAM”.")
:::

::: {.slide field="Materials"}
![No skill](gallery/prompt-liion2-noskill.jpg "Prompt: “Draw why fast charging plates lithium on graphite. Show the Li⁺ concentration gradient across the electrolyte, the anode potential falling below 0 V vs Li, and metal forming on the particles”.")
![With skill](gallery/prompt-liion2-ours.jpg "Prompt: “Use the schematic-figure skill. Draw why fast charging plates lithium on graphite. Show the Li⁺ concentration gradient across the electrolyte, the anode potential falling below 0 V vs Li, and metal forming on the particles”.")
:::

::: {.slide field="Earth science"}
![No skill](gallery/prompt-elnino-noskill.jpg "Prompt: “Draw a cross-section of the equatorial Pacific in normal years and in El Niño years. Show the Walker circulation, the thermocline and the warm pool”.")
![With skill](gallery/prompt-elnino-ours.jpg "Prompt: “Use the schematic-figure skill. Draw a cross-section of the equatorial Pacific in normal years and in El Niño years. Show the Walker circulation, the thermocline and the warm pool”.")
:::

::: {.slide field="Social science"}
![No skill](gallery/prompt-echo2-noskill.jpg "Prompt: “Draw why a rumour crosses between two communities but a behaviour that needs two adopting neighbours stays trapped. Show both spreads on the same network with a few bridge people”.")
![With skill](gallery/prompt-echo2-ours.jpg "Prompt: “Use the schematic-figure skill. Draw why a rumour crosses between two communities but a behaviour that needs two adopting neighbours stays trapped. Show both spreads on the same network with a few bridge people”.")
:::

::: {.slide field="Machine learning"}
![No skill](gallery/prompt-flash-noskill.jpg "Prompt: “Draw how FlashAttention computes attention without storing the full attention matrix. Show the GPU's HBM and on-chip SRAM, the Q, K and V tiles moving between them, and the running softmax that is updated tile by tile”.")
![With skill](gallery/prompt-flash-ours.jpg "Prompt: “Use the schematic-figure skill. Draw how FlashAttention computes attention without storing the full attention matrix. Show the GPU's HBM and on-chip SRAM, the Q, K and V tiles moving between them, and the running softmax that is updated tile by tile”.")
:::

::::

We should be clear about two limits. First, we are not experts in most of these fields, so we cannot vouch for every detail of these figures. Second, these prompts describe well-established concepts. In our experience the skill does much worse on a novel concept, unless it gets a detailed technical description of it (more tips later).

So what is a skill, and how do you use it? In case you are new to AI agents: a skill is a folder that an AI model loads on top of its built-in abilities. It holds written instructions, and it can also hold code and tools. Our skill holds the instructions for making publication-ready figures, a drawing library, 3D kits and automatic checks. The figure below shows how an AI model works when you ask it to draw a figure without and with our skill.

![The same request, "Draw Fig. 1 for this paper", without and with the skill. With the skill, the drawing agent loads a folder of instructions (SKILL.md), drawing code, optional 3D kits, automatic checks and design references. Like every diagram in this post, this figure was drawn by the skill itself.](skill_vs_noskill.svg){#fig:skill}

Another nice feature of our skill is that the result is not just a picture. Suppose you use an image generation AI model, it will give you pixels, but the skill gives you the figure as vector graphics (SVG and PDF) together with the code that draws it. You can then open the file in Illustrator or Inkscape and move a label yourself. You can also ask the AI to change one thing, and it edits only that part.

Notably, the skill is not a free lunch. With the skill, the agent spends about four times longer on a figure, for both Opus 5.5 and GPT-6 Astra. But on average it still needs less than 20 minutes to make a finished schematic figure, which is of course worth the time!

![Minutes per figure for Opus 5.5 and GPT-6 Astra, without and with the skill, on the 50 test papers. Bars: means. Error bars: 95% intervals. Dots: one figure each.](plot_cost.svg){#fig:cost}

Here are some tips to use the skill in practice, having one of the below can usually lead to a satisfactory result in our experience:

- **Give it the full story.** A short request will work for well-known concepts. For a novel scientific concept, the skill needs a detailed technical description to work well. Example:

  > "Use the schematic-figure skill to design Fig. 1 for our paper [attach technical description]."

- **Show it a style to follow.** An example figure, from your earlier papers or one you admire, gives the skill a target for colours, line weights and level of detail. Example:

  > "Use the schematic-figure skill. Follow the colours and line weights of the attached figure from our last paper [attach example figure]. Draw our new device in the same style [attach technical description]."

- **Ask for several ideas at once.** We often run three agents in parallel on the same request. Each comes back with a different design, and we combine the best parts into one figure. Example:

  > "Use the schematic-figure skill. Make three different designs of this figure with three parallel agents for our paper [attach technical description] and combine them in a single sheet to show me."

If you just want to try the skill, download it from [our GitHub repo](https://github.com/lgwrightlab/schematic-figure) and give it to your favorite AI model. You can also ask the model to install the skill for you :). In the rest of this post we are going to share how we developed it and some lessons we have learned along the way.

## How did we develop the skill at this scale?

Developing such a skill rigorously is not an easy task. We collected at least 100 recently published papers from different fields of science, masked the figure-related text out of each paper, and asked the AI to design a schematic figure from what remains. Then we need to decide how good each result is (for example, with another AI model as the judge), work out how to improve the drawing, and iterate many times until the results are satisfactory.

All of this sounds like a big effort! But it turns out that Claude Code's built-in [dynamic workflows](https://code.claude.com/docs/en/workflows) make it much easier. You just prompt the system in natural language, for example: "find me 100 open-access papers in the subfield of ..., and prepare a dataset of figures and corresponding text descriptions of the technical part of each paper, with the figure information masked out". Claude then designs a gated pipeline that collects the dataset for you. The same idea applies to improving and evaluating the skill. Below is the workflow Claude built to collect our papers.

![The workflow that collected our papers. One prompt becomes a script: seven collector agents run in parallel, one per field. The papers are split into training and test papers. For each paper, a text writer removes the figure from the text, and a main-point writer lists the paper's main points.](collection_workflow.svg){#fig:collect}

## How do we score a figure?

After preparing the dataset, we need to figure out a way to quickly judge the quality of the generated figure. The metric is inspired by the Turing test: we test if an AI agent made figure can be distinguished by human made one by asking an evaluator (admittedly, an AI evaluator) if the resulting figure “looks published”. In particular, the metric is computed by showing an AI judge one figure and asking the judge to estimate how likely that figure was a published "Fig. 1", from 0 to 100. Before using it on our skill, we checked it on figures drawn without it. A good metric should rank the real published figure well above a plain AI drawing.

Running this evaluation on 50 test papers, we find that the "looks" published metric can distinguish AI generated figure reliably.

![The looks-published metric, checked on figures drawn without the skill: the published Fig. 1 against Opus 5.5 and GPT-6 Astra without the skill, on 50 test papers, with Opus 5.5 and Astra as judges. A good metric ranks the published figure first. Bars: means. Error bars: 95% intervals. Dots: one paper each.](plot_metric_check.svg){#fig:metric}

The judge's reasons show what it looks for. Here is its reason for one figure by Opus 5.5 without the skill:

> Without the skill (biology, scored 15 out of 100): "The figure has a uniform matplotlib look, with sentence-style panel titles, explanatory captions written into the panels, synthetic-looking heatmaps and plain box-and-arrow panels, which reads more like code-generated work than a professionally illustrated Nature Fig. 1."

Therefore, on our training set papers, we will be able to use those feedback from the evaluators to design our skills, and therefore in the next iteration see if this score is increased in the next iteration.

## How did the skill improve?

Before we start to develop and optimize a skill, we need to make sure our skill is generalizable. To make sure that we split the papers we collected to two groups: one training set and one test set. During the skill optimization stage we will only let AI models draw and evaluate themselves on the training set, and at last we will do evaluation on the test set papers so that we know the plotting skills we have developed are properly transferred and generalized to the test figures.

There are several useful tricks that we used (1) every time we launch an AI agent to finish a figure, in addition to the figure we also request it to give us suggestions on what is the biggest "friction" in our skill, and how to improve the skill (2) before we do the training, we can also first give AI agents published figures and ask it to fully reproduce it. These two points combined will construct a pretty good plotting library for AI agents for figure plotting. For example, we see that AI agents suggesting we construct a frequent component library, add blender and RDKit (an open-source chemistry toolkit) to the skill.

Then we simply run a Claude Code dynamic workflow to go through about 15 versions of the skill to try to increase the "looks published" score of the training figures. We stopped after about 15 versions because we observed the saturation of score increase. The whole workflow looks like following:

![The improvement loop. A drawing agent draws the training papers with the current skill, judges score them, Claude reads the judges' reasons and changes the skill, and the loop repeats. We steer it from time to time. After the last version the skill was frozen and drawn once on the test papers, whose results never fed back into the skill.](improve_loop.svg){#fig:loop}

We also want to note that this is not fully an AI autonomous process, we still closely monitor the behaviors of output figures and steer the workflow from time to time, for example below are some suggestions we gave Claude:

- **Jinchen:** "Make the figure fewer, bigger and bolder: fewer elements, larger text, and no big empty spaces." A layout survey then showed that published figures set their text about twice as large as ours, on 27 of 28 papers.
- **Logan:** "Mixing 3D and 2D is the biggest flaw: the light should go through the lens, not lie flat on the page with the lens pasted on top." Claude then added a small 3D light engine, and the light now enters, passes through and leaves each lens in the right order.

![Looks published, from 0 to 100, at each version of the skill on the training papers. Dashed lines: the published figures and Opus 5.5 without the skill. Error bars: 95% intervals. Dots: one paper each.](plot_history.svg){#fig:history}


## How does it do on new papers?

After "training" the skill we also evaluate the performance of it on our test set papers, using the same scoring mechanism. From the figure below we can see that under an Opus 5.5 evaluator, both models score twice as high as without the skill, and interestingly, with an Astra evaluator, Opus 5.5 with the skill can be comparable with published figures! We can see that Astra judge is not favoring its own model. The interesting remaining question is what leads to these distinct behaviors from evaluators from OpenAI and Anthropic?

![Looks published for the 50 test papers, from 0 to 100. Opus 5.5 and GPT-6 Astra each drew every paper with and without the skill. (a) Opus 5.5 as the judge. (b) GPT-6 Astra as the judge. Bars: means. Error bars: 95% intervals. Dots: one paper each.](plot_judges.svg){#fig:scores}

We looked into it, and below is an example skill-made figure where Opus and Astra judges disagree. The Opus judge thinks it does not "look published" for the following reason:

> Opus 5.5 judge (scored 35 out of 100; the published figure scored 85): "The figure is polished and physically coherent in Nature style, but its uniform code-drawn look (regular gradient wedges, generic octagon layers, sparse panel d with lots of empty space) suggests it was generated rather than produced by a journal art team."

The GPT-6 Astra judge sees the same figure very differently:

> GPT-6 Astra judge (scored 97 out of 100; the published figure scored 78): "The coherent multipanel layout, precise particle-physics notation, consistent visual styling, and polished detector and decay schematics strongly resemble a Nature-family introductory research figure."

:::: {.gallery}
::: {.slide field="Physics (test paper)" title="Exploring baryon semileptonic decays through polarization and entanglement" venue="Nature (2026)" doi="10.1038/s41586-026-10818-8" license="CC BY 4.0" authors="BESIII Collaboration"}
![Published](gallery/phys-17-pub.jpg)
![With skill](gallery/phys-17-ours.jpg)
:::
::::

So we can see that when asked the same question "whether the figure looks" published, Opus seem to enter a "detective" mode trying to identify which figure is code/AI generated, but Astra is viewing it in a more human/editor way.

And we observe that this is not a single example: out of the 50 figures scored by an Opus judge, 38 are scored lower than the published figure because they have some "code-drawn look". The ones it does not call code-drawn score 57 on average, close to the published figures' 63. You can imagine in real publishing, whether a schematic figure is code-drawn looking is probably not what matters most for communicating science.

## Do the figures carry the science?

So what matters for a schematic figure? We have been focusing on the artistry part of the figure so far (perhaps because that is the part we have always struggled most with), but scientific figures are not just about aesthetics! The purpose of these figures is to communicate visually specific critical information about the research. We need to make sure that the generated figures actually contain the important scientific information from the paper!

To test this, we design a workflow where a blind reader sees only the figure and lists what it claims. A scorer then checks the list against the paper's main points, which another agent wrote from the full text. On 21 test papers, readers recall more main points from the skill's figures than from the published ones, with fewer words on the figure. Figures drawn without the skill score highest, but they carry almost three times as many words. The paper's title alone gives 0.10, the floor of this score.

![How main-point recall is scored, on one training paper. A blind reader sees only the figure and writes down what it claims. A scorer, who sees the paper and its main points but not the figure, marks each main point as conveyed, partial or missed.](recall_example.svg){#fig:recallex}

![Main points a blind reader recalls from the figure alone, on 21 test papers, from 0 to 1. The label under each bar gives the figure's mean number of words. Dashed line: the paper's title alone. Bars: means. Error bars: 95% intervals. Dots: one paper each.](plot_recall_test.svg){#fig:recall}

## What has the skill learned?

Looking back at all the versions, the skill mainly taught the agent three kinds of things:

- The most important is a design process. Before it writes any code, the agent reads the paper, sketches a few concepts, builds two drafts, picks one and critiques it like a reviewer would. Without the skill, the agent usually goes straight to drawing. 

- The second is a toolbox: parts for each field, a molecule tool, Blender for 3D objects and a small engine that draws light through lenses. 

- The third is a set of automatic checks that catch overlapping labels, tiny text and sentence-style headings before a person ever sees the figure.

![What the skill adds. The agent works through the steps along the top. Each lane is one part of the skill.](skill_anatomy.svg){#fig:anatomy}

But do they really matter and which part matters more? We removed one part at a time and redrew the 28 training papers. Removing the design process lowers the score under both judges. Removing any other part does not measurably change it, although under the Astra judge every removal costs a few points on average. However, you can imagine that items like parts library may lead to more token savings because the agents won't need to draw them from scratch, automatic check items like avoiding collisions or aligning the labels can be less apparent to vision models than experienced human researchers. So we expect every component to be helpful here.

![Change in looks published when one part of the skill is removed, on the 28 training papers. (a) Opus 5.5 as the judge. (b) GPT-6 Astra as the judge. Bars: mean change. Error bars: 95% intervals. Dots: one paper each.](plot_ablation.svg){#fig:ablation}

## How does it do in our own field?

We also test on a few of Logan's papers on physical neural networks and optical computing. From our expertise they can convey the main ideas of the papers very well.

:::: {.gallery}
::: {.slide field="Physical neural networks" title="Deep physical neural networks trained with backpropagation" venue="Nature (2022)" doi="10.1038/s41586-021-04223-6" license="CC BY 4.0" authors="Wright et al."}
![Published](gallery/lab-pnn-pub.jpg)
![With skill](gallery/lab-pnn-ours.jpg)
:::

::: {.slide field="Few-photon optical neural network" title="An optical neural network using less than 1 photon per multiplication" venue="Nature Communications (2022)" doi="10.1038/s41467-021-27774-8" license="CC BY 4.0" authors="Wang et al."}
![Published](gallery/lab-onn-pub.jpg)
![With skill](gallery/lab-onn-ours.jpg)
:::

::: {.slide field="Optical image sensing" title="Image sensing with multilayer nonlinear optical neural networks" venue="Nature Photonics (2023); figure from the arXiv version" doi="10.48550/arXiv.2207.14293" license="CC BY 4.0 (arXiv version)" authors="Wang et al."}
![Published](gallery/lab-sensing-pub.jpg)
![With skill](gallery/lab-sensing-ours.jpg)
:::

::: {.slide field="Multimode wave control" title="Arbitrary control over multimode wave propagation for machine learning" venue="Nature Physics (2025)" doi="10.1038/s41567-025-03094-2" license="CC BY 4.0" authors="Onodera et al."}
![Published](gallery/lab-multimode-pub.jpg)
![With skill](gallery/lab-multimode-ours.jpg)
:::

::: {.slide field="On-chip nonlinear photonics" title="Programmable on-chip nonlinear photonics" venue="Nature (2025)" doi="10.1038/s41586-025-09620-9" license="CC BY 4.0" authors="Yanagimoto et al."}
![Published](gallery/lab-onchip-pub.jpg)
![With skill](gallery/lab-onchip-ours.jpg)
:::
::::

But we can also spot some technical errors in the plot, for example in the deep physical neural network figure, the pulse shaper is drawn incorrectly because different wavelengths should be recombined into a single pulse (e.g. using a grating). The figure also splits parameters and data incorrectly: the experiment used an affine transformation of the input, $x \to a \odot x + b$, where $a$ and $b$ are the trained parameters.  


## Where does this leave us?

As amazing as this is, we are not suggesting that anyone can outsource figure design to AI. What the skill changes is speed and ambition: we can try many more designs much faster. We still need careful judgement and deep thought about what the figure should show.

Two lessons from this project apply well beyond figures. First, it is better to let AI models work in code than pixels (like diffusion models), since it is much easier for code to be checked, edited and rerun. [Surya’s post on training Qwen to paint with code](https://surya.website/rling-qwen-to-paint-with-code) reaches the same conclusion from a different direction. Second, we think automatic hillclimbing a well defined evaluator with AI will become much more efficient than traditional R&D for at least some large class of research problems. Just as we finished this skill, Anthropic described [the same recipe](https://claude.dev/blog/automating-eval-design-and-hillclimbing/) for any Claude application, including built-in commands that build the evaluation and run the hillclimbing for you.

At last we do want to note that after the model release of GPT-6 Astra and Opus 5.5 we are seeing a very obvious jump in model capability and this vision and drawing capability is just one of them. In many other aspects of our daily research these latest models have fully transformed our way to do research. We will use this lab blog to keep sharing our experience with these latest models, for example how this "intelligence jump" has allowed fully autonomous AI driven optical experimental systems.

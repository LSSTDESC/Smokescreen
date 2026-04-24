---
title: '`Smokescreen`: A Python package for data vector blinding and encryption in cosmological analyses'
tags:
  - Python
  - cosmology
  - blinding
  - dark energy
  - weak lensing
  - survey science
  - data analysis
authors:
  - name: Arthur Loureiro
    orcid: 0000-0002-4371-0876
    corresponding: true
    affiliation: "1, 2"
  - name: Jessica Muir
    orcid: 0000-0002-7579-770X
    affiliation: "3"
  - name: Jonathan Blazek
    orcid: 0000-0002-4687-4657
    affiliation: "4"
  - name: Nora Elisa Chisari
    orcid: 0000-0003-4221-6718
    affiliation: "5, 6"
  - name: Pedro H. Costa Ribeiro
    orcid: 0009-0007-9603-8335
    affiliation: "7, 8"
  - name: Christos Georgiou
    orcid: 0000-0001-9707-0109
    affiliation: "9"
  - name: C. Danielle Leonard
    orcid: 0000-0002-7810-6134
    affiliation: "10"
  - name: Bruno Moraes
    orcid: 0000-0002-5898-0975
    affiliation: "11, 7"
  - name: Marc Paterno
    orcid: 0000-0003-0808-8388
    affiliation: "12"
  - name: "Nikolina Šarčević"
    orcid: 0000-0001-7301-6415
    affiliation: "13"
  - name: "Tilman Tröster"
    orcid: 0000-0003-3520-2406
    affiliation: "14"
  - name: Sandro D. P. Vitenti
    orcid: 0000-0002-4587-7178
    affiliation: "8"
  - name: the LSST Dark Energy Science Collaboration
affiliations:
  - index: 1
    name: Oskar Klein Centre for Cosmoparticle Physics, Department of Physics, Stockholm University, Stockholm, SE-106 91, Sweden
  - index: 2
    name: Astrophysics Group, Blackett Laboratory, Imperial College London, London SW7 2AZ, UK
  - index: 3
    name: University of Cincinnati, Cincinnati, Ohio 45221, USA
  - index: 4
    name: Department of Physics, Northeastern University, Boston, MA 02115, USA
  - index: 5
    name: Institute for Theoretical Physics, Utrecht University, Princetonplein 5, 3584 CC, Utrecht, the Netherlands
  - index: 6
    name: Leiden Observatory, Leiden University, Niels Bohrweg 2, 2333 CA, Leiden, the Netherlands
  - index: 7
    name: "Instituto de Física, Universidade Federal do Rio de Janeiro, Cidade Universitária, Rio de Janeiro, 21941-909, Brazil"
  - index: 8
    name: "Departamento de Física, Universidade Estadual de Londrina, Rod. Celso Garcia Cid, Km 380, 86057 970, Londrina, Paraná, Brazil"
  - index: 9
    name: "Institut de Física d'Altes Energies (IFAE), The Barcelona Institute of Science and Technology, Campus UAB, 08193 Bellaterra (Barcelona), Spain"
  - index: 10
    name: School of Mathematics, Statistics and Physics, Newcastle University, Newcastle upon Tyne, NE1 7RU, United Kingdom
  - index: 11
    name: "CBPF - Centro Brasileiro de Pesquisas Físicas, 22290-180, Rio de Janeiro, RJ, Brazil"
  - index: 12
    name: Fermi National Accelerator Laboratory, Batavia, IL 60510-0500, U.S.A.
  - index: 13
    name: Department of Physics, Duke University, Science Dr, Durham, NC 27710, USA
  - index: 14
    name: Institute for Particle Physics and Astrophysics, ETH Zurich, 8093 Zurich, Switzerland
date: 24 April 2026
bibliography: paper.bib
---

# Summary

Smokescreen is an open-source Python library for data-vector concealment (blinding) in cosmological analyses.
Data-vector blinding works by applying cosmology-dependent shifts to the observed data vector, moving it away from the true cosmological signal without affecting its statistical properties, so that analysts cannot infer the true result until the analysis is frozen and the blinding is lifted.
The package computes these shifts using Firecrown[^1] likelihoods applied to data vectors stored in the SACC format[^2], ensuring that the theoretical model used for blinding is identical to that used for inference whilst remaining agnostic to the specific observable being blinded.
To prevent accidental unblinding, the original SACC file, containing the true cosmology, is encrypted.
Although developed for the Vera C. Rubin Observatory Legacy Survey of Space and Time (LSST), Smokescreen is applicable to any experiment using Firecrown likelihoods and the SACC data format.

[^1]: [https://firecrown.readthedocs.io/en/latest/](https://firecrown.readthedocs.io/en/latest/)
[^2]: [https://sacc.readthedocs.io/en/latest/intro.html](https://sacc.readthedocs.io/en/latest/intro.html)

# Statement of need

Modern cosmological analyses require robust data concealment (blinding) strategies to prevent experimenter bias.
Cosmological experiments are particularly challenging to blind due to a fundamental limitation: we can only observe one Universe, making it extremely hard to design analyses in a double-blind or even single-blind manner.
Additionally, cosmological signals are not localized events but statistical patterns distributed across large data sets such as correlation functions or power spectra, leaving no clear "signal region" that can simply be hidden.
Without a principled approach, analysts risk unconsciously tuning their pipelines towards an expected result or towards the results of other experiments, compromising the scientific integrity of the measurement.

@Muir2020 formalised this discussion by defining three criteria for a reliable data concealment strategy: **(I)** the concealment must hide the true results while producing a physically reasonable posterior that preserves known parameter degeneracies; **(II)** it must retain the ability to perform validation tests, including goodness-of-fit and systematic null tests; and **(III)** it must be straightforward to implement and unblind, while still preventing accidental unblinding.
@Muir2020 further showed that applying cosmology-dependent shifts in data vector space satisfies all three requirements.

Smokescreen follows this approach: given a reference cosmology and a randomly-drawn blinded cosmology, it computes the difference between the corresponding theory predictions and applies the shift to the observed data vector.
With LSST Y1 data forthcoming and DESC analyses [@2012-LSST_DESC] requiring a collaboration-wide blinding strategy, no existing tool in the DESC software ecosystem (or outside it) provided a standardised implementation of this method.
Smokescreen was developed to fill this gap.

# State of the field

Blinding in cosmological surveys can be implemented at several stages of the analysis pipeline.
Catalogue-level methods [e.g., @2016MNRAS.460.2245J; @Brieden2020] provide robust concealment but are difficult to implement, particularly for multi-probe experiments.
Posterior-level methods [e.g., @Conley2006] are simple but leave the data vectors unblinded throughout the analysis.
Covariance-level blinding [@Sellentin2020] is mathematically elegant but harder to apply in practice, as covariance matrices in multi-probe analyses are constructed in a variety of ways — analytically, from simulations, or via resampling methods, for example.
Data vector blinding [@Muir2020] provides a practical compromise, offering stronger guarantees than posterior-level methods while remaining easier to implement than catalogue- or covariance-level methods.

The Dark Energy Survey [@2026-DES], Kilo Degree Survey [@2025-KiDS_Legacy], and Hyper Suprime-Cam [@2023-HSC] have used combinations of these strategies in their analyses, but these implementations were largely *ad hoc* and not easily reusable.
Smokescreen provides a dedicated open-source library for data vector blinding designed to integrate with collaboration-wide analysis pipelines.
By making the concealment procedure transparent and reproducible, it also allows the wider community to inspect and verify how blinding shifts are computed prior to and post unblinding.

# Software design

Smokescreen is structured around a single primary abstraction, the `ConcealDataVector` class, with thin command-line and encryption wrappers layered on top.
The design follows a separation-of-concerns principle keeping four responsibilities independent: **(I)** cosmological parameter perturbation (`param_shifts.py`), **(II)** theory vector computation via an external likelihood framework (`datavector.py`), **(III)** data security (`encryption.py`), and **(IV)** user-facing orchestration (`__main__.py`).
This structure allows any Firecrown[^3]-compatible likelihood to be used, guaranteeing that the theoretical modelling used for concealment is identical to that used for inference, preserving Criterion II of @Muir2020. Smokescreen can perform shifts in any of the base cosmological parameters present in CCL [@2019-Chisari-CCL].

[^3]: Firecrown is DESC's likelihood library, see [https://github.com/LSSTDESC/firecrown](https://github.com/LSSTDESC/firecrown) for more information.

Smokescreen's test suite is implemented using `pytest` and currently achieves 94% code coverage as tracked by `Codecov`.
Rather than merely checking array shapes or return types, tests verify physical correctness: for instance, that additive and multiplicative blinding factors are computed exactly as prescribed by \ref{eq:theory_vecs}–\ref{eq:factors}, that SACC consistency checks raise errors on data vector or covariance mismatches to floating-point tolerance, that invalid parameter keys or shift distributions are caught at instantiation, and that the full concealment pipeline, from shift sampling through to the saved output file and its metadata, produces the expected result end-to-end.

## Core blinding algorithm

Smokescreen implements the data vector blinding methodology of @Muir2020 in five steps.
First, for each cosmological parameter $\theta_i$ the user specifies the parameters of a shift distribution (deterministic, flat uniform, or Gaussian; see *Parameter shift strategies* below) from which $\Delta\theta_i$ is drawn.
Second, a concealed cosmology is constructed:

$$
\boldsymbol{\theta}_{\rm blind} = \boldsymbol{\theta}_{\rm ref} +
\boldsymbol{\Delta\theta}.
\label{eq:blind_cosmo}
$$

where $\theta_{\rm ref}$ is a reference cosmology defined by the user. Third, the theory vector, $T(\boldsymbol{\theta},\boldsymbol{s})$, is evaluated by the Firecrown likelihood object at both cosmologies with nuisance parameters $\boldsymbol{s}_{\rm ref}$ fixed at their reference values:

$$
\mathbf{d}_{\rm ref} = T\!\left(\boldsymbol{\theta}_{\rm ref},\,
\boldsymbol{s}_{\rm ref}\right), \qquad
\mathbf{d}_{\rm blind} = T\!\left(\boldsymbol{\theta}_{\rm blind},\,
\boldsymbol{s}_{\rm ref}\right).
\label{eq:theory_vecs}
$$

Fourth, a blinding factor is computed in either additive or multiplicative form:

$$
f^{\rm add} = \mathbf{d}_{\rm blind} - \mathbf{d}_{\rm ref}, \qquad
f^{\rm mult} = \mathbf{d}_{\rm blind} \,/\, \mathbf{d}_{\rm ref},
\label{eq:factors}
$$

applied according to the observable. Fifth, the factor is applied to the measured data vector:

$$
\hat{\mathbf{d}} = \mathbf{d}_{\rm obs} + f^{\rm add} \quad \text{or} \quad
\hat{\mathbf{d}} = \mathbf{d}_{\rm obs} \cdot f^{\rm mult}.
\label{eq:blind_datavec}
$$

Fixing $\boldsymbol{s}_{\rm ref}$ in both evaluations ensures the blinding factor carries only the cosmological shift, leaving the covariance matrix unchanged and allowing standard inference pipelines to run on $\hat{\mathbf{d}}$ without modification.

## Software architecture

Figure \ref{fig:architecture} shows the workflow as a sequential data-flow diagram.
The `ConcealDataVector` class orchestrates the process: it evaluates the theory vectors (\ref{eq:theory_vecs}–\ref{eq:factors}), applies the blinding factor (\ref{eq:blind_datavec}), and writes the output SACC file[^4].

[^4]: The SACC file format stores correlations, covariances, and associated metadata for cosmological analyses.

Two validation guards prevent common configuration errors.
`_verify_sacc_consistency()` checks the return SACC from the likelihood matches the user's input to floating-point tolerance ($10^{-10}$), while `_check_amplitude_parameter()` ensures consistent specification of the amplitude parameters $A_s$/$\sigma_8$ across the reference cosmology, Firecrown's `CCLFactory`[^5], and the shift dictionary.

[^5]: Firecrown interfaces with the DESC Core Cosmology Library, CCL [@2019-Chisari-CCL].

Supporting modules handle parameter shift generation (`param_shifts.py`, implemented as a stateless module for independent unit testing and modularity), symmetric encryption via `Fernet`[^6] (`AES-128-CBC + HMAC-SHA256` with a fresh key per blinding operation) (`encryption.py`, also exposed through command line interface (CLI) subcommands), and SACC format auto-detection with cosmology construction (`utils.py`).

[^6]: [https://github.com/pyca/cryptography](https://github.com/pyca/cryptography)

![Smokescreen data-flow architecture. Solid arrows show the main execution sequence; dashed arrows show outputs produced by each step; green boxes show outputs. `datavector_main()` orchestrates `ConcealDataVector`, which triggers encryption; `encrypt_main()` provides a standalone encryption path; `decrypt_main()` restores the original SACC file given the `.encrpt` and `.key` files.](figures/Smokescreen_diagram.pdf){#fig:architecture width="100%"}

## Firecrown likelihood integration

Smokescreen requires only a Python module exporting a `build_likelihood(build_parameters)` factory returning a `(Likelihood, ModelingTools)` tuple conforming to the Firecrown interface — the same interface used by Firecrown with the `CosmoSIS`/`Cobaya`/`NumCosmos` [@2015-Cosmosis; @2021-Cobaya; @Vitenti2012c, respectively] connectors.
Therefore, existing likelihood modules do not require modification.

## Parameter shift strategies

Three shift distributions are implemented: deterministic ($\theta_i^{\rm blind} = \rm{const}$), uniform ($\theta_i^{\rm blind} \sim \mathcal{U}(a,b)$), and Gaussian ($\theta_i^{\rm blind} \sim \mathcal{N}(\mu,\sigma)$).
Reproducibility is ensured through integer or string seeds, with strings mapped to `NumPy`-compatible integers via `MD5` hashing.
Unknown parameter keys raise a `ValueError` during validation, preventing silent misapplication of shifts.

## Security and data integrity

After the concealed SACC file is written, the original is encrypted with `Fernet` and deleted by default.
The `.key` file is stored separately from the `.encrpt` data file, allowing a blinding committee to distribute them through independent channels.
The blinded SACC embeds audit metadata (seed, timestamp, username) sufficient to reconstruct the blinding configuration without external logs.

## CLI and configuration

Smokescreen exposes three subcommands — `datavector`, `encrypt`, and `decrypt` — implemented with `jsonargparse`[^7].
Arguments may be provided as command-line interface (CLI) flags or through a `YAML` configuration file (`--config  config.yaml`); `--print_config` displays the current argument schema.
The `reference_cosmology` argument accepts a partial parameter dictionary, completed using `pyccl.CosmologyVanillaLCDM` [@2019-Chisari-CCL] defaults.
Input/output format (`FITS` or `HDF5`) is auto-detected and preserved.

[^7]: [https://github.com/omni-us/jsonargparse/](https://github.com/omni-us/jsonargparse/)

# Application: LSST Y1 3×2pt concealment

We demonstrate Smokescreen on a simulated LSST Y1 3×2pt data vector comprising cosmic shear $C_\ell^{\gamma\gamma}$, galaxy–galaxy lensing $C_\ell^{g\gamma}$, and galaxy clustering $C_\ell^{gg}$ [@Prat2023] across five tomographic redshift bins, yielding 415 data points sampled at 20 log-spaced multipoles $\ell \in [20, 2000]$ with the samples containing galaxy clustering restricted to scales $k\leq 0.1$ Mpc$^{-1}$.

### Smokescreen configuration

Two blinded realisations ("Blind A" and "Blind B") were produced with deterministic $A_s$ and $w$ shifts from the fiducial value $A_{s}^{\rm fid} = 1.9019 \times 10^{-9}$, and $w^{\rm fid}=-1.0$.

Blind A settings are:

```yaml
path_to_sacc: "./sacc_forecasting_y1_3x2pt.sacc"
likelihood_path: "./3x2pt_likelihood.py"
output_suffix: "blind_A"
shifts_dict:
    A_s: 2.00e-09  # +5.2% shift from fiducial
    w: -1.1  # +10.0% shift from fiducial
shift_distribution: "flat"
systematics:
    lens0_bias: 1.2497
    lens1_bias: 1.3809
    lens2_bias: 1.5231
    lens3_bias: 1.6716
    lens4_bias: 1.8245
    ia_bias: 1.0
    alphaz: 0.0
    z_piv: 0.62
reference_cosmology:
    A_s: 1.9019e-09
    Omega_c: 0.2906
keep_original_sacc: true
```

While Blind B uses:

```yaml
output_suffix: "blind_B"
shifts_dict:
    A_s: 1.80e-09  # -5.2% shift from fiducial
    w: -0.9  # -10.0% shift from fiducial
```

and is otherwise identical.

In a non-determinist shift case, the user would specify a list with two values, e.g. the limits of a uniform distribution and a seed:

```yaml
shifts_dict:
    A_s: [1.70e-09, 2.20e-09]
    w: [-1.3, -0.8]
shift_distribution: "flat"
seed: 2112
```

Finally, the concealment of the data vector is invoked as:

```
smokescreen datavector --config conceal_lsst_y1_3x2pt_blind_[A/B].yaml
```

producing `sacc_forecasting_y1_3x2pt_blind_[A/B].sacc` and an encrypted copy of the original. The resulting concealed data vectors are shown in Figure \ref{fig:data-vectors}.

![Example of multi-probe concealment for a simulated LSST Y1 3×2pt data vector: (left) cosmic shear, (middle) galaxy clustering, and (right) galaxy–galaxy lensing. Green circles show the original data vector ($A_s=1.9\times10^{-9}$, $w=-1.0$). Red squares (purple triangles) show *Blind A* (*Blind B*), produced by deterministic shifts to $A_s=2.0\times10^{-9}$, $w=-1.1$ ($A_s=1.8\times10^{-9}$, $w=-0.9$).](figures/datavector_shift_As_Omega_c_w0.pdf){#fig:data-vectors width="100%"}

## Cosmological validation

Following @Muir2020, valid concealment shifts should move the posterior best-fit sufficiently to blind the posterior while leaving the goodness-of-fit unchanged (Criterion II).
We verify this with a lightweight inference over three cosmological parameters: $A_s$, $w$, and $\Omega_{\rm cdm}$ only[^8], using CosmoSIS [@2015-Cosmosis] and the same Firecrown likelihood supplied to Smokescreen.
Deterministic shifts allow direct comparison with the known input cosmology.
A full validation on realistic simulated analyses, including the complete parameter space and systematics, will be presented in a forthcoming LSST DESC study.

[^8]: Note that only $A_s$ and $w$ are concealed in this test, while $\Omega_{\rm cdm}$ is kept the same.

Figure \ref{fig:triangle} confirms the expected behaviour: posteriors shift towards the blinded cosmology, whilst the goodness-of-fit remains unchanged ($\chi^2_{\rm red} = 0$ for the noiseless fiducial vector).
The Bayesian log-evidence $\log Z$, computed via `Nautilus` [@nautilus], is likewise unaffected: $|\Delta\log Z| \leq 1$ for both blinded runs (Blind A: $-0.97$, Blind B: $-0.47$), which is inconclusive on the Jeffreys scale and confirms the blinded analyses are statistically indistinguishable from the unblinded one. The results are summarised in Table \ref{tab:evidence}.

| | $A_s\times10^{-9}$ | $w$ | $\Omega_{\rm cdm}$ | $\chi_{\rm red}^2$ | $\log Z$ |
|---|---|---|---|---|---|
| True Cosmology | $1.88$ | $-0.99$ | $0.292$ | $0.0039$ | $-16.67 \pm 0.03$ |
| Blind A | $1.97$ | $-1.09$ | $0.294$ | $0.0084$ | $-17.64 \pm 0.03$ |
| Blind B | $1.79$ | $-0.90$ | $0.290$ | $0.0069$ | $-17.14 \pm 0.03$ |

: Best fit values, goodness-of-fit, and log-evidence for all three cases in Figure \ref{fig:triangle}. \label{tab:evidence}

![Marginalised 1D and 2D posterior distributions from cosmological inference on the data vectors shown in Figure \ref{fig:data-vectors}, using the same Firecrown likelihood provided to Smokescreen. The true cosmology (cyan), Blind A (red), and Blind B (purple) posteriors shift consistently towards their respective input concealing cosmologies, marked by filled circles and dashed lines. Cross markers indicate the posterior best-fits reported in Table \ref{tab:evidence}. Note that $\Omega_{\rm cdm}$ was not shifted by Smokescreen, yet its posterior shifts a tiny amount as a consequence of the known $A_s$–$\Omega_{\rm cdm}$–$w$ degeneracy, demonstrating that Criterion I is satisfied.](figures/triangle_plot.pdf){#fig:triangle width="90%"}

# Research impact statement

Smokescreen is designed as a standard blinding infrastructure for LSST DESC cosmological analyses ahead of LSST's decade-long survey.
It eliminates inconsistencies between blinding and inference models that can arise from independent *ad hoc* implementations across analysis teams.
Adoption is already extending beyond LSST DESC: the KiDS collaboration is using Smokescreen to blind their upcoming $6\times2$pt legacy analysis, demonstrating its applicability to any experiment using Firecrown likelihoods and the SACC format.
More broadly, we hope Smokescreen will help drive the community towards more consistent, open, and verifiable blinding infrastructures ahead of the Stage-IV survey era.

# Availability

**Source:** [github.com/LSSTDESC/Smokescreen](https://github.com/LSSTDESC/Smokescreen/tree/main)
**License:** BSD 3-Clause License.
**Install (conda):** `conda install -c conda-forge lsstdesc-smokescreen`
**Install (PyPI):** `pip install smokescreen`
**Documentation:** [lsstdesc.org/Smokescreen/](https://lsstdesc.org/Smokescreen/)
**Examples:** [github.com/LSSTDESC/Smokescreen/tree/main/examples](https://github.com/LSSTDESC/Smokescreen/tree/main/examples)
**Notebooks:** [github.com/LSSTDESC/Smokescreen/tree/main/notebooks](https://github.com/LSSTDESC/Smokescreen/tree/main/notebooks)

# AI usage disclosure

Generative AI tools, including GitHub Copilot and Claude Code, played a minor supporting role in the development of Smokescreen, primarily in the generation of unit tests and in resolving small, localised bugs.
All AI-assisted code was reviewed and edited by the authors before being incorporated into the codebase.
The core design of the library, its scientific grounding, and all key implementation decisions were made entirely by the authors.
The writing in this paper is our own; AI assistance was limited to occasional grammar corrections and light rephrasing to improve fluency, as several of the authors are non-native English speakers.

# Acknowledgments

This paper has undergone internal review in the LSST Dark Energy Science Collaboration. We thank Joe Zuntz and Jayme Ruiz-Zapatero for acting as DESC internal reviewers for this work.
AL acknowledges support from the Swedish National Space Agency (Rymdstyrelsen) under Career Grant Project Dnr 2024-00171 and from the research project grant 'Understanding the Dynamic Universe' funded by the Knut and Alice Wallenberg Foundation under Dnr KAW 2018.0067. Smokescreen was developed as a part of the Stockholm University in-kind software contributions to the Vera Rubin Observatory's Legacy Survey of Space and Time. CG is funded by the MICINN project PID2022-141079NB-C32. IFAE is partially funded by the CERCA program of the Generalitat de Catalunya. NŠ is supported in part by the OpenUniverse effort, which is funded by NASA under JPL Contract Task 70-711320, 'Maximizing Science Exploitation of Simulated Cosmological Survey Data Across Surveys.' TT acknowledges funding from the Swiss National Science Foundation under the Ambizione project PZ00P2\_193352

# Software acknowledgments

This project is largely possible thanks to several key software tools and packages.
We gratefully acknowledge the Python programming language, without which this work would not have been possible.[^9]
Our development and analysis efforts relied heavily on essential Python libraries, including: NumPy [@numpy], SciPy [@scipy], Matplotlib [@matplotlib], ChainConsumer [@Hinton2016], AstroPy [@astropy:2013; @astropy:2018; @astropy:2022], HDF5 [@andrew_collette_2022_6575970]
and cosmology packages like CCL [@2019-Chisari-CCL], CosmoSIS [@2015-Cosmosis],
CAMB [@Lewis2000; @Howlett2012], HMCode2020 [@2021MNRAS.502.1401M], and NaMaster [@2019MNRAS.484.4127A].

We also acknowledge the use of Jupyter Notebooks [@jupyter] as an interactive computing environment for prototyping and documenting analyses.

[^9]: [https://www.python.org](https://www.python.org)

# Author contributions

We outline the different contributions below using keywords based on the Contribution Roles Taxonomy (CRediT; @brand15).
**AL (core developer & maintainer of Smokescreen):**
Conceptualization, Methodology, Software, Validation, Formal analysis,
Investigation, Resources, Writing - Original Draft, Visualization, Project administration;
**JM:** Conceptualization, Methodology, Project administration;
**JB:** Conceptualization, Project administration;
**NEC:** LSST DESC Builder, contributor to `pyCCL`;
**PHCR:** Data Curation, Software*;
**CG:** Software;
**CDL:** LSST DESC Builder, contributor to `pyCCL`;
**BM:** Software*;
**MP:** Software;
**NŠ:** Writing - Review & Editing, Visualization;
**TT:** LSST DESC Builder, contributor to `pyCCL` & `Firecrown`.
**SPDV:** Software*;

\* not direct Smokescreen development, but software used in the work presented here.

# Blinding

Investigating ways to mitigate experimenter bias in the LSST DESC cosmology analysis.

> "Blind analyses are an effective way to reduce or eliminate experimenter's bias, the unintended biasing of a result by the scientists making a measurement. While blind analysis methods have become common in certain sub-fields of physics and astronomy, they are not yet widespread in the community of scientists preparing for LSST data and future CMB surveys." - *KIPAC Workshop "Blind Analysis in  High-Stakes Survey Science", March 13-15, 2017, SLAC*

> "The first principle [of science] is that you must not fool yourself--and you are the easiest person to fool.” - Richard Feynman

### Key Project CX8: Blinding Strategy for Cosmology Analysis

This is a DC2 project in the [LSST DESC Science Roadmap](http://lsstdesc.org/sites/default/files/DESC_SRM_V1_0.pdf), designed to get us started on thinking about the problem of experimenter bias. This repository hosts our research into suitable strategies that we might adopt for the LSST DESC analysis. The project has two deliverables, which could be two parts of the same research note:

1. **Identified strategies for individual probe analyses.** (CX8.1TJP, December 2017) Blind analysis strategies for different types of measurements and analyses are commonly used in other fields, such as medicine, and particle physics. These can serve as a starting point to identify viable blind analysis strategies for individual probe analyses. After carrying out a literature review, we'll make some recommendations and then implement them in likelihood code (if only as toy examples).
2. **Identified strategies for joint probe analyses.** (CX8.2TJP, June 2018) It's possible that a synthesis of the blind analysis strategies for individual probes could lead to a blind analysis concept for joint probes - or we may need an entirely different approach. One of the outstanding questions is how we can test the consistency of individual probes before unblinding the joint analysis. We'll aim to write some recommendations and again do some tests in code.

### Contact, Licence, Credits etc

If you are interested in this project, please get in touch [via the issues](https://github.com/LSSTDESC/Blinding/issues). This is research in progress: if you use any of the ideas or code in this repository in your own research, please cite it as _(LSST DESC in preparation)_ and provide a link to this repository: https://github.com/LSSTDESC/Blinding

Active people:
* Elisabeth Krause
* Phil Marshall
* _your name here_

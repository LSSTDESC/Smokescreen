# Contributing to Smokescreen

Thank you for your interest in contributing to Smokescreen! We welcome contributions from the broader astronomy and cosmology community, not just DESC members.

## Getting Started

1. **Fork the repository** and clone it locally.
2. **Install the development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
or 
   ```bash
   conda env create -f environment.yml
   conda activate desc_smokescreen
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Open an issue** related to your contribution and link your PR to it.

## How to Contribute

### Reporting Bugs
Please **open an issue** on GitHub with a clear description of the problem, a minimal reproducible example, and the version of Smokescreen you are using.

### Suggesting Enhancements
**Open an issue** describing the proposed feature, its motivation, and — where possible — a sketch of the intended API or behaviour.

### Submitting a Pull Request
1. Ensure your changes are covered by tests. Smokescreen uses `pytest`; run the test suite with:
   ```bash
   pytest
   ```
2. Follow the existing code style. We use `flake8` for linting.
3. Update the documentation and changelog where relevant.
4. **Open an issue related to your PR**
5. Open a pull request against the `main` branch with a clear description of your changes and the motivation behind them. Link it to the issue you opened.

## Code of Conduct

Contributors are expected to adhere to a standard of respectful and inclusive collaboration. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

## Scope

Smokescreen is designed to be likelihood- and probe-agnostic, delegating theory calculations to [Firecrown](https://github.com/LSSTDESC/firecrown). Contributions that extend blinding support to new Firecrown likelihoods, improve interoperability, or add new blinding schemes are especially welcome.

## Contact

For questions about contributing, feel free to open an issue or reach out to the maintainers via the DESC Slack (for DESC members) or GitHub Discussions and issues.

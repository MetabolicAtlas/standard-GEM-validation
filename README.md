## standard-GEM validation

This repository stores the validation results for genome‑scale metabolic models (GEMs) that adopt the [standard-GEM](https://github.com/MetabolicAtlas/standard-GEM) format. A small utility in [`runner.py`](runner.py) running daily with GitHub Actions discovers repositories tagged with `standard-gem`, runs a suite of tests from the [`tests`](tests) package, and writes the outcomes to JSON files in [`results`](results). Avatars of repository owners are cached in [`avatars`](avatars).

### Cite us

If you use _standard-GEM_ or this validation pipeline in your scientific work, please cite:

> Anton, M., et al (2023). _standard-GEM: standardization of open-source genome-scale metabolic models_. bioRxiv, 2023-03 [doi:10.1101/2023.03.21.512712](https://www.biorxiv.org/content/10.1101/2023.03.21.512712)


### Using the validation data

The generated JSON files and avatars are published through GitHub Pages so that they can be consumed by other services. They are available at:

```
https://metabolicatlas.github.io/standard-GEM-validation/index.json
https://metabolicatlas.github.io/standard-GEM-validation/results/<model>.json
https://metabolicatlas.github.io/standard-GEM-validation/avatars/<avatar>.png
```

Each JSON file contains metadata about the repository, release history, and test results for the model.

A minimal redirect page [`gh-pages-index.html`](gh-pages-index.html) points to the interactive overview on [metabolicatlas.org](https://metabolicatlas.org/gem/standard-gems). That site uses the data published from this repository to display up‑to‑date information about standard‑GEM models.
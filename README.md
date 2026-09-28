# standard-GEM 

The `standard-GEM` initiative provides a community-driven, git-based template that streamlines the creation, curation, and long-term maintenance of genome-scale metabolic models (GEMs). By embedding FAIR principles directly into the model development workflow, standard-GEM ensures transparency, provenance tracking, and reproducibility at every stage. It defines a clear repository structure, enforces best practices in documentation, and integrates with automated validation pipelines, lowering the cost of model upkeep while raising quality and openness. Already adopted by multiple high-profile GEMs, standard-GEM transforms models from static research outputs into evolving digital infrastructure, enabling reliable reuse across platforms and fostering collaborative, community-driven systems biology research.

> For an up-to-date listing of GEMs as result of this validation, see [metabolicatlas.org/gems/standard-gems](https://metabolicatlas.org/gems/standard-gems).

# standard-GEM validation

This repository stores the validation results for genome‑scale metabolic models (GEMs) that adopt the [standard-GEM](https://github.com/MetabolicAtlas/standard-GEM) format. A small utility in [`runner.py`](https://github.com/MetabolicAtlas/standard-GEM-validation/blob/main/runner.py) running daily with GitHub Actions discovers repositories tagged with `standard-gem`, runs a suite of tests from the [`tests`](https://github.com/MetabolicAtlas/standard-GEM-validation/tree/main/tests) package, and writes the outcomes to JSON files in [`results`](https://github.com/MetabolicAtlas/standard-GEM-validation/tree/main/results). Avatars of repository owners are cached in [`avatars`](https://github.com/MetabolicAtlas/standard-GEM-validation/tree/main/avatars).

## Cite us

If you use _standard-GEM_ or this validation pipeline in your scientific work, please cite:

> Anton, M., et al (2023). _standard-GEM: standardization of open-source genome-scale metabolic models_. bioRxiv, 2023-03 [doi:10.1101/2023.03.21.512712](https://www.biorxiv.org/content/10.1101/2023.03.21.512712)


## Documentation and validation data

The [project homepage](https://metabolicatlas.github.io/standard-GEM-validation/) renders this README automatically.

Documentation source lives in [`docs/index.md`](https://github.com/MetabolicAtlas/standard-GEM-validation/blob/main/docs/index.md) and is published as a single page at [`/docs/`](https://metabolicatlas.github.io/standard-GEM-validation/docs). Each JSON file contains metadata about the repository, release history, model metrics (reaction and metabolite counts) for each validated release, and test results for the model.

The generated JSON files, and avatars are published through GitHub Pages so that they can be read by people and consumed by other services:

```
https://metabolicatlas.github.io/standard-GEM-validation/index.json
https://metabolicatlas.github.io/standard-GEM-validation/results/<model>.json
https://metabolicatlas.github.io/standard-GEM-validation/avatars/<avatar>.png
```

The interactive overview on [metabolicatlas.org](https://metabolicatlas.org/gems/standard-gems) uses the data published from this repository to display up-to-date information about standard-GEM models.

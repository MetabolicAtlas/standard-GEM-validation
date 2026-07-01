---
title: Documentation
description: Documentation for the standard-GEM validation framework, published data, and GitHub Pages deployment.
permalink: /docs/
---

# standard-GEM validation

{: .lead }
This repository discovers genome-scale metabolic model repositories that follow the standard-GEM convention, runs a compact validation suite, and publishes the results through GitHub Pages.

The documentation is a single page at:

```text
https://metabolicatlas.github.io/standard-GEM-validation/docs/
```

## Public endpoints

The GitHub Pages site publishes both this documentation and the generated validation artifacts:

```text
https://metabolicatlas.github.io/standard-GEM-validation/docs/
https://metabolicatlas.github.io/standard-GEM-validation/index.json
https://metabolicatlas.github.io/standard-GEM-validation/results/<model>.json
https://metabolicatlas.github.io/standard-GEM-validation/avatars/<avatar>.png
```

The interactive standard-GEM overview on metabolicatlas.org consumes these data files:

[https://metabolicatlas.org/gems/standard-gems](https://metabolicatlas.org/gems/standard-gems)

## Validation framework

The validation framework is intentionally small. The orchestration lives in `runner.py`; individual checks live as plain Python functions in the `tests/` package.

### Repository discovery

`runner.matrix()` refreshes `index.json` with repositories tagged `standard-gem`:

| Provider | Discovery source |
| --- | --- |
| GitHub | GraphQL repository search for `topic:standard-gem`, including forks |
| GitLab | GraphQL project search for the `standard-gem` topic |

The GitHub repository for the standard itself is excluded from the discovered model list. Existing repositories in `index.json` are retained and merged with newly discovered repositories.

### Validation target selection

For each repository, `runner.validate(name_with_owner, provider)` writes one result file under `results/`.

The runner:

1. Collects repository metadata such as owner, commit count, contributor count, latest commit date, and owner avatar.
2. Looks up the latest standard-GEM release from `MetabolicAtlas/standard-GEM`.
3. Finds the first model release that has not already been stored in the local result file.
4. Falls back to the `main` branch when there is no new release to validate.
5. Downloads available model files from the repository `model/` directory.
6. Runs all discovered test functions and writes the result JSON.

The model file base name is the repository name. The runner looks for these formats:

```text
model/<repository-name>.yml
model/<repository-name>.xml
model/<repository-name>.mat
model/<repository-name>.json
```

### Standard check

For each validated tag or branch, the runner compares the repository `.standard-GEM.md` file with the selected standard-GEM version. Markdown checkbox states are ignored, so `[ ]` and `[x]` do not affect the comparison.

The result is stored under `standard-GEM` as a boolean keyed by standard version.

### Test discovery

`runner.discover_tests()` imports every Python module in `tests/` and collects public functions. Any function whose name does not start with `_` is treated as a validation check.

Each test function receives the model name and returns:

```text
test_module, description, module_version, status, errors
```

`runner.result_json_string()` converts that tuple into the JSON shape used in result files. Error output is capped to 300 characters.

### Current checks

| Result key | Source | What it checks | Status value |
| --- | --- | --- | --- |
| `cobrapy-load-yaml` | `tests/cobra.py` | The YAML model can be loaded by cobrapy. | Boolean |
| `cobrapy-load-sbml` | `tests/cobra.py` | The SBML model can be loaded by cobrapy. | Boolean |
| `cobrapy-load-matlab` | `tests/cobra.py` | The Matlab model can be loaded by cobrapy. | Boolean |
| `cobrapy-load-json` | `tests/cobra.py` | The JSON model can be loaded by cobrapy. | Boolean |
| `cobrapy-validate-sbml` | `tests/cobra.py` | The SBML model has no fatal, error, schema, or COBRA errors according to cobrapy. | Boolean |
| `yamllint` | `tests/yaml.py` | The YAML model passes yamllint with default rules and disabled line length checks. | Boolean |
| `memote-score` | `tests/memote.py` | A focused Memote suite for annotation, consistency, coverage, duplicate, transport, and balance checks. | Numeric score or `false` |

Missing files are reported as failed checks with an explanatory error string.

## Published data

The GitHub Pages deployment publishes machine-readable validation data alongside this documentation.

### Repository index

`index.json` lists known standard-GEM repositories grouped by provider:

```json
{
  "github": [
    "SysBioChalmers/yeast-GEM"
  ],
  "gitlab": [
    "group/project"
  ]
}
```

Public URL:

```text
https://metabolicatlas.github.io/standard-GEM-validation/index.json
```

### Result files

Each model has a result file under `results/`:

```text
https://metabolicatlas.github.io/standard-GEM-validation/results/<model>.json
```

At the top level, each file is keyed by model name:

```json
{
  "yeast-GEM": {
    "metadata": {},
    "releases": []
  }
}
```

`metadata` contains:

| Field | Meaning |
| --- | --- |
| `owner` | Repository owner, organization, or namespace. |
| `avatar` | Cached avatar filename under `avatars/`, when available. |
| `commits` | Commit count reported by the provider. |
| `contributors` | Contributor count reported by the provider. |
| `latest_commit_date` | Latest default-branch commit timestamp reported by the provider. |

`releases` is an ordered list of validated tags or branches. Each entry stores the standard-GEM comparison and the collected test results:

```json
[
  {
    "v1.0.0": {
      "standard-GEM": [
        { "0.5": true },
        {
          "test_results": {
            "yamllint": {
              "description": "Check if the model in YAML format is formatted correctly.",
              "version": "1.37.1",
              "status": true,
              "errors": []
            }
          }
        }
      ]
    }
  }
]
```

### Avatars

Repository owner avatars are cached in `avatars/` and published as static files:

```text
https://metabolicatlas.github.io/standard-GEM-validation/avatars/<avatar>.png
```

The avatar filename is referenced by each model result file under `metadata.avatar`.

## Deployment

GitHub Pages is deployed by `.github/workflows/results-to-pages.yml`.

The workflow runs when changes land on `main`, when triggered manually, and on its daily schedule. It builds the Markdown documentation in `docs/` with Jekyll, then copies the generated validation artifacts into the same site artifact.

### Site source

Documentation source lives in `docs/index.md`. It renders to `/docs/` through its front matter permalink.

The site uses the Just the Docs Jekyll theme through `remote_theme` in `docs/_config.yml`.

### Deployment artifact

The deployed artifact contains:

```text
/
  docs/
  index.json
  results/
  avatars/
```

The documentation is available under `/docs/`, while validation data is available from the same public JSON and avatar paths.

## License

This repository is distributed under the GNU General Public License version 3. The full license text is available in [`LICENSE.md`](https://github.com/MetabolicAtlas/standard-GEM-validation/blob/main/LICENSE.md).

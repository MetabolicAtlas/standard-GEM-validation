"""Utility functions to validate GEM repositories against the standard."""

import json
import inspect
import requests
from importlib import import_module
from os import environ
from pathlib import Path


API_ENDPOINT = "https://api.github.com/graphql"
API_TOKEN = environ.get("GH_TOKEN")
if not API_TOKEN:
    raise EnvironmentError("GH_TOKEN environment variable not set")

MODEL_FILENAME = "model"
MODEL_FORMATS = [".yml", ".xml", ".mat", ".json"]
RELEASES = 5

HEADERS = {"Authorization": f"token {API_TOKEN}"}
ADDITIONAL_BRANCH_TAGS = ["main"]


def discover_tests():
    """Return all test callables found in the tests package."""

    test_functions = []
    tests_dir = Path(__file__).resolve().parent / "tests"
    for module_path in tests_dir.glob("*.py"):
        module_name = f"tests.{module_path.stem}"
        try:
            module = import_module(module_name)
        except Exception:
            continue
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("_"):
                test_functions.append(func)
    return test_functions

# TESTS = [
#     tests.cobra.loadYaml,
#     tests.cobra.loadSbml,
#     tests.cobra.loadMatlab,
#     tests.cobra.loadJson,
#     tests.cobra.validateSbml,
#     tests.yaml.validate,
#     tests.memote.scoreAnnotationAndConsistency,
# ]

TESTS = discover_tests()

def gem_repositories():
    """Return repositories tagged with standard-GEM excluding the template."""

    json_request = {
        "query": """
        { search(
            type: REPOSITORY,
            query: \"\"\"fork:true topic:standard-GEM\"\"\",
            first: 100
        ) {
            repos: edges {
                repo: node {
                    ... on Repository { nameWithOwner }
                }
            }
        }}
        """,
    }
    response = requests.post(API_ENDPOINT, json=json_request, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()["data"]["search"]["repos"]
    repositories = (edge["repo"]["nameWithOwner"] for edge in data)
    return [repo for repo in repositories if "standard-GEM" not in repo]

def releases(name_with_owner):
    """Return release tags for a given repository."""

    owner, repo = name_with_owner.split("/")
    json_request = {
        "query": f"""
        {{ repository(
            owner: \"{owner}\",
            name: \"{repo}\"
        ) {{
            releases(first: {RELEASES}){{
                edges {{
                    node {{ tagName }}
                }}
            }}
        }} }}
        """,
    }
    response = requests.post(API_ENDPOINT, json=json_request, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()["data"]["repository"]["releases"]["edges"]
    release_tags = [edge["node"]["tagName"] for edge in data]
    return ADDITIONAL_BRANCH_TAGS + release_tags if release_tags else []

def matrix():
    """Write a JSON index of repositories to disk."""

    with open("index.json", "w") as file:
        json.dump(list(gem_repositories()), file)

def gem_follows_standard(name_with_owner, release, version):
    """Check whether a repository follows the specified standard version."""

    repo_url = (
        f"https://raw.githubusercontent.com/{name_with_owner}/{release}/.standard-GEM.md"
    )
    repo_standard = requests.get(repo_url, timeout=10)
    if repo_standard.status_code == 404:
        return False
    standard_url = (
        "https://raw.githubusercontent.com/MetabolicAtlas/standard-GEM/"
        f"{version}/.standard-GEM.md"
    )
    requests.get(standard_url, timeout=10)
    return True

def validate(name_with_owner):
    """Validate a repository and write test results to disk."""

    owner, model = name_with_owner.split("/")
    data = {name_with_owner: []}
    standard_versions = releases("MetabolicAtlas/standard-GEM")[-1:]
    for model_release in releases(name_with_owner):
        release_data = {}
        for version in standard_versions:
            print(f"{name_with_owner}: {model_release} | standard-GEM version: {version}")
            gem_is_standard = gem_follows_standard(name_with_owner, model_release, version)
            test_results = {}
            if gem_is_standard:
                for model_format in MODEL_FORMATS:
                    my_model = model + model_format
                    url = (
                        f"https://raw.githubusercontent.com/{name_with_owner}/"
                        f"{model_release}/model/{my_model}"
                    )
                    response = requests.get(url, timeout=10)
                    if response.ok:
                        with open(my_model, "w") as file:
                            file.write(response.text)
                for test in TESTS:
                    test_results.update(result_json_string(test, model))
            else:
                print("is not following standard")
            release_data = {
                "standard-GEM": [
                    {version: gem_is_standard},
                    {"test_results": test_results},
                ]
            }
        data[name_with_owner].append({model_release: release_data})
    with open(f"results/{owner}_{model}.json", "w") as output:
        json.dump(data, output, indent=2, sort_keys=True)

def result_json_string(test_to_run, model):
    """Return a JSON-serialisable dictionary with test results."""

    test_module, description, module_version, status, errors = test_to_run(model)
    return {
        test_module: {
            "description": description,
            "version": module_version,
            "status": status,
            "errors": errors[:300],
        }
    }

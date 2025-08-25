"""Utility functions to validate GEM repositories against the standard."""

import json
import inspect
import re
import requests
from importlib import import_module
from os import environ
from pathlib import Path
from urllib.parse import quote, urlparse


# GitHub configuration
GITHUB_ENDPOINT = "https://api.github.com/graphql"
GITHUB_TOKEN = environ.get("GH_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GH_TOKEN environment variable not set")
GITHUB_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# GitLab configuration
GITLAB_ENDPOINT = "https://gitlab.com/api/graphql"
GITLAB_TOKEN = environ.get("GL_TOKEN")
if not GITLAB_TOKEN:
    raise EnvironmentError("GL_TOKEN environment variable not set")
GITLAB_HEADERS = {"Authorization": f"Bearer {GITLAB_TOKEN}"}

MODEL_FILENAME = "model"
MODEL_FORMATS = [".yml", ".xml", ".mat", ".json"]
RELEASES = 5
ADDITIONAL_BRANCHES = ["main"]
AVATARS_DIR = Path("avatars")
RESULTS_DIR = Path("results")


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

TESTS = discover_tests()

# TESTS = [
#     tests.cobra.loadYaml,
#     tests.cobra.loadSbml,
#     tests.cobra.loadMatlab,
#     tests.cobra.loadJson,
#     tests.cobra.validateSbml,
#     tests.yaml.validate,
#     tests.memote.scoreAnnotationAndConsistency,
# ]

def github_repositories():
    """Return GitHub repositories tagged with standard-GEM excluding the template."""

    json_request = {
        "query": """
        { search(
            type: REPOSITORY,
            query: \"\"\"fork:true topic:standard-gem\"\"\",
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
    response = requests.post(
        GITHUB_ENDPOINT, json=json_request, headers=GITHUB_HEADERS, timeout=10
    )
    response.raise_for_status()
    data = response.json()["data"]["search"]["repos"]
    repositories = (edge["repo"]["nameWithOwner"] for edge in data)
    # "standard-GEM" is itself a repository - make sure to avoid it
    return [repo for repo in repositories if "standard-GEM" not in repo]

def gitlab_repositories():
    """Return GitLab projects tagged with standard-GEM."""

    json_request = {
        "query": """
        { projects(topics: [\"standard-gem\"], first: 100) {
            edges {
                node { fullPath }
            }
        }}
        """,
    }
    response = requests.post(
        GITLAB_ENDPOINT, json=json_request, headers=GITLAB_HEADERS, timeout=10
    )
    response.raise_for_status()
    data = response.json()["data"]["projects"]["edges"]
    repositories = [edge["node"]["fullPath"] for edge in data]
    return repositories

def gem_repositories():
    """Return repositories grouped by provider."""

    return {
        "github": github_repositories(),
        "gitlab": gitlab_repositories(),
    }

def matrix():
    """Write a provider-keyed JSON index of repositories to disk."""

    with open("index.json", "r+") as handle:
        current = json.load(handle)

        discovered = gem_repositories()
        for provider in set(current) | set(discovered):
            repos = set(current[provider])
            repos.update(discovered[provider])
            current[provider] = sorted(repos)

        handle.seek(0)
        json.dump(current, handle, indent=2, sort_keys=True)
        handle.truncate()

def repository_metadata(name_with_owner, provider, existing_avatar):
    """Return metadata for a repository."""

    owner, repo = name_with_owner.rsplit("/", 1)
    if provider == "github":
        json_request = {
            "query": f"""
            {{
                repository(owner: \"{owner}\", name: \"{repo}\") {{
                    owner {{
                        login
                        ... on Organization {{ avatarUrl name }}
                        ... on User {{ avatarUrl name }}
                    }}
                    defaultBranchRef {{
                        target {{
                            ... on Commit {{
                                committedDate
                                history {{ totalCount }}
                            }}
                        }}
                    }}
                }}
            }}
            """,
        }
        response = requests.post(
            GITHUB_ENDPOINT, json=json_request, headers=GITHUB_HEADERS, timeout=10
        )
        response.raise_for_status()
        repo_data = response.json()["data"]["repository"]
        commit_data = repo_data["defaultBranchRef"]["target"]
        commit_count = commit_data["history"]["totalCount"]
        latest_commit_date = commit_data["committedDate"]
        owner_data = repo_data["owner"]
        owner_name = owner_data.get("login")
        avatar_url = owner_data.get("avatarUrl")
        avatar_filename = existing_avatar
        if not avatar_filename and avatar_url:
            AVATARS_DIR.mkdir(exist_ok=True)
            ext = Path(urlparse(avatar_url).path).suffix or ".png"
            safe_owner = re.sub(r"[^A-Za-z0-9._-]", "_", owner_name or "avatar")
            filename = f"{safe_owner}{ext}"
            file_path = AVATARS_DIR / filename
            if not file_path.exists():
                img_resp = requests.get(avatar_url, timeout=10)
                img_resp.raise_for_status()
                with open(file_path, "wb") as img_file:
                    img_file.write(img_resp.content)
            avatar_filename = filename
        contrib_url = (
            f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true"
        )
        contrib_response = requests.get(
            contrib_url, headers=GITHUB_HEADERS, timeout=10
        )
        contrib_response.raise_for_status()
        if "link" in contrib_response.headers:
            match = re.search(
                r"&page=(\d+)>; rel=\"last\"",
                contrib_response.headers["link"],
            )
            if match:
                contributor_count = int(match.group(1))
            else:
                contributor_count = len(contrib_response.json())
        else:
            contributor_count = len(contrib_response.json())

        return {
            "commits": commit_count,
            "contributors": contributor_count,
            "latest_commit_date": latest_commit_date,
            "owner": owner_name,
            "avatar": avatar_filename,
        }

    elif provider == "gitlab":
        encoded = quote(name_with_owner, safe="")
        headers = {"Private-Token": GITLAB_TOKEN}
        project_response = requests.get(
            f"https://gitlab.com/api/v4/projects/{encoded}",
            headers=headers,
            timeout=10,
        )
        project_response.raise_for_status()
        project = project_response.json()
        namespace = project.get("namespace", {})
        owner_name = (
            namespace.get("full_path")
            or namespace.get("name")
            or name_with_owner.split("/")[0]
        )
        avatar_url = namespace.get("avatar_url")
        avatar_filename = existing_avatar
        if not avatar_filename and avatar_url:
            AVATARS_DIR.mkdir(exist_ok=True)
            ext = Path(urlparse(avatar_url).path).suffix or ".png"
            safe_owner = re.sub(r"[^A-Za-z0-9._-]", "_", owner_name or "avatar")
            filename = f"{safe_owner}{ext}"
            file_path = AVATARS_DIR / filename
            if not file_path.exists():
                img_resp = requests.get(avatar_url, timeout=10)
                img_resp.raise_for_status()
                with open(file_path, "wb") as img_file:
                    img_file.write(img_resp.content)
            avatar_filename = filename
        commits_response = requests.get(
            f"https://gitlab.com/api/v4/projects/{project['id']}/repository/commits?per_page=1",
            headers=headers,
            timeout=10,
        )
        commits_response.raise_for_status()
        commits = commits_response.json()
        latest_commit_date = commits[0]["committed_date"] if commits else None
        commit_count = int(commits_response.headers.get("X-Total", len(commits)))

        contributors_response = requests.get(
            f"https://gitlab.com/api/v4/projects/{project['id']}/repository/contributors",
            headers=headers,
            timeout=10,
        )
        contributors_response.raise_for_status()
        contributor_count = len(contributors_response.json())

        return {
            "commits": commit_count,
            "contributors": contributor_count,
            "latest_commit_date": latest_commit_date,
            "owner": owner_name,
            "avatar": avatar_filename,
        }

    else:
        raise ValueError(f"Unknown provider: {provider}")

###### Per-repository validation below ######

def releases(name_with_owner, provider):
    """Return release tags for a given repository."""

    owner, repo = name_with_owner.rsplit("/", 1)
    releases_info = []
    if provider == "github":
        json_request = {
            "query": f"""
            {{ repository(
                owner: \"{owner}\",
                name: \"{repo}\"
            ) {{
                releases(first: {RELEASES}){{
                    edges {{
                        node {{ tagName createdAt }}
                    }}
                }}
            }} }}
            """,
        }
        response = requests.post(
            GITHUB_ENDPOINT, json=json_request, headers=GITHUB_HEADERS, timeout=10
        )
        response.raise_for_status()
        data = response.json()["data"]["repository"]["releases"]["edges"]
        releases_info = [
            (edge["node"]["tagName"], edge["node"]["createdAt"])
            for edge in data
        ]
    elif provider == "gitlab":
        json_request = {
            "query": f"""
            {{ project(fullPath: \"{name_with_owner}\") {{
                releases(first: {RELEASES}) {{
                    edges {{ node {{ tagName releasedAt}} }}
                }}
            }} }}
            """,
        }
        response = requests.post(
            GITLAB_ENDPOINT, json=json_request, headers=GITLAB_HEADERS, timeout=10
        )
        response.raise_for_status()
        data = response.json()["data"]["project"]["releases"]["edges"]
        releases_info = [
            (edge["node"]["tagName"], edge["node"]["releasedAt"])
            for edge in data
        ]
    else:
        raise ValueError(f"Unknown provider: {provider}")
    releases_info.sort(key=lambda x: x[1] or "", reverse = True)
    release_names = [name for name, _ in releases_info]
    return ADDITIONAL_BRANCHES + release_names

def gem_follows_standard(name_with_owner, release, version, provider):
    """Check whether a repository follows the specified standard version."""

    if provider == "github":
        repo_url = (
            f"https://raw.githubusercontent.com/{name_with_owner}/{release}/.standard-GEM.md"
        )
    elif provider == "gitlab":
        repo_url = (
            f"https://gitlab.com/{name_with_owner}/-/raw/{release}/.standard-GEM.md"
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
    repo_standard = requests.get(repo_url, timeout=10)
    if repo_standard.status_code == 404:
        return False

    standard_url = (
        "https://raw.githubusercontent.com/MetabolicAtlas/standard-GEM/"
        f"{version}/.standard-GEM.md"
    )
    standard_md = requests.get(standard_url, timeout=10)
    if standard_md.status_code == 404:
        return False

    def strip_checkboxes(text):
        """Remove Markdown checkboxes such as ``[ ]`` or ``[x]`` from *text*."""
        return re.sub(r"\[[ xX]\]", "", text)
    
    repo_clean = strip_checkboxes(repo_standard.text)
    standard_clean = strip_checkboxes(standard_md.text)
    return repo_clean == standard_clean
    
def run_validation(name_with_owner, tag, provider, standard_versions, model, data, filename):
    validating_tag = {}
    for version in standard_versions:
        print(f"{name_with_owner}: {tag} | standard-GEM version: {version}")
        gem_is_standard = gem_follows_standard(name_with_owner, tag, version, provider)
        test_results = {}
        if gem_is_standard:
            for model_format in MODEL_FORMATS:
                my_model = model + model_format
                if provider == "github":
                    url = (
                        f"https://raw.githubusercontent.com/{name_with_owner}/"
                        f"{tag}/model/{my_model}"
                    )
                else:
                    url = (
                        f"https://gitlab.com/{name_with_owner}/-/raw/"
                        f"{tag}/model/{my_model}"
                    )
                response = requests.get(url, timeout=10)
                if response.ok:
                    with open(my_model, "w") as file:
                        file.write(response.text)
            for test in TESTS:
                test_results.update(result_json_string(test, model))
        else:
            print("is not following standard")
        validating_tag["standard-GEM"] = [
            {version: gem_is_standard},
            {"test_results": test_results},
        ]
    if tag in ADDITIONAL_BRANCHES and data[model]["releases"] != []:
        for r in data[model]["releases"]:
            for t in r:
                if t == tag:
                    data[model]["releases"][tag] = validating_tag
    else: 
        data[model]["releases"] = [{tag: validating_tag}] + data[model]["releases"]
    with open(filename, "w") as output:
        json.dump(data, output, indent=2, sort_keys=True)


def validate(name_with_owner, provider):
    """Validate a repository and write test results to disk."""

    owner, model = name_with_owner.rsplit("/", 1)
    filename = RESULTS_DIR / f"{model}.json"
    prev_avatar = None
    prev_releases = []
    if filename.exists():
        with open(filename) as file:
            previous = json.load(file)
            prev_avatar = previous[model].get("metadata", {}).get("avatar")
            prev_releases = previous[model].get("releases", [])
    metadata = repository_metadata(name_with_owner, provider, prev_avatar)
    data = {model: {"metadata": metadata, "releases": prev_releases}}
    standard_versions = releases("MetabolicAtlas/standard-GEM", "github")[-1:]
    validated_any = False
    if not validated_any:
        newer_releases = releases(name_with_owner, provider)
        for model_release in newer_releases:
            existing_tags = {k for release in prev_releases for k in release}
            if model_release not in existing_tags:
                print(f"{model_release} | {existing_tags}")
                to_validate = model_release
                validated_any = True
                break

    if not validated_any:
        to_validate = ADDITIONAL_BRANCHES[0]

    run_validation(name_with_owner, to_validate, provider, standard_versions, model, data, filename)
    
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

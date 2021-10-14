import requests
import json
from os import environ
import tests.cobra
import tests.yaml

API_ENDPOINT = 'https://api.github.com/graphql'
API_TOKEN = environ['GH_TOKEN']
MODEL_FILENAME = 'model.yml'
RELEASES = 10

header_auth = {'Authorization': 'token %s' % API_TOKEN}
additional_branch_tags = []
# additional_branch_tags = ['develop']

def gem_repositories():
    json_request = {"query" : """
        { search(
            type: REPOSITORY,
            query: \"\"\"fork:true topic:standard-GEM\"\"\",
            first: 100
            )
            { repos:
                edges {
                    repo: node {
                        ... on Repository { nameWithOwner }
                    }
                }
            }
        }""" }
    r = requests.post(url=API_ENDPOINT, json=json_request, headers=header_auth)
    json_data = json.loads(r.text)['data']['search']['repos']
    gem_repositories = map(lambda x: x['repo']['nameWithOwner'], json_data)
    filtered_repositories = filter(lambda x: 'standard-GEM' not in x, gem_repositories)
    return filtered_repositories

def releases(nameWithOwner):
    owner, repo =  nameWithOwner.split('/')
    json_request = { "query": """
        { repository(
            owner: \"%s\",
            name: \"%s\"
            )
            { releases(last: %s){
                    edges {
                        node { tagName }
                   }
                }
            }
        }""" % (owner, repo, RELEASES) }
    r = requests.post(url=API_ENDPOINT, json=json_request, headers=header_auth)
    json_data = json.loads(r.text)['data']['repository']['releases']['edges']
    release_tags = list(map(lambda x: x['node']['tagName'], json_data))
    if not release_tags:
        return []
    return release_tags + additional_branch_tags

def matrix():
    m = list(map(lambda g: { 'gem': g }, gem_repositories()))
    print(json.dumps({"include": m }))

def gem_follows_standard(nameWithOwner, release, version):
    repo_standard = requests.get('https://raw.githubusercontent.com/{}/{}/.standard-GEM.md'.format(nameWithOwner, release))
    if repo_standard.status_code ==  404:
        return False
    repo_standard = repo_standard.text
    raw_standard = requests.get('https://raw.githubusercontent.com/MetabolicAtlas/standard-GEM/{}/.standard-GEM.md'.format(version)).text
    import difflib
    the_diff = difflib.ndiff(repo_standard, raw_standard)
    return True

def validate(nameWithOwner):
    owner, model = nameWithOwner.split('/')
    data = {}
    data[nameWithOwner] = []
    for model_release in releases(nameWithOwner):
        release_data = {}
        standard_gem_releases = releases('MetabolicAtlas/standard-GEM')
        last_standard = standard_gem_releases[len(standard_gem_releases)-1:]
        for standard_version in last_standard:
            print("{}: {} | Standard-GEM: {}".format(nameWithOwner, model_release, standard_version))
            gem_is_standard = gem_follows_standard(nameWithOwner, model_release, standard_version)
            test_results = {}
            if gem_is_standard:
                response = requests.get('https://raw.githubusercontent.com/{}/{}/model/{}.yml'.format(nameWithOwner, model_release, model))
                with open(MODEL_FILENAME, 'w') as file:
                    file.write(response.text)
                test_results.update(tests.yaml.validate(MODEL_FILENAME))
                test_results.update(tests.cobra.validate(MODEL_FILENAME))
            else:
                print('is not following standard')
            release_data = { 'standard-GEM' : [ { standard_version : gem_is_standard }, { 'test_results' : test_results} ] }
        data[nameWithOwner].append({ model_release: release_data })
    with open('results/{}_{}.json'.format(owner, model), 'w') as output:
        output.write(json.dumps(data, indent=2, sort_keys=True))

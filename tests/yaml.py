import yamllint
from yamllint.config import YamlLintConfig
import json

def validate(model_name):
    description = 'Check if the model in YAML format is formatted correctly.'
    print(description)
    is_valid = False
    errors = ''
    try:
        conf = YamlLintConfig('{extends: default, rules: {line-length: disable}}')
        with open(model_name + '.yml', 'r') as file:
            errors = list(map(str, yamllint.linter.run(file, conf)))
        if len(errors) == 0:
            is_valid = True
        else:
            errors = json.dumps(errors)
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'yamllint', description, yamllint.__version__, is_valid, errors
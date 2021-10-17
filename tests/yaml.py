import yamllint
from yamllint.config import YamlLintConfig
import json

def validate(model_filename):
    print('  validate YAML with yamllint')
    is_valid_yaml = False
    errors = ''
    try:
        conf = YamlLintConfig('{extends: default, rules: {line-length: disable}}')
        with open(model_filename + '.yml', 'r') as file:
            errors = list(map(str, yamllint.linter.run(file, conf)))
        if len(errors) == 0:
            is_valid_yaml = True
        else:
            errors = json.dumps(errors)
    except Exception as e:
        print(e)
    return {'yamllint': { yamllint.__version__ : str(is_valid_yaml), 'errors': errors } }
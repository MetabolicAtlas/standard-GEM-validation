import yamllint
from yamllint.config import YamlLintConfig

def validate(model_filename):
    print('  validate YAML with yamllint')
    is_valid_yaml = False
    try:
        conf = YamlLintConfig('{extends: default, rules: {line-length: disable}}')
        with open(model_filename, 'r') as file:
            gen = yamllint.linter.run(file, conf)
        is_valid_yaml = len(list(gen)) == 0
    except Exception as e:
        print(e)
    return {'yamllint': { yamllint.__version__ : is_valid_yaml } }
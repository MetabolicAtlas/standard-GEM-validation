import cobra
import json
from os.path import exists

def validate(model_filename):
    print('  load model with cobrapy')
    is_valid_cobrapy = False
    errors = ''
    try:
        cobra.io.load_yaml_model(model_filename + '.yml')
        cobra.io.read_sbml_model(model_filename + '.xml')
        if exists(model_filename + '.mat'):
            cobra.io.load_matlab_model(model_filename + '.mat')
        if exists(model_filename + '.json'):
            cobra.io.load_json_model(model_filename + '.json')
        is_valid_cobrapy = True
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'cobrapy-yaml-load': { cobra.__version__ : is_valid_cobrapy, 'errors': errors } }
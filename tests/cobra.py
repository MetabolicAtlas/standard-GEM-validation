import cobra
import json
from os.path import exists

def load(model_filename):
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
    return {'cobrapy-load': { cobra.__version__ : is_valid_cobrapy, 'errors': errors } }

def validateSBML(model_filename):
    print('  validate sbml with cobrapy')
    is_valid_sbml = False
    try:
        result = cobra.io.sbml.validate_sbml_model(model_filename)
        if result[1] != {}:
            raise Exception(result[1])
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'cobrapy-validate-sbml': { cobra.__version__ : is_valid_sbmls, 'errors': errors } }
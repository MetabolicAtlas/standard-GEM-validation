import cobra
import json
from os.path import exists, getsize

def load(model_filename):
    print('  load model with cobrapy')
    is_valid_cobrapy = False
    errors = ''
    try:
        cobra.io.load_yaml_model(model_filename + '.yml')
        cobra.io.read_sbml_model(model_filename + '.xml')
        matFile = model_filename + '.matFile'
        if exists(matFile) and getsize(matFile) > 0:
            cobra.io.load_matlab_model(matFile)
        jsonFile = model_filename + '.json'
        if exists(jsonFile) and getsize(jsonFile) > 0:
            cobra.io.load_json_model(jsonFile)
        is_valid_cobrapy = True
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'cobrapy-load': { cobra.__version__ : is_valid_cobrapy, 'errors': errors } }

def validateSBML(model_filename):
    print('  validate sbml with cobrapy')
    is_valid_sbml = False
    try:
        _, result = cobra.io.sbml.validate_sbml_model(model_filename + '.xml')
        if result != {}:
            raise Exception(result)
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'cobrapy-validate-sbml': { cobra.__version__ : is_valid_sbml, 'errors': errors } }
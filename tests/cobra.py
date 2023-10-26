import cobra
import json

def loadYaml(model_name):
    print('load yaml')
    is_valid = False
    errors = ''
    try:
        cobra.io.load_yaml_model(model_name + '.yml')
        is_valid = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-yaml', cobra.__version__, is_valid, errors

def loadSbml(model_name):
    print('load sbml')
    is_valid = False
    errors = ''
    try:
        cobra.io.read_sbml_model(model_name + '.xml')
        is_valid = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-sbml', cobra.__version__, is_valid, errors

def loadMatlab(model_name):
    print('load matlab')
    is_valid = False
    errors = ''
    try:
        cobra.io.load_matlab_model(model_name + '.mat')
        is_valid = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-matlab', cobra.__version__, is_valid, errors

def loadJson(model_name):
    print('load json')
    is_valid = False
    errors = ''
    try:
        cobra.io.load_json_model(model_name + '.json')
        is_valid = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-json', cobra.__version__, is_valid, errors


def validateSbml(model_name):
    print('validate sbml with cobrapy')
    is_valid = False
    try:
        _, result = cobra.io.sbml.validate_sbml_model(model_name + '.xml')
        if result == {}:
            is_valid = True
        else:
            raise Exception(result)
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-validate-sbml', cobra.__version__, is_valid, errors
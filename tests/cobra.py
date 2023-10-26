import cobra
import json
from pathlib import Path

def loadYaml(model_name):
    description = 'Check if the model in YAML can be loaded with cobrapy.'
    print(description)
    status = False
    errors = ''
    try:
        cobra.io.load_yaml_model(model_name + '.yml')
        status = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-yaml',  description, cobra.__version__, status, errors

def loadSbml(model_name):
    description = 'Check if the model in SBML format can be loaded with cobrapy.'
    print(description)
    status = False
    errors = ''
    try:
        cobra.io.read_sbml_model(model_name + '.xml')
        status = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-sbml', description, cobra.__version__, status, errors

def loadMatlab(model_name):
    description = 'Check if the model in Matlab format can be loaded with cobrapy.'
    print(description)
    status = False
    errors = ''
    try:
        data_dir = Path(".") / ".." 
        data_dir = data_dir.resolve()
        model_path = data_dir / "{}.mat".format(model_name)
        cobra.io.load_matlab_model(str(model_path.resolve()))
        status = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-matlab', description, cobra.__version__, status, errors

def loadJson(model_name):
    description = 'Check if the model in JSON format can be loaded with cobrapy.'
    print(description)
    status = False
    errors = ''
    try:
        cobra.io.load_json_model(model_name + '.json')
        status = True
    except FileNotFoundError:
        errors = "File missing"
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-load-json', description, cobra.__version__, status, errors


def validateSbml(model_name):
    description = 'Check with cobrapy if the model in SBML format is valid.'
    print(description)
    status = False
    errors = ''
    try:
        _, result = cobra.io.sbml.validate_sbml_model(model_name + '.xml')
        if result['SBML_FATAL'] == [] and result['SBML_ERROR'] == [] and result['SBML_SCHEMA_ERROR'] == [] and result['COBRA_FATAL'] == [] and result['COBRA_ERROR'] == []:
            status = True
        else:
            raise Exception(result)
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return 'cobrapy-validate-sbml', description, cobra.__version__, status, errors
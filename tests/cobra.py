import cobra

def validate(model_filename):
    print('  load yml with cobrapy')
    is_valid_cobrapy = False
    try:
        cobra.io.load_yaml_model(model_filename)
        is_valid_cobrapy = True
    except Exception as e:
        print(e)
    return {'cobrapy-yaml-load': { cobra.__version__ : is_valid_cobrapy } }
import memote
import cobra
import json
from memote.support import consistency
# needed by memote.support.consitency
from memote.support import consistency_helpers as con_helpers

def get_consistency(model_filename):
    errors = ''
    is_consistent = 'Not tested'
    try:
        model = cobra.io.read_sbml_model(model_filename + '.xml')
        is_consistent = consistency.check_stoichiometric_consistency(model)
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    
    return {'memote-tests': { memote.__version__ : is_consistent, 'errors': errors } }
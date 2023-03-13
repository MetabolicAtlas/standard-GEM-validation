import cobra
import json
import memote

def scoreAnnotationAndConsistency(model_name):
    print('  memote scoring')
    memote_score = False
    errors = ''
    try:
        model = cobra.io.read_sbml_model(model_name + '.xml')
        _, results = memote.suite.api.test_model(model=model, results=True, exclusive=['basic', 'annotation', 'consistency'])
        processed_results = memote.suite.api.snapshot_report(results, None, False)
        results_json = json.loads(processed_results)
        memote_score = results_json['score']['total_score']
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'memote-score': { memote.__version__ : memote_score, 'errors': errors } }
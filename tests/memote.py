import cobra
import json
import memote

def scoreAnnotationAndConsistency(model_name):
    print('memote scoring')
    memote_score = False
    errors = ''
    try:
        model = cobra.io.read_sbml_model(model_name + '.xml')
        _, results = memote.suite.api.test_model(model=model, results=True, exclusive=['test_stoichiometric_consistency', 'test_reaction_mass_balance', 'test_reaction_charge_balance', 'test_find_disconnected', 'test_find_reactions_unbounded_flux_default_condition', 'test_metabolite_annotation_presence', 'test_metabolite_annotation_overview', 'test_metabolite_annotation_wrong_ids', 'test_metabolite_id_namespace_consistency', 'test_reaction_annotation_presence', 'test_reaction_annotation_overview', 'test_reaction_annotation_wrong_ids', 'test_reaction_id_namespace_consistency', 'test_gene_product_annotation_presence', 'test_gene_product_annotation_overview', 'test_gene_product_annotation_wrong_ids', 'test_model_id_presence', 'test_metabolites_presence', 'test_reactions_presence', 'test_genes_presence', 'test_compartments_presence', 'test_metabolic_coverage', 'test_unconserved_metabolites', 'test_inconsistent_min_stoichiometry', 'test_find_unique_metabolites', 'test_find_duplicate_metabolites_in_compartments', 'test_metabolites_charge_presence', 'test_metabolites_formula_presence', 'test_find_medium_metabolites', 'test_find_pure_metabolic_reactions', 'test_find_constrained_pure_metabolic_reactions', 'test_find_transport_reactions', 'test_find_constrained_transport_reactions', 'test_find_candidate_irreversible_reactions', 'test_find_reactions_with_partially_identical_annotations', 'test_find_duplicate_reactions', 'test_find_reactions_with_identical_genes'])
        processed_results = memote.suite.api.snapshot_report(results, config=None, html=False)
        results_json = json.loads(processed_results)
        print(results_json['score'])
        memote_score = results_json['score']['total_score']
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return {'memote-score': { memote.__version__ : memote_score, 'errors': errors } }
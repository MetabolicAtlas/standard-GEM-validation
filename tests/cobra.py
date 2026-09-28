import cobra
import json
import re
from pathlib import Path


_SCIENTIFIC_NAME = re.compile(
    r"\b(?:Candidatus\s+)?(?P<genus>[A-Z][a-z]{2,})\s+"
    r"[a-z][a-z.-]+(?:\s+[a-z][a-z.-]+)?\b"
)
_NON_TAXONOMIC_GENERA = {
    "Consensus",
    "Generic",
    "Genome",
    "Metabolic",
    "Model",
    "Reference",
    "Taxonomic",
    "Taxonomy",
    "The",
}
_TAXONOMY_ID = re.compile(r"\d+$")
_REFERENCE_GENOME_ID = re.compile(r"GC[AF]_\d+\.\d+$", re.IGNORECASE)
_REFERENCE_GENOME_NAMESPACES = ("insdc.gca", "insdc.gcf")


def _annotation_values(model, namespace):
    value = model.annotation.get(namespace)
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _has_scientific_name(model):
    text = " ".join(
        [model.name or ""]
        + [str(value) for value in model.notes.values() if value]
    )
    return any(
        match.group("genus") not in _NON_TAXONOMIC_GENERA
        for match in _SCIENTIFIC_NAME.finditer(text)
    )


def _missing_metadata(model):
    missing = []
    if not _has_scientific_name(model):
        missing.append("taxonomic name")

    taxonomy_ids = _annotation_values(model, "taxonomy")
    if not any(_TAXONOMY_ID.fullmatch(value) for value in taxonomy_ids):
        missing.append("taxonomy ID")

    reference_genome_ids = []
    for namespace in _REFERENCE_GENOME_NAMESPACES:
        reference_genome_ids.extend(_annotation_values(model, namespace))
    if not any(
        _REFERENCE_GENOME_ID.fullmatch(value) for value in reference_genome_ids
    ):
        missing.append("reference genome")
    return missing

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
        cobra.io.load_matlab_model(model_name + '.mat')
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


def validateMetadata(model_name):
    description = (
        "Check that the SBML model includes a taxonomic name, taxonomy ID, "
        "and reference genome."
    )
    print(description)
    model_path = Path(f"{model_name}.xml")
    if not model_path.is_file():
        return (
            "cobrapy-sbml-metadata",
            description,
            cobra.__version__,
            False,
            "File missing",
        )

    status = False
    errors = ""
    try:
        model = cobra.io.read_sbml_model(str(model_path))
        missing = _missing_metadata(model)
        status = not missing
        if missing:
            errors = json.dumps({"missing": missing})
    except Exception as e:
        errors = json.dumps(str(e))
        print(e)
    return "cobrapy-sbml-metadata", description, cobra.__version__, status, errors

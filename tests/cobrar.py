import json
import subprocess
from pathlib import Path


def loadSbml(model_name):
    description = "Check if the model in SBML format can be loaded with cobrar."
    print(description)
    model_path = Path(f"{model_name}.xml")
    file_missing = not model_path.is_file()
    try:
        result = subprocess.run(
            [
                "Rscript",
                "--vanilla",
                "-e",
                """
cat(as.character(packageVersion("cobrar")), "\\n", sep = "")
model_path <- commandArgs(trailingOnly = TRUE)[[1]]
invisible(cobrar::readSBMLmod(model_path))
""",
                str(model_path.resolve()),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        return (
            "cobrar-load-sbml",
            description,
            "unknown",
            False,
            json.dumps(str(error)),
        )
    output_lines = result.stdout.splitlines()
    version = output_lines[0].strip() if output_lines else "unknown"
    status = result.returncode == 0 and not file_missing
    errors = ""
    if file_missing:
        errors = "File missing"
    elif not status:
        errors = json.dumps((result.stderr or result.stdout).strip())
        print(result.stderr or result.stdout)
    return "cobrar-load-sbml", description, version, status, errors

"""Data loading and output paths shared by the notebooks."""
from pathlib import Path
import os
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCAFFOLDS = ["anthraquinone", "benzophenone", "diphenyl-ether", "xanthone"]

def load(name):
    """Read data/<name>.csv; empty cells are missing values."""
    frame = pd.read_csv(DATA / f"{name}.csv", float_precision="round_trip")
    if name == "molecular_features":
        frame["Scaffold"] = pd.Categorical(frame["Scaffold"], categories=SCAFFOLDS)
    return frame

def work_in_outputs(notebook):
    """Create outputs/<notebook>/ and make it the working directory.

    Figures and generated CSVs are saved there with relative paths; data/ is never written.
    """
    output = ROOT / "outputs" / notebook
    for folder in (output, output / "plots", output / "schemes"):
        folder.mkdir(parents=True, exist_ok=True)
    os.chdir(output)
    return output

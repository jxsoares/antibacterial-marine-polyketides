# antibacterial-marine-polyketides

Data and notebooks for:

> Soares, J.X.; Afonso, I.; Omerbasic, A.; Loureiro, D.R.P.; Pinto, M.M.M.; Afonso, C.M.M. The Chemical Space of Marine Antibacterials: Diphenyl Ethers, Benzophenones, Xanthones, and Anthraquinones. *Molecules* **2023**, *28*, 4073. https://doi.org/10.3390/molecules28104073

The repository provides the curated dataset of 246 marine diphenyl ethers, benzophenones, xanthones and anthraquinones (structures, sources and antibacterial assays) as CSV files, and the notebooks that produce the results and figures of the article.

```text
data/        CSV files
notebooks/   analysis notebooks, numbered in run order
src/         support code used by the notebooks
```

## Notebooks

The notebooks are committed already executed, so results and figures can be read directly on GitHub.

| Notebook | Content |
| --- | --- |
| `01_molecular-features` | RDKit descriptors (via DeepChem) merged with SwissADME properties; size, lipophilicity, solubility, flexibility, saturation and polarity by scaffold |
| `02_scaffold-source` | Scaffold distribution, producing organisms and geographic origin |
| `03_pca` | Principal component analysis of the molecular features, scaling comparison and loadings |
| `04_clustering` | Butina clustering on Morgan fingerprints, cluster centroids and representative structures |
| `05_antibacterial-activity` | Assay counts by scaffold, unit, Gram type and species; activity by scaffold and by cluster |
| `06_tmap` | Antibacterial potential ranking and TMAP chemical space maps |

## Running

Python 3.11 is required.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
jupyter execute --inplace notebooks/*.ipynb
```

Each notebook reads from `data/` and saves its figures and generated tables to `outputs/<notebook>/`, which is not tracked. `data/` is never modified. Notebooks 02–06 read the provided `data/molecular_features.csv` and cluster files, so any notebook can be run on its own.

`06_tmap` additionally needs the plotting extras (`pip install -e '.[tmap]'`) and the native [TMAP](https://github.com/reymond-group/tmap) library, installed following its upstream instructions; the PyPI package named `tmap` is a different project. On macOS Apple Silicon it can be built from source with the recipe tested for this repository:

```sh
pip install -e '.[tmap,native-build]'
python src/build_tmap_macos.py
```

The interactive TMAP maps are written as HTML files to `outputs/06_tmap/schemes/`.

## Data

Plain UTF-8 CSV; an empty cell is a missing value. `ID` identifies a compound in every file (prefix `AQ` anthraquinone, `BZ` benzophenone, `DP` diphenyl ether, `XT` xanthone).

| File | Rows | Content |
| --- | ---: | --- |
| `compounds.csv` | 253 | Name, scaffold, type, subtype, SMILES, DOI of the structure report, semi-synthetic flag |
| `sources.csv` | 252 | Producing fungus, bacterium or sponge, strain, marine association, sea, region and country, with source DOI |
| `antibacterial_assays.csv` | 1081 | One row per compound–bacterium assay: species, strain, Gram type (1 positive, 0 negative), activity flag, MIC, inhibition zone and IC50 values as reported, and the derived `logMIC` and `logDD` |
| `swissadme_descriptors.csv` | 253 | Physicochemical, lipophilicity and solubility properties from SwissADME |
| `swissadme_drug_likeness.csv` | 258 | Pharmacokinetics, drug-likeness and medicinal chemistry outputs from SwissADME |
| `molecular_features.csv` | 253 | Compounds with RDKit descriptors and SwissADME properties, as used in the article; notebook 01 recomputes it |
| `clusters_cutoff_0_5.csv` | 246 | Butina cluster of each compound at distance cutoff 0.5, as used in the article; notebook 04 recomputes it |
| `clusters_cutoff_0_66.csv` | 253 | Same at cutoff 0.66; notebook 04 gives the same clusters with clusters 4–8 numbered differently |
| `table_s2.csv` | 246 | Table S2 of the article |

Seven hybrid dimers (XT026–XT030, XT032, XT033) are listed under two scaffolds, which is why some files have 253 rows for 246 compounds. A compound can have more than one row in `sources.csv` and `swissadme_drug_likeness.csv`.

## Differences from the published article

The environment is a reconstruction with newer library versions (RDKit 2023.09 instead of 2021.03). Table S2 is reproduced exactly; the cluster representatives and groupings shown in the figures, and a few summary statistics quoted in the text, differ slightly. Text values in `data/` were cleaned after publication (stray spaces and spelling variants), which changes the source-organism counts in `02_scaffold-source`.

## Licence and citation

Code is released under the MIT licence (`LICENSE`). The files in `data/` are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). If you use either, please cite the article above (`CITATION.cff`).

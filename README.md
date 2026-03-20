# DeepChemStable

DeepChemStable: chemical stability prediction using an attention-based graph convolution network.

This repository is a forked/adapted version of the original DeepChemStable work, prepared for local reproduction, testing, and downstream integration. The original scientific work is described in the paper [DeepChemStable: Chemical Stability Prediction with an Attention-Based Graph Convolution Network](https://pubs.acs.org/doi/10.1021/acs.jcim.8b00672).

## Installation

Make sure you are under folder `DeepChemStable`.

```shell
conda create -n DeepChemStable python
conda activate DeepChemStable
pip install -r requirments.txt
```

The environment file includes RDKit, TensorFlow, scikit-learn, pandas, matplotlib, scipy, ipykernel, ipywidgets, tqdm, rich, and requests.

## Model Weights

The prediction pipeline expects model weights under `DeepChemStable_model/`.

You can download them from [weights](https://drive.google.com/drive/folders/1ZczOgMkoA8fVlqab43jtfK0tJU6fhnOr?usp=drive_link) and place them into `DeepChemStable_model/`.

The expected files are:

1. `DeepChemStable_model/fingerprint_variables.bin`
2. `DeepChemStable_model/prediction_variables.bin`

## Quick Start

Make sure you are under folder `DeepChemStable`.

Run the prediction command:

```shell
python predict.py <input_csv> <num_molecules>
```

Example:

```shell
python predict.py inputs/example_input.csv 5000
```

`<num_molecules>` should match the number of data rows in the input CSV file.

## Input Format

The input file should be a CSV file with the header:

```text
substance_id,smiles,label
```

Notes:

1. `substance_id` is the identifier for each compound.
2. `smiles` is the molecular SMILES string.
3. For inference-only usage, set all values in the `label` column to `0`.

See `inputs/example_input.csv` for a complete example.

## Output

After prediction, the project generates:

1. `results.csv`, which stores `substance_id`, `Probability`, and `Label`.
2. `figures/`, which stores visualization results for predictive unstable compounds with highlighted unstable fragments.

See `outputs/example_output.csv` for an example prediction output.

## Reproducibility / Training

This repository also includes scripts for training and preprocessing:

1. `train.py`: model training script.
2. `preprocessData.py`: dataset preprocessing and train/dev/test splitting.
3. `DeepChemStable_Automation.ipynb`: notebook workflow for automation and exploration.

## Example Files

1. Input example: `inputs/example_input.csv`
2. Output example: `outputs/example_output.csv`

## Troubleshooting

If prediction fails because of problematic molecules or malformed SMILES in a batch, you can use:

```shell
python find_bad_SMILES.py <failed_batch.csv>
```

This helper script recursively isolates problematic entries from a failing batch.

## Acknowledgements

This repository is not the original DeepChemStable release. It is a forked/adapted version based on the original DeepChemStable work. We sincerely thank the original authors for developing the model and publishing the original scientific study.

## Original Paper

Please cite and acknowledge the original work:

1. Title: *DeepChemStable: Chemical Stability Prediction with an Attention-Based Graph Convolution Network*
2. Journal page: https://pubs.acs.org/doi/10.1021/acs.jcim.8b00672

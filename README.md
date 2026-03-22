# DeepChemStable

DeepChemStable: chemical stability prediction using an attention-based graph convolution network.

This repository is a forked/adapted version of the original DeepChemStable work, prepared for local reproduction, testing, and downstream integration. The original scientific work is described in the paper [DeepChemStable: Chemical Stability Prediction with an Attention-Based Graph Convolution Network](https://pubs.acs.org/doi/10.1021/acs.jcim.8b00672).

## Installation

First clone the repo and cd into the directory:

```shell
git clone https://github.com/Kirinwinn/DeepChemStable.git
cd into DeepChemStable
conda create -n DeepChemStable python==3.10.0
conda activate DeepChemStable
pip install -r requirments.txt
```

## Download

The prediction pipeline expects model weights under `DeepChemStable_model/`. You can download them via [weights](https://drive.google.com/drive/folders/1ZczOgMkoA8fVlqab43jtfK0tJU6fhnOr?usp=drive_link) and place them into `DeepChemStable_model/`.

The expected files are:

1. `DeepChemStable_model/fingerprint_variables.bin`
2. `DeepChemStable_model/prediction_variables.bin`

## Usage

Activate the environment and run the prediction command:

```bash
conda activate DeepChemStable
cd into DeepChemStable
python predict.py <input_csv> <num_molecules>
```

Example:

```bash
python predict.py inputs/example_input.csv 5000
```

*Note 1:`<num_molecules>` should match the number of data rows in the input CSV file.*

or you can also use the notebook named `DeepChemStable_Automation.ipynb`:

```bash
conda activate DeepChemStable

pip install ipykernel

python -m ipykernel install --user --name "DeepChemStable" --display-name "DeepChemStable"
```

## Example

The format of input file should be a CSV file with the header:

```txt
substance_id,smiles,label
```

1. `substance_id` is the identifier for each compound;
2. `smiles` is the molecular SMILES string;
3. For inference-only usage, set all values in the `label` column to `0`;

Please check the `example_input.csv` in the `inputs` folder for a complete understanding.

After prediction, the project generates:

4. `results.csv`, which stores `substance_id`, `Probability`, and `Label`;

5. `figures/`, which stores visualization results for predictive unstable compounds with highlighted unstable fragments.

Please See `outputs/example_output.csv` for an example prediction output.

## Troubleshooting

If prediction fails because of problematic molecules or malformed SMILES in a batch, you can use:

```shell
python find_bad_SMILES.py <failed_batch.csv>
```

This script isolates problematic entries from a failing batch.

## Acknowledgements

This repository is not the original DeepChemStable release. It is a fork version based on the original [DeepChemStable](https://github.com/zhoujuncsu/DeepChemStable). We sincerely thank the original authors for developing the model and publishing the original scientific study.

1. Title: *DeepChemStable: Chemical Stability Prediction with an Attention-Based Graph Convolution Network*
2. Journal page: https://pubs.acs.org/doi/10.1021/acs.jcim.8b00672

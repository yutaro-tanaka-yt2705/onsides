"""
create_onsides_datafiles.py

Creates a tab delimited file of the extracted advese events from the product labels.
Input is the results files generated by the predict.py script.

"""

import os
import csv
import argparse
import pandas as pd

# These are determined in the Compare notebook by looking at the validation data

# TODO: Need to add in Version 02.

thresholds = {
# Onsides V01, reference method 8, nwords 125, epochs 10, all other parmas are defaults
# this value is taken from the Experiment 7 notebook.
    'AR': 2.397288988618289,
# Onsides V01-BW, reference method 8, nwords 125, epochs 25, all other params are defaults
# this value is taken from the Expiemrent 8 notebook. Note that reference method 0 produced
# slightly better validation F1 score, but I wanted everything to be as consisent as possible
# so choose method 8 anyway. Can come back to this decision in the future.
    'BW': 2.794294238090515,
}

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--results', help='Path to results file to generate the data tables from.', type=str, required=True)
    parser.add_argument('--examples', help='Path to the example file that corresponds to the results file.', type=str, required=True)

    args = parser.parse_args()

    resultspath = args.results

    fnnoext = os.path.split(resultspath)[-1].split('.')[0]
    if len(fnnoext.split('_')) != 9:
        raise Exception("Results filename not in format expected: {prefix}_{appset}_{refset}_{np_random_seed}_{split_method}_{EPOCHS}_{LR}_{max_length}_{batch_size}.csv.gz")

    prefix = fnnoext.split('_')[0]
    appset = fnnoext.split('_')[1]
    refset = fnnoext.split('_')[2]
    refsection = refset.split('-')[1]
    np_random_seed = int(fnnoext.split('_')[3])
    split_method = fnnoext.split('_')[4]
    EPOCHS = int(fnnoext.split('_')[5])
    LR = fnnoext.split('_')[6]
    max_length = fnnoext.split('_')[7]
    batch_size = fnnoext.split('_')[7]

    print(f" prefix: {prefix}")
    print(f" appset: {appset}")
    print(f" refset: {refset}")
    print(f" np_random_seed: {np_random_seed}")
    print(f" split_method: {split_method}")
    print(f" EPOCHS: {EPOCHS}")
    print(f" LR: {LR}")
    print(f" threshold: {thresholds[refsection]}")
    print(f" max_length: {LR}")
    print(f" batch-size: {batch_size}")

    res = pd.read_csv(resultspath, header=None, names=['Pred0', 'Pred1'])

    print(f"Loading results file...", flush=True)
    print(f" res.shape: {res.shape}")

    datapath = args.examples
    ex = pd.read_csv(datapath)

    print(f"Loding examples file...", flush=True)
    print(f" ex.shape: {ex.shape}")

    if ex.shape[0] != res.shape[0]:
        raise Exception("ERROR: Results file and examples file have different numbers of rows.")

    print(f"Concatenating results file to examples file...", flush=True)
    df = pd.concat([ex, res], axis=1)

    print(f"Grouping predictions by drug label and adverse event term, and taking the mean prediction score...", flush=True)
    df_grouped = df.groupby(by=['drug', 'llt']).mean().reset_index()

    print(f"Applying the pre-determined threshold to the prediction values to get predictions...")
    predictions = df_grouped[df_grouped['Pred1'] > thresholds[refsection]]
    predictions = predictions.rename(columns={'drug': 'xml_id', 'llt': 'concept_name', 'llt_id':'concept_id'})

    print(f"Predictions data frame created...")
    print(f" predictions.shape: {predictions.shape}")

    out_filename = f'./results/onsides.db/{prefix}_{appset}_{refset}_{np_random_seed}_{split_method}_{EPOCHS}_{LR}_{max_length}_{batch_size}.csv.gz'
    print(f"Saving to gzipped file: {out_filename}...")
    predictions.to_csv(out_filename)

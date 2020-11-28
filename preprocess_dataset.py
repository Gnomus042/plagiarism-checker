from collections import Counter
import json
import os

from plagiarism_detector import *


def word_sequences(data_path):
    sequences = {}
    files = os.listdir(data_path)
    for idx, file in enumerate(files):
        path = os.path.join(data_path, file)
        sequences[file] = WordSequences.sequences_counter(open(path, encoding="utf8").read())
        print(f'{idx + 1} from {len(files)}')
    return sequences


def threegrams_sequences(data_path):
    sequences = {}
    files = os.listdir(data_path)
    for idx, file in enumerate(files):
        path = os.path.join(data_path, file)
        sequences[file] = JaccardDistance.threegrams_counter(open(path, encoding="utf8").read())
        print(f'{idx + 1} from {len(files)}')
    return sequences

if __name__ == "__main__":
    dataset = input('Dataset: ')
    dataset_path = data_path = os.path.join('storage', dataset)
    if not os.path.exists(dataset_path):
        raise Exception("Invalid dataset name")
    sequences = word_sequences(os.path.join(data_path, 'data'))
    open(os.path.join(dataset_path, 'word_sequences.json'), 'w').write(json.dumps(sequences))

    threegrams = threegrams_sequences(os.path.join(data_path, 'data'))
    open(os.path.join(dataset_path, 'threegrams.json'), 'w').write(json.dumps(threegrams))

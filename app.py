import os
from flask import Flask, Response, render_template, request, jsonify, send_file
from plagiarism_detector import *

import config

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', datasets=config.datasets, methods=config.methods)


@app.route('/examples/<dataset_key>')
def get_examples_list(dataset_key):
    if dataset_key not in config.datasets:
        return Response(status=404)
    path = os.path.join('storage', config.datasets[dataset_key], 'data')
    return jsonify(os.listdir(path))


@app.route('/example/<dataset_key>/<example>')
def get_example(dataset_key, example):
    if dataset_key not in config.datasets:
        return Response(status=404)
    path = os.path.join('storage', config.datasets[dataset_key], 'data', example)
    if not os.path.exists(path):
        return Response(status=404)
    return send_file(path)


@app.route('/analyze', methods=['POST'])
def analyze():
    dataset = request.form['dataset']
    method = request.form['method']
    text = request.form['text']
    id = request.form['id']
    if method in ['lcs', 'sentence-naive']:
        texts = []
        files = os.listdir(os.path.join('storage', config.datasets[dataset], 'data'))
        for file in files:
            texts.append(open(os.path.join('storage', config.datasets[dataset], 'data', file), encoding='utf-8').read())
        if method == 'lcs':
            plagiarism_checker = LongestCommonSubsequence(texts, files)
        else:
            plagiarism_checker = SentenceCounter(texts, files)
    elif method == 'jaccard':
        plagiarism_checker = JaccardDistance(os.path.join('storage', config.datasets[dataset], 'threegrams.json'))
    else:
        plagiarism_checker = WordSequences(os.path.join('storage', config.datasets[dataset], 'word_sequences.json'))
    return jsonify(plagiarism_checker.find_similar(text, exclude=[id]))


if __name__ == '__main__':
    app.run()

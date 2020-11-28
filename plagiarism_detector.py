from collections import Counter
import re
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()


def preprocess(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = str(text).lower()
    text = word_tokenize(text)
    text = [item for item in text if item not in stop_words]
    text = [stemmer.stem(item) for item in text]
    # text = [lemma.lematize(word=w, pos='v') for w in text]
    text = [item for item in text if len(item) > 2]
    text = ' '.join(text)
    return text


class SentenceCounter:
    def __init__(self, texts, ids):
        self.sentences = {ids[i]: self.preprocess(texts[i]) for i in range(len(texts))}

    @staticmethod
    def preprocess(text):
        return [preprocess(x) for x in text.split('.')]

    def find_similar(self, text, exclude=[]):
        target_seq = self.preprocess(text)
        similar_docs = []
        for key in self.sentences:
            if key in exclude:
                continue
            seq = self.sentences[key]
            score = self.score(target_seq, seq)
            similar_docs.append({
                'score': score,
                'example': key
            })
        return [x for x in sorted(similar_docs, key=lambda x: x['score']) if x['score'] > 0]

    def score(self, seq1, seq2):
        score = 0
        for seq in seq1:
            score += 0.01 * int(seq in seq2) * len(seq)
        if score > 1:
            score = 1
        return score


class JaccardDistance:
    def __init__(self, sequenses):
        self.threegrams = json.loads(open(sequenses).read())

    @staticmethod
    def threegrams_counter(text):
        c = Counter()
        text = preprocess(text).split(' ')
        cuts = [' '.join(text[j:j + 3]) for j in range(len(text) - 3)]
        c.update(cuts)
        return c

    def find_similar(self, text, exclude=[]):
        target_seq = self.threegrams_counter(text)
        similar_docs = []
        for key in self.threegrams:
            if key in exclude:
                continue
            seq = self.threegrams[key]
            score = self.score(target_seq, seq)
            similar_docs.append({
                'score': score,
                'example': key
            })
        return [x for x in sorted(similar_docs, key=lambda x: x['score']) if x['score'] > 0]

    def score(self, target_seqs, other_seqs):
        intersection = 0
        for seq in target_seqs:
            if seq in other_seqs:
                intersection += min(target_seqs[seq], other_seqs[seq])
        union = 0
        for c in target_seqs.values():
            union += c
        for c in other_seqs.values():
            union += c
        return intersection / union


class LongestCommonSubsequence:
    def __init__(self, texts, ids):
        self.texts = {ids[i]: preprocess(texts[i]).split(' ') for i in range(len(texts))}

    def lcs(self, X, Y):
        m = len(X)
        n = len(Y)
        L = [[None] * (n + 1) for i in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif X[i - 1] == Y[j - 1]:
                    L[i][j] = L[i - 1][j - 1] + 1
                else:
                    L[i][j] = max(L[i - 1][j], L[i][j - 1])

        return L[m][n]

    def find_similar(self, text, exclude=[]):
        text = preprocess(text).split(' ')
        similar_texts = []
        for text_id in self.texts:
            if text_id in exclude:
                continue
            similar_texts.append({
                'score': self.score(text, self.texts[text_id]),
                'example': text_id
            })
        return [x for x in sorted(similar_texts, key=lambda x: x['score']) if x['score'] > 0]

    def score(self, text1, text2):
        lcs = self.lcs(text1, text2)
        return (lcs - min(20, lcs)) / min(len(text1), len(text2))


class WordSequences:
    def __init__(self, sequences_file):
        self.sequences = json.loads(open(sequences_file).read())

    @staticmethod
    def sequences_counter(text):
        c = Counter()
        text = preprocess(text).split(' ')
        for i in range(5, 15, 5):
            cuts = [' '.join(text[j:j + i]) for j in range(len(text) - i)]
            c.update(cuts)
        return c

    def find_similar(self, text, exclude=[]):
        target_seq = self.sequences_counter(text)
        similar_docs = []
        for key in self.sequences:
            if key in exclude:
                continue
            seq = self.sequences[key]
            score = self.score(target_seq, seq)
            similar_docs.append({
                'score': score,
                'example': key
            })
        return [x for x in sorted(similar_docs, key=lambda x: x['score']) if x['score'] > 0]

    def score(self, target_seqs, other_seqs):
        score = 0
        for seq in target_seqs.keys():
            score += 0.0005 * int(seq in other_seqs) * len(seq)
        if score > 1:
            score = 1
        return score

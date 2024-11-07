import numpy as np
import conllu
from sklearn_crfsuite import CRF
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to load and parse a corpus
def load_corpus(file_path):
    with open(file_path, 'rb') as f:
        data_str = f.read().decode('utf-8')
    return conllu.parse(data_str)

# Load multiple corpora
corpus_files = [
    'corpora\\en_atis-ud-train.conllu',
    'corpora\\en_eslspok-ud-train.conllu',
    'corpora\\en_ewt-ud-train.conllu',
    'corpora\\en_gum-ud-train.conllu',
    'corpora\\en_lines-ud-train.conllu',
    'corpora\\en_partut-ud-train.conllu'
]

# Combine all corpora into a single dataset
combined_train_data = []
for corpus_file in corpus_files:
    combined_train_data.extend(load_corpus(corpus_file))

# Function to extract features from a sentence
def extract_features(sentence, idx):
    word = sentence[idx]['form']
    features = {
        'word': word,
        'is_first': idx == 0,
        'is_last': idx == len(sentence) - 1,
        'prev_word': '' if idx == 0 else sentence[idx - 1].get('form', ''),
        'next_word': '' if idx == len(sentence) - 1 else sentence[idx + 1].get('form', ''),
        'prev_tag': '' if idx == 0 else sentence[idx - 1].get('upostag', ''),
        'next_tag': '' if idx == len(sentence) - 1 else sentence[idx + 1].get('upostag', '')
    }

    # Add rule to tag words ending with ".com" or starting with "http/https"
    if word.endswith(('.Com','.com' , '.org' , '.co')) or word.startswith(('www.', 'http', 'https')):
        features['is_link'] = True
    else:
        features['is_link'] = False

    return features


# Function to prepare the dataset for training
def extract_dataset_features(dataset):
    X = []
    y = []
    for sentence in dataset:
        X_sentence = []
        y_sentence = []
        for i in range(len(sentence)):
            X_sentence.append(extract_features(sentence, i))
            if X_sentence[-1]['is_link']:
                y_sentence.append('LINK')
            else:
                y_sentence.append(sentence[i]['upostag'])
        X.append(X_sentence)
        y.append(y_sentence)
    return X, y

# Load training data
train_data = combined_train_data
X_train, y_train = extract_dataset_features(train_data)

# Initialize and train CRF model
crf = CRF()
crf.fit(X_train, y_train)

@app.route('/tag', methods=['POST'])
def tag_text():
    # Get text from request
    data = request.get_json()
    text = data['text']
    
    # Convert input text to the format expected by the model
    sentences = text.split('. ')  # Simple sentence splitting
    X_input = []
    for sentence in sentences:
        sentence_tokens = [{'form': token} for token in sentence.split()]
        X_sentence = [extract_features(sentence_tokens, i) for i in range(len(sentence_tokens))]
        X_input.append(X_sentence)

    # Predict tags
    y_pred = crf.predict(X_input)

    # Prepare response
    tagged_sentences = []
    for i, sentence in enumerate(X_input):
        tagged_sentence = [{'word': sentence[j]['word'], 'tag': y_pred[i][j]} for j in range(len(sentence))]
        tagged_sentences.append(tagged_sentence)

    return jsonify(tagged_sentences)

if __name__ == '__main__':
    app.run(debug=True)

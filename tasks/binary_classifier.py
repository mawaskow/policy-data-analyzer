import spacy
import os
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
import time
import cupy as cp
import json

from data_loading.src.utils import *
#from model_evaluation.src.model_evaluator import *
from data_augmentation.src.zero_shot_classification.latent_embeddings_classifier import *

def data_load(data_path, experiment):
    '''
    eventually going to split this into subfunctions
    but at the moment we are just trying to adapt this from the jupiter notebook
    '''
    with open(data_path+experiment+"sentences.json", "r", encoding="utf-8") as f:
        sentences = json.load(f)
    with open(data_path+experiment+"labels.json", "r", encoding="utf-8") as f:
        labels = json.load(f)
    train_sents, test_sents, train_labels, test_labels = train_test_split(sentences,labels, test_size=0.2)
    # these are how to evaluate your data distributions
    #label_names = unique_labels(train_labels)
    #numeric_train_labels = labels2numeric(train_labels, label_names)
    #plot_data_distribution(numeric_train_labels, label_names)
    #
    # load model
    model_name = "paraphrase-xlm-r-multilingual-v1"
    # eventually will be able to load pretrained model from training via a path?
    bin_model = SentenceTransformer(model_name)
    all_sent_embs = encode_all_sents(test_sents, bin_model)

    # they noted that the projection matrix made stuff worse
    #proj_matrix = cp.asnumpy(calc_proj_matrix(train_sents, 50, es_nlp, bin_model, 0.01))
    #all_sent_embs = encode_all_sents(test_sents, bin_model, proj_matrix)

    #all_test_embs = encode_all_sents(test_sents, bin_model)

    all_test_embs = encode_all_sents(test_sents, bin_model)
    clf = RandomForestClassifier(n_estimators=100, max_depth=3, random_state=9)
    clf.fit(np.vstack(all_sent_embs), train_labels)
    clf_preds = [clf.predict(sent_emb)[0] for sent_emb in all_test_embs]
    print(classification_report(test_labels, clf_preds))

def main():
    if spacy.prefer_gpu():
        print("Using the GPU")
    else:
        print("Using the CPU")
    # load spacy model
    es_nlp = spacy.load('es_core_news_lg')

    data_path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\text_preprocessing\\output\\reduced\\"
    experiment="Pre_tagged_0.5_"
    data_load(data_path, experiment)

if __name__ == '__main__':
    main()
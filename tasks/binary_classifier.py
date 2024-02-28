import spacy
import os
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer
import time
import cupy as cp
import json

from data_loading.src.utils import *
#from model_evaluation.src.model_evaluator import *
#from data_augmentation.src.zero_shot_classification.latent_embeddings_classifier import *

def main():
    if spacy.prefer_gpu():
        print("Using the GPU")
    else:
        print("Using the CPU")
    es_nlp = spacy.load('es_core_news_lg')

if __name__ == '__main__':
    main()
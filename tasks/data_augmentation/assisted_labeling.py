import json
import os
from os import listdir
from os.path import isfile, join
import random
import time
import datetime
import csv

# Model libraries
from sentence_transformers import SentenceTransformer
import sentencepiece
from scipy.spatial import distance
import numpy as np

from json import JSONEncoder

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def labeled_sentences_from_dataset(dataset):
    sentence_tags_dict = {}
    for document in dataset.values():
        sentence_tags_dict.update(document['sentences'])
    return sentence_tags_dict

def create_sentence_embeddings(model, sentences_dict, file):
    embeddings = {}
    for sentence_id, sentence_map in sentences_dict.items():
        embeddings[sentence_id] = model.encode(sentence_map['text'].lower(), show_progress_bar=False)
    return embeddings
    
def sentence_similarity_search(model, queries, sentence_embeddings, sentences, similarity_limit, results_limit, filename):
    results = {}
    for query in queries:
        Ti = time.perf_counter()
        similarities = get_distance(model, sentence_embeddings, sentences, query, similarity_limit)
        results[query] = similarities[0:results_limit]#results[transformer][query] = similarities[0:results_limit]
        Tf = time.perf_counter()
        print(f"similarity search for query {query} has been done in {Tf - Ti:0.4f} seconds")
    return results

# This function helps debugging misspelling in the values of the dictionary
def check_dictionary_values(dictionary):
    check_country = {}
    check_incentive = {}
    for key, value in dictionary.items():
        incentive, country = value.split("-")
        check_incentive[incentive] = 0
        check_country[country] = 0
    print(check_incentive)
    print(check_country)

def get_distance( model, sentence_emb, sentences_dict, query, similarity_treshold):
    #pc has cuda
    #query_embedding = model.encode(query.lower(), show_progress_bar=False, device='cuda')
    # work laptop does not
    query_embedding = model.encode(query.lower(), show_progress_bar=False)
    highlights = []
    for sentence in sentences_dict.keys():
        try:
            sentence_embedding = sentence_emb[sentence]
            score = 1 - distance.cosine(sentence_embedding, query_embedding)
            if score > similarity_treshold:
                highlights.append([sentence, score, sentences_dict[sentence]['text']])
        except KeyError as err:
            print(sentence)
            print(sentence_emb.keys())
            print(err)
    highlights = sorted(highlights, key = lambda x : x[1], reverse = True)
    return highlights

# To show the contents of the results dict, particularly, the length of the first element and its contents
def show_results(results_dictionary):
    i = 0
    for key1 in results_dictionary:
        for key2 in results_dictionary[key1]:
            if i == 0:
                print(len(results_dictionary[key1][key2]))
                print(results_dictionary[key1][key2])
            i += 1

# Adding the rank to each result
def add_rank(results_dictionary):
#     for model in results_dictionary:
    for keyword in results_dictionary:#[model]:
        i = 1
        for result in results_dictionary[keyword]:#[model][keyword]:
            result.insert(1, i)
            i += 1
    return results_dictionary

# For experiments 2 and 3 this function is to save results in separate csv files
def save_results_as_separate_csv(results_dictionary, queries_dictionary, date):
    #pc
    #path = "C:/Users/Allie/Documents/GitHub/policy-data-analyzer/tasks/data_augmentation/output/sample/"
    # work laptop
    path = "C:/Users/Ales/Documents/GitHub/policy-data-analyzer/tasks/data_augmentation/output/sample/"
#     for model, value in results_dictionary.items():
    for exp_title, result in results_dictionary.items():#value.items():
        filename = queries_dictionary[exp_title]
        file = path + filename + ".csv"
        with open(file, 'w', newline='', encoding='utf-8') as f:
            write = csv.writer(f)
            write.writerows(result)
#             print(filename)
    
############################################################################

policy_dict = {}
objs = []
language = "spanish"
#pc
#os.chdir("C:/Users/Allie/Documents/GitHub/policy-data-analyzer/tasks/")
# work laptop
os.chdir("C:/Users/Ales/Documents/GitHub/policy-data-analyzer/tasks/")
#C:\Users\allie\Documents\GitHub\policy-data-analyzer\tasks\text_preprocessing\output\new
mypath = "./text_preprocessing/output/new/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

#policy_dict.keys()

for f in onlyfiles:
    #serializedObject = obj.get()['Body'].read()
    #policy_dict = {**policy_dict, **json.loads(serializedObject)}
    with open(join(mypath, f), 'r') as file:
        data = json.load(file)
    policy_dict = {**policy_dict, **data}

sentences = labeled_sentences_from_dataset(policy_dict)

#checking it has all 61 files
'''
#len(sentences.keys())
i = 0
for j in sentences.keys():
    if j[-2:] == '_0':
        i+=1
print(i)
'''

sample_sentence_ids = random.sample(list(sentences), 10)
sample_sentences = {}
for s_id in sample_sentence_ids:
    sample_sentences.update({s_id: sentences[s_id]})

Ti = time.perf_counter()

# We will use only one transformer to compute embeddings
transformer_name = 'xlm-r-bert-base-nli-stsb-mean-tokens'

path = "./data_augmentation/output/sample/"
today = datetime.date.today()
today = today.strftime('%Y-%m-%d')
filename = "Embeddings_" + today + "_ES.json"
file = path + filename

#pc has cuda
#model = SentenceTransformer(transformer_name, device="cuda")
#work laptop does not
model = SentenceTransformer(transformer_name)
#sample
#embs = create_sentence_embeddings(model, sample_sentences, file)
#all
embs = create_sentence_embeddings(model, sentences, file)

Tf = time.perf_counter()

print(f"The building of a sentence embedding database in the two(?) current models has taken {Tf - Ti:0.4f} seconds")

with open(file, 'w+') as fp:
    json.dump(embs, fp, cls = NumpyArrayEncoder)

queries_dict = {
    "Otorgamiento de estímulos crediticios por parte de el estado" : "Credit-México",
"Estos créditos podrían beneficiar a sistemas productivos asociados a la pequeña y mediana producción" : "Credit-Perú",
"Se asocia con créditos de enlace del Banco del Estado" : "Credit-Chile", 
"Acceso al programa de garantía crediticia para la actividad económica" : "Credit-Guatemala",
"El banco establecerá líneas de crédito para que el sistema financiero apoye la pequeña, mediana y microempresa" : "Credit-El Salvador",
"Dentro de los incentivos económicos se podrá crear un bono para retribuir a los propietarios por los bienes y servicios generados." : "Direct_payment-México",
"Acceso a los fondos forestales para el pago de actividad" : "Direct_payment-Perú",
"Se bonificará el 90% de los costos de repoblación para las primeras 15 hectáreas y de un 75% respecto las restantes" : "Direct_payment-Chile",
"El estado dará un incentivo que se pagará una sola vez a los propietarios forestales" : "Direct_payment-Guatemala",
"Incentivos en dinero para cubrir los costos directos e indirectos del establecimiento y manejo de areas de producción" : "Direct_payment-El Salvador",
"Toda persona física o moral que cause daños estará obligada a repararlo o compensarlo" : "Fine-México",
"Disminuir los riesgos para el inversionista implementando mecanismos de aseguramiento" : "Guarantee-México",
"Podrá garantizarse el cumplimiento de la actividad mediante fianza otorgada a favor del estado por cualquiera de las afianzadoras legalmente autorizadas." : "Guarantee-Guatemala",
"El sujeto de derecho podrá recibir insumos para la instalación y operación de infraestructuras para la actividad económica." : "Supplies-México",
"Se facilitará el soporte técnico a  través de la utilización de guías, manuales, protocolos, paquetes tecnológicos, procedimientos, entre otros." : "Supplies-Perú",
"Se concederán incentivos en especie para fomentar la actividad en forma de insumos" : "Supplies-El Salvador",
"Se otorgarán incentivos fiscales para la actividad primaria y también la actividad de transformación" : "Tax_deduction-México",
"De acuerdo con los lineamientos aprobados se concederá un 25% de descuento en el pago del derecho de aprovechamiento" : "Tax_deduction-Perú",
"Las bonificaciones percibidas o devengadas se considerarán como ingresos diferidos en el pasivo circulante y no se incluirán para el cálculo de la tasa adicional ni constituirán renta para ningún efecto legal hasta el momento en que se efectúe la explotación o venta" : "Tax_deduction-Chile",
"Los contratistas que suscriban contratos de exploración y/o explotación, quedan exentos de cualquier impuesto sobre los dividendos, participaciones y utilidades" : "Tax_deduction-Guatemala",
"Exención de los derechos e impuestos, incluyendo el Impuesto a la Transferencia de Bienes Muebles y a la Prestación de Servicios, en la importación de sus bienes, equipos y accesorios, maquinaria, vehículos, aeronaves o embarcaciones" : "Tax_deduction-El Salvador",
"Se facilitará formación Permanente Además del acompañamiento técnico, los sujetos de derecho participarán en un proceso permanente de formación a lo largo de todo el año, que les permita enriquecer sus habilidades y capacidades " : "Technical_assistance-México",
"Contribuir en la promoción para la gestión, a través de la capacitación, asesoramiento, asistencia técnica y educación de los usuarios" : "Technical_assistance-Perú",
"Asesoría prestada al usuario por un operador acreditado, conducente a elaborar, acompañar y apoyar la adecuada ejecución técnica en terreno de aquellas prácticas comprometidas en el Plan de Manejo" : "Technical_assistance-Chile",
"Para la ejecución de programas de capacitación, adiestramiento y otorgamiento de becas para la preparación de personal , así como para el desarrollo de tecnología en actividades directamente relacionadas con las operaciones objeto del contrato" : "Technical_assistance-Guatemala",
"Apoyo técnico y en formulación de proyectos y conexión con mercados" : "Technical_assistance-El Salvador"}

queries = []
for query in queries_dict:
    queries.append(query)

check_dictionary_values(queries_dict)

transformer_name ='xlm-r-bert-base-nli-stsb-mean-tokens'
similarity_threshold = 0.2
search_results_limit = 1000
today = datetime.date.today()
today = today.strftime('%Y-%m-%d')
# name = "Pre_tagged_" + today + "_" + filter_language
name = "Pre_tagged_" + today

model = SentenceTransformer(transformer_name)
#sample
#results_dict = sentence_similarity_search(model, queries, embs, sample_sentences, similarity_threshold, search_results_limit, name)
#all
results_dict = sentence_similarity_search(model, queries, embs, sentences, similarity_threshold, search_results_limit, name)

path = "./data_augmentation/output/sample/"
fname = name + ".json"
file = path + fname
with open(file, 'w+') as fp:
    json.dump(results_dict, fp, indent=4)

#pc
#path = "C:/Users/Allie/Documents/GitHub/policy-data-analyzer/tasks/data_augmentation/output/sample/"
# work laptop
path = "C:/Users/Ales/Documents/GitHub/policy-data-analyzer/tasks/data_augmentation/output/sample/"
file = path + name +".json"
with open(file, "r") as f:
    results_ = json.load(f)

results = add_rank(results_)
len(results_)

# Save the results as separete csv files

save_results_as_separate_csv(results, queries_dict, today)
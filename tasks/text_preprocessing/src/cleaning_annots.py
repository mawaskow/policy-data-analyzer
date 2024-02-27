import PyPDF2
import os
import glob
import fitz
import json
import time
import argparse
import tqdm

ann_cls_lst = [
    "Direct payment",
    "Credit",
    "Tax deduction",
    "Technical assistance",
    "Supplies",
    "Fine"
]

ann_cls_dct = {
    "direct": "Direct payment",
    "direct payment": "Direct payment",
    "credit": "Credit",
    "tax deduction": "Tax deduction",
    "technical assistance": "Technical assistance",
    "supplies": "Supplies",
    "fine": "Fine",
    "techical assistance": "Technical assistance",
    "tax credit": "Tax deduction",
    "pes": "Direct payment",
    "technical support": "Technical assistance",
    "direct payments": "Direct payment",
    "fines":"Fine"
}

def merge_label(input_string):
    label_lst = []
    try:
        input_string = input_string.split(",")
        for i in input_string:
            i = i.strip().lower()
            if i in ann_cls_dct.keys():
                label_lst.append(ann_cls_dct[i])
            elif i[:15] in ann_cls_dct.keys():
                label_lst.append(ann_cls_dct[i[:15]])
            else:
                i=i.replace("(", "")
                i=i.replace(")","")
                i=i.split(" ")
                for j in i:
                    if j=='pes':
                        label_lst.append("Direct payment")
        return label_lst
    except Exception as e:
        return [e]

def label_show(input_path):
    '''
    Shows the labels that dont match when the labels are just strings
    '''
    with open(input_path, "r", encoding="utf-8") as f:
        pdf_ann = json.load(f)
    i=0
    j=0
    #traverse by filename
    for fn in pdf_ann.keys():
        # then pagenumber
        for pn in pdf_ann[fn].keys():
            #then sentence in page
            for sn in pdf_ann[fn][pn].keys():
                j+=1
                label = pdf_ann[fn][pn][sn]['label']
                if label not in ann_cls_lst:
                    print(label)
                    i=i+1
    print(i, j)

def label_show_lst(input_path):
    '''
    shows the labels that arent in the directory
    when the labels are stored in lists
    '''
    with open(input_path, "r", encoding="utf-8") as f:
        pdf_ann = json.load(f)
    i=0
    j=0
    #traverse by filename
    for fn in pdf_ann.keys():
        # then pagenumber
        for pn in pdf_ann[fn].keys():
            #then sentence in page
            for sn in pdf_ann[fn][pn].keys():
                j+=1
                label = pdf_ann[fn][pn][sn]['label']
                for lb in range(len(label)):
                    if label[lb] not in ann_cls_lst:
                        print(label[lb])
                        i=i+1
    print(i, j)

def main(input, output):
    #label_show(input)
    '''
    # testing labels
    input_strings = ["Direct payment (PES)", "Forest, Agriculture (Crop)", "Direct payment (PES), Credit,",
                     "Credit, Technical assistance", " a policy in itself but a very important criticism of the inadequacies of previous financial incentive programs, namely PRODEFOR, PROCYMAF, PRODEPLAN. This argues that the programs lack long-term security due to dependency on budgets and lack of private investment. It also states that the previous programs were inflexible to different regional situations.",
                     "Fines", "Direct payments (PES), Technical assistance", "Other (Environmental education)",
                     "Unknown, Technical assistance", "PES, credit, technical assistance"]
    for i in input_strings:
        print(i, "BECOMES", merge_label(i))
    '''
    with open(input,"r", encoding="utf-8") as f:
        mess = json.load(f)
    for pdf in tqdm.tqdm(mess.keys()):
        for pg in mess[pdf].keys():
            for snt in mess[pdf][pg].keys():
                mess[pdf][pg][snt]["label"] = merge_label(mess[pdf][pg][snt]["label"])
    with open(output, "w", encoding="utf-8") as fo:
        json.dump(mess, fo, ensure_ascii=False, indent=4)
    label_show_lst(output)
    print("done")


if __name__ == '__main__':
    #input_path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\text_preprocessing\\output\\fixed_labels.json"
    input_path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\output\\pdf_extract.json"
    output_path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\text_preprocessing\\output\\fixed_labels.json"
    main(input_path, output_path)
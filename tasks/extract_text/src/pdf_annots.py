import PyPDF2
import os
import glob
import fitz
import json
import time
    
def text_cleaning(text):
    """Cleans a piece of text by removing escaped characters. (from src make_pfs)

    Args:
        text (str): string with text

    Returns:
        str: cleaned piece of text
    """
    # Remove escaped characters
    escapes = ''.join([chr(char) for char in range(1, 32)])
    text = text.translate(str.maketrans('', '', escapes))
    return text

def pdf_comments_to_sim_dct(file_path):
    """
    This function extracts comments from a PDF file and returns them as a list.
    Parameters:
    file_path (str): The path to the PDF file
    Returns:
    list: A list of comments extracted from the PDF file
    """
    simple_dct = {}
    try:
        # Open the PDF file
        with open(file_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            # Get the number of pages in the PDF file
            num_pages = len(pdf_reader.pages)
            # Loop through each page in the PDF file
            for page_num in range(num_pages):
                # Get the page object
                page = pdf_reader.pages[page_num]
                # Get the annotations for the page
                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        try:
                            comment = annot.get_object()["/Contents"]
                            simple_dct[page_num] = comment
                        except:
                            pass
            # Return the dct of comments
            return simple_dct
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        return {}

def pdf_highlight_to_dct(file_path):
    highlt_dct = {}
    doc = fitz.open(file_path)
    # taking page for further processing
    for page_num in range(len(doc)):
        page = doc[page_num]
        highlights = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:
                all_coordinates = annot.vertices
                if len(all_coordinates) == 4:
                    highlight_coord = fitz.Quad(all_coordinates).rect
                    highlights.append(highlight_coord)
                else:
                    all_coordinates = [all_coordinates[x:x+4] for x in range(0, len(all_coordinates), 4)]
                    for i in range(0,len(all_coordinates)):
                        coord = fitz.Quad(all_coordinates[i]).rect
                        highlights.append(coord)
            # this throws No attribute .parent: type(self)=<class 'fitz.Annot'> id(self)=#########: have set id(self.parent)=#######.
            annot = annot.next
        all_words = page.get_text("words")
        # List to store all the highlighted texts
        highlight_text = []
        for h in highlights:
            sentence = [w[4] for w in all_words if fitz.Rect(w[0:4]).intersects(h)]
            highlight_text.append(" ".join(sentence))
        if highlight_text:
            highlt_dct[page_num] = text_cleaning(" ".join(highlight_text))
    return highlt_dct

'''
experiment = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\input\\onedrive_docs\\Chile\\2019CVE 1713470_Chile.pdf"
cmts = []
print(f"Processing {experiment}...")
try:
    #cmts = pdf_comments_to_lst(experiment)
    cmts = pdf_comments_to_sim_dct(experiment)
    hlts = pdf_highlight_to_dct(experiment)
except Exception as e:  # In case the file is corrupted
    print(e)
    print(f"Attempting to recover experiment...")
    #pdfReader = file_recovery(file, myzip)  # attempting to recover file
print(cmts.keys(), cmts)
print(hlts.keys(), hlts)
'''

INPUT_PATH = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\input\\onedrive_docs\\"
filenames = []
dir_path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\input\\onedrive_docs\\**\\*.*"
pdf_dct = {}
for file in glob.glob(dir_path, recursive=True):
    filenames.append(file)
start = time.time()
for file in filenames:
    print(f"Processing {file}...")
    fname = file.split('\\')[-1][:-4]
    pdf_dct[fname] = {}
    try:
        cmts = pdf_comments_to_sim_dct(os.path.join(INPUT_PATH, file))
        hlts = pdf_highlight_to_dct(os.path.join(INPUT_PATH, file))
    except Exception as e:  # In case the file is corrupted
        print(e)
        print(f"Attempting to recover {file}...")
        #pdfReader = file_recovery(file, myzip)  # attempting to recover file
    for i in cmts.keys():
        if i in hlts.keys():
            pdf_dct[fname][i] = {}
            pdf_dct[fname][i]["sentence"] = hlts[i]
            # label cleaning
            label = cmts[i].split("\n")[0]
            label = label.split("\r")[0][3:]
            pdf_dct[fname][i]["label"] = label
        else:
            print(fname, "did not have key:", i)

print("writing to json")

path = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\output\\"
name = "pdfextract"
fname = name + ".json"
file = path + fname
with open(file, 'w+') as fp:
    json.dump(pdf_dct, fp, indent=4)

print(f"all done in {round(time.time()-start)}s")
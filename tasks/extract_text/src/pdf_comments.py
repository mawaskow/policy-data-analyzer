import PyPDF2
import os
from os import listdir, walk
from os.path import isfile, join
from zipfile import ZipFile
from collections import defaultdict
from io import BytesIO
import glob

def extract_comments_from_pdf(file_path):
    """
    This function extracts comments from a PDF file and returns them as a list.
    Parameters:
    file_path (str): The path to the PDF file
    Returns:
    list: A list of comments extracted from the PDF file
    """
    try:
        # Open the PDF file
        with open(file_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            # Get the number of pages in the PDF file
            num_pages = len(pdf_reader.pages)
            # Initialize an empty list to store comments
            comments = []
            coords = []
            # Loop through each page in the PDF file
            for page_num in range(num_pages):
                # Get the page object
                page = pdf_reader.pages[page_num]
                # Get the annotations for the page
                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        try:
                            comment = annot.get_object()["/Contents"]
                            comments.append(comment)
                        except:
                            pass
                        subtype = annot.get_object()["/Subtype"]
                        if subtype == "/Highlight":
                            cos = annot.get_object()["/QuadPoints"]
                            #x1, y1, x2, y2, x3, y3, x4, y4 = coords
                            coords.append(cos)
            # Return the list of comments
            return comments
    except Exception as e:
        # Log the error
        print(f"Error: {e}")
        return []

experiment = "C:\\Users\\allie\\Documents\\GitHub\\policy-data-analyzer\\tasks\\extract_text\\input\\onedrive_docs\\Chile\\2019CVE 1713470_Chile.pdf"

cmts = []

pdf_dict = defaultdict(dict)

print(f"Processing {experiment}...")
try:
    cmts = extract_comments_from_pdf(experiment)
except Exception as e:  # In case the file is corrupted
    print(e)
    print(f"Attempting to recover experiment...")
    #pdfReader = file_recovery(file, myzip)  # attempting to recover file
print(cmts)

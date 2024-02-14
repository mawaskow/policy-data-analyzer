# -*- coding: utf-8 -*-
"""
Extracts text and metadata from pdf files. Reads pdf files from ../input/onedrive_docs.zip 
and outputs extracted information to ../output/pdf_files.json.
"""
import json
import logging
import os
from collections import defaultdict
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from pikepdf import Pdf
from PyPDF2 import PdfReader


def text_cleaning(text):
    """Cleans a piece of text by removing escaped characters.

    Args:
        text (str): string with text

    Returns:
        str: cleaned piece of text
    """
    # Remove escaped characters
    escapes = ''.join([chr(char) for char in range(1, 32)])
    text = text.translate(str.maketrans('', '', escapes))
    return text


def file_recovery(filename, zipfile):
    """Attempts to recover a pdf file inside a zip that wasn't read correctly.

    Args:
        filename (str): file path string
        zipfile (ZipFile): ZipFile instance where file is located

    Returns:
        PdfReader: new PdfReader instance from where text will be read
    """
    with Pdf.open(BytesIO(zipfile.read(filename))) as pdf_file:  # attempting to recovery file
        path_to_file = os.path.join(OUTPUT_PATH, os.path.basename(filename))
        pdf_file.save(path_to_file)  # writes the file to disk
        pdfReader = PdfReader(path_to_file)  # attempts to read the file again
        os.remove(path_to_file)
    return pdfReader

def text_reader():
    """Function to solve TypeError: ord() expected string of length 1, but 
     int found error. TO IMPLEMENT.
    """
    # Useful link: https://stackoverflow.com/questions/55993860/getting-typeerror-ord-expected-string-of-length-1-but-int-found-error
    pass

# set default values here in main()
def main():
    logger = logging.getLogger(__name__)
    logger.info('Making pdf_files.json from base pdf files')

    with ZipFile(INPUT_PATH) as myzip:
        # List files inside zip
        filenames = list(map(lambda x: x.filename, filter(lambda x: not x.is_dir(), myzip.infolist())))
        pdf_dict = defaultdict(dict)
        for file in filenames:
            logger.info(f"Processing {file}...")
            try:
                pdfReader = PdfReader(BytesIO(myzip.read(file)))  # read file
                # doc_dict holds the attributes of each pdf file
                doc_dict = {i[1:]: str(j) for i, j in pdfReader.metadata.items()}
                doc_dict["Country"], doc_dict["Text"] = file.split("/")[0], ""
                for page in range(len(pdfReader.pages)):
                    try:
                        page_text = pdfReader.pages[page].extract_text()  # extracting pdf text
                    except TypeError as e:
                        logger.warning(e)
                        logger.info(f"Skipping {file}...")
                        continue
                    page_text = text_cleaning(page_text)  # clean pdf text
                    doc_dict["Text"] += page_text  # concatenate pages' text
                pdf_dict[os.path.splitext(os.path.basename(file))[0]] = doc_dict
            except Exception as e:  # In case the file is corrupted
                logger.warning(e)
                logger.info(f"Attempting to recover {file}...")
                pdfReader = file_recovery(file, myzip)  # attempting to recover file

    with open(os.path.join(OUTPUT_PATH, 'pdf_files.json'), 'w', encoding="utf-8") as outfile:
        try:
            json.dump(pdf_dict, outfile, ensure_ascii=False, indent=4)
        except UnicodeEncodeError as e:
            logger.warning(e)
            logger.info(f"Skipping...")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # Necessary paths
    TASK_DIR = Path(__file__).resolve().parents[1]
    OUTPUT_PATH = os.path.join(TASK_DIR, "output")
    INPUT_PATH = os.path.join(TASK_DIR, "input", "onedrive_docs.zip")

    main()

'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--creds_file', required=True,
                        help="AWS credentials JSON file")
    parser.add_argument('-l', '--language', required=True,
                        help="Language for sentence preprocessing/splitting. Current options are: english, spanish")
    parser.add_argument('-n', '--min_num_words', default=5,
                        help="Minimum number of words that a sentence needs to have to be stored")
    parser.add_argument('-p', '--print_every', default=100,
                        help="Print status of preprocessing every X iterations")

    args = parser.parse_args()

    main(args.creds_file, args.language, int(args.min_num_words), int(args.print_every))
'''
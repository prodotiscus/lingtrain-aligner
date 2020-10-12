from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

import json
import PyPDF2


class PageBuffer:
    def __init__(self, page=0):
        self.minimal = page
        self.page = page
        self.pages = {}

    def write(self, x):
        if self.page not in self.pages:
            self.pages[self.page] = x
        else:
            self.pages[self.page] += x

    def get_pages(self):
        for n in range(self.minimal, self.page):
            yield n, self.pages[n]

    def create_json(self):
        return json.dumps(self.__dict__, indent=2)


class PageBufferFromJSON(PageBuffer):
    def __init__(self, json_string):
        PageBuffer.__init__(self)
        self.__dict__ = json.loads(json_string)


def put_pdf_into_buffer(file_path):
    buff = PageBuffer()
    with open(file_path, "rb") as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, buff, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            buff.page += 1

    return buff


class ClassifyLine:
    def __init__(self, content, index):
        ...

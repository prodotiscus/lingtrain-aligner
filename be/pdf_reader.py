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
        self.occurrences = {}

    def write(self, x):
        if self.page not in self.pages:
            self.pages[self.page] = x
        else:
            self.pages[self.page] += x

    def get_pages(self):
        for n in range(self.minimal, self.page):
            yield n, self.pages[n]

    def by_line(self, rules):
        for page_index, page_content in self.get_pages():
            for line_index, line_content in enumerate(page_content.splitlines()):
                line = FlaggedPageLine(line_content, self, page_index, line_index)
                for (func, flg) in rules.items():
                    if func(line):
                        line.flags = flg
                yield page_index, line_index, line

    def create_json(self):
        return json.dumps(self.__dict__, indent=2)


class FlaggedPageLine:
    def __init__(self, linestring, buffer, pin, lin):
        self.text = linestring
        self.buffer = buffer
        self.pin = pin
        self.lin = lin
        self._flags = []

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, new_flags):
        for f in set(new_flags):
            if f not in self._flags:
                self._flags.append(f)
                self.buffer.occurrences[f] = (self.pin, self.lin)

    def __gt__(self, flag):
        if flag not in self.buffer.occurrences:
            return False
        o = self.buffer.occurrences[flag]
        return self.pin > o[0] or self.lin > o[1]

    def __lt__(self, flag):
        if flag not in self.buffer.occurrences:
            return False
        o = self.buffer.occurrences[flag]
        return o[0] > self.pin or o[1] > self.lin


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

from be.pdf_reader import *
import PyPDF2


def test_main():
    r = PyPDF2.PdfFileReader("Nabokov-Pale_Fire.pdf")

    writer = PyPDF2.PdfFileWriter()

    for page in range(0, 4):
        writer.addPage(r.getPage(page))

    output_filename = "Nabokov-Pale_Fire-cut-0-4.pdf"

    with open(output_filename, "wb") as output:
        writer.write(output)

    buffer = put_pdf_into_buffer(output_filename)

    assert True

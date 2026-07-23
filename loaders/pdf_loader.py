from pypdf import PdfReader


def load_pdf(filename):
    """
    Reads a PDF and returns all text.
    """

    reader = PdfReader(filename)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text
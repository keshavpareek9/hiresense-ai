import pdfplumber


def extract_text_from_pdf(file) -> str:
    """
    Extract text from an uploaded PDF file.
    Combines text from all pages.
    """

    text_chunks = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)

    return "\n".join(text_chunks)

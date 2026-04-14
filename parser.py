# Reads a resume PDF and returns the plain text.

import pdfplumber


def parse_resume(file_path):
    """Pull text from every page of a PDF and join them together."""
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return '\n'.join(text_parts)

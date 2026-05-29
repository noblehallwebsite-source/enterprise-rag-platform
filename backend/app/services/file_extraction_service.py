import logging
from pypdf import PdfReader
from docx import Document

logger = logging.getLogger(__name__)

def extract_pdf_text(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(f"[EXTRACTOR ERROR] Failed parsing PDF at {file_path}: {str(e)}")
        raise e

def extract_docx_text(file_path: str) -> str:
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.error(f"[EXTRACTOR ERROR] Failed parsing DOCX at {file_path}: {str(e)}")
        raise e
import io
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        if page_text := page.extract_text():
            text += page_text + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks using Langchain."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

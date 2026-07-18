import io
from typing import List, Dict
from pypdf import PdfReader
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentParser:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

    def extract_text(self, file_content: bytes, file_ext: str) -> str:
        """Extract text from supported file types."""
        if file_ext == "txt":
            return file_content.decode("utf-8", errors="ignore")
            
        elif file_ext == "pdf":
            reader = PdfReader(io.BytesIO(file_content))
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return "\n".join(text)
            
        elif file_ext == "docx":
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")

    def chunk_text(self, text: str) -> List[str]:
        """Split text into smaller chunks."""
        return self.text_splitter.split_text(text)

    def process_document(self, file_content: bytes, file_ext: str) -> List[Dict[str, str]]:
        """Extract and chunk document, returning list of chunk dicts."""
        raw_text = self.extract_text(file_content, file_ext)
        chunks = self.chunk_text(raw_text)
        
        return [{"text": chunk, "chunk_index": i} for i, chunk in enumerate(chunks)]

document_parser = DocumentParser()

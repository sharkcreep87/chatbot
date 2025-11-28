import os
import re
from typing import List, Dict, Any
import pdfplumber
from pathlib import Path


class PDFService:
    """Service for processing PDF files"""

    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from a PDF file"""
        text_content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            return "\n\n".join(text_content)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                last_break = max(last_period, last_newline)

                if last_break > start:
                    end = last_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap if end < len(text) else end

        return chunks

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF"""
        metadata = {}

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata['num_pages'] = len(pdf.pages)
                metadata['pdf_metadata'] = pdf.metadata or {}

                # Extract some basic stats
                total_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        total_text += text

                metadata['total_characters'] = len(total_text)
                metadata['total_words'] = len(total_text.split())

        except Exception as e:
            metadata['error'] = str(e)

        return metadata

    async def save_upload(self, file_content: bytes, filename: str, user_id: int) -> str:
        """Save uploaded file to disk"""
        # Create user-specific directory
        user_dir = self.upload_dir / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)

        # Generate unique filename
        file_path = user_dir / filename

        # If file exists, add counter
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(filename)
            file_path = user_dir / f"{name}_{counter}{ext}"
            counter += 1

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        return str(file_path)


# Create singleton instance
pdf_service = PDFService()

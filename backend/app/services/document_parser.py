from pathlib import Path
import logging

import fitz
from docx import Document
from PIL import Image

logger = logging.getLogger(__name__)


class DocumentParser:

    def parse(self, file_path: str) -> str:
        extension = Path(file_path).suffix.lower()

        if extension == ".pdf":
            return self._parse_pdf(file_path)
        if extension == ".docx":
            return self._parse_docx(file_path)
        if extension == ".doc":
            return self._parse_legacy_doc(file_path)
        if extension == ".txt":
            return self._parse_txt(file_path)
        if extension in {".png", ".jpg", ".jpeg"}:
            return self._parse_image(file_path)

        raise ValueError(f"Unsupported file type: {extension}")

    def _parse_pdf(self, file_path: str) -> str:
        text = ""
        pdf = fitz.open(file_path)
        for page in pdf:
            text += page.get_text()
        pdf.close()
        return text.strip()

    def _parse_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()

    def _parse_legacy_doc(self, file_path: str) -> str:
        try:
            from unstructured.partition.auto import partition

            elements = partition(filename=file_path)
            text = "\n".join(str(element) for element in elements).strip()
            if text:
                return text
        except Exception as exc:
            logger.warning("Legacy DOC parsing failed for %s: %s", file_path, exc)

        raise ValueError(
            "Legacy .doc parsing failed. Please upload a .docx, .pdf, or .txt version."
        )

    def _parse_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read().strip()

    def _parse_image(self, file_path: str) -> str:
        """
        Attempt OCR using pytesseract if installed.
        Falls back to returning image metadata for LLM context.
        """
        try:
            import pytesseract
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="eng")
            return text.strip() if text.strip() else self._image_metadata(file_path)
        except ImportError:
            logger.info("pytesseract not installed — using image metadata for context.")
            return self._image_metadata(file_path)
        except Exception as exc:
            logger.warning("OCR failed for %s: %s", file_path, exc)
            return self._image_metadata(file_path)

    @staticmethod
    def _image_metadata(file_path: str) -> str:
        try:
            img = Image.open(file_path)
            name = Path(file_path).name
            return (
                f"[Image document: {name}, size {img.size[0]}x{img.size[1]}px, "
                f"format {img.format}]. "
                "This appears to be a scanned legal document. "
                "Please provide the text content manually or use a PDF/DOCX version for best results."
            )
        except Exception:
            return "[Image document — text extraction not available for this file.]"


document_parser = DocumentParser()

from pathlib import Path
import tempfile

from fastapi import UploadFile

from app.services.file_validator import file_validator
from app.services.document_parser import document_parser


class UploadService:

    async def process_upload(self, file: UploadFile):

        extension = file_validator.validate(file)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(await file.read())

            temp_path = temp_file.name

        extracted_text = document_parser.parse(temp_path)

        Path(temp_path).unlink(missing_ok=True)

        return {
            "text": extracted_text,
            "file_name": file.filename,
            "file_size": file.size
        }


upload_service = UploadService()
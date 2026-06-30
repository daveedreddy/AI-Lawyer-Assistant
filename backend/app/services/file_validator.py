from fastapi import UploadFile

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg"
}


class FileValidator:

    @staticmethod
    def validate(file: UploadFile):

        extension = "." + file.filename.split(".")[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return extension


file_validator = FileValidator()
from fastapi import UploadFile

ALLOWED_EXTENSIONS = {
    ".doc",
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
        if not file.filename or "." not in file.filename:
            raise ValueError("Uploaded file must have a valid file extension.")

        extension = "." + file.filename.rsplit(".", 1)[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        return extension


file_validator = FileValidator()

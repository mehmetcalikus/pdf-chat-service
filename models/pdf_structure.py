from uuid import uuid4

class PDF:
    def __init__(self, pdf_id: str, filename: str, text: str, page_count: int):
        self.pdf_id = pdf_id
        self.filename = filename
        self.text = text
        self.page_count = page_count

    def to_dict(self):
        return {
            "pdf_id": self.pdf_id,
            "filename": self.filename,
            "page_count": self.page_count,
            "text": self.text
        }

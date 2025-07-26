from PyPDF2 import PdfReader

from PyPDF2 import PdfReader

def extract_fields_from_pdf(pdf_path):
    fields = {}
    reader = PdfReader(pdf_path)
    
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                field = annot.get_object()
                key = field.get("/T")
                val = field.get("/V")

                if key:
                    # Normalize to string (e.g. convert NameObject, TextStringObject, or None to str)
                    fields[key] = str(val).strip() if val is not None else ""

    return fields

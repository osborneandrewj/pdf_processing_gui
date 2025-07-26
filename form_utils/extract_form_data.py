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


# Example usage
pdf_path = "test_pdfs/example.pdf"
fields = extract_fields_from_pdf(pdf_path)

# Print out formatted summary
print(f"Site #: {fields.get('Site Number:', 'Unknown')}")
print(f"Site Address: {fields.get('Site Address:', '')}")
print(f"Shipping Address: {fields.get('Shipping Address:', '')}")
print(f"PO #: {fields.get('Genoa Purchase Order:', '')}\n")

for i in [1, 2]:
    width = fields.get(f"W{i} Rough Opening Width:", "Unknown")
    height = fields.get(f"W{i} Rough Opening Height:", "Unknown")
    qty = fields.get(f"W{i} Quantity:", "0")
    std = fields.get(f"W{i} Use Standard:", "Off")
    notes = fields.get(f"W{i} Notes:", "")
    
    if qty and qty != "0":
        print(f"Window {i}")
        print("Genoa Custom Interior Self Closing Slider")
        dims = 'Standard Size (47-5/8" x 35-5/8")' if std == "Yes" else f"Dimensions: {width}\" x {height}\""
        print(dims)
        print("Frame: Aluminum (Not Loaded)")
        print("BR: Level 1")
        print("Glazing: Acrylic")
        print(f"Direction: {'Left Hand Slide' if i == 1 else 'Right Hand Slide'}")
        if notes:
            print(f"Notes: {notes}")
        print()

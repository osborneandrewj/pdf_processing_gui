from form_utils.extract_form_data import extract_fields_from_pdf
from pathlib import Path
import re

def get_value(field_dict):
    if isinstance(field_dict, dict):
        return field_dict.get("/V", "").strip()
    return str(field_dict).strip()

def clean_dimension(val):
    if not val:
        return "None"
    return val.replace('"', '').replace('”', '').replace("″", "").strip()

from fractions import Fraction

def inches_to_float(dim_str):
    """
    Convert a string like '47-1/2' or '35 3/8"' to float inches.
    """
    dim_str = dim_str.replace('"', "").replace("”", "").strip()
    if not dim_str:
        return None
    try:
        if "-" in dim_str:
            whole, frac = dim_str.split("-")
            return float(whole) + float(Fraction(frac))
        elif " " in dim_str:
            whole, frac = dim_str.split(" ")
            return float(whole) + float(Fraction(frac))
        else:
            return float(Fraction(dim_str))
    except Exception:
        return None

def float_to_frac_string(value):
    """
    Convert float inches to string like '47-1/8'
    """
    whole = int(value)
    frac = Fraction(value - whole).limit_denominator(8)
    if frac == 0:
        return f"{whole}"
    return f"{whole}-{frac.numerator}/{frac.denominator}"

def format_output(fields):
    output_lines = []
    site_number = fields.get("Site Number", "Unknown").strip()
    output_lines.append(f"Site # {site_number}\n")

    for i in range(1, 3):  # Only W1 and W2
        prefix = f"W{i}"
        width_raw = fields.get(f"{prefix} Rough Opening Width", "").strip()
        height_raw = fields.get(f"{prefix} Rough Opening Height", "").strip()
        quantity = fields.get(f"{prefix} Quantity", "").strip()

        direction = "Left Hand Slide" if i == 1 else "Right Hand Slide"

        if not any([width_raw, height_raw, quantity]):
            continue

        for q in range(int(quantity) if quantity.isdigit() else 1):
            output_lines.append(f"Window {i}")
            output_lines.append("Genoa Custom Interior Self Closing Slider")

            dims = []

            # Convert and subtract 3/8"
            width_val = inches_to_float(width_raw)
            height_val = inches_to_float(height_raw)

            if width_val:
                dims.append(float_to_frac_string(width_val - 0.375))
            if height_val:
                dims.append(float_to_frac_string(height_val - 0.375))

            if dims:
                output_lines.append(f"Dimensions: {' x '.join(dims)}")

            output_lines.append("Frame: Aluminum (Not Loaded)")
            output_lines.append("BR: Level 1")
            output_lines.append("Glazing: Acrylic")
            output_lines.append(f"Direction: {direction}")
            output_lines.append("")

    return "\n".join(output_lines)

def process_pdf(input_path, output_path):
    fields = extract_fields_from_pdf(input_path)
    print("🔎 Raw Fields Found:")
    for k, v in fields.items():
        print(f"{k}: {v}")

    formatted = format_output(fields)
    print("\n📄 Final Formatted Output:\n" + formatted)

    with open(output_path, "w") as f:
        f.write(formatted)

    print(f"✅ Saved: {output_path}")


if __name__ == "__main__":
    input_pdf = "test_pdfs/example.pdf"
    output_txt = "output/window_order_output.txt"
    Path("output").mkdir(exist_ok=True)

    process_pdf(input_pdf, output_txt)

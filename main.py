from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from pathlib import Path
import zipfile
from datetime import datetime

# Import your existing processing functions
from form_utils.extract_form_data import extract_fields_from_pdf
from fractions import Fraction
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size

# Your existing processing functions
def get_value(field_dict):
    if isinstance(field_dict, dict):
        return field_dict.get("/V", "").strip()
    return str(field_dict).strip()

def clean_dimension(val):
    if not val:
        return "None"
    return val.replace(""", "").replace(""", "").replace("″", "").strip()

def inches_to_float(dim_str):
    """Convert a string like "47-1/2" or "35 3/8"" to float inches."""
    dim_str = dim_str.replace(""", "").replace(""", "").strip()
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
    """Convert float inches to string like "47-1/8"""
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
                output_lines.append(f"Dimensions: {" x ".join(dims)}")
            
            output_lines.append("Frame: Aluminum (Not Loaded)")
            output_lines.append("BR: Level 1")
            output_lines.append("Glazing: Acrylic")
            output_lines.append(f"Direction: {direction}")
            output_lines.append("")
    
    return "\n".join(output_lines)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            file.save(temp_pdf.name)
            
            # Process the PDF
            fields = extract_fields_from_pdf(temp_pdf.name)
            formatted_output = format_output(fields)
            
            # Create output file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"window_order_{timestamp}.txt"
            
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_output:
                temp_output.write(formatted_output)
                temp_output_path = temp_output.name
        
        # Clean up input file
        os.unlink(temp_pdf.name)
        
        return jsonify({
            "success": True,
            "output": formatted_output,
            "filename": output_filename,
            "download_path": temp_output_path,
            "debug_fields": dict(fields)  # Add field names for debugging
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<path:filepath>")
def download_file(filepath):
    try:
        return send_file(filepath, as_attachment=True, download_name="window_order.txt")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
import base64
import io
from pathlib import Path

import fitz
from PIL import Image


def pdf_to_pil_image(pdf_input):
    """
    Universal Input Handler:
    - If input is a STRING or PATH -> It opens the file from disk (Dev Mode).
    - If input is BYTES -> It reads from memory (Production/API Mode).
    """
    print(f"🔄 Processing PDF input type: {type(pdf_input)}")

    try:
        # Case A: Production (Bytes from API)
        if isinstance(pdf_input, (bytes, bytearray, io.BytesIO)):
            # "stream" tells fitz to read from RAM, not disk
            doc = fitz.open(stream=pdf_input, filetype="pdf")

        # Case B: Dev/Test (File Path)
        elif isinstance(pdf_input, (str, Path)):
            doc = fitz.open(pdf_input)

        else:
            print("❌ Error: Unsupported input type")
            return None

        # --- Standard Logic (Same for both) ---
        page = doc.load_page(0)
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img

    except Exception as e:
        print(f"❌ Conversion Failed: {e}")
        return None


def pil_to_base64(pil_image):
    """Converts PIL Image -> Base64 String for the LLM"""
    buffered = io.BytesIO()

    # Save as JPEG (Much smaller/faster than PNG for LLMs)
    pil_image.save(buffered, format="JPEG")

    # Get the raw bytes and encode them
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Return standard data URI format
    return f"data:image/jpeg;base64,{img_str}"

from app.utils.pdf_transcibe import pdf_to_pil_image, pil_to_base64
from langchain_core.messages import HumanMessage

def get_inbody_analysis_message(file_path):
    pil_image = pdf_to_pil_image(file_path)
    
    if pil_image is None:
        return None
    
    image_data = pil_to_base64(pil_image)
    
    message = HumanMessage(
        content=[
            {
                "type": "text", 
                "text": "this image contain my inbody information please analyze it."
            },
            {
                "type": "image_url",
                "image_url": {"url": image_data}  # Pass the Base64 string here
            }
        ]
    )
    return message
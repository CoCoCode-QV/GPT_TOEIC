import streamlit as st
from dotenv import dotenv_values
from PyPDF2 import PdfReader
from docx import Document
import openai
from PIL import Image
import pytesseract
import pdfplumber
import tempfile
import io


def get_text_from_word(word_docs):
    text = ""
    for doc in word_docs:
        doc = Document(doc)
        for para in doc.paragraphs:
            text += para.text
    return text


def get_text_from_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# def extract_text_from_pdf_image(pdf_image_paths):
#     text = ""
#     for pdf_path in pdf_image_paths:
#         with pdfplumber.open(pdf_path) as pdf:
#             for i, page in enumerate(pdf.pages):
#                 if page.chars:  # If the page has textual content
#                     for char in page.chars:
#                         text += char
#                 else:  # If the page contains an image
#                     print(f"Page {i + 1} contains an image.")
#                     images = page.images
#                     for idx, img in enumerate(images):
#                         image_data = img["stream"].get("Data")
#                         if image_data:
#                             image = io.BytesIO(image_data)
#                             image.seek(0)
#                             image = Image.open(image)
#                             with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
#                                 image.save(temp_file.name, format="PNG")
#                                 output = pytesseract.image_to_string(temp_file.name)
#                                 print(f"Extracted text from page {i + 1}, image {idx + 1}:")
#                                 text += output
#     return text


def get_text_from_uploaded_files(uploaded_files):
    pdf_docs = [file for file in uploaded_files if file.name.endswith(".pdf")]
    word_docs = [file for file in uploaded_files if file.name.endswith((".docx", ".doc"))]

    pdf_text = get_text_from_pdf(pdf_docs)
    word_text = get_text_from_word(word_docs)

    return pdf_text + "\n\n" + word_text


def Generation(usePrompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": usePrompt}
        ]
    )

    return completion.choices[0].message.content


def main():

    st.set_page_config(page_title="ChatBot", page_icon=":books:")

    st.header("Fine tuning with multiple PDFs")

    prompt = None
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader("Upload your PDFs or word here and click on Process", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                secrets = dotenv_values(".env")
                openai.api_key = secrets["OPENAI_API_KEY"]
                windows_path = r'D:\OCR\tesseract.exe'
                pytesseract.tesseract_cmd = windows_path
                raw_text = get_text_from_uploaded_files(uploaded_files)
                st.write(raw_text)
                prompt = f"""
                `Here's the content from the PDF file:
                {raw_text}

                Now, let's fine-tune the model using a few examples. 

                Question: 
                    Let's create a set of questions similar to the Toeic test just trained above to practice.\n
                
                
                """


    if prompt:
        st.text_area("Kim Nhung:", value=Generation(prompt),height=900, max_chars=None)


if __name__=="__main__":
    main()
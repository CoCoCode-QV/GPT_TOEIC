import streamlit as st
from dotenv import dotenv_values
from PyPDF2 import PdfReader
from docx import Document
from openai import OpenAI
from PIL import Image
import pytesseract


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


secrets = dotenv_values(".env")
client = OpenAI(
  api_key=secrets["OPENAI_API_KEY"]
)


def Generation(usePrompt):
    completion = client.chat.completions.create(
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
                raw_text = get_text_from_uploaded_files(uploaded_files)
                print(raw_text)
                prompt = f"""
                `Here's the content from the PDF file:
                {raw_text}

                Now, let's fine-tune the model using a few examples. 

                Question: 
                    Let's create a set of questions similar to the Toeic test just trained above\n
                    The important thing is to have enough questions like the model I gave you and the same number of questions.\n
                   If the training data is part 6 or part 7, it is necessary to create passages similar to the trained data and questions appropriate to each created passage.\n
                
                """


    if prompt:
        st.text_area("Kim Nhung:", value=Generation(prompt),height=900, max_chars=None)


if __name__=="__main__":
    main()
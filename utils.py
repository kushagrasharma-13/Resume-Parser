import PyPDF2

def extract_text_from_pdf(uploaded_file):
    pdf_text = ""
    reader = PyPDF2.PdfReader(uploaded_file)
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        pdf_text += page.extract_text() + "\n"
    return pdf_text

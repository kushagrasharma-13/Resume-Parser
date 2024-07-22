import json
import os
import streamlit as st
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent
from utils import extract_text_from_pdf

load_dotenv()

class ResumeParsingAgent(AssistantAgent):
    def __init__(self, name="resume_parsing_agent", llm_config=None):
        system_message = (
            "You are an AI specialized in extracting and organizing information from resumes. "
            "Please analyze the provided resume text and return the information in a structured JSON format with the following sections:\n"
            "1. Contact Information\n"
            "2. Professional Experience\n"
            "3. Projects\n"
            "4. Skills\n"
            "5. Education\n"
            "6. Achievements\n"
            "7. Extra-Curricular Activities\n"

            "The output must contain only the JSON file and no other comments or data"
        )
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)

class ResumeUserProxyAgent(UserProxyAgent):
    def __init__(self, name="user_proxy", llm_config=None):
        super().__init__(name=name, llm_config=llm_config, human_input_mode="NEVER", max_consecutive_auto_reply=0, code_execution_config=False)

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
llm_config = {
    "model": "llama3-8b-8192",
    "api_key": GROQ_API_KEY,
    "api_type": "groq",
    "base_url": "https://api.groq.com/openai/v1",
}

# Initialize the Resume Parsing Assistant Agent
resume_parsing_agent = ResumeParsingAgent(llm_config=llm_config)
resume_user_proxy = ResumeUserProxyAgent(llm_config=llm_config)

# Function to clean text
def clean_text(text):
    replacements = {
        '\u2013': '-',
        '\u2014': '-',
        '\u201c': '"',
        '\u201d': '"',
        '\u2022': '',
        '\u2019': "'",
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

def preprocess_resume_text(resume_text):
    cleaned_text = clean_text(resume_text)
    lines = cleaned_text.split('\n')
    processed_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(processed_lines)

def postprocess_parsed_resume(parsed_resume):
    parsed_resume_json = json.loads(parsed_resume)

    if "Contact Information" not in parsed_resume_json:
        parsed_resume_json["Contact Information"] = {}
    contact_info_defaults = {"Email": "Not Provided", "Phone": "Not Provided", "LinkedIn": "Not Provided", "GitHub": "Not Provided"}
    parsed_resume_json["Contact Information"] = {**contact_info_defaults, **parsed_resume_json["Contact Information"]}
    return parsed_resume_json

def parse_resume_single_call(resume_text):
    prompt = (
        "Please analyze the provided resume text and return the information in a structured JSON format with the following sections:\n"
        "1. Contact Information\n"
        "2. Professional Experience\n"
        "3. Projects\n"
        "4. Skills\n"
        "5. Education\n"
        "6. Achievements\n"
        "7. Extra-Curricular Activities\n\n"
        "Resume Text:\n"
        f"{resume_text}\n\n"
        "Return the extracted information in the following JSON format:\n"
        "{\n"
        "  'Contact Information': { 'Email': '', 'Phone': '', 'LinkedIn': '', 'GitHub': '' },\n"
        "  'Professional Experience': [],\n"
        "  'Projects': [],\n"
        "  'Skills': [],\n"
        "  'Education': [],\n"
        "  'Achievements': [],\n"
        "  'Extra-Curricular Activities': []\n"
        "}"
    )
    
    response = resume_user_proxy.initiate_chat(resume_parsing_agent, message=prompt)
    print("#######################################################")
    print(response.chat_history[-1]["content"].strip())
    print("#######################################################")
    return response.chat_history[-1]["content"].strip()

st.title("Resume Parser to JSON")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
default_file_path = "Kushagra_Sharma_Resume.pdf"

if uploaded_file is not None:
    resume_text = extract_text_from_pdf(uploaded_file)
    file_name = uploaded_file.name
else:
    with open(default_file_path, "rb") as file:
        resume_text = extract_text_from_pdf(file)
    file_name = default_file_path

preprocessed_resume_text = preprocess_resume_text(resume_text)
raw_parsed_resume = parse_resume_single_call(preprocessed_resume_text)
parsed_resume = postprocess_parsed_resume(raw_parsed_resume)

st.text(f"Currently using file: {file_name}")
print(parsed_resume)
st.json(parsed_resume)

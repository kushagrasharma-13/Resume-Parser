import re
from utils import extract_text_from_pdf
import streamlit as st

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

def extract_contact_info(line, resume_json):
    phone_number_pattern = re.compile(r'\+?\d[\d\s\-]+\d')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    linkedin_pattern = re.compile(r'(linkedin.com/in/[A-Za-z0-9-_]+)', re.IGNORECASE)
    github_pattern = re.compile(r'(github.com/[A-Za-z0-9-_]+)', re.IGNORECASE)

    contact_lines = re.split(r'\s*[—-]\s*|\s*\|\|\s*|\s*,\s*', line)
    for item in contact_lines:
        item = item.strip()
        if not item:
            continue
        if "Email" not in resume_json["Contact Information"] and email_pattern.search(item):
            resume_json["Contact Information"]["Email"] = email_pattern.search(item).group()
        elif "Phone" not in resume_json["Contact Information"] and phone_number_pattern.search(item):
            resume_json["Contact Information"]["Phone"] = phone_number_pattern.search(item).group()
        elif "LinkedIn" not in resume_json["Contact Information"] and linkedin_pattern.search(item):
            resume_json["Contact Information"]["LinkedIn"] = linkedin_pattern.search(item).group()
        elif "GitHub" not in resume_json["Contact Information"] and github_pattern.search(item):
            resume_json["Contact Information"]["GitHub"] = github_pattern.search(item).group()

def parse_resume(resume_text):
    resume_json = {
        "Contact Information": {},
        "Professional Experience": [],
        "Projects": [],
        "Skills": [],
        "Education": [],
        "Achievements": [],
        "Extra-Curricular Activities": []
    }

    section_keywords = {
        "Contact Information": ["Contact Information", "Contact Info", "Contact"],
        "Professional Experience": ["Professional Experience", "Work Experience", "Experience"],
        "Projects": ["Projects", "Project"],
        "Skills": ["Skills", "Technical Skills"],
        "Education": ["Education", "Academic Background"],
        "Achievements": ["Achievements", "Awards", "Honors"],
        "Extra-Curricular Activities": ["Extra-Curricular Activities", "Extracurricular Activities", "Activities", "Volunteer Experience"]
    }

    contact_info_patterns = ["@", "linkedin", "github", "phone", "+91"]
    section = None

    lines = resume_text.split('\n')
    for line in lines:
        line = clean_text(line.strip())
        if not line:
            continue

        section_detected = False
        for key, keywords in section_keywords.items():
            if any(keyword.lower() in line.lower() for keyword in keywords):
                section = key
                section_detected = True
                break

        if section_detected:
            continue

        if section == "Contact Information" or any(pattern in line.lower() for pattern in contact_info_patterns):
            section = "Contact Information"
            extract_contact_info(line, resume_json)
        elif section and section != "Contact Information":
            resume_json[section].append(line)

    if "Phone" not in resume_json["Contact Information"]:
        resume_json["Contact Information"]["Phone"] = "Not Provided"
    if "Email" not in resume_json["Contact Information"]:
        resume_json["Contact Information"]["Email"] = "Not Provided"
    if "LinkedIn" not in resume_json["Contact Information"]:
        resume_json["Contact Information"]["LinkedIn"] = "Not Provided"
    if "GitHub" not in resume_json["Contact Information"]:
        resume_json["Contact Information"]["GitHub"] = "Not Provided"

    return resume_json

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

parsed_resume = parse_resume(resume_text)
st.text(f"Currently using file: {file_name}")
st.json(parsed_resume)

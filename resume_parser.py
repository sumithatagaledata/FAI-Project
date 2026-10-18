"""
Resume Parser Module.

Extracts text from PDF resumes using pypdf and identifies structured sections:
- Name
- Email & Phone
- Skills
- Education
- Experience
- Projects
- Certifications

If any field cannot be found, returns 'Not Available' instead of fabricating data.
"""

import re
import os
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from nlp_processor import extract_skills, extract_experience_years, extract_education_level


class ResumeParser:
    """Extracts raw text and structured candidate information from resume files."""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Reads and extracts plain text from a PDF file using pypdf.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Resume file not found at {pdf_path}")
            
        full_text = []
        try:
            reader = PdfReader(pdf_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    full_text.append(text)
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            raise ValueError(f"Failed to read PDF file: {str(e)}")
            
        extracted_content = "\n".join(full_text).strip()
        return extracted_content

    @classmethod
    def parse_resume(cls, pdf_path: str, filename: str = "") -> Dict[str, Any]:
        """
        Parses PDF and extracts structured information dictionary.
        """
        raw_text = cls.extract_text_from_pdf(pdf_path)
        if not raw_text or len(raw_text.strip()) < 10:
            return {
                "name": filename.replace(".pdf", "").replace("_", " ").title() if filename else "Not Available",
                "email": "Not Available",
                "phone": "Not Available",
                "education": "Not Available",
                "experience_years": 0.0,
                "skills": [],
                "projects": "Not Available",
                "certifications": "Not Available",
                "raw_text": raw_text or "",
                "resume_filename": filename or os.path.basename(pdf_path),
                "is_empty": True
            }

        # Clean text
        cleaned_text = cls._clean_text(raw_text)

        # 1. Contact Info Extraction
        email = cls._extract_email(cleaned_text)
        phone = cls._extract_phone(cleaned_text)
        name = cls._extract_name(cleaned_text, filename, email)

        # 2. Section Segmentations
        sections = cls._segment_sections(cleaned_text)

        # 3. Skills Extraction
        skills = extract_skills(cleaned_text)
        if sections.get("skills"):
            section_skills = extract_skills(sections["skills"])
            skills = sorted(list(set(skills + section_skills)))

        # 4. Experience Extraction
        exp_years = extract_experience_years(cleaned_text)
        experience_summary = sections.get("experience") or (f"{exp_years:g} years of industry experience" if exp_years > 0 else "Not Available")

        # 5. Education Extraction
        edu_info = extract_education_level(cleaned_text)
        education_summary = sections.get("education") or (f"{edu_info['level']} Degree" if edu_info['level'] != "Not Specified" else "Not Available")

        # 6. Projects & Certifications
        projects = sections.get("projects", "Not Available")
        certifications = sections.get("certifications", "Not Available")

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "education": education_summary,
            "experience_years": exp_years,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "raw_text": cleaned_text,
            "resume_filename": filename or os.path.basename(pdf_path),
            "is_empty": False
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Removes duplicate whitespace and normalizes newlines."""
        text = text.replace('\r', '\n')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    @staticmethod
    def _extract_email(text: str) -> str:
        """Extracts candidate email address."""
        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        match = re.search(pattern, text)
        return match.group(0) if match else "Not Available"

    @staticmethod
    def _extract_phone(text: str) -> str:
        """Extracts candidate phone number."""
        patterns = [
            r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,12}'
        ]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                phone = match.group(0).strip()
                # Basic check for reasonable length
                digits = re.sub(r'\D', '', phone)
                if 10 <= len(digits) <= 14:
                    return phone
        return "Not Available"

    @classmethod
    def _extract_name(cls, text: str, filename: str = "", email: str = "") -> str:
        """
        Heuristic extraction of candidate's name from header or filename.
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Check first 5 non-empty lines
        for line in lines[:5]:
            # Skip if line contains email, phone, or section headers
            if "@" in line or any(char.isdigit() for char in line):
                continue
            if any(h in line.lower() for h in ["resume", "curriculum", "vitae", "contact", "profile", "summary"]):
                continue
            
            # Words count between 2 and 4 and all alphabetic
            words = line.split()
            if 1 <= len(words) <= 4 and all(w.replace('.', '').isalpha() for w in words):
                if len(line) <= 40:
                    return line.title()

        # Fallback to email username if available
        if email != "Not Available" and "@" in email:
            uname = email.split("@")[0]
            clean_uname = re.sub(r'[^a-zA-Z]', ' ', uname).strip()
            if clean_uname:
                return clean_uname.title()

        # Fallback to sanitized filename
        if filename:
            name_part = os.path.splitext(filename)[0]
            name_part = re.sub(r'[_\-\d]', ' ', name_part).strip()
            if name_part:
                return name_part.title()

        return "Not Available"

    @staticmethod
    def _segment_sections(text: str) -> Dict[str, str]:
        """
        Splits resume text into common conceptual sections:
        Education, Experience, Skills, Projects, Certifications.
        """
        section_headers = {
            "education": ["education", "academic background", "academics", "qualifications"],
            "experience": ["experience", "work experience", "employment history", "work history", "professional experience"],
            "skills": ["skills", "technical skills", "core competencies", "technologies", "expertise"],
            "projects": ["projects", "academic projects", "key projects", "personal projects"],
            "certifications": ["certifications", "certificates", "licenses", "courses", "achievements"]
        }

        lines = text.split('\n')
        current_section = None
        sections_content: Dict[str, List[str]] = {k: [] for k in section_headers}

        for line in lines:
            line_clean = line.strip().lower()
            matched_header = None
            
            for sec_name, headers in section_headers.items():
                if any(line_clean == h or line_clean.startswith(h + ":") or line_clean.startswith(h + " -") for h in headers):
                    matched_header = sec_name
                    break
                    
            if matched_header:
                current_section = matched_header
            elif current_section:
                sections_content[current_section].append(line)

        # Format sections
        result = {}
        for sec, content_lines in sections_content.items():
            content = '\n'.join(content_lines).strip()
            if content and len(content) > 5:
                result[sec] = content[:400] # Limit to relevant length

        return result

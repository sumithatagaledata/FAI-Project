"""
Sample Resume & Demonstration Data Generator.

Uses ReportLab to generate 5 realistic PDF resumes spanning various skillsets
and experience tiers to enable 1-click live demo during college project presentations.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

if os.environ.get("VERCEL"):
    SAMPLES_DIR = "/tmp/sample_resumes"
else:
    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")

SAMPLE_JOB_TITLE = "Senior Python & AI Developer"
SAMPLE_JOB_DESCRIPTION = """We are seeking a Senior Python & AI Developer with 3+ years of experience in building scalable backend systems and machine learning workflows.

Key Requirements:
- Strong proficiency in Python, SQL, and REST API development with Flask or FastAPI.
- Hands-on experience with Machine Learning libraries including Pandas, NumPy, Scikit-Learn, and NLP.
- Practical knowledge of PostgreSQL, SQLite, and Docker for containerized deployment.
- Experience with Git version control, Unit Testing, and Agile practices.
- Education: Bachelor's degree (B.Tech / B.E. / B.Sc) or Master's in Computer Science, Data Science, or related discipline.
"""

SAMPLE_CANDIDATES = [
    {
        "filename": "Aarav_Sharma_Senior_Python_AI.pdf",
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "title": "Senior Python & Machine Learning Engineer",
        "summary": "Innovative Software Engineer with 5+ years of experience designing scalable Python backends, REST APIs, and production Machine Learning pipelines.",
        "skills": "Python, Machine Learning, Scikit-Learn, Pandas, NumPy, Flask, FastAPI, SQL, PostgreSQL, Docker, Git, REST API, Unit Testing, Data Structures",
        "experience": "Senior Software Engineer (2021 - Present) at TechCorp Solutions: Developed Flask and FastAPI microservices. Integrated Scikit-Learn and Pandas ML models for automated analytics.\nPython Developer (2019 - 2021) at DataLogic Inc: Built SQL queries and RESTful APIs, containerized apps using Docker.",
        "education": "B.Tech in Computer Science and Engineering (2015 - 2019), National Institute of Technology.",
        "projects": "AI Resume Screener: Built an NLP-based recruitment filter using Python, Flask, and TF-IDF.\nPredictive Analytics Engine: Created scikit-learn classification pipeline processing 50k+ records.",
        "certifications": "AWS Certified Solutions Architect, DeepLearning.AI Machine Learning Specialization."
    },
    {
        "filename": "Priya_Patel_Data_Scientist.pdf",
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "+91 98111 22334",
        "title": "Data Scientist & AI Specialist",
        "summary": "Data Scientist with 3.5 years of experience specializing in Machine Learning, Natural Language Processing, and statistical data modeling.",
        "skills": "Python, Machine Learning, Deep Learning, NLP, Natural Language Processing, PyTorch, Pandas, NumPy, SQL, MySQL, Git, Data Analysis, Data Visualization",
        "experience": "Data Scientist (2022 - Present) at InsightAI Labs: Implemented NLP pipelines and deep learning models with PyTorch. Optimized SQL queries for large-scale data retrieval.\nJunior Data Analyst (2020 - 2022) at Quant Analytics: Performed exploratory data analysis with Pandas and Matplotlib.",
        "education": "M.Tech in Data Science (2018 - 2020), Indian Institute of Technology.\nB.E. in Information Technology (2014 - 2018).",
        "projects": "Customer Sentiment Classifier: Built an NLP text analysis tool with 92% accuracy.\nAutomated Sales Forecasting: Developed machine learning regression models in Python.",
        "certifications": "TensorFlow Developer Certificate, Advanced SQL for Data Scientists."
    },
    {
        "filename": "Rahul_Verma_Fullstack_Dev.pdf",
        "name": "Rahul Verma",
        "email": "rahul.verma@example.com",
        "phone": "+91 97222 33445",
        "title": "Full Stack Web Developer",
        "summary": "Full Stack Developer with 2.5 years of experience crafting responsive web interfaces and Python backend architectures.",
        "skills": "Python, Django, Flask, JavaScript, React, HTML, CSS, REST API, PostgreSQL, MongoDB, Git, Agile",
        "experience": "Full Stack Developer (2021 - Present) at WebSphere Dynamics: Built modern web dashboards with React and Django backends. Implemented secure REST APIs with token authentication.",
        "education": "B.Tech in Information Technology (2017 - 2021), State Technical University.",
        "projects": "E-Commerce Web Portal: Full-stack platform using React, Flask, and PostgreSQL.\nTask Collaboration Suite: Real-time project management tool built with Django and WebSockets.",
        "certifications": "Certified Full Stack Developer (Coursera), Meta Front-End Specialization."
    },
    {
        "filename": "Sneha_Rao_Data_Analyst_Fresher.pdf",
        "name": "Sneha Rao",
        "email": "sneha.rao@example.com",
        "phone": "+91 96333 44556",
        "title": "Junior Data Analyst (Fresher)",
        "summary": "Motivated Graduate with 1 year of internship experience in data wrangling, SQL queries, and Python data visualization.",
        "skills": "Python, SQL, SQLite, Pandas, NumPy, Matplotlib, Seaborn, Data Analysis, Data Visualization, Excel, Git",
        "experience": "Data Analyst Intern (2023 - 2024) at MetricsHub: Analyzed customer behavior datasets using Pandas and SQL. Built interactive charts with Seaborn and Matplotlib.",
        "education": "B.Sc in Computer Science (2020 - 2023), City Science College.",
        "projects": "Healthcare Data Analysis: Cleaned and visualized Covid-19 statistics using Pandas.\nMovie Recommendation System: Implemented collaborative filtering algorithm in Python.",
        "certifications": "Google Data Analytics Professional Certificate, Python for Data Science."
    },
    {
        "filename": "Vikram_Singh_DevOps_Engineer.pdf",
        "name": "Vikram Singh",
        "email": "vikram.singh@example.com",
        "phone": "+91 95444 55667",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "summary": "Infrastructure specialist with 4+ years of experience in CI/CD automation, cloud architecture, and container orchestration.",
        "skills": "Docker, Kubernetes, AWS, Linux, Bash, CI/CD, Terraform, Jenkins, Git, Python, Nginx, Ansible",
        "experience": "DevOps Engineer (2020 - Present) at CloudNine Systems: Managed AWS ECS and Kubernetes clusters. Automated deployment pipelines with Jenkins and Terraform.\nSystem Administrator (2018 - 2020) at InfraTech: Maintained Linux server fleet and Bash automation scripts.",
        "education": "B.Tech in Computer Science (2014 - 2018), Global Engineering Institute.",
        "projects": "Automated Multi-Cloud Deployer: Created Terraform templates for reproducible cloud setups.\nKubernetes Microservice Mesh: Deployed resilient container clusters on AWS.",
        "certifications": "Certified Kubernetes Administrator (CKA), AWS Certified DevOps Engineer."
    }
]


def generate_pdf_resume(cand: dict, output_path: str):
    """Generates a professional PDF resume using ReportLab."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CandName',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'CandSub',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563eb"),
        fontName="Helvetica-Bold",
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'CandContact',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    story = []

    # Header
    story.append(Paragraph(cand["name"], title_style))
    story.append(Paragraph(cand["title"], subtitle_style))
    contact_text = f"Email: {cand['email']} | Phone: {cand['phone']} | Location: Bangalore, India"
    story.append(Paragraph(contact_text, contact_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    story.append(Paragraph(cand["summary"], body_style))

    # Technical Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_heading))
    story.append(Paragraph(cand["skills"], body_style))

    # Work Experience
    story.append(Paragraph("WORK EXPERIENCE", section_heading))
    for exp_item in cand["experience"].split("\n"):
        if exp_item.strip():
            story.append(Paragraph(f"• {exp_item.strip()}", body_style))

    # Education
    story.append(Paragraph("EDUCATION", section_heading))
    for edu_item in cand["education"].split("\n"):
        if edu_item.strip():
            story.append(Paragraph(f"• {edu_item.strip()}", body_style))

    # Projects
    story.append(Paragraph("KEY PROJECTS", section_heading))
    for proj_item in cand["projects"].split("\n"):
        if proj_item.strip():
            story.append(Paragraph(f"• {proj_item.strip()}", body_style))

    # Certifications
    story.append(Paragraph("CERTIFICATIONS", section_heading))
    story.append(Paragraph(cand["certifications"], body_style))

    doc.build(story)


def generate_all_sample_resumes() -> str:
    """Generates all 5 sample resumes in the sample_resumes directory."""
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    generated_paths = []
    for cand in SAMPLE_CANDIDATES:
        out_path = os.path.join(SAMPLES_DIR, cand["filename"])
        generate_pdf_resume(cand, out_path)
        generated_paths.append(out_path)
    return SAMPLES_DIR

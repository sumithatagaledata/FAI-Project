"""
NLP and AI Matching Engine for Resume Screening.

Implements:
1. Text Preprocessing, Tokenization, and Stopwords Filtering
2. Comprehensive Skills Taxonomy & Skill Normalization
3. Experience & Education Requirement Extractors
4. Pure Python TF-IDF Vectorizer & Cosine Similarity Calculation
5. Multi-Factor Scoring Engine (Skills 50%, Experience 20%, Education 10%, TF-IDF 20%)
6. Explainability Generator ("Why this candidate matched")
"""

import re
import math
from collections import Counter
from typing import List, Dict, Set, Tuple, Any, Optional

# ==========================================
# 1. STOP WORDS SET (Pure Python NLP)
# ==========================================
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves", "will", "shall", "may", "might", "must", "also",
    "including", "responsibilities", "responsible", "working", "work", "role", "duties", "summary",
    "details", "experienced", "proficient", "strong", "knowledge", "ability", "team", "project", "projects"
}

# ==========================================
# 2. SKILL TAXONOMY & NORMALIZATION DICTIONARY
# ==========================================
# Canonical Skill Name -> List of aliases and matching keywords
SKILL_TAXONOMY: Dict[str, List[str]] = {
    # Programming Languages
    "Python": ["python", "py", "python3"],
    "Java": ["java", "core java", "j2ee"],
    "C++": ["c++", "cpp"],
    "C": [" c ", "c lang", "c language"],
    "C#": ["c#", "csharp", "c sharp", ".net"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript", "ts"],
    "Go": ["golang", " go "],
    "Rust": ["rust"],
    "PHP": ["php"],
    "Ruby": ["ruby", "rails", "ruby on rails"],
    "Swift": ["swift", "ios"],
    "Kotlin": ["kotlin", "android"],
    "SQL": ["sql", "structured query language", "plsql", "t-sql"],
    "R": [" r ", "r-lang", "r language"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Bash": ["bash", "shell scripting", "powershell", "shell script"],

    # AI, ML & Data Science
    "Machine Learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
    "Deep Learning": ["deep learning", "neural networks", "ann", "cnn", "rnn", "lstm", "transformers"],
    "Natural Language Processing": ["nlp", "natural language processing", "text processing", "llm", "large language models"],
    "Computer Vision": ["computer vision", "cv", "image processing", "opencv"],
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-Learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow", "tf"],
    "PyTorch": ["pytorch", "torch"],
    "Keras": ["keras"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "NLTK": ["nltk", "spacy"],
    "Data Analysis": ["data analysis", "data analytics", "eda", "exploratory data analysis"],
    "Data Visualization": ["data visualization", "power bi", "tableau", "dashboarding"],

    # Web & Backend Frameworks
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "React": ["react", "react.js", "reactjs"],
    "Node.js": ["node", "node.js", "nodejs"],
    "Express.js": ["express", "express.js", "expressjs"],
    "Angular": ["angular", "angularjs"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Spring Boot": ["spring boot", "spring", "springboot"],
    "ASP.NET": ["asp.net", "dotnet core", ".net core"],
    "Next.js": ["next.js", "nextjs"],
    "Tailwind CSS": ["tailwind", "tailwind css", "tailwindcss"],
    "Bootstrap": ["bootstrap"],
    "REST API": ["rest", "rest api", "restful", "web apis", "restful api", "json apis"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "microservice architecture"],

    # Databases & Big Data
    "PostgreSQL": ["postgresql", "postgres", "psql"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo", "nosql"],
    "SQLite": ["sqlite", "sqlite3"],
    "Redis": ["redis", "caching"],
    "Oracle": ["oracle", "oracle db"],
    "Cassandra": ["cassandra"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "Apache Spark": ["spark", "pyspark", "apache spark"],
    "Hadoop": ["hadoop", "hdfs"],
    "Kafka": ["kafka", "apache kafka"],

    # Cloud & DevOps
    "Docker": ["docker", "containerization", "containers"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "Azure": ["azure", "microsoft azure"],
    "Google Cloud": ["gcp", "google cloud", "google cloud platform"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "Git": ["git", "github", "gitlab", "bitbucket", "version control"],
    "Linux": ["linux", "ubuntu", "centos", "unix", "debian"],
    "Terraform": ["terraform"],
    "Jenkins": ["jenkins"],
    "Ansible": ["ansible"],
    "Nginx": ["nginx", "apache server"],

    # Core CS & Software Engineering
    "Data Structures": ["data structures", "dsa", "algorithms", "problem solving"],
    "Object-Oriented Programming": ["oop", "oops", "object oriented programming", "object-oriented"],
    "System Design": ["system design", "software architecture", "scalability", "distributed systems"],
    "Unit Testing": ["unit testing", "pytest", "junit", "tdd", "test driven development"],
    "Agile": ["agile", "scrum", "kanban", "jira"],
    "Web Scraping": ["web scraping", "beautifulsoup", "selenium", "scrapy"]
}

# ==========================================
# 3. EDUCATION LEVELS TAXONOMY
# ==========================================
EDUCATION_LEVELS = {
    "phd": {"rank": 4, "labels": ["ph.d", "phd", "doctorate", "doctor of philosophy"]},
    "masters": {"rank": 3, "labels": ["m.tech", "mtech", "m.s", "ms", "m.sc", "msc", "mca", "master", "masters", "post graduate", "mba"]},
    "bachelors": {"rank": 2, "labels": ["b.tech", "btech", "b.e", "be", "b.sc", "bsc", "bca", "bachelor", "bachelors", "undergraduate", "b.com", "bba"]},
    "diploma": {"rank": 1, "labels": ["diploma", "associate", "higher secondary", "12th"]}
}


# ==========================================
# 4. TEXT PREPROCESSING & TOKENIZATION
# ==========================================

def clean_and_tokenize(text: str) -> List[str]:
    """
    Cleans and tokenizes text:
    - Converts to lowercase
    - Removes punctuation and symbols
    - Removes stopwords and short tokens (< 2 chars)
    """
    if not text:
        return []
    
    # Lowercase
    text = text.lower()
    
    # Replace non-alphanumeric (keeping spaces and hyphens)
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
    
    tokens = text.split()
    
    # Filter stopwords and short tokens
    cleaned = []
    for token in tokens:
        token = token.strip('.').strip()
        if token and token not in STOP_WORDS and len(token) > 1:
            cleaned.append(token)
            
    return cleaned


def extract_skills(text: str) -> List[str]:
    """
    Extracts canonical skills from any text using the predefined SKILL_TAXONOMY.
    Uses regex boundary matching for exact alias hits.
    """
    if not text:
        return []
        
    text_lower = f" {text.lower()} "
    detected_skills = []
    
    for canonical, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Escape regex special chars in alias (e.g., c++, c#)
            pattern = r'(?:\b|(?<=\s))' + re.escape(alias.strip()) + r'(?:\b|(?=\s))'
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected_skills.append(canonical)
                break
                
    return sorted(list(set(detected_skills)))


def extract_experience_years(text: str) -> float:
    """
    Heuristic regex extractor for years of experience.
    Looks for patterns like:
    - "5 years experience", "3+ yrs", "2.5 years of experience", "experience: 4 years"
    """
    if not text:
        return 0.0
        
    text_lower = text.lower()
    
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?',
        r'(?:experience|exp)\s*:\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)?',
        r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?\s*in\s*(?:software|development|industry|engineering|data)',
    ]
    
    extracted_years = []
    for pat in patterns:
        matches = re.findall(pat, text_lower)
        for m in matches:
            try:
                val = float(m)
                if 0.5 <= val <= 40.0:  # Sensible range filter
                    extracted_years.append(val)
            except ValueError:
                continue
                
    if extracted_years:
        # Return maximum detected experience years
        return max(extracted_years)
        
    # Check for date ranges (e.g., 2019 - 2023 -> 4 years)
    year_ranges = re.findall(r'(20\d\d)\s*(?:-|to|–)\s*(20\d\d|present|current)', text_lower)
    total_range_years = 0
    current_year = 2026
    for start_yr, end_yr in year_ranges:
        try:
            sy = int(start_yr)
            ey = current_year if ("present" in end_yr or "current" in end_yr) else int(end_yr)
            diff = max(0, ey - sy)
            total_range_years += diff
        except ValueError:
            pass
            
    return float(total_range_years) if total_range_years > 0 else 0.0


def extract_education_level(text: str) -> Dict[str, Any]:
    """
    Identifies highest degree/education level found in text.
    """
    if not text:
        return {"level": "Not Specified", "rank": 0}
        
    text_lower = text.lower()
    highest_rank = 0
    highest_level = "Not Specified"
    
    for level_key, info in EDUCATION_LEVELS.items():
        for label in info["labels"]:
            pattern = r'\b' + re.escape(label) + r'\b'
            if re.search(pattern, text_lower):
                if info["rank"] > highest_rank:
                    highest_rank = info["rank"]
                    highest_level = level_key.capitalize()
                break
                
    return {"level": highest_level, "rank": highest_rank}


# ==========================================
# 5. PURE PYTHON TF-IDF & COSINE SIMILARITY
# ==========================================

class CustomTFIDFMatcher:
    """
    Pure Python TF-IDF Vectorizer and Cosine Similarity Calculator.
    Calculates semantic text overlap without external heavy dependencies.
    """
    
    @staticmethod
    def compute_tf(tokens: List[str]) -> Dict[str, float]:
        """Term Frequency: Count(t, d) / Total_tokens(d)"""
        if not tokens:
            return {}
        counts = Counter(tokens)
        total = len(tokens)
        return {term: count / total for term, count in counts.items()}

    @classmethod
    def compute_similarity(cls, doc1_text: str, doc2_text: str) -> float:
        """
        Computes Cosine Similarity between two documents (0.0 to 1.0).
        Cosine(A, B) = (A . B) / (||A|| * ||B||)
        """
        tokens1 = clean_and_tokenize(doc1_text)
        tokens2 = clean_and_tokenize(doc2_text)
        
        if not tokens1 or not tokens2:
            return 0.0
            
        tf1 = cls.compute_tf(tokens1)
        tf2 = cls.compute_tf(tokens2)
        
        # Vocabulary of both documents
        vocab = set(tf1.keys()).union(set(tf2.keys()))
        
        # In dual-document comparison:
        # IDF(t) = log(1 + (Total_Docs / (1 + Doc_Freq_t))) + 1
        idf = {}
        for term in vocab:
            df = (1 if term in tf1 else 0) + (1 if term in tf2 else 0)
            idf[term] = math.log((2.0 + 1.0) / (df + 1.0)) + 1.0
            
        # Build TF-IDF vectors
        vec1 = [tf1.get(term, 0.0) * idf[term] for term in vocab]
        vec2 = [tf2.get(term, 0.0) * idf[term] for term in vocab]
        
        # Dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Vector magnitudes
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
            
        similarity = dot_product / (norm1 * norm2)
        return round(min(1.0, max(0.0, similarity)), 4)


# ==========================================
# 6. RESUME MATCHING & SCORING ENGINE
# ==========================================

# Configurable Weights (Sum = 1.0 or 100%)
SCORING_WEIGHTS = {
    "skill": 0.50,       # 50%
    "experience": 0.20,  # 20%
    "education": 0.10,   # 10%
    "text_similarity": 0.20 # 20%
}

def analyze_job_description(jd_text: str) -> Dict[str, Any]:
    """
    Parses Job Description to extract target requirements:
    - Required Skills
    - Expected Experience in years
    - Target Education level
    - Key Terminology
    """
    skills = extract_skills(jd_text)
    exp_years = extract_experience_years(jd_text)
    edu_info = extract_education_level(jd_text)
    tokens = clean_and_tokenize(jd_text)
    
    return {
        "required_skills": skills,
        "required_experience": exp_years,
        "required_education": edu_info["level"],
        "required_edu_rank": edu_info["rank"],
        "keywords": list(set(tokens))
    }


def evaluate_candidate_match(
    resume_data: Dict[str, Any],
    job_reqs: Dict[str, Any],
    raw_jd_text: str
) -> Dict[str, Any]:
    """
    Computes comprehensive match score and component breakdowns:
    1. Skill Match Score (0 - 100)
    2. Experience Match Score (0 - 100)
    3. Education Match Score (0 - 100)
    4. Text Similarity Score (0 - 100)
    5. Overall Weighted Match Score (0 - 100)
    6. Detailed explainability bullet points
    """
    resume_skills = resume_data.get("skills", [])
    raw_resume_text = resume_data.get("raw_text", "")
    
    # 1. Skill Match Calculation
    job_skills_set = set([s.lower() for s in job_reqs.get("required_skills", [])])
    cand_skills_set = set([s.lower() for s in resume_skills])
    
    if job_skills_set:
        matched_set = job_skills_set.intersection(cand_skills_set)
        skill_score = (len(matched_set) / len(job_skills_set)) * 100.0
    else:
        skill_score = 75.0 if cand_skills_set else 50.0
    skill_score = min(100.0, round(skill_score, 1))
    
    # Matched, Missing, and Additional Skill lists
    matched_skills = [s for s in job_reqs.get("required_skills", []) if s.lower() in cand_skills_set]
    missing_skills = [s for s in job_reqs.get("required_skills", []) if s.lower() not in cand_skills_set]
    additional_skills = [s for s in resume_skills if s.lower() not in job_skills_set]
    
    # 2. Experience Match Calculation
    req_exp = job_reqs.get("required_experience", 0.0)
    cand_exp = resume_data.get("experience_years", 0.0)
    
    if req_exp == 0.0:
        exp_score = 100.0 if cand_exp > 0 else 80.0
    else:
        if cand_exp >= req_exp:
            exp_score = 100.0
        else:
            exp_score = (cand_exp / req_exp) * 100.0
    exp_score = min(100.0, round(exp_score, 1))
    
    # 3. Education Match Calculation
    req_edu_rank = job_reqs.get("required_edu_rank", 0)
    cand_edu_info = extract_education_level(resume_data.get("education", "") + " " + raw_resume_text)
    cand_edu_rank = cand_edu_info["rank"]
    
    if req_edu_rank == 0:
        edu_score = 100.0 if cand_edu_rank > 0 else 80.0
    else:
        if cand_edu_rank >= req_edu_rank:
            edu_score = 100.0
        elif cand_edu_rank > 0:
            edu_score = 65.0
        else:
            edu_score = 40.0
    edu_score = min(100.0, round(edu_score, 1))
    
    # 4. Text & Keyword Cosine Similarity
    tfidf_sim = CustomTFIDFMatcher.compute_similarity(raw_jd_text, raw_resume_text)
    tfidf_score = min(100.0, round(tfidf_sim * 100.0 * 1.35, 1)) # Scaled for rich document overlap
    
    # 5. Final Overall Weighted Score
    final_score = (
        (SCORING_WEIGHTS["skill"] * skill_score) +
        (SCORING_WEIGHTS["experience"] * exp_score) +
        (SCORING_WEIGHTS["education"] * edu_score) +
        (SCORING_WEIGHTS["text_similarity"] * tfidf_score)
    )
    final_score = min(100.0, max(0.0, round(final_score, 1)))
    
    # Visual Badge Category
    if final_score >= 85.0:
        badge = "Excellent Match"
        badge_class = "badge-excellent"
    elif final_score >= 70.0:
        badge = "Strong Match"
        badge_class = "badge-strong"
    elif final_score >= 55.0:
        badge = "Moderate Match"
        badge_class = "badge-moderate"
    else:
        badge = "Low Match"
        badge_class = "badge-low"
        
    # 6. Explainability Insights
    explanations = []
    
    # Skill insights
    if matched_skills:
        explanations.append(f"Strong match for {len(matched_skills)} core skill(s): {', '.join(matched_skills[:4])}.")
    if missing_skills:
        explanations.append(f"Missing {len(missing_skills)} required skill(s): {', '.join(missing_skills[:3])}.")
    if additional_skills:
        explanations.append(f"Candidate brings {len(additional_skills)} bonus skill(s): {', '.join(additional_skills[:3])}.")
        
    # Experience insights
    if req_exp > 0:
        if cand_exp >= req_exp:
            explanations.append(f"Satisfies experience criteria ({cand_exp:g} yrs detected vs {req_exp:g} yrs required).")
        else:
            explanations.append(f"Has {cand_exp:g} yrs experience (Job asks for {req_exp:g} yrs).")
    elif cand_exp > 0:
        explanations.append(f"Demonstrates {cand_exp:g} years of relevant industry experience.")
        
    # Education insights
    if cand_edu_info["level"] != "Not Specified":
        explanations.append(f"Holds {cand_edu_info['level']} degree qualification.")
    else:
        explanations.append("Formal degree details not explicitly highlighted in resume.")
        
    return {
        "final_score": final_score,
        "skill_score": skill_score,
        "exp_score": exp_score,
        "edu_score": edu_score,
        "tfidf_score": tfidf_score,
        "badge": badge,
        "badge_class": badge_class,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills,
        "explanations": explanations,
        "detected_education": cand_edu_info["level"]
    }

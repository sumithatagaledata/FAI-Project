"""
Automated Verification and Unit Test Suite for AI Resume Screening System.
"""

import os
import unittest
import json
from algorithms import merge_sort, quick_sort, CandidateMaxHeap, binary_search_by_name, analyze_skill_gap, SkillInvertedIndex
from nlp_processor import extract_skills, extract_experience_years, CustomTFIDFMatcher, evaluate_candidate_match, analyze_job_description
from sample_generator import generate_all_sample_resumes, SAMPLE_JOB_DESCRIPTION, SAMPLES_DIR
from resume_parser import ResumeParser
import database
from app import app


class TestResumeScreeningSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        database.init_db()
        generate_all_sample_resumes()

    def test_01_algorithms_sorting(self):
        data = [{"name": "C", "match_score": 50}, {"name": "A", "match_score": 90}, {"name": "B", "match_score": 75}]
        sorted_desc = merge_sort(data, key=lambda x: x["match_score"], reverse=True)
        self.assertEqual(sorted_desc[0]["name"], "A")
        self.assertEqual(sorted_desc[1]["name"], "B")
        self.assertEqual(sorted_desc[2]["name"], "C")

        sorted_asc = quick_sort(data, key=lambda x: x["match_score"], reverse=False)
        self.assertEqual(sorted_asc[0]["name"], "C")
        self.assertEqual(sorted_asc[2]["name"], "A")

    def test_02_max_heap(self):
        heap = CandidateMaxHeap(key=lambda x: x["score"])
        heap.push({"name": "Low", "score": 40})
        heap.push({"name": "High", "score": 95})
        heap.push({"name": "Mid", "score": 70})

        top = heap.peek()
        self.assertEqual(top["name"], "High")
        self.assertEqual(top["score"], 95)

        extracted = heap.pop()
        self.assertEqual(extracted["name"], "High")
        self.assertEqual(heap.peek()["name"], "Mid")

    def test_03_inverted_index_and_set_gap(self):
        idx = SkillInvertedIndex()
        idx.add_candidate(1, ["Python", "SQL", "Flask"])
        idx.add_candidate(2, ["JavaScript", "React", "Python"])

        python_cands = idx.search_by_skill("python")
        self.assertIn(1, python_cands)
        self.assertIn(2, python_cands)

        gap = analyze_skill_gap(["Python", "SQL", "Docker"], ["Python", "Django"])
        self.assertIn("Python", gap["matched"])
        self.assertIn("SQL", gap["missing"])
        self.assertIn("Docker", gap["missing"])
        self.assertIn("Django", gap["additional"])

    def test_04_nlp_processor(self):
        text = "We require 4+ years experience in Python, PostgreSQL, Machine Learning, Docker."
        skills = extract_skills(text)
        self.assertIn("Python", skills)
        self.assertIn("PostgreSQL", skills)
        self.assertIn("Machine Learning", skills)
        self.assertIn("Docker", skills)

        exp = extract_experience_years(text)
        self.assertEqual(exp, 4.0)

        # TF-IDF similarity
        doc1 = "Python developer with machine learning experience in Flask and SQL."
        doc2 = "Senior Python engineer building machine learning models and SQL databases."
        sim = CustomTFIDFMatcher.compute_similarity(doc1, doc2)
        self.assertGreater(sim, 0.25)

    def test_05_resume_parser_and_pdf_extraction(self):
        pdf_path = os.path.join(SAMPLES_DIR, "Aarav_Sharma_Senior_Python_AI.pdf")
        self.assertTrue(os.path.exists(pdf_path))
        
        parsed = ResumeParser.parse_resume(pdf_path, filename="Aarav_Sharma_Senior_Python_AI.pdf")
        self.assertEqual(parsed["name"], "Aarav Sharma")
        self.assertIn("aarav.sharma@example.com", parsed["email"])
        self.assertIn("Python", parsed["skills"])
        self.assertIn("Machine Learning", parsed["skills"])
        self.assertGreaterEqual(parsed["experience_years"], 3.0)

    def test_06_database_crud(self):
        job_id = database.save_job("Test Role", "Python Developer required", ["Python"], 2.0)
        self.assertIsInstance(job_id, int)
        
        job = database.get_job(job_id)
        self.assertEqual(job["job_title"], "Test Role")

        cand_parsed = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "+91 99999 88888",
            "education": "B.Tech",
            "experience_years": 3.0,
            "skills": ["Python", "SQL"],
            "raw_text": "Sample text",
            "projects": "Test Project",
            "certifications": "Cert 1",
            "resume_filename": "test.pdf"
        }
        match_res = {
            "final_score": 88.0,
            "skill_score": 90.0,
            "exp_score": 100.0,
            "edu_score": 100.0,
            "tfidf_score": 75.0,
            "badge": "Strong Match",
            "badge_class": "badge-strong",
            "matched_skills": ["Python"],
            "missing_skills": [],
            "additional_skills": ["SQL"],
            "explanations": ["Strong match"]
        }
        cand_id = database.save_candidate(job_id, cand_parsed, match_res)
        self.assertIsInstance(cand_id, int)

        cand = database.get_candidate_by_id(cand_id)
        self.assertEqual(cand["name"], "Test Candidate")
        self.assertEqual(cand["match_score"], 88.0)

        # Cleanup
        database.delete_job(job_id)
        self.assertIsNone(database.get_job(job_id))

    def test_07_flask_routes(self):
        client = app.test_client()

        # 1. Landing Page
        res = client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AI Based', res.data)

        # 2. Dashboard
        res = client.get('/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Recruiter Screening Dashboard', res.data)

        # 3. 1-Click Demo API
        res = client.post('/api/load-sample')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("/results/", data["redirect_url"])

        # 4. Results Page
        res = client.get(data["redirect_url"])
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Aarav Sharma', res.data)
        self.assertIn(b'Priya Patel', res.data)

        # 5. Candidate Detail Page
        cands = database.get_all_jobs()
        self.assertGreater(len(cands), 0)
        job_id = cands[0]["id"]
        job_cands = database.get_candidates_for_job(job_id)
        self.assertGreater(len(job_cands), 0)
        first_cand_id = job_cands[0]["id"]

        cand_res = client.get(f'/candidate/{first_cand_id}')
        self.assertEqual(cand_res.status_code, 200)
        self.assertIn(b'Why This Candidate Matched', cand_res.data)
        self.assertIn(b'Skills Gap Analysis', cand_res.data)

        # 6. Binary Search on Candidates
        sorted_by_name = merge_sort(job_cands, key=lambda x: x["name"].lower(), reverse=False)
        target = sorted_by_name[0]["name"]
        found = binary_search_by_name(sorted_by_name, target)
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], target)

        # 7. History Page
        res = client.get('/history')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Screening History', res.data)


if __name__ == '__main__':
    unittest.main()

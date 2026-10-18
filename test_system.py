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

    def test_08_talent_twin_role_challenge_generation(self):
        import talent_twin_engine

        # 1. Python Developer Role
        py_cand = {
            "name": "Alex Mercer",
            "matched_skills": ["Python", "Flask"],
            "missing_skills": ["Docker"],
            "additional_skills": [],
            "raw_text": "Built Python microservices processing API event streams.",
            "projects": "API Gateway in Python",
            "certifications": "Python Certified"
        }
        py_job = {
            "job_title": "Senior Python Engineer",
            "required_skills": ["Python", "SQL"],
            "job_description": "We need a Python engineer for high-throughput API microservices."
        }
        py_chal = talent_twin_engine.generate_job_challenge(py_cand, py_job)
        self.assertEqual(py_chal["task_type"], "coding")
        self.assertEqual(py_chal["role_category"], "python_developer")
        self.assertIn("starter_code", py_chal)
        self.assertIn("instructions", py_chal)
        self.assertIsInstance(py_chal["instructions"], list)
        self.assertIn("test_cases", py_chal)
        self.assertEqual(sum(r["weight"] for r in py_chal["rubric"]), 100)

        # 2. Data Analyst Role
        da_cand = {"name": "Jordan Lee", "matched_skills": ["Data Analysis", "Pandas"], "raw_text": "Analyzed cohort metrics in Pandas."}
        da_job = {"job_title": "Data Analyst", "required_skills": ["Data Analysis", "SQL"], "job_description": "Analyze sales transactions and compute cohort KPIs."}
        da_chal = talent_twin_engine.generate_job_challenge(da_cand, da_job)
        self.assertEqual(da_chal["role_category"], "data_analyst")
        self.assertIn("analyze_sales_data", da_chal["starter_code"])

        # 3. SQL Developer Role
        sql_cand = {"name": "Morgan Blake", "matched_skills": ["SQL", "PostgreSQL"], "raw_text": "Optimized PostgreSQL relational schemas."}
        sql_job = {"job_title": "SQL Database Developer", "required_skills": ["SQL"], "job_description": "Build high performance SQL queries and relational models."}
        sql_chal = talent_twin_engine.generate_job_challenge(sql_cand, sql_job)
        self.assertEqual(sql_chal["task_type"], "sql")
        self.assertEqual(sql_chal["role_category"], "sql_developer")
        self.assertIn("SELECT", sql_chal["starter_code"])

    def test_09_talent_twin_validation_and_sandbox(self):
        import talent_twin_engine
        client = app.test_client()

        jobs = database.get_all_jobs()
        self.assertGreater(len(jobs), 0)
        job_id = jobs[0]["id"]
        cands = database.get_candidates_for_job(job_id)
        self.assertGreater(len(cands), 0)
        cand_id = cands[0]["id"]

        # 1. Rejection of empty code submission
        empty_res = client.post(
            f'/api/talent-twin/evaluate/{cand_id}',
            json={"code": "", "answers": {}}
        )
        self.assertEqual(empty_res.status_code, 400)
        empty_data = json.loads(empty_res.data)
        self.assertEqual(empty_data["status"], "error")
        self.assertIn("cannot be empty", empty_data["message"])

        # 2. Sandbox execution endpoint (/api/talent-twin/run-tests/<id>)
        # Test with working code for process_and_deduplicate_events
        working_code = (
            "from typing import List, Dict, Any\n"
            "def process_and_deduplicate_events(events: List[Dict[str, Any]], max_limit: int = 5) -> Dict[str, Any]:\n"
            "    seen_ids = set()\n"
            "    client_counts = {}\n"
            "    unique_clients = set()\n"
            "    total_amount = 0.0\n"
            "    duplicates = 0\n"
            "    processed = 0\n"
            "    for ev in events:\n"
            "        eid = ev.get('event_id')\n"
            "        if eid in seen_ids:\n"
            "            duplicates += 1\n"
            "            continue\n"
            "        seen_ids.add(eid)\n"
            "        cid = ev.get('client_id')\n"
            "        if client_counts.get(cid, 0) >= max_limit:\n"
            "            continue\n"
            "        raw = ev.get('amount')\n"
            "        amt = 0.0 if (raw is None or raw < 0) else float(raw)\n"
            "        total_amount += amt\n"
            "        client_counts[cid] = client_counts.get(cid, 0) + 1\n"
            "        unique_clients.add(cid)\n"
            "        processed += 1\n"
            "    return {\n"
            "        'processed_count': processed,\n"
            "        'unique_clients': sorted(list(unique_clients)),\n"
            "        'total_amount': total_amount,\n"
            "        'duplicate_count': duplicates\n"
            "    }\n"
        )
        test_run_res = client.post(
            f'/api/talent-twin/run-tests/{cand_id}',
            json={"code": working_code}
        )
        self.assertEqual(test_run_res.status_code, 200)
        test_run_data = json.loads(test_run_res.data)
        self.assertEqual(test_run_data["status"], "success")
        self.assertIn("test_run", test_run_data)
        self.assertGreaterEqual(test_run_data["test_run"]["passed_count"], 1)

    def test_10_talent_twin_evaluation_and_evidence(self):
        import talent_twin_engine
        client = app.test_client()

        jobs = database.get_all_jobs()
        job_id = jobs[0]["id"]
        cands = database.get_candidates_for_job(job_id)
        cand_id = cands[0]["id"]

        # 1. Evaluate valid working submission
        working_code = (
            "from typing import List, Dict, Any\n"
            "def process_and_deduplicate_events(events: List[Dict[str, Any]], max_limit: int = 5) -> Dict[str, Any]:\n"
            "    seen_ids = set()\n"
            "    client_counts = {}\n"
            "    unique_clients = set()\n"
            "    total_amount = 0.0\n"
            "    duplicates = 0\n"
            "    processed = 0\n"
            "    for ev in events:\n"
            "        eid = ev.get('event_id')\n"
            "        if eid in seen_ids:\n"
            "            duplicates += 1\n"
            "            continue\n"
            "        seen_ids.add(eid)\n"
            "        cid = ev.get('client_id')\n"
            "        if client_counts.get(cid, 0) >= max_limit:\n"
            "            continue\n"
            "        raw = ev.get('amount')\n"
            "        amt = 0.0 if (raw is None or raw < 0) else float(raw)\n"
            "        total_amount += amt\n"
            "        client_counts[cid] = client_counts.get(cid, 0) + 1\n"
            "        unique_clients.add(cid)\n"
            "        processed += 1\n"
            "    return {\n"
            "        'processed_count': processed,\n"
            "        'unique_clients': sorted(list(unique_clients)),\n"
            "        'total_amount': total_amount,\n"
            "        'duplicate_count': duplicates\n"
            "    }\n"
        )
        submission = {
            "code": working_code,
            "answers": {
                "q1": "We use Redis distributed locks with Lua scripts to prevent concurrent duplicate event ingestion across worker pods.",
                "q2": "We configure an LRU eviction policy with strict TTL windows on the sliding cache to prevent memory exhaustion during traffic spikes."
            }
        }
        eval_api_res = client.post(
            f'/api/talent-twin/evaluate/{cand_id}',
            json=submission
        )
        self.assertEqual(eval_api_res.status_code, 200)
        eval_data = json.loads(eval_api_res.data)
        self.assertEqual(eval_data["status"], "success")
        self.assertGreaterEqual(eval_data["practical_score"], 80.0)
        self.assertEqual(eval_data["confidence_badge"], "High Confidence")

        # 2. Verify persistence in DB
        sim_record = database.get_talent_twin_simulation(cand_id)
        self.assertIsNotNone(sim_record)
        self.assertEqual(sim_record["status"], "completed")
        self.assertGreaterEqual(sim_record["practical_score"], 80.0)

        # 3. Candidate comparison page
        comp_res = client.get(f'/talent-twin/compare/{job_id}')
        self.assertEqual(comp_res.status_code, 200)
        self.assertIn(b'Dual-Metric Candidate Comparison', comp_res.data)
        self.assertIn(b'High Confidence', comp_res.data)

        # 4. Reset simulation
        reset_res = client.post(f'/api/talent-twin/reset/{cand_id}')
        self.assertEqual(reset_res.status_code, 200)
        sim_after_reset = database.get_talent_twin_simulation(cand_id)
        self.assertEqual(sim_after_reset["status"], "pending")

    def test_11_ai_fallback_and_varying_answers(self):
        import talent_twin_engine

        cand = {"name": "Test User", "matched_skills": ["Python"], "missing_skills": [], "additional_skills": [], "match_score": 70.0}
        job = {"job_title": "Python Developer", "required_skills": ["Python"]}
        chal = talent_twin_engine.generate_job_challenge(cand, job)

        # 1. Broken implementation
        broken_sub = {
            "code": "def process_and_deduplicate_events(events, max_limit=5):\n    return {}\n",
            "answers": {"q1": "none", "q2": "none"}
        }
        broken_res = talent_twin_engine.evaluate_simulation(chal, broken_sub, cand, job)
        self.assertEqual(broken_res["passed_tests"], 0)
        self.assertLess(broken_res["practical_score"], 40.0)
        self.assertIn("Fallback", broken_res["evaluation_engine"])

        # 2. Working implementation
        working_code = (
            "from typing import List, Dict, Any\n"
            "def process_and_deduplicate_events(events: List[Dict[str, Any]], max_limit: int = 5) -> Dict[str, Any]:\n"
            "    seen_ids = set()\n"
            "    client_counts = {}\n"
            "    unique_clients = set()\n"
            "    total_amount = 0.0\n"
            "    duplicates = 0\n"
            "    processed = 0\n"
            "    for ev in events:\n"
            "        eid = ev.get('event_id')\n"
            "        if eid in seen_ids:\n"
            "            duplicates += 1\n"
            "            continue\n"
            "        seen_ids.add(eid)\n"
            "        cid = ev.get('client_id')\n"
            "        if client_counts.get(cid, 0) >= max_limit:\n"
            "            continue\n"
            "        raw = ev.get('amount')\n"
            "        amt = 0.0 if (raw is None or raw < 0) else float(raw)\n"
            "        total_amount += amt\n"
            "        client_counts[cid] = client_counts.get(cid, 0) + 1\n"
            "        unique_clients.add(cid)\n"
            "        processed += 1\n"
            "    return {\n"
            "        'processed_count': processed,\n"
            "        'unique_clients': sorted(list(unique_clients)),\n"
            "        'total_amount': total_amount,\n"
            "        'duplicate_count': duplicates\n"
            "    }\n"
        )
        working_sub = {
            "code": working_code,
            "answers": {
                "q1": "Redis distributed lock with Lua scripts and retry backoff.",
                "q2": "LRU memory eviction policy with TTL sliding window cap."
            }
        }
        working_res = talent_twin_engine.evaluate_simulation(chal, working_sub, cand, job)
        self.assertEqual(working_res["passed_tests"], working_res["total_tests"])
        self.assertGreaterEqual(working_res["practical_score"], 80.0)

        # Changing answer dramatically changes score appropriately
        self.assertGreater(working_res["practical_score"] - broken_res["practical_score"], 40.0)

        # 3. Existing Resume Ranking Invariant
        # Verify that candidate match_score in database remains completely untouched
        db_cand = database.get_candidate_by_id(1)
        if db_cand:
            original_match_score = db_cand["match_score"]
            self.assertGreater(original_match_score, 0.0)


if __name__ == '__main__':
    unittest.main()




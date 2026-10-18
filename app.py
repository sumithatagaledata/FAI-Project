"""
Flask Application for AI-Based Resume Screening System.

Routes:
- GET  /                     : Landing page
- GET  /dashboard            : Recruiter screening setup dashboard
- POST /screen               : Process uploaded PDF resumes and run AI screening
- GET  /results/<job_id>     : Ranked candidates dashboard with filter/search
- GET  /candidate/<id>       : In-depth candidate profile with match explainability
- GET  /history              : Previous screening sessions
- POST /api/load-sample      : 1-Click sample data generator & automated screener
- POST /api/clear-data       : Database & uploads reset
- POST /api/delete-candidate/<id> : Delete individual candidate
- POST /api/delete-job/<id>  : Delete job screening session
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename

import database
from resume_parser import ResumeParser
from nlp_processor import analyze_job_description, evaluate_candidate_match
from algorithms import (
    merge_sort, quick_sort, CandidateMaxHeap,
    binary_search_by_name, linear_search_candidates, SkillInvertedIndex
)
from sample_generator import (
    generate_all_sample_resumes, SAMPLE_JOB_TITLE,
    SAMPLE_JOB_DESCRIPTION, SAMPLES_DIR
)
import talent_twin_engine

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Initialize Flask app
app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATES_DIR)
app.secret_key = "fai-resume-screener-secret-key-2026"

# Configuration
if os.environ.get("VERCEL"):
    UPLOAD_FOLDER = "/tmp/uploads"
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")


ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB max upload size

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize SQLite database schema
database.init_db()


@app.template_filter('format_exp')
def format_exp_filter(val):
    """Formats float experience numbers cleanly (e.g. 3.0 -> '3', 3.5 -> '3.5')."""
    if val is None:
        return "0"
    try:
        f = float(val)
        return str(int(f)) if f.is_integer() else str(round(f, 1))
    except (ValueError, TypeError):
        return str(val)


def allowed_file(filename: str) -> bool:
    """Checks if uploaded file has valid .pdf extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/static/<path:filename>')
def serve_static(filename: str):
    """Fallback static asset handler for serverless environments."""
    return send_from_directory(STATIC_DIR, filename)


@app.route('/')
def index():
    """Landing page and recruiter portal for Talentora AI."""
    summary = database.get_dashboard_summary()
    return render_template(
        'index.html',
        summary=summary,
        sample_title=SAMPLE_JOB_TITLE,
        sample_jd=SAMPLE_JOB_DESCRIPTION
    )


@app.route('/dashboard')
def dashboard():
    """Recruiter dashboard / screener interface."""
    summary = database.get_dashboard_summary()
    return render_template(
        'dashboard.html',
        summary=summary,
        sample_title=SAMPLE_JOB_TITLE,
        sample_jd=SAMPLE_JOB_DESCRIPTION
    )



@app.route('/screen', methods=['POST'])
def screen_resumes():
    """
    Main Screening Route:
    1. Validates Job Title, Description, and PDF Files
    2. Parses each PDF using ResumeParser
    3. Analyzes Job Requirements using NLP Engine
    4. Computes Match Scores & Explainability
    5. Applies Custom DSA: Merge Sort & Max-Heap for Candidate Ranking
    6. Persists data to SQLite Database
    7. Redirects to Results Dashboard
    """
    job_title = request.form.get('job_title', '').strip() or "Untitled Position"
    job_description = request.form.get('job_description', '').strip()

    if not job_description or len(job_description) < 20:
        flash("Please provide a detailed Job Description (at least 20 characters) to screen candidates against.", "error")
        return redirect(url_for('dashboard'))

    uploaded_files = request.files.getlist('resumes')
    if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ''):
        flash("Please upload at least one valid PDF resume.", "error")
        return redirect(url_for('dashboard'))

    # Step 1: Analyze Job Description with NLP Engine
    job_reqs = analyze_job_description(job_description)
    job_id = database.save_job(
        job_title=job_title,
        job_description=job_description,
        required_skills=job_reqs["required_skills"],
        required_experience=job_reqs["required_experience"]
    )

    parsed_candidates_list = []
    inverted_index = SkillInvertedIndex()
    seen_filenames = set()

    # Step 2: Process each uploaded PDF
    for file in uploaded_files:
        if file and file.filename and allowed_file(file.filename):
            safe_fname = secure_filename(file.filename)
            
            # Handle duplicates
            if safe_fname in seen_filenames:
                safe_fname = f"{len(seen_filenames)+1}_{safe_fname}"
            seen_filenames.add(safe_fname)

            save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_fname)
            file.save(save_path)

            try:
                # Extract text & entities
                parsed_cand = ResumeParser.parse_resume(save_path, filename=safe_fname)
                
                # NLP matching and score breakdown
                match_results = evaluate_candidate_match(parsed_cand, job_reqs, job_description)
                
                # Save into SQLite Database
                cand_id = database.save_candidate(job_id, parsed_cand, match_results)
                parsed_cand["id"] = cand_id
                parsed_cand["match_score"] = match_results["final_score"]
                parsed_cand["badge"] = match_results["badge"]
                parsed_cand["badge_class"] = match_results["badge_class"]
                parsed_cand["matched_skills"] = match_results["matched_skills"]
                parsed_cand["missing_skills"] = match_results["missing_skills"]
                parsed_cand["additional_skills"] = match_results["additional_skills"]
                
                parsed_candidates_list.append(parsed_cand)

                # Index candidate skills into DSA Inverted Index
                inverted_index.add_candidate(cand_id, parsed_cand.get("skills", []))

            except Exception as e:
                print(f"Error processing {safe_fname}: {e}")
                continue

    if not parsed_candidates_list:
        flash("Failed to extract valid text from the uploaded PDF resumes. Please ensure they contain readable text.", "error")
        return redirect(url_for('dashboard'))

    # Step 3: DSA Candidate Ranking using Custom Merge Sort
    sorted_candidates = merge_sort(parsed_candidates_list, key=lambda c: c["match_score"], reverse=True)

    # Step 4: DSA Max-Heap verification for Top Candidate
    max_heap = CandidateMaxHeap(key=lambda c: c["match_score"])
    for cand in parsed_candidates_list:
        max_heap.push(cand)
    top_cand = max_heap.peek()

    # Step 5: Save Screening Summary Session
    avg_score = round(sum(c["match_score"] for c in parsed_candidates_list) / len(parsed_candidates_list), 1)
    top_score = top_cand["match_score"] if top_cand else 0.0
    database.save_session(job_id, len(parsed_candidates_list), avg_score, top_score)

    flash(f"Screening complete! {len(parsed_candidates_list)} resumes evaluated and ranked.", "success")
    return redirect(url_for('view_results', job_id=job_id))


@app.route('/results/<int:job_id>')
def view_results(job_id: int):
    """
    Results Page:
    - Summary KPI cards (Total, Avg Score, Top Score, Top Candidate)
    - Ranked candidate table with visual score meters
    - Live Search & Filtering tools
    """
    job = database.get_job(job_id)
    if not job:
        flash("Screening session not found.", "error")
        return redirect(url_for('dashboard'))

    candidates = database.get_job_talent_twin_comparison(job_id)

    # DSA Merge Sort to ensure strict ranking
    ranked_candidates = merge_sort(candidates, key=lambda c: c["match_score"], reverse=True)

    # Assign sequential ranks
    for idx, cand in enumerate(ranked_candidates):
        cand["rank"] = idx + 1

    # KPI stats
    total_count = len(ranked_candidates)
    avg_score = round(sum(c["match_score"] for c in ranked_candidates) / total_count, 1) if total_count > 0 else 0.0
    top_candidate = ranked_candidates[0] if ranked_candidates else None

    # Collect all unique detected skills for interactive filter pills
    all_skills_set = set()
    for c in ranked_candidates:
        all_skills_set.update(c.get("skills", []))
    available_skills = sorted(list(all_skills_set))

    return render_template(
        'results.html',
        job=job,
        candidates=ranked_candidates,
        total_count=total_count,
        avg_score=avg_score,
        top_candidate=top_candidate,
        available_skills=available_skills
    )


@app.route('/candidate/<int:candidate_id>')
def candidate_detail(candidate_id: int):
    """
    Detailed Candidate View:
    - Full extracted resume details
    - 4-factor scoring breakdown (Skills 50%, Experience 20%, Education 10%, Text Similarity 20%)
    - Explainability Card ("Why this candidate matched")
    - Skill gap chips (Matched, Missing, Bonus)
    - Talent Twin Evidence & Simulation status
    """
    cand = database.get_candidate_by_id(candidate_id)
    if not cand:
        flash("Candidate record not found.", "error")
        return redirect(url_for('dashboard'))

    job = database.get_job(cand["job_id"])
    
    # Calculate candidate rank relative to the job's candidates
    all_job_cands = database.get_candidates_for_job(cand["job_id"])
    sorted_cands = merge_sort(all_job_cands, key=lambda c: c["match_score"], reverse=True)
    rank = 1
    for idx, c in enumerate(sorted_cands):
        if c["id"] == candidate_id:
            rank = idx + 1
            break

    cand["rank"] = rank
    cand["total_pool"] = len(sorted_cands)

    # Talent Twin simulation status and evidence analysis
    sim = database.get_talent_twin_simulation(candidate_id)
    evidence = talent_twin_engine.analyze_skill_evidence(cand, job)

    return render_template('candidate.html', candidate=cand, job=job, simulation=sim, evidence=evidence)


@app.route('/talent-twin/<int:candidate_id>')
def talent_twin_view(candidate_id: int):
    """
    Talent Twin — AI Job Simulation & Evidence Intelligence View:
    - Generates or retrieves role-specific interactive job challenge
    - Supports Coding, Data Analysis, and Situational Problem Solving
    - Displays interactive challenge runner & animated intelligence dashboard
    """
    cand = database.get_candidate_by_id(candidate_id)
    if not cand:
        flash("Candidate record not found.", "error")
        return redirect(url_for('dashboard'))

    job = database.get_job(cand["job_id"])
    if not job:
        flash("Screening session not found.", "error")
        return redirect(url_for('dashboard'))

    # Retrieve existing simulation or generate new challenge
    sim = database.get_talent_twin_simulation(candidate_id)
    if not sim or not sim.get("challenge"):
        challenge = talent_twin_engine.generate_job_challenge(cand, job)
        database.save_talent_twin_challenge(candidate_id, cand["job_id"], challenge)
        sim = database.get_talent_twin_simulation(candidate_id)

    # Calculate rank
    all_job_cands = database.get_candidates_for_job(cand["job_id"])
    sorted_cands = merge_sort(all_job_cands, key=lambda c: c["match_score"], reverse=True)
    rank = 1
    for idx, c in enumerate(sorted_cands):
        if c["id"] == candidate_id:
            rank = idx + 1
            break
    cand["rank"] = rank
    cand["total_pool"] = len(sorted_cands)

    evidence = talent_twin_engine.analyze_skill_evidence(cand, job)

    return render_template(
        'talent_twin.html',
        candidate=cand,
        job=job,
        simulation=sim,
        challenge=sim.get("challenge", {}),
        results=sim.get("results", {}),
        evidence=evidence
    )


@app.route('/talent-twin/compare/<int:job_id>')
def talent_twin_compare(job_id: int):
    """
    Recruiter Dual-Metric Comparison Board:
    Compares candidate resume match scores side-by-side with practical Talent Twin simulation performance.
    """
    job = database.get_job(job_id)
    if not job:
        flash("Job screening session not found.", "error")
        return redirect(url_for('history'))

    candidates = database.get_job_talent_twin_comparison(job_id)
    total_candidates = len(candidates)
    completed_sims = [c for c in candidates if c.get("sim_completed")]
    avg_practical = round(sum(c["practical_score"] for c in completed_sims) / len(completed_sims), 1) if completed_sims else 0.0

    return render_template(
        'talent_twin_compare.html',
        job=job,
        candidates=candidates,
        total_candidates=total_candidates,
        completed_count=len(completed_sims),
        avg_practical=avg_practical
    )


@app.route('/api/talent-twin/evaluate/<int:candidate_id>', methods=['POST'])
def api_evaluate_talent_twin(candidate_id: int):
    """
    Evaluates candidate job simulation submission:
    Runs practical rubrics, computes verified skill scores, confidence indicator, and interview questions.
    """
    cand = database.get_candidate_by_id(candidate_id)
    if not cand:
        return jsonify({"status": "error", "message": "Candidate not found"}), 404

    job = database.get_job(cand["job_id"])
    sim = database.get_talent_twin_simulation(candidate_id)
    if not sim or not sim.get("challenge"):
        challenge = talent_twin_engine.generate_job_challenge(cand, job)
        database.save_talent_twin_challenge(candidate_id, cand["job_id"], challenge)
        sim = database.get_talent_twin_simulation(candidate_id)

    payload = request.get_json() or {}
    code_submission = payload.get("code", "")
    answers = payload.get("answers", {})

    submission_data = {
        "code": code_submission,
        "answers": answers
    }

    # Execute functional evaluation
    results = talent_twin_engine.evaluate_simulation(
        challenge=sim.get("challenge", {}),
        submission_data=submission_data,
        candidate=cand,
        job=job
    )

    # Persist evaluation in database
    database.save_talent_twin_evaluation(
        candidate_id=candidate_id,
        submission_data=submission_data,
        results_data=results,
        practical_score=results["practical_score"],
        confidence_score=results["confidence_score"],
        confidence_badge=results["confidence_badge"]
    )

    return jsonify({
        "status": "success",
        "message": "Talent Twin simulation evaluated successfully!",
        "results": results,
        "practical_score": results["practical_score"],
        "confidence_badge": results["confidence_badge"],
        "confidence_score": results["confidence_score"]
    })


@app.route('/api/talent-twin/reset/<int:candidate_id>', methods=['POST'])
def api_reset_talent_twin(candidate_id: int):
    """Resets candidate simulation to initial unsubmitted state."""
    database.reset_talent_twin_simulation(candidate_id)
    return jsonify({
        "status": "success",
        "message": "Candidate Talent Twin simulation reset."
    })



@app.route('/history')
def history():
    """View all previous job screening sessions."""
    jobs = database.get_all_jobs()
    return render_template('history.html', jobs=jobs)


@app.route('/api/load-sample', methods=['POST'])
def load_sample_demo():
    """
    1-Click Demo API:
    Generates 5 realistic PDF resumes and screens them against sample Job Description.
    """
    try:
        # Generate sample PDFs
        generate_all_sample_resumes()

        # Create Job in DB
        job_reqs = analyze_job_description(SAMPLE_JOB_DESCRIPTION)
        job_id = database.save_job(
            job_title=SAMPLE_JOB_TITLE,
            job_description=SAMPLE_JOB_DESCRIPTION,
            required_skills=job_reqs["required_skills"],
            required_experience=job_reqs["required_experience"]
        )

        sample_files = os.listdir(SAMPLES_DIR)
        parsed_cands = []

        for fname in sample_files:
            if fname.endswith('.pdf'):
                fpath = os.path.join(SAMPLES_DIR, fname)
                parsed = ResumeParser.parse_resume(fpath, filename=fname)
                match_res = evaluate_candidate_match(parsed, job_reqs, SAMPLE_JOB_DESCRIPTION)
                cand_id = database.save_candidate(job_id, parsed, match_res)
                parsed["id"] = cand_id
                parsed["match_score"] = match_res["final_score"]
                parsed_cands.append(parsed)

        # Apply custom Merge Sort for ranking
        sorted_cands = merge_sort(parsed_cands, key=lambda c: c["match_score"], reverse=True)
        avg_score = round(sum(c["match_score"] for c in sorted_cands) / len(sorted_cands), 1)
        top_score = sorted_cands[0]["match_score"] if sorted_cands else 0.0

        database.save_session(job_id, len(sorted_cands), avg_score, top_score)

        return jsonify({
            "status": "success",
            "message": "Sample demonstration data loaded successfully!",
            "redirect_url": url_for('view_results', job_id=job_id)
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/delete-candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate_api(candidate_id: int):
    """Deletes a candidate record."""
    cand = database.get_candidate_by_id(candidate_id)
    if cand:
        job_id = cand["job_id"]
        database.delete_candidate(candidate_id)
        return jsonify({"status": "success", "redirect_url": url_for('view_results', job_id=job_id)})
    return jsonify({"status": "error", "message": "Candidate not found"}), 404


@app.route('/api/delete-job/<int:job_id>', methods=['POST'])
def delete_job_api(job_id: int):
    """Deletes a job screening session."""
    database.delete_job(job_id)
    return jsonify({"status": "success", "redirect_url": url_for('history')})


@app.route('/api/clear-data', methods=['POST'])
def clear_all():
    """Resets entire database and clears uploads."""
    database.clear_all_data()
    return jsonify({"status": "success", "message": "All screening data reset successfully."})


if __name__ == '__main__':
    print("\n========================================================")
    print("AI-Based Resume Screening System running locally at:")
    print(">> http://127.0.0.1:5000")
    print("========================================================\n")
    app.run(debug=True, host='127.0.0.1', port=5000)

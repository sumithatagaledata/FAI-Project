/**
 * ResumeAI - Futuristic Client Motion & Interactive Neural Architecture
 */

// ==========================================
// 0. LIVE ANIMATED NEURAL WALLPAPER ENGINE
// ==========================================

function initNeuralWallpaper() {
    const canvas = document.getElementById('neuralCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Respect user's motion preferences
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let width = 0;
    let height = 0;
    let nodes = [];
    let animationFrameId = null;

    // Mouse coordinates for interactive attraction
    const mouse = {
        x: null,
        y: null,
        radius: 140
    };

    window.addEventListener('mousemove', (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener('mouseleave', () => {
        mouse.x = null;
        mouse.y = null;
    });

    function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        initNodes();
    }

    function initNodes() {
        nodes = [];
        const nodeCount = Math.floor(Math.min(width * height / 18000, 70));
        const colors = [
            'rgba(99, 102, 241, ', // electric violet
            'rgba(6, 182, 212, ',  // neon cyan
            'rgba(168, 85, 247, '  // luminous purple
        ];

        for (let i = 0; i < Math.max(nodeCount, 35); i++) {
            const colorPrefix = colors[i % colors.length];
            nodes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: prefersReducedMotion ? 0 : (Math.random() - 0.5) * 0.55,
                vy: prefersReducedMotion ? 0 : (Math.random() - 0.5) * 0.55,
                radius: Math.random() * 1.8 + 1.2,
                colorPrefix: colorPrefix,
                baseAlpha: Math.random() * 0.45 + 0.35,
                pulseSpeed: Math.random() * 0.02 + 0.01,
                pulseVal: Math.random() * Math.PI
            });
        }
    }

    function draw() {
        ctx.clearRect(0, 0, width, height);

        const connectionDistance = 145;

        // Draw connections between nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < connectionDistance) {
                    const alpha = (1 - dist / connectionDistance) * 0.20;
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`;
                    ctx.lineWidth = 0.85;
                    ctx.stroke();
                }
            }
        }

        // Draw mouse connections if hovering
        if (mouse.x !== null && mouse.y !== null && !prefersReducedMotion) {
            for (let i = 0; i < nodes.length; i++) {
                const dx = nodes[i].x - mouse.x;
                const dy = nodes[i].y - mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < mouse.radius) {
                    const alpha = (1 - dist / mouse.radius) * 0.45;
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
                    ctx.lineWidth = 1.1;
                    ctx.stroke();
                }
            }
        }

        // Update and draw nodes
        for (let i = 0; i < nodes.length; i++) {
            const n = nodes[i];

            if (!prefersReducedMotion) {
                n.x += n.vx;
                n.y += n.vy;

                // Bounce off edges smoothly
                if (n.x < 0 || n.x > width) n.vx *= -1;
                if (n.y < 0 || n.y > height) n.vy *= -1;

                // Subtle mouse interaction
                if (mouse.x !== null && mouse.y !== null) {
                    const dx = n.x - mouse.x;
                    const dy = n.y - mouse.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < mouse.radius && dist > 0) {
                        const force = (mouse.radius - dist) / mouse.radius;
                        n.x += (dx / dist) * force * 0.5;
                        n.y += (dy / dist) * force * 0.5;
                    }
                }

                n.pulseVal += n.pulseSpeed;
            }

            const currentAlpha = n.baseAlpha + Math.sin(n.pulseVal) * 0.15;

            // Outer subtle glow halo
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.radius * 2.6, 0, Math.PI * 2);
            ctx.fillStyle = `${n.colorPrefix}${Math.max(0, currentAlpha * 0.25)})`;
            ctx.fill();

            // Inner crisp node
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
            ctx.fillStyle = `${n.colorPrefix}${Math.min(1, currentAlpha)})`;
            ctx.fill();
        }

        if (!prefersReducedMotion) {
            animationFrameId = requestAnimationFrame(draw);
        }
    }

    window.addEventListener('resize', () => {
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        resize();
        draw();
    });

    resize();
    draw();
}

// ==========================================
// 1. STATE & MODAL CONTROLS
// ==========================================

let selectedFilesList = [];
let currentFilesDataTransfer = new DataTransfer();

function openUploadModal() {
    const modal = document.getElementById('uploadResumesModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeUploadModal() {
    const modal = document.getElementById('uploadResumesModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}

function handleModalBackdropClick(event) {
    if (event.target.id === 'uploadResumesModal') {
        closeUploadModal();
    }
}

// Global Keyboard Accessibility (ESC closes modal, Ctrl+K for search)
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeUploadModal();
        const notifDropdown = document.getElementById('notificationDropdown');
        if (notifDropdown) notifDropdown.classList.remove('active');
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('candidateSearchInput');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

function toggleJdAccordion() {
    const body = document.getElementById('jdAccordionBody');
    const label = document.getElementById('jdToggleBtn');
    if (body) {
        const isHidden = body.style.display === 'none';
        body.style.display = isHidden ? 'block' : 'none';
        if (label) {
            label.innerHTML = isHidden 
                ? '<i class="fa-solid fa-chevron-up"></i> Hide JD' 
                : '<i class="fa-solid fa-pen-to-square"></i> Edit JD Requirements';
        }
    }
}

function fillSampleJobData() {
    const titleInput = document.getElementById('job_title');
    const jdInput = document.getElementById('job_description');
    const label = document.getElementById('jdSectionLabel');

    if (titleInput) {
        titleInput.value = "Senior Python & AI Developer";
    }
    if (jdInput) {
        jdInput.value = `We are seeking a Senior Python & AI Developer with 3+ years of experience in building scalable backend systems, REST APIs, and machine learning workflows.
Key Requirements:
- Strong proficiency in Python, Flask/FastAPI, SQL, and database indexing.
- Hands-on experience with Machine Learning libraries (Pandas, NumPy, Scikit-learn, TF-IDF).
- Practical knowledge of Docker containerization and Git version control.
- Education: Bachelor's or Master's degree in Computer Science or related engineering.`;
    }
    if (label) {
        label.innerHTML = 'Position: <strong>Senior Python & AI Developer</strong>';
    }
}

// ==========================================
// 2. DRAG & DROP & FILE CHIP RENDERING
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Neural Wallpaper Engine
    initNeuralWallpaper();

    // 2. Navbar scroll glass effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.site-navbar');
        if (navbar) {
            if (window.scrollY > 20) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    });

    // 3. Dropzone configuration
    const dropzone = document.getElementById('dropzone');
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                handleFileSelect(files);
            }
        }, false);
    }

    // 4. Close dropdowns on outside click
    document.addEventListener('click', (e) => {
        const notifWrap = document.querySelector('.notification-wrap');
        const dropdown = document.getElementById('notificationDropdown');
        if (notifWrap && dropdown && !notifWrap.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
});

function handleFileSelect(files) {
    if (!files || files.length === 0) return;

    currentFilesDataTransfer = new DataTransfer();
    selectedFilesList = [];

    Array.from(files).forEach(file => {
        if (file.name.toLowerCase().endsWith('.pdf')) {
            currentFilesDataTransfer.items.add(file);
            selectedFilesList.push(file);
        }
    });

    const fileInput = document.getElementById('resumesInput');
    if (fileInput) {
        fileInput.files = currentFilesDataTransfer.files;
    }

    renderSelectedFileChips();
}

function renderSelectedFileChips() {
    const prompt = document.getElementById('dropzonePrompt');
    const selectedWrap = document.getElementById('dropzoneSelected');
    const chipsContainer = document.getElementById('selectedChipsContainer');

    if (!selectedWrap || !chipsContainer) return;

    if (selectedFilesList.length === 0) {
        if (prompt) prompt.style.display = 'block';
        selectedWrap.style.display = 'none';
        chipsContainer.innerHTML = '';
        return;
    }

    if (prompt) prompt.style.display = 'none';
    selectedWrap.style.display = 'block';
    chipsContainer.innerHTML = '';

    const maxDisplay = 2;
    const displayFiles = selectedFilesList.slice(0, maxDisplay);
    const remainingCount = selectedFilesList.length - maxDisplay;

    displayFiles.forEach((file, index) => {
        const chip = document.createElement('div');
        chip.className = 'file-chip-pill';
        chip.innerHTML = `
            <i class="fa-solid fa-file-pdf file-chip-icon"></i>
            <span class="file-chip-name" title="${file.name}">${file.name}</span>
            <span class="file-chip-remove" onclick="removeSelectedFile(event, ${index})">&times;</span>
        `;
        chipsContainer.appendChild(chip);
    });

    if (remainingCount > 0) {
        const moreBadge = document.createElement('div');
        moreBadge.className = 'file-chip-more';
        moreBadge.textContent = `+ ${remainingCount} more files`;
        chipsContainer.appendChild(moreBadge);
    }
}

function removeSelectedFile(event, index) {
    event.stopPropagation();
    selectedFilesList.splice(index, 1);

    currentFilesDataTransfer = new DataTransfer();
    selectedFilesList.forEach(file => {
        currentFilesDataTransfer.items.add(file);
    });

    const fileInput = document.getElementById('resumesInput');
    if (fileInput) {
        fileInput.files = currentFilesDataTransfer.files;
    }

    renderSelectedFileChips();
}

// ==========================================
// 3. TABLE FILTERING, SORTING & SEARCH
// ==========================================

function filterRankingsTable() {
    const searchInput = document.getElementById('candidateSearchInput');
    const skillSelect = document.getElementById('skillDropdownFilter');
    const tableBody = document.getElementById('rankingsTableBody');

    if (!tableBody) return;

    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const selectedSkill = skillSelect ? skillSelect.value.toLowerCase().trim() : '';
    const rows = tableBody.getElementsByClassName('ranking-row');

    Array.from(rows).forEach(row => {
        const name = row.getAttribute('data-name') || '';
        const email = row.getAttribute('data-email') || '';
        const skills = row.getAttribute('data-skills') || '';

        const matchesQuery = !query || name.includes(query) || email.includes(query) || skills.includes(query);
        const matchesSkill = !selectedSkill || skills.includes(selectedSkill);

        if (matchesQuery && matchesSkill) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function filterBySkillPill(skill) {
    const searchInput = document.getElementById('candidateSearchInput');
    const skillSelect = document.getElementById('skillDropdownFilter');
    if (skillSelect) {
        skillSelect.value = skill;
    } else if (searchInput) {
        searchInput.value = skill;
    }
    filterRankingsTable();

    const rankingsSection = document.getElementById('rankingsSection');
    if (rankingsSection) {
        rankingsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function sortRankingsTable(criteria) {
    const tableBody = document.getElementById('rankingsTableBody');
    if (!tableBody) return;

    const rows = Array.from(tableBody.getElementsByClassName('ranking-row'));

    rows.sort((a, b) => {
        const scoreA = parseFloat(a.getAttribute('data-score')) || 0;
        const scoreB = parseFloat(b.getAttribute('data-score')) || 0;
        const expA = parseFloat(a.getAttribute('data-exp')) || 0;
        const expB = parseFloat(b.getAttribute('data-exp')) || 0;
        const nameA = a.getAttribute('data-name') || '';
        const nameB = b.getAttribute('data-name') || '';

        if (criteria === 'score_desc') return scoreB - scoreA;
        if (criteria === 'score_asc') return scoreA - scoreB;
        if (criteria === 'exp_desc') return expB - expA;
        if (criteria === 'name_asc') return nameA.localeCompare(nameB);
        return 0;
    });

    rows.forEach(row => tableBody.appendChild(row));
}

function clearRankingsFilters() {
    const searchInput = document.getElementById('candidateSearchInput');
    const skillSelect = document.getElementById('skillDropdownFilter');
    const sortSelect = document.getElementById('sortDropdownFilter');

    if (searchInput) searchInput.value = '';
    if (skillSelect) skillSelect.value = '';
    if (sortSelect) sortSelect.value = 'score_desc';

    filterRankingsTable();
    sortRankingsTable('score_desc');
}

function handleGlobalSearch(query) {
    const tableSearch = document.getElementById('candidateSearchInput');
    if (tableSearch) {
        tableSearch.value = query;
        filterRankingsTable();
        const rankingsSection = document.getElementById('rankingsSection');
        if (rankingsSection && query.length > 2) {
            rankingsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
}

function toggleNotificationDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

function toggleRowMenu(event, candId) {
    event.stopPropagation();
    window.location.href = `/candidate/${candId}`;
}

// ==========================================
// 4. FORM SUBMIT & 1-CLICK DEMO
// ==========================================

function handleFormSubmit(e) {
    const fileInput = document.getElementById('resumesInput');
    const jdInput = document.getElementById('job_description');

    if (!jdInput || !jdInput.value.trim()) {
        alert("Please enter a Job Description before proceeding.");
        return false;
    }

    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert("Please select at least one PDF resume to screen.");
        return false;
    }

    closeUploadModal();
    showLoading("Extracting & Scoring Resumes...", "Running PDF text extraction, TF-IDF cosine matching, and Merge Sort ranking.");
    return true;
}

function triggerSampleDemo() {
    closeUploadModal();
    showLoading("Generating Demonstration Resumes...", "Creating 5 sample PDF candidate profiles across different experience tiers and executing AI ranking.");

    fetch('/api/load-sample', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = data.redirect_url;
        } else {
            hideLoading();
            alert("Demo error: " + data.message);
        }
    })
    .catch(err => {
        hideLoading();
        alert("Failed to load demo: " + err);
    });
}

function deleteJob(jobId) {
    if (confirm("Are you sure you want to delete this screening session and its evaluated candidates?")) {
        showLoading("Removing Session...", "Deleting screening records from database.");
        fetch(`/api/delete-job/${jobId}`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();
                } else {
                    hideLoading();
                    alert("Delete failed: " + data.message);
                }
            })
            .catch(err => {
                hideLoading();
                alert("Error deleting session: " + err);
            });
    }
}

function confirmClearData() {
    if (confirm("Are you sure you want to reset all stored screening sessions and resume data?")) {
        showLoading("Resetting Database...", "Clearing stored candidates, jobs, and upload cache.");
        fetch('/api/clear-data', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                window.location.href = '/';
            })
            .catch(err => {
                hideLoading();
                alert("Failed to reset: " + err);
            });
    }
}

function showLoading(title, subtitle) {
    const overlay = document.getElementById('loadingOverlay');
    const titleEl = document.getElementById('loadingTitle');
    const subEl = document.getElementById('loadingSubtitle');

    if (titleEl && title) titleEl.textContent = title;
    if (subEl && subtitle) subEl.textContent = subtitle;
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
}

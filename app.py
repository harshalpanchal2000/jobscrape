"""JobScrape — LinkedIn Job Scraper with Streamlit UI."""

import streamlit as st
import pandas as pd
from datetime import datetime

from scraper import scrape_jobs, scrape_job_description, filter_jobs_by_relevance, TIME_FILTERS, EXPERIENCE_FILTERS
from exporter import export_to_excel

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobScrape",
    page_icon="",
    layout="wide",
)

# ── Fig Mint–inspired styling ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Global overrides ─────────────────────────────────── */
    .stApp {
        background-color: #f5f0ea;
    }
    section[data-testid="stSidebar"] {
        background-color: #ece5db;
        border-right: 1px solid #d4cdc4;
    }

    /* ── Force dark text on all sidebar elements ──────────── */
    section[data-testid="stSidebar"] * {
        color: #3a3530 !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {
        font-family: 'Inter', sans-serif;
        color: #4a4540 !important;
        font-size: 0.85rem;
    }
    section[data-testid="stSidebar"] h2 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #1a1815 !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: #3a3530 !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] span {
        color: #1a1815 !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: #8a8279 !important;
    }
    /* Sidebar button — white text on dark button */
    section[data-testid="stSidebar"] .stButton button,
    section[data-testid="stSidebar"] .stButton button *,
    section[data-testid="stSidebar"] .stButton button p,
    section[data-testid="stSidebar"] .stButton button span {
        background-color: #1a1815 !important;
        color: #ffffff !important;
        border: none !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover,
    section[data-testid="stSidebar"] .stButton button:hover * {
        background-color: #2c2823 !important;
        color: #ffffff !important;
    }

    /* ── Force dark text on main area elements ────────────── */
    .stApp label,
    .stApp .stTextInput label,
    .stApp .stSelectbox label {
        color: #3a3530 !important;
    }
    .stApp input {
        color: #1a1815 !important;
    }
    .stApp input::placeholder {
        color: #8a8279 !important;
    }
    .stApp .stSelectbox [data-baseweb="select"] span {
        color: #1a1815 !important;
    }

    /* ── Header ───────────────────────────────────────────── */
    .hero {
        padding: 40px 0 20px 0;
    }
    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3.2rem;
        font-weight: 900;
        color: #1a1815;
        line-height: 1.1;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        color: #6b6259;
        font-weight: 300;
        letter-spacing: 0.2px;
    }
    .hero-line {
        width: 60px;
        height: 2px;
        background: #1a1815;
        margin: 24px 0;
    }

    /* ── Stat cards ───────────────────────────────────────── */
    .stat-row {
        display: flex;
        gap: 16px;
        margin: 20px 0;
    }
    .stat-card {
        background: #fff;
        border: 1px solid #d4cdc4;
        border-radius: 4px;
        padding: 18px 24px;
        flex: 1;
        text-align: center;
    }
    .stat-number {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1815;
    }
    .stat-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        color: #8a8279;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 4px;
    }

    /* ── Job cards ────────────────────────────────────────── */
    .job-card {
        background: #fff;
        border: 1px solid #d4cdc4;
        border-radius: 4px;
        padding: 20px 24px;
        margin-bottom: 14px;
        transition: box-shadow 0.2s ease;
    }
    .job-card:hover {
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .job-number {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 0.85rem;
        color: #b0a89e;
        margin-bottom: 4px;
    }
    .job-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1815;
        line-height: 1.3;
    }
    .job-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #6b6259;
        margin-top: 8px;
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
    }
    .job-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }

    /* ── Section headers ──────────────────────────────────── */
    .section-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1815;
        margin: 32px 0 16px 0;
        letter-spacing: -0.3px;
    }
    .section-line {
        width: 40px;
        height: 1.5px;
        background: #1a1815;
        margin-bottom: 20px;
    }

    /* ── Welcome state ────────────────────────────────────── */
    .welcome {
        text-align: center;
        padding: 80px 20px;
    }
    .welcome-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #1a1815;
        margin-bottom: 12px;
    }
    .welcome-sub {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: #8a8279;
        font-weight: 300;
        max-width: 480px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Dividers ─────────────────────────────────────────── */
    .divider {
        height: 1px;
        background: #d4cdc4;
        margin: 28px 0;
    }

    /* ── Footer ───────────────────────────────────────────── */
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        padding: 12px 24px;
        text-align: right;
        z-index: 999;
        background: #ece5db;
        border-top-left-radius: 8px;
        border-top: 1px solid #d4cdc4;
        border-left: 1px solid #d4cdc4;
    }
    .footer-made {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: #1a1815;
        letter-spacing: 0.3px;
        margin-bottom: 1px;
    }
    .footer-made span {
        font-weight: 600;
    }
    .footer-copyright {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: #8a8279;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Hide default Streamlit branding ──────────────────── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">JobScrape.</div>
    <div class="hero-sub">Scrape LinkedIn job listings, filter results, and export to Excel.</div>
    <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Search controls ───────────────────────────────────────────────
with st.sidebar:
    st.header("Search")

    keywords = st.text_input("Keywords", placeholder="e.g. Data Analyst, Python Developer")
    location = st.text_input("Location", placeholder="e.g. Ontario, Remote, India")

    search_mode = st.radio(
        "Keyword matching",
        ["Exact phrase", "Any of these words"],
        index=0,
        help="**Exact phrase**: matches the full phrase. "
             "**Any of these words**: matches any individual word.",
    )

    st.markdown("---")

    time_filter = st.selectbox("Date Posted", list(TIME_FILTERS.keys()), index=1)

    exp_options = [k for k in EXPERIENCE_FILTERS.keys() if k != "Any"]
    experience_levels = st.multiselect(
        "Experience Level",
        exp_options,
        default=[],
        help="Leave empty for all levels.",
    )

    include_companies_input = st.text_input(
        "Include companies",
        placeholder="e.g. Google, Microsoft",
        help="Comma-separated. Only show these companies.",
    )
    exclude_companies_input = st.text_input(
        "Exclude companies",
        placeholder="e.g. Infosys, Wipro",
        help="Comma-separated. Hide these companies.",
    )

    st.markdown("---")

    num_pages = st.slider("Pages to scrape", min_value=1, max_value=50, value=2,
                          help="~25 jobs per page")
    fetch_jd = st.checkbox("Fetch job descriptions", value=True,
                           help="~2s per job for rate-limit safety")

    search_btn = st.button("Search Jobs", type="primary", use_container_width=True)

# ── Session state ────────────────────────────────────────────────────────────
if "jobs" not in st.session_state:
    st.session_state.jobs = []

# ── Search action ────────────────────────────────────────────────────────────
if search_btn:
    if not keywords.strip():
        st.error("Please enter keywords to search.")
    else:
        with st.spinner(f"Searching for \"{keywords}\"..."):
            progress_bar = st.progress(0, text="Starting search...")

            def update_progress(current, total):
                progress_bar.progress(
                    current / total,
                    text=f"Scraping page {current} of {total}..."
                )

            exact_match = search_mode == "Exact phrase"
            jobs = scrape_jobs(
                keywords, location, num_pages,
                time_filter=time_filter,
                experience_levels=experience_levels,
                exact_match=exact_match,
                progress_callback=update_progress,
            )

            # Filter out irrelevant results before fetching JDs
            original_count = len(jobs)
            jobs = filter_jobs_by_relevance(jobs, keywords)

            # Apply company include/exclude filters
            inc = [c.strip().lower() for c in include_companies_input.split(",") if c.strip()]
            exc = [c.strip().lower() for c in exclude_companies_input.split(",") if c.strip()]
            if inc:
                jobs = [j for j in jobs if any(c in j["company"].lower() for c in inc)]
            if exc:
                jobs = [j for j in jobs if not any(c in j["company"].lower() for c in exc)]

            removed = original_count - len(jobs)

            if fetch_jd and jobs:
                progress_bar.progress(1.0, text="Fetching job descriptions...")
                jd_progress = st.progress(0, text="Fetching descriptions...")
                failed_count = 0
                for i, job in enumerate(jobs):
                    job["description"] = scrape_job_description(job["url"])
                    if job["description"] == "[Failed to fetch]":
                        failed_count += 1
                    jd_progress.progress(
                        (i + 1) / len(jobs),
                        text=f"Fetching JD {i + 1} of {len(jobs)}"
                             f"{f' ({failed_count} failed)' if failed_count else ''}..."
                    )
                jd_progress.empty()

            progress_bar.empty()

        st.session_state.jobs = jobs

        if jobs:
            jd_fetched = sum(1 for j in jobs if j.get("description") and j["description"] != "[Failed to fetch]")
            jd_failed = sum(1 for j in jobs if j.get("description") == "[Failed to fetch]")
            msg = f"Found {len(jobs)} relevant jobs."
            if removed:
                msg += f" Filtered out {removed} irrelevant."
            if fetch_jd:
                msg += f" JDs: {jd_fetched}/{len(jobs)}."
            st.success(msg)
            if jd_failed:
                st.warning(f"{jd_failed} descriptions failed to fetch (rate limited).")
        else:
            st.warning("No jobs found. Try different keywords or location.")

# ── Display results ──────────────────────────────────────────────────────────
jobs = st.session_state.jobs

if jobs:
    # ── Filters ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Filter Results</div><div class="section-line"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        filter_title = st.text_input("Filter by title", placeholder="e.g. Senior, Manager")
    with col2:
        locations = sorted(set(j["location"] for j in jobs if j["location"] != "N/A"))
        filter_location = st.selectbox("Filter by location", ["All"] + locations)

    # Apply filters
    filtered = jobs
    if filter_title:
        filtered = [j for j in filtered if filter_title.lower() in j["title"].lower()]
    if filter_location != "All":
        filtered = [j for j in filtered if j["location"] == filter_location]

    # ── Stats ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-number">{len(jobs)}</div>
            <div class="stat-label">Total Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(filtered)}</div>
            <div class="stat-label">After Filters</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(j["company"] for j in filtered))}</div>
            <div class="stat-label">Companies</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Export button ────────────────────────────────────────────────────────
    col_export, col_spacer = st.columns([1, 3])
    with col_export:
        excel_buffer = export_to_excel(filtered)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name=f"linkedin_jobs_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

    # ── Job cards ────────────────────────────────────────────────────────────
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Listings ({len(filtered)})</div><div class="section-line"></div>', unsafe_allow_html=True)

    for i, job in enumerate(filtered):
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div class="job-number">No. {i + 1}</div>
                <div class="job-title">{job['title']}</div>
                <div class="job-meta">
                    <span class="job-meta-item">{job['company']}</span>
                    <span class="job-meta-item">{job['location']}</span>
                    <span class="job-meta-item">{job['posted']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_link, col_desc = st.columns([1, 3])
            with col_link:
                if job["url"]:
                    st.link_button("View on LinkedIn", job["url"])

            if job.get("description"):
                with st.expander("View Job Description"):
                    st.text(job["description"])

else:
    # ── Welcome state ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="welcome">
        <div class="welcome-title">Welcome to JobScrape.</div>
        <div class="welcome-sub">
            Enter your keywords and location in the sidebar,<br>
            then press <b>Search Jobs</b> to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-made">Made by <span>Harshal Panchal</span></div>
    <div class="footer-copyright">&copy; 2025 Suntrail AI Labs Inc.</div>
</div>
""", unsafe_allow_html=True)

"""JobScrape — LinkedIn Job Scraper with Streamlit UI."""

import streamlit as st
import pandas as pd
from datetime import datetime

from scraper import scrape_jobs, scrape_job_description, filter_jobs_by_relevance, TIME_FILTERS, EXPERIENCE_FILTERS
from exporter import export_to_excel

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobScrape — LinkedIn Job Scraper",
    page_icon="🔍",
    layout="wide",
)

# ── Custom styling ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0A66C2;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-top: 0;
    }
    .job-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background: #fafafa;
    }
    .job-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #0A66C2;
    }
    .job-company {
        font-size: 0.95rem;
        color: #333;
    }
    .job-location {
        font-size: 0.85rem;
        color: #666;
    }
    .stat-box {
        background: #0A66C2;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">JobScrape</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Scrape LinkedIn job listings, filter results, and export to Excel</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Sidebar — Search controls ───────────────────────────────────────────────
with st.sidebar:
    st.header("Search Settings")

    keywords = st.text_input("Job Keywords", placeholder="e.g. Data Scientist, Python Developer")
    location = st.text_input("Location", placeholder="e.g. New York, Remote, India")

    st.markdown("##### Search Mode")
    search_mode = st.radio(
        "Keyword matching",
        ["Exact phrase", "Any of these words"],
        index=0,
        help="**Exact phrase**: searches for \"data analyst\" as a whole. "
             "**Any of these words**: matches jobs containing \"data\" OR \"analyst\".",
    )

    st.markdown("##### Filters")
    time_filter = st.selectbox("Date Posted", list(TIME_FILTERS.keys()), index=1,
                               help="Filter jobs by when they were posted")

    # Multi-select experience levels (exclude "Any" from choices — leave empty for any)
    exp_options = [k for k in EXPERIENCE_FILTERS.keys() if k != "Any"]
    experience_levels = st.multiselect(
        "Experience Level",
        exp_options,
        default=[],
        help="Select one or more levels. Leave empty for all levels.",
    )

    st.markdown("##### Company Filter")
    include_companies_input = st.text_input(
        "Include only these companies",
        placeholder="e.g. Google, Microsoft, Amazon",
        help="Comma-separated. Only show jobs from these companies. Leave empty for all.",
    )
    exclude_companies_input = st.text_input(
        "Exclude these companies",
        placeholder="e.g. Infosys, Wipro, Staffing Inc",
        help="Comma-separated. Hide jobs from these companies.",
    )

    st.markdown("##### Scraping")
    num_pages = st.slider("Pages to scrape", min_value=1, max_value=50, value=2,
                          help="Each page returns ~25 jobs. 50 pages = ~1250 jobs max.")
    fetch_jd = st.checkbox("Fetch job descriptions", value=True,
                           help="Extracts full JD from each listing (included in Excel export). "
                                "Adds ~2s per job for rate-limit safety.")

    search_btn = st.button("🔍 Search Jobs", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("**Tips:**")
    st.markdown("- **Exact phrase** avoids unrelated results")
    st.markdown("- Select multiple experience levels at once")
    st.markdown("- Company filters are case-insensitive")
    st.markdown("- ~2s delay per JD to avoid rate limits")

# ── Session state ────────────────────────────────────────────────────────────
if "jobs" not in st.session_state:
    st.session_state.jobs = []

# ── Search action ────────────────────────────────────────────────────────────
if search_btn:
    if not keywords.strip():
        st.error("Please enter job keywords to search.")
    else:
        with st.spinner(f"Scraping LinkedIn for \"{keywords}\" jobs..."):
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
            msg = f"Found {len(jobs)} relevant jobs!"
            if removed:
                msg += f" (filtered out {removed} irrelevant)"
            if fetch_jd:
                msg += f" JDs fetched: {jd_fetched}/{len(jobs)}."
            st.success(msg)
            if jd_failed:
                st.warning(f"{jd_failed} job descriptions failed to fetch (rate limited). Try again later for those.")
        else:
            st.warning("No jobs found. Try different keywords or location.")

# ── Display results ──────────────────────────────────────────────────────────
jobs = st.session_state.jobs

if jobs:
    # ── Filters ──────────────────────────────────────────────────────────────
    st.subheader("Filter Results")
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
    st.markdown("---")
    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("Total Found", len(jobs))
    stat2.metric("After Filters", len(filtered))
    stat3.metric("Companies", len(set(j["company"] for j in filtered)))

    # ── Export button ────────────────────────────────────────────────────────
    st.markdown("---")
    col_export, col_spacer = st.columns([1, 3])
    with col_export:
        excel_buffer = export_to_excel(filtered)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name=f"linkedin_jobs_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )

    # ── Job cards ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(f"Job Listings ({len(filtered)})")

    for i, job in enumerate(filtered):
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <span class="job-title">{i + 1}. {job['title']}</span><br>
                <span class="job-company">🏢 {job['company']}</span> &nbsp;|&nbsp;
                <span class="job-location">📍 {job['location']}</span> &nbsp;|&nbsp;
                <span style="color: #888; font-size: 0.85rem;">📅 {job['posted']}</span>
            </div>
            """, unsafe_allow_html=True)

            col_link, col_desc = st.columns([1, 3])
            with col_link:
                if job["url"]:
                    st.link_button("🔗 View on LinkedIn", job["url"])

            if job.get("description"):
                with st.expander(f"📄 View Job Description"):
                    st.text(job["description"])

else:
    # ── Empty state ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; color: #999;">
        <h2>👋 Welcome to JobScrape</h2>
        <p>Enter job keywords and location in the sidebar, then click <b>Search Jobs</b> to get started.</p>
    </div>
    """, unsafe_allow_html=True)

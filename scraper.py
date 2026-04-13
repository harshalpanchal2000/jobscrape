"""LinkedIn job scraper using public job search pages."""

import time
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


# LinkedIn filter codes
TIME_FILTERS = {
    "Any time": "",
    "Past 24 hours": "r86400",
    "Past week": "r604800",
    "Past month": "r2592000",
}

EXPERIENCE_FILTERS = {
    "Any": "",
    "Internship": "1",
    "Entry level": "2",
    "Associate": "3",
    "Mid-Senior level": "4",
    "Director": "5",
    "Executive": "6",
}


def scrape_jobs(keywords, location="", num_pages=2, time_filter="Any time",
                experience_levels=None, exact_match=True, progress_callback=None):
    """Scrape LinkedIn public job listings.

    Args:
        keywords: Job title or search keywords.
        location: City, state, or country.
        num_pages: Number of pages to scrape (25 jobs per page).
        time_filter: One of TIME_FILTERS keys (e.g. "Past 24 hours").
        experience_levels: List of EXPERIENCE_FILTERS keys (e.g. ["Entry level", "Associate"]).
        exact_match: If True, search for the exact phrase (wraps in quotes).
        progress_callback: Optional callable(current_page, total_pages) for UI updates.

    Returns:
        List of dicts with job data.
    """
    if experience_levels is None:
        experience_levels = []

    # Wrap keywords in quotes for exact phrase matching
    search_keywords = f'"{keywords}"' if exact_match and keywords else keywords

    jobs = []

    for page in range(num_pages):
        if progress_callback:
            progress_callback(page + 1, num_pages)

        start = page * 25
        params = {
            "keywords": search_keywords,
            "location": location,
            "start": start,
        }

        # Add time filter (f_TPR = time posted range)
        time_code = TIME_FILTERS.get(time_filter, "")
        if time_code:
            params["f_TPR"] = time_code

        # Add experience level filter (f_E supports comma-separated codes)
        exp_codes = [
            EXPERIENCE_FILTERS[lvl]
            for lvl in experience_levels
            if lvl in EXPERIENCE_FILTERS and EXPERIENCE_FILTERS[lvl]
        ]
        if exp_codes:
            params["f_E"] = ",".join(exp_codes)

        try:
            resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.find_all("div", class_="base-card")

        for card in cards:
            job = _parse_card(card)
            if job:
                jobs.append(job)

        if page < num_pages - 1:
            time.sleep(1.5)

    return jobs


def scrape_job_description(url, max_retries=2):
    """Fetch the full job description from a LinkedIn job posting URL.

    Includes rate-limiting delay and retry logic to avoid 429 errors.
    """
    for attempt in range(max_retries):
        # Rate-limiting delay before each request
        time.sleep(2)

        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)

            # Handle rate limiting explicitly
            if resp.status_code == 429:
                wait_time = 5 * (attempt + 1)  # 5s, then 10s
                time.sleep(wait_time)
                continue

            resp.raise_for_status()
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            return "[Failed to fetch]"

        soup = BeautifulSoup(resp.text, "lxml")
        desc_div = soup.find("div", class_="show-more-less-html__markup")
        if desc_div:
            return desc_div.get_text(separator="\n", strip=True)
        return ""

    return "[Failed to fetch]"


def _parse_card(card):
    """Extract job info from a single LinkedIn job card."""
    title_el = card.find("h3", class_="base-search-card__title")
    company_el = card.find("h4", class_="base-search-card__subtitle")
    location_el = card.find("span", class_="job-search-card__location")
    link_el = card.find("a", class_="base-card__full-link")
    time_el = card.find("time")

    if not title_el or not link_el:
        return None

    job_url = link_el.get("href", "").split("?")[0]

    return {
        "title": title_el.get_text(strip=True),
        "company": company_el.get_text(strip=True) if company_el else "N/A",
        "location": location_el.get_text(strip=True) if location_el else "N/A",
        "url": job_url,
        "posted": time_el.get("datetime", "N/A") if time_el else "N/A",
        "description": "",
    }

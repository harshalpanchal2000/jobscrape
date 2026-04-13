# JobScrape

A local-first LinkedIn job scraper with a clean Streamlit dashboard. Search jobs, filter results, fetch full job descriptions, and export everything to a styled Excel file.

Built by **Harshal Panchal** | &copy; 2025 Suntrail AI Labs Inc.

---

## Features

- **LinkedIn Job Scraping** — Scrapes public LinkedIn job listings (title, company, location, posted date, URL)
- **Exact Phrase Search** — Search `"data analyst"` as a whole phrase, or match any individual word
- **Experience Level Filter** — Multi-select: Internship, Entry, Associate, Mid-Senior, Director, Executive
- **Date Posted Filter** — Past 24 hours, past week, past month, or any time
- **Company Filters** — Include only specific companies or exclude unwanted ones (e.g. staffing agencies)
- **Relevance Filter** — Automatically removes garbage results that don't match your keywords
- **Job Description Fetching** — Extracts full JD from each listing with rate-limit handling and retry logic
- **Excel Export** — Styled `.xlsx` with LinkedIn-blue headers, clickable hyperlinks, and full job descriptions
- **Up to 50 pages** — Scrape up to ~1,250 jobs per search

---

## Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/harshalpanchal2000/jobscrape.git
   cd jobscrape
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**

   ```bash
   streamlit run app.py
   ```

   The app will open in your browser at `http://localhost:8501`.

---

## Usage

1. Enter **keywords** (e.g. "Data Analyst") and **location** (e.g. "Ontario") in the sidebar
2. Choose **Exact phrase** or **Any of these words** for keyword matching
3. Set filters: date posted, experience level, include/exclude companies
4. Adjust **pages to scrape** (each page = ~25 jobs)
5. Click **Search Jobs**
6. Browse results, expand job descriptions, and filter by title or location
7. Click **Download Excel** to export results with full JDs and clickable links

---

## Project Structure

```
jobscrape/
├── app.py                  # Streamlit dashboard (main entry point)
├── scraper.py              # LinkedIn public job scraper
├── exporter.py             # Styled Excel export
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── .gitignore
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| Scraping | requests + BeautifulSoup |
| Excel Export | openpyxl |
| HTML Parsing | lxml |

---

## License

&copy; 2025 Suntrail AI Labs Inc. All rights reserved.

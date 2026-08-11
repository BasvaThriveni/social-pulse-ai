# Social Pulse AI

> Turn social media posts into actionable intelligence.

A Streamlit app that fetches an X/Twitter profile's recent posts and uses
Gemini to generate a summary, topic breakdown, sentiment/tone read, key
insights, and marketing/content recommendations — plus a chat feature to ask
free-form questions about that profile's posts.

## How it's wired together

- **Scraping** is done by the existing, unmodified script at
  `/home/user/Swinfy/Twitter/scrape_recent_tweets.py`. This app imports it
  directly (`social_pulse/scraper.py`) instead of duplicating its logic, and
  authenticates using the existing `cookies.json` in that same folder.
- **Analysis** is done by Gemini (`google-genai` SDK) via
  `social_pulse/ai.py`, using the API key stored in
  `/home/user/Swinfy/API/geminiapikey.env`.

**No secrets live inside this project.** Both credential files stay in their
original locations outside `SocialPulseAI/`, and `.gitignore` blocks `*.env`,
`cookies.json`, and any stray CSV exports from ever being committed.

## Project structure

```
SocialPulseAI/
├── app.py                  # Streamlit UI
├── requirements.txt
├── README.md
├── .gitignore
└── social_pulse/
    ├── config.py           # locates secrets outside the project; never prints them
    ├── scraper.py           # wraps the existing scrape_recent_tweets.py
    ├── ai.py                # Gemini analysis + "Ask the Profile" Q&A
    └── style.py              # custom CSS for the SaaS-style UI
```

## Running it

```bash
cd /home/user/Swinfy/SocialPulseAI
python3 -m pip install --user -r requirements.txt
python3 -m playwright install chromium   # only needed once; already installed on this machine
python3 -m streamlit run app.py
```

Then open the printed local URL (default `http://localhost:8501`).

## Using the app

1. Enter an X/Twitter username in the sidebar (no `@` needed).
2. Pick how many recent posts to analyze (3–20).
3. Click **Analyze Profile**.
4. Browse the Summary / Topics / Sentiment / Key Insights / Marketing
   Insights tabs, scroll the Recent Posts feed, and download the raw data as
   CSV.
5. Use **Ask the Profile** at the bottom to chat with Gemini about the
   fetched posts — answers are grounded only in that data.

## Notes

- Scraping is a real browser session (Playwright/Chromium) against x.com, so
  a profile analysis typically takes 20–90 seconds depending on network
  conditions and how many posts are requested.
- Private, suspended, or nonexistent profiles surface a clear error instead
  of hanging.
- Only original posts are counted (pinned tweets and retweets are skipped by
  the underlying scraper).

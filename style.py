"""Custom CSS to give the Streamlit app a polished SaaS look."""

CUSTOM_CSS = """
<style>
:root {
    --sp-bg: #0b0f19;
    --sp-panel: #131a2a;
    --sp-panel-border: #232c42;
    --sp-accent: #7c5cff;
    --sp-accent-2: #34d3b0;
    --sp-text: #e7eaf3;
    --sp-text-dim: #9aa4bf;
}

.stApp {
    background: radial-gradient(circle at 15% 0%, #171f33 0%, #0b0f19 45%) fixed;
}

section[data-testid="stSidebar"] {
    background: var(--sp-panel);
    border-right: 1px solid var(--sp-panel-border);
}

h1, h2, h3 { color: var(--sp-text) !important; letter-spacing: -0.02em; }

.sp-hero {
    padding: 1.75rem 2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(124,92,255,0.18), rgba(52,211,176,0.10));
    border: 1px solid var(--sp-panel-border);
    margin-bottom: 1.5rem;
}
.sp-hero h1 {
    font-size: 2.1rem;
    margin: 0 0 0.35rem 0;
    background: linear-gradient(90deg, #b6a8ff, #7c5cff 40%, #34d3b0);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sp-hero p { color: var(--sp-text-dim); font-size: 1.02rem; margin: 0; }

.sp-badge {
    display: inline-block;
    padding: 0.15rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    background: rgba(124,92,255,0.15);
    color: #b6a8ff;
    border: 1px solid rgba(124,92,255,0.35);
    margin-bottom: 0.75rem;
}

.sp-card {
    background: var(--sp-panel);
    border: 1px solid var(--sp-panel-border);
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
}
.sp-card h4 {
    margin-top: 0;
    color: var(--sp-text);
    font-size: 0.95rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--sp-accent-2);
}

.sp-metric-row { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem; }
.sp-metric {
    flex: 1;
    min-width: 120px;
    background: var(--sp-panel);
    border: 1px solid var(--sp-panel-border);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.sp-metric .val { font-size: 1.5rem; font-weight: 700; color: var(--sp-accent-2); }
.sp-metric .lbl { font-size: 0.75rem; color: var(--sp-text-dim); text-transform: uppercase; letter-spacing: 0.04em; }

.sp-topic-chip {
    display: inline-block;
    background: rgba(52,211,176,0.12);
    border: 1px solid rgba(52,211,176,0.35);
    color: #8ee9d2;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.85rem;
    margin: 0.2rem 0.35rem 0.2rem 0;
}

.sp-tweet {
    background: var(--sp-panel);
    border: 1px solid var(--sp-panel-border);
    border-left: 3px solid var(--sp-accent);
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.7rem;
}
.sp-tweet .meta { color: var(--sp-text-dim); font-size: 0.78rem; margin-top: 0.5rem; }

.stButton > button {
    background: linear-gradient(135deg, var(--sp-accent), #5b3fd6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(124,92,255,0.35);
}
.stButton > button:hover { filter: brightness(1.08); }

.sp-footer { color: var(--sp-text-dim); font-size: 0.8rem; text-align: center; margin-top: 2rem; }
</style>
"""

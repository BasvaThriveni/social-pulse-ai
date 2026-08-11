import html

import pandas as pd
import streamlit as st

from social_pulse.ai import AIError, analyze_profile, ask_profile
from social_pulse.config import ConfigError
from social_pulse.scraper import ScrapeError, fetch_recent_tweets, tweets_to_dataframe
from social_pulse.style import CUSTOM_CSS

st.set_page_config(
    page_title="Social Pulse AI",
    page_icon="\U0001F4E1",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None  # {"username", "rows", "df", "analysis"}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def render_hero():
    st.markdown(
        """
        <div class="sp-hero">
            <span class="sp-badge">AI Social Intelligence</span>
            <h1>Social Pulse AI</h1>
            <p>Turn social media posts into actionable intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("### \U0001F50D Analyze a Profile")
        username = st.text_input(
            "X / Twitter username",
            placeholder="e.g. elonmusk",
            help="Enter the handle without the @ symbol (or with it — either works).",
        )
        count = st.slider("Number of recent posts", min_value=3, max_value=20, value=5)
        analyze_clicked = st.button("⚡ Analyze Profile", use_container_width=True)

        st.markdown("---")
        st.markdown(
            "<span style='color:#9aa4bf; font-size:0.82rem;'>"
            "Fetches live posts via a Playwright-based scraper, then runs "
            "them through Gemini for summarization, sentiment, and content "
            "strategy insights."
            "</span>",
            unsafe_allow_html=True,
        )
        return username, count, analyze_clicked


def render_metrics(df: pd.DataFrame):
    total_likes = int(pd.to_numeric(df["likes"], errors="coerce").fillna(0).sum())
    total_retweets = int(pd.to_numeric(df["retweets"], errors="coerce").fillna(0).sum())
    total_replies = int(pd.to_numeric(df["replies"], errors="coerce").fillna(0).sum())
    total_views = int(pd.to_numeric(df["views"], errors="coerce").fillna(0).sum())

    def fmt(n):
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)

    st.markdown(
        f"""
        <div class="sp-metric-row">
            <div class="sp-metric"><div class="val">{len(df)}</div><div class="lbl">Posts analyzed</div></div>
            <div class="sp-metric"><div class="val">{fmt(total_likes)}</div><div class="lbl">Total likes</div></div>
            <div class="sp-metric"><div class="val">{fmt(total_retweets)}</div><div class="lbl">Total retweets</div></div>
            <div class="sp-metric"><div class="val">{fmt(total_replies)}</div><div class="lbl">Total replies</div></div>
            <div class="sp-metric"><div class="val">{fmt(total_views)}</div><div class="lbl">Total views</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analysis(analysis: dict):
    tab_summary, tab_topics, tab_sentiment, tab_insights, tab_marketing = st.tabs(
        ["\U0001F4CB Summary", "\U0001F3F7️ Topics", "\U0001F3AD Sentiment", "\U0001F4A1 Key Insights", "\U0001F4C8 Marketing Insights"]
    )

    with tab_summary:
        st.markdown(f'<div class="sp-card">{html.escape(analysis["summary"])}</div>', unsafe_allow_html=True)

    with tab_topics:
        chips = "".join(f'<span class="sp-topic-chip">{html.escape(t)}</span>' for t in analysis["main_topics"])
        st.markdown(f'<div class="sp-card">{chips}</div>', unsafe_allow_html=True)

    with tab_sentiment:
        s = analysis["sentiment"]
        st.markdown(
            f'<div class="sp-card"><h4>{html.escape(s["overall_tone"])}</h4>'
            f'<p>{html.escape(s["explanation"])}</p></div>',
            unsafe_allow_html=True,
        )

    with tab_insights:
        items = "".join(f"<li>{html.escape(i)}</li>" for i in analysis["key_insights"])
        st.markdown(f'<div class="sp-card"><ul>{items}</ul></div>', unsafe_allow_html=True)

    with tab_marketing:
        items = "".join(f"<li>{html.escape(i)}</li>" for i in analysis["marketing_insights"])
        st.markdown(f'<div class="sp-card"><ul>{items}</ul></div>', unsafe_allow_html=True)


def render_recent_posts(df: pd.DataFrame):
    st.markdown("### \U0001F5D2️ Recent Posts")
    for _, row in df.iterrows():
        text_html = html.escape(row["text"]) if row["text"] else "<i>(no text)</i>"
        created_at = html.escape(str(row["created_at"])) if row["created_at"] else "unknown date"
        url = html.escape(str(row["url"]), quote=True)
        st.markdown(
            f"""
            <div class="sp-tweet">
                {text_html}
                <div class="meta">
                    {created_at} &nbsp;|&nbsp;
                    ❤️ {row['likes']} &nbsp;
                    \U0001F501 {row['retweets']} &nbsp;
                    \U0001F4AC {row['replies']} &nbsp;
                    \U0001F441️ {row['views']} &nbsp;
                    <a href="{url}" target="_blank" style="color:#8ee9d2;">View on X →</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download posts as CSV",
        data=csv_bytes,
        file_name=f"{st.session_state.result['username']}_posts.csv",
        mime="text/csv",
        use_container_width=False,
    )


def render_ask_profile():
    st.markdown("### \U0001F4AC Ask the Profile")
    st.caption("Ask a question about the fetched posts. Gemini will answer using ONLY that data.")

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])

    question = st.chat_input("e.g. What products or launches did they mention?")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_profile(
                        st.session_state.result["username"],
                        st.session_state.result["rows"],
                        question,
                    )
                except AIError as e:
                    answer = f"⚠️ {e}"
                st.write(answer)
        st.session_state.chat_history.append({"question": question, "answer": answer})


def run_analysis(username: str, count: int):
    st.session_state.chat_history = []
    progress = st.empty()
    try:
        with progress.container():
            with st.spinner(
                f"\U0001F310 Fetching @{username}'s recent posts... this takes about 20-30s "
                "for a few posts, longer for higher counts."
            ):
                rows = fetch_recent_tweets(username, count)
            with st.spinner("\U0001F9E0 Gemini is analyzing the posts..."):
                analysis = analyze_profile(username, rows)
        progress.empty()
        st.session_state.result = {
            "username": username.lstrip("@").strip(),
            "rows": rows,
            "df": tweets_to_dataframe(rows),
            "analysis": analysis,
        }
        st.toast(f"Analysis complete for @{username}", icon="✅")
    except (ScrapeError, ConfigError) as e:
        progress.empty()
        st.session_state.result = None
        st.error(f"\U0001F6AB Couldn't fetch posts: {e}")
    except AIError as e:
        progress.empty()
        st.session_state.result = None
        st.error(f"\U0001F6AB AI analysis failed: {e}")
    except Exception as e:
        progress.empty()
        st.session_state.result = None
        st.error(f"\U0001F6AB Unexpected error: {e}")


def main():
    render_hero()
    username, count, analyze_clicked = render_sidebar()

    if analyze_clicked:
        if not username.strip():
            st.warning("Enter a username first.")
        else:
            run_analysis(username.strip(), count)

    result = st.session_state.result
    if result is None:
        st.info("\U0001F44B Enter a username in the sidebar and click **Analyze Profile** to get started.")
        return

    st.markdown(f"## Results for @{result['username']}")
    render_metrics(result["df"])
    render_analysis(result["analysis"])
    st.markdown("---")
    render_recent_posts(result["df"])
    st.markdown("---")
    render_ask_profile()

    st.markdown(
        '<div class="sp-footer">Social Pulse AI · Posts fetched live via Playwright · '
        'Analysis by Gemini</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

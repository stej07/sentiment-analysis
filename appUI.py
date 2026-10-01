"""
appUI.py - Streamlit UI for the Real-Time Sentiment Analysis System with Web Scraping.

It loads the model dumped by the notebook (sentiment_analysis.ipynb):
    models/sentiment_model.joblib   (falls back to models/sentiment_model_baseline.joblib)
    models/model_meta.json          (optional: metrics shown in the sidebar)

Run:
    pip install streamlit scikit-learn pandas requests beautifulsoup4 joblib
    streamlit run appUI.py
"""
import datetime
import json
import re
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

import joblib
import numpy as np
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "sentiment_model.joblib"
BASELINE_PATH = BASE_DIR / "models" / "sentiment_model_baseline.joblib"
META_PATH = BASE_DIR / "models" / "model_meta.json"

HEADERS = {"User-Agent": "SentimentStudentProject/1.0 (university course project; Python requests)"}
ORDER = ["positive", "neutral", "negative"]
EMOJI = {"positive": "😊", "neutral": "😐", "negative": "😠"}
EXAMPLES = {
    "Positive": "Delivery was fast and the product quality is excellent.",
    "Negative": "The product stopped working after two days.",
    "Neutral": "The phone was released yesterday.",
    "Mixed": "The phone camera is excellent, but the battery drains quickly.",
}

# --------------------------------------------------------------------------
# Text cleaning - MUST stay identical to clean_text() in the notebook
# --------------------------------------------------------------------------
CONTRACTIONS = [(r"won't", "will not"), (r"can't", "can not"), (r"cannot", "can not"),
                (r"n't", " not"), (r"'re", " are"), (r"'ve", " have"), (r"'ll", " will"),
                (r"'m", " am"), (r"'d", " would")]


def clean_text(text):
    text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)                  # HTML tags
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)    # URLs
    text = text.lower().replace("\u2019", "'")            # lowercase + curly apostrophe
    for pat, rep in CONTRACTIONS:
        text = re.sub(pat, rep, text)
    text = re.sub(r"[^a-z\s]", " ", text)                 # keep letters only
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------
# Model loading + prediction
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading model...")
def load_model():
    path = MODEL_PATH if MODEL_PATH.exists() else BASELINE_PATH
    if not path.exists():
        return None, {}, None
    model = joblib.load(path)
    meta = {}
    if META_PATH.exists():
        try:
            meta = json.loads(META_PATH.read_text())
        except Exception:
            meta = {}
    return model, meta, path.name


def predict_texts(model, texts):
    """Return a DataFrame: text, sentiment, confidence and one probability column per class."""
    texts = [str(t) for t in texts]
    cleaned = [clean_text(t) for t in texts]
    classes = list(model.classes_)
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(cleaned)
    else:  # e.g. LinearSVC: softmax over decision scores (a confidence proxy, not a calibrated probability)
        scores = model.decision_function(cleaned)
        if scores.ndim == 1:
            scores = np.vstack([-scores, scores]).T
        e = np.exp(scores - scores.max(axis=1, keepdims=True))
        probs = e / e.sum(axis=1, keepdims=True)
    out = pd.DataFrame(probs, columns=[f"p_{c}" for c in classes])
    out.insert(0, "confidence", probs.max(axis=1).round(3))
    out.insert(0, "sentiment", [classes[i] for i in probs.argmax(axis=1)])
    out.insert(0, "text", texts)
    return out


# --------------------------------------------------------------------------
# Web scraping
# --------------------------------------------------------------------------
DEFAULT_SELECTOR = "p, li, blockquote, h1, h2, h3"


def robots_check(url):
    """Return (allowed, reason). robots.txt is fetched with our own User-Agent.

    urllib's RobotFileParser.read() uses the default 'Python-urllib' agent, which many sites
    (e.g. Wikipedia) answer with 403 - and the parser then treats a 403 as "everything is
    disallowed". Following RFC 9309 instead: 4xx = no robots.txt rules, 5xx = unreachable.
    """
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    try:
        resp = requests.get(robots_url, headers=HEADERS, timeout=10)
    except requests.RequestException:
        return True, "robots.txt unreachable (continuing)"
    if resp.status_code == 200:
        rp = robotparser.RobotFileParser()
        rp.parse(resp.text.splitlines())
        if rp.can_fetch(HEADERS["User-Agent"], url):
            return True, "allowed by robots.txt"
        return False, f"{robots_url} disallows this page for crawlers"
    if 400 <= resp.status_code < 500:
        return True, f"no usable robots.txt (HTTP {resp.status_code})"
    return False, f"robots.txt could not be read (HTTP {resp.status_code})"


def scrape_texts(url, selector="", max_items=50, min_chars=25, respect_robots=True):
    """Fetch `url` and return a list of text blocks matched by the CSS selector."""
    url = url.strip()
    if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
        raise ValueError("Please enter a full URL starting with http:// or https://")
    if respect_robots:
        allowed, reason = robots_check(url)
        if not allowed:
            raise PermissionError(f"{reason}. Try another page, or untick 'Respect robots.txt' "
                                  "only if the site's terms allow scraping.")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "form"]):
        tag.decompose()
    seen, texts = set(), []
    for el in soup.select(selector.strip() or DEFAULT_SELECTOR):
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        if len(t) >= min_chars and t not in seen:
            seen.add(t)
            texts.append(t)
        if len(texts) >= max_items:
            break
    return texts


# --------------------------------------------------------------------------
# UI helpers
# --------------------------------------------------------------------------
def overall_label(df):
    share = df["sentiment"].value_counts(normalize=True)
    top = share.idxmax()
    return top, float(share.max())


def render_results(df, name):
    if df.empty:
        st.info("Nothing to show yet.")
        return
    counts = df["sentiment"].value_counts().reindex(ORDER).fillna(0).astype(int)
    top, share = overall_label(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Texts analysed", len(df))
    for col, lab in zip((c2, c3, c4), ORDER):
        col.metric(f"{EMOJI[lab]} {lab.title()}", int(counts[lab]), f"{counts[lab] / len(df):.0%}", delta_color="off")
    st.markdown(f"**Overall sentiment: {EMOJI[top]} {top.title()}** ({share:.0%} of texts)")

    st.bar_chart(counts.rename("texts"))
    show = df[["text", "sentiment", "confidence"]].copy()
    show["sentiment"] = show["sentiment"].map(lambda s: f"{EMOJI.get(s, '')} {s}")
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button("Download results (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name=f"{name}_sentiment.csv", mime="text/csv", key=f"dl_{name}")


def sidebar(meta, model_file):
    st.sidebar.header("Model")
    st.sidebar.write(f"**File:** `{model_file}`")
    if meta:
        st.sidebar.write(f"**Algorithm:** {meta.get('model_name', '?')}"
                         f"{' (GridSearchCV-tuned)' if meta.get('tuned') else ''}")
        st.sidebar.metric("Test accuracy", f"{meta.get('test_accuracy', 0):.1%}")
        st.sidebar.metric("Test macro-F1", f"{meta.get('test_f1_macro', 0):.1%}")
        st.sidebar.caption(f"Trained: {meta.get('trained_at', '?')} | scikit-learn {meta.get('sklearn_version', '?')}")
        try:
            import sklearn
            if meta.get("sklearn_version") and meta["sklearn_version"] != sklearn.__version__:
                st.sidebar.warning(f"Model was trained with scikit-learn {meta['sklearn_version']} but "
                                   f"{sklearn.__version__} is installed. Re-run the notebook if you see errors.")
        except Exception:
            pass
    st.sidebar.divider()
    st.sidebar.caption("Scrape only pages you are allowed to use. The scraper checks robots.txt by default.")


# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
def tab_single(model):
    st.subheader("Analyse a single text")
    st.session_state.setdefault("single_text", "")
    cols = st.columns(len(EXAMPLES))
    for col, (label, example) in zip(cols, EXAMPLES.items()):
        col.button(f"Example: {label}", key=f"ex_{label}", use_container_width=True,
                   on_click=lambda e=example: st.session_state.update(single_text=e))
    text = st.text_area("Review / comment / headline", key="single_text", height=130,
                        placeholder="Type or paste some text...")
    if st.button("Analyse sentiment", type="primary", key="btn_single"):
        if not text.strip():
            st.warning("Please enter some text.")
            return
        res = predict_texts(model, [text]).iloc[0]
        st.markdown(f"### {EMOJI[res['sentiment']]} {res['sentiment'].title()}  ·  confidence {res['confidence']:.0%}")
        probs = pd.Series({c: res[f"p_{c}"] for c in model.classes_}).reindex(ORDER)
        st.bar_chart(probs.rename("probability"))
        if hasattr(model, "predict_proba") is False:
            st.caption("This model has no probability output; bars show a softmax of its decision scores.")


def tab_scrape(model):
    st.subheader("Scrape a web page and analyse it")
    url = st.text_input("Page URL", placeholder="https://example.com/product-reviews", key="scrape_url")
    c1, c2, c3 = st.columns([2, 1, 1])
    selector = c1.text_input("CSS selector (optional)", placeholder=f"default: {DEFAULT_SELECTOR}", key="scrape_sel",
                             help="E.g. 'div.review p' or 'span.text'. Leave empty to use paragraphs, list items, quotes and headings.")
    max_items = c2.number_input("Max texts", 1, 500, 50, key="scrape_max")
    min_chars = c3.number_input("Min characters", 1, 500, 25, key="scrape_min")
    respect = st.checkbox("Respect robots.txt", value=True, key="scrape_robots")

    if st.button("Scrape & analyse", type="primary", key="btn_scrape"):
        try:
            with st.spinner("Scraping..."):
                texts = scrape_texts(url, selector, int(max_items), int(min_chars), respect)
            if not texts:
                st.warning("No text found. Try a different CSS selector or lower the minimum characters.")
            else:
                st.session_state["scrape_df"] = predict_texts(model, texts)
        except Exception as e:
            st.error(f"Scraping failed: {e}")
    if "scrape_df" in st.session_state:
        render_results(st.session_state["scrape_df"], "scraped")

    st.divider()
    st.subheader("Live monitor (real time)")
    st.caption("Re-scrapes the same page every few seconds and tracks how the sentiment mix changes. "
               "Use the page's Stop button in the top-right corner to interrupt.")
    m1, m2 = st.columns(2)
    interval = m1.slider("Seconds between refreshes", 5, 300, 30, key="mon_interval")
    rounds = m2.slider("Number of refreshes", 2, 30, 5, key="mon_rounds")
    if st.button("Start live monitor", key="btn_monitor"):
        if not url.strip():
            st.warning("Enter a URL above first.")
            return
        history = []
        status, chart_box, table_box = st.empty(), st.empty(), st.empty()
        for i in range(int(rounds)):
            try:
                texts = scrape_texts(url, selector, int(max_items), int(min_chars), respect)
                if texts:
                    df = predict_texts(model, texts)
                    share = df["sentiment"].value_counts(normalize=True).reindex(ORDER).fillna(0) * 100
                    history.append({"time": datetime.datetime.now().strftime("%H:%M:%S"), "texts": len(df),
                                    **{k: round(v, 1) for k, v in share.items()}})
                    status.info(f"Refresh {i + 1}/{rounds} at {history[-1]['time']} - {len(df)} texts")
                    chart_box.line_chart(pd.DataFrame(history).set_index("time")[ORDER])
                    table_box.dataframe(pd.DataFrame(history), hide_index=True, use_container_width=True)
                else:
                    status.warning(f"Refresh {i + 1}/{rounds}: no text found")
            except Exception as e:
                status.error(f"Refresh {i + 1}/{rounds} failed: {e}")
            if i < int(rounds) - 1:
                time.sleep(int(interval))
        status.success("Live monitor finished.")


def tab_batch(model):
    st.subheader("Analyse a CSV file")
    up = st.file_uploader("Upload a CSV with a text column", type=["csv"], key="batch_file")
    if up is None:
        return
    try:
        data = pd.read_csv(up)
    except Exception as e:
        st.error(f"Could not read the CSV: {e}")
        return
    if data.empty:
        st.warning("The file has no rows.")
        return
    st.dataframe(data.head(), use_container_width=True, hide_index=True)
    guess = next((c for c in data.columns if str(c).lower() in ("text", "review", "comment", "content")), data.columns[0])
    col = st.selectbox("Text column", list(data.columns), index=list(data.columns).index(guess), key="batch_col")
    if st.button("Analyse file", type="primary", key="btn_batch"):
        texts = data[col].dropna().astype(str).tolist()[:5000]
        st.session_state["batch_df"] = predict_texts(model, texts)
    if "batch_df" in st.session_state:
        render_results(st.session_state["batch_df"], "batch")


def main():
    st.set_page_config(page_title="Real-Time Sentiment Analysis", page_icon="💬", layout="wide")
    st.title("💬 Real-Time Sentiment Analysis with Web Scraping")
    st.caption("Web scraping + NLP + machine learning: classify text as Positive, Neutral or Negative.")

    model, meta, model_file = load_model()
    if model is None:
        st.error("Model file not found. Run **sentiment_analysis.ipynb** first - it creates "
                 "`models/sentiment_model.joblib` next to this file - then reload this page.")
        st.stop()
    sidebar(meta, model_file)

    t1, t2, t3 = st.tabs(["✍️ Single text", "🌐 Live web scraping", "📄 Batch CSV"])
    with t1:
        tab_single(model)
    with t2:
        tab_scrape(model)
    with t3:
        tab_batch(model)


if __name__ == "__main__":
    main()

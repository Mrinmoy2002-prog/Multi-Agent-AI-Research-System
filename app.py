import re
import time
import threading
import datetime
import streamlit as st
from pipeline import run_research_pipeline

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def strip_markdown_bold_italic(text: str) -> str:
    """Remove **bold**, *italic*, __bold__, _italic_ markers."""
    if not text:
        return text
    text = re.sub(r'\*{1,3}([^*\n]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_\n]+)_{1,3}', r'\1', text)
    return text

def clean_whitespace(text: str) -> str:
    """Collapse 3+ consecutive blank lines into a single blank line."""
    if not text:
        return text
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def build_markdown_file(topic: str, report: str, feedback: str) -> str:
    """Assemble a clean markdown document for download."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    clean_report   = strip_markdown_bold_italic(report or "")
    clean_feedback = strip_markdown_bold_italic(feedback or "")
    return f"""# Research Report: {topic}

_Generated: {ts}_

---

## Report

{clean_report}

---

## Critic Feedback

{clean_feedback}
"""

def word_count(text: str) -> int:
    return len(text.split()) if text else 0

def estimate_read_time(text: str) -> str:
    wpm = 200
    mins = max(1, round(word_count(text) / wpm))
    return f"{mins} min read"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;800&display=swap');

:root {
    --bg:        #0a0a0f;
    --surface:   #111118;
    --surface2:  #16161f;
    --border:    #1e1e2e;
    --accent:    #7fff6e;
    --accent2:   #6e9fff;
    --accent3:   #ff6e9f;
    --accent4:   #ffc84f;
    --muted:     #44445a;
    --text:      #e8e8f0;
    --text-dim:  #8888a8;
    --mono:      'Space Mono', monospace;
    --sans:      'Syne', sans-serif;
    --radius:    4px;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px);
    pointer-events: none; z-index: 9999;
}

/* ── Header ── */
.site-header { border-bottom: 1px solid var(--border); padding: 2rem 0 1.6rem; margin-bottom: 2.4rem; }
.site-header h1 {
    font-family: var(--sans); font-weight: 800;
    font-size: clamp(2rem,4vw,3.2rem); letter-spacing:-.02em; line-height:1; margin:0;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 60%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.site-header p { font-family: var(--mono); font-size:.78rem; color:var(--text-dim); margin:.5rem 0 0; letter-spacing:.12em; text-transform:uppercase; }

/* ── Input card ── */
.input-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding:1.6rem 1.8rem 1.4rem;
    margin-bottom: 2rem; position:relative; overflow:hidden;
}
.input-card::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,var(--accent),var(--accent2)); }

/* ── Inputs ── */
.stTextInput > div > div > input, .stTextArea textarea {
    background: #0d0d16 !important; border:1px solid var(--border) !important;
    border-radius: var(--radius) !important; color:var(--text) !important;
    font-family: var(--mono) !important; font-size:.88rem !important; padding:.75rem 1rem !important;
}
.stTextInput > div > div > input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(127,255,110,.12) !important;
}
label, .stTextInput label, .stTextArea label {
    font-family: var(--mono) !important; font-size:.75rem !important;
    letter-spacing:.1em !important; text-transform:uppercase !important; color:var(--text-dim) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: var(--mono) !important; font-size:.82rem !important;
    letter-spacing:.12em !important; text-transform:uppercase !important;
    background: var(--accent) !important; color:#0a0a0f !important;
    border:none !important; border-radius:var(--radius) !important;
    padding:.65rem 2rem !important; font-weight:700 !important;
    transition: opacity .15s, transform .1s !important;
}
.stButton > button:hover { opacity:.88 !important; transform:translateY(-1px) !important; }
.stButton > button:active { transform:translateY(0) !important; }
.stButton > button:disabled { opacity:.3 !important; }

/* download button — different colour */
.dl-btn > button { background: var(--accent2) !important; color:#0a0a0f !important; }

/* ── Pipeline grid ── */
.pipeline-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; margin-bottom:2rem; }
.step-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:1rem 1.2rem; transition:border-color .2s;
}
.step-card.active { border-color:var(--accent); }
.step-card.done   { border-color:var(--accent2); }
.step-card.error  { border-color:var(--accent3); }
.step-num   { font-family:var(--mono); font-size:.65rem; color:var(--muted); letter-spacing:.1em; text-transform:uppercase; margin-bottom:.4rem; }
.step-label { font-family:var(--sans); font-weight:600; font-size:.9rem; color:var(--text); }
.step-status { font-family:var(--mono); font-size:.7rem; margin-top:.4rem; }
.step-status.idle    { color:var(--muted); }
.step-status.running { color:var(--accent); }
.step-status.done    { color:var(--accent2); }
.step-status.error   { color:var(--accent3); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.blink { animation: blink 1s step-end infinite; }

/* ── Stats bar ── */
.stats-bar {
    display:flex; gap:1.6rem; align-items:center;
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:.9rem 1.4rem;
    margin-bottom:1.6rem; flex-wrap:wrap;
}
.stat-item { display:flex; flex-direction:column; gap:.15rem; }
.stat-label { font-family:var(--mono); font-size:.62rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:.1em; }
.stat-value { font-family:var(--sans); font-weight:600; font-size:.95rem; color:var(--text); }
.stat-value.green  { color:var(--accent);  }
.stat-value.blue   { color:var(--accent2); }
.stat-value.yellow { color:var(--accent4); }
.stat-value.pink   { color:var(--accent3); }
.stat-sep { width:1px; height:2rem; background:var(--border); }

/* ── Result panels ── */
.result-block {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:1.4rem 1.6rem; margin-bottom:1.2rem;
}
.result-block-header {
    display:flex; align-items:center; gap:.7rem;
    margin-bottom:1rem; padding-bottom:.8rem; border-bottom:1px solid var(--border);
}
.result-block-icon {
    width:28px; height:28px; border-radius:50%;
    display:flex; align-items:center; justify-content:center; font-size:.9rem; flex-shrink:0;
}
.result-block-icon.search { background:rgba(127,255,110,.12); }
.result-block-icon.reader { background:rgba(110,159,255,.12); }
.result-block-icon.report { background:rgba(255,200,80,.12);  }
.result-block-icon.critic { background:rgba(255,110,159,.12); }
.result-block-title    { font-family:var(--sans); font-weight:600; font-size:.95rem; }
.result-block-subtitle { font-family:var(--mono); font-size:.65rem; color:var(--text-dim); letter-spacing:.08em; text-transform:uppercase; margin-left:auto; }
.result-content {
    font-family:var(--mono); font-size:.8rem; line-height:1.75; color:#b0b0cc;
    white-space:pre-wrap; word-break:break-word; max-height:320px; overflow-y:auto; padding-right:.4rem;
}
.result-content::-webkit-scrollbar { width:4px; }
.result-content::-webkit-scrollbar-thumb { background:var(--border); border-radius:2px; }

/* ── Full report section ── */
.full-report-wrapper {
    background: var(--surface2); border:1px solid var(--border);
    border-top: 3px solid var(--accent4);
    border-radius:var(--radius); padding:2rem 2.4rem 2.4rem; margin-top:2rem;
}
.report-section-title {
    font-family:var(--sans) !important; font-weight:800 !important; font-size:1.3rem !important;
    color:var(--accent4) !important; margin:0 0 1.6rem !important; letter-spacing:-.01em !important;
    border-bottom: 1px solid var(--border); padding-bottom: .8rem !important;
}
.report-md-body p, .report-md-body li, .report-md-body h1,
.report-md-body h2, .report-md-body h3, .report-md-body h4 { color: #d0d0e8; }
/* Streamlit wraps st.markdown output in its own div — target elements directly */
.full-report-wrapper h1 { font-family:var(--sans) !important; font-size:1.45rem !important; font-weight:800 !important; color:var(--text) !important; margin:1.6rem 0 .6rem !important; }
.full-report-wrapper h2 { font-family:var(--sans) !important; font-size:1.15rem !important; font-weight:700 !important; color:var(--accent2) !important; margin:1.4rem 0 .5rem !important; border-bottom:1px solid var(--border) !important; padding-bottom:.3rem !important; }
.full-report-wrapper h3 { font-family:var(--sans) !important; font-size:1rem !important; font-weight:600 !important; color:var(--accent4) !important; margin:1.1rem 0 .4rem !important; }
.full-report-wrapper h4 { font-family:var(--sans) !important; font-size:.92rem !important; font-weight:600 !important; color:var(--text-dim) !important; margin:.9rem 0 .35rem !important; }
.full-report-wrapper p  { font-family:var(--sans) !important; font-size:.93rem !important; line-height:1.85 !important; color:#c8c8e0 !important; margin:.3rem 0 .75rem !important; }
.full-report-wrapper ul,
.full-report-wrapper ol  { padding-left:1.5rem !important; margin:.3rem 0 .75rem !important; }
.full-report-wrapper li  { font-family:var(--sans) !important; font-size:.91rem !important; line-height:1.75 !important; color:#c0c0d8 !important; margin:.2rem 0 !important; }
.full-report-wrapper blockquote { border-left:3px solid var(--accent) !important; padding:.4rem .9rem !important; margin:.7rem 0 !important; color:var(--text-dim) !important; font-style:italic !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    font-family: var(--mono) !important; font-size:.78rem !important;
    color: var(--text-dim) !important; text-transform:uppercase; letter-spacing:.1em;
    background: var(--surface) !important; border:1px solid var(--border) !important;
    border-radius:var(--radius) !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important; border:1px solid var(--border) !important;
    border-top:none !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div { background:linear-gradient(90deg,var(--accent),var(--accent2)) !important; }

/* ── Misc ── */
.stAlert { border-radius:var(--radius) !important; font-family:var(--mono) !important; font-size:.82rem !important; }
hr { border-color:var(--border) !important; }
#MainMenu, footer, header { visibility:hidden; }
.block-container { padding-top:2rem !important; max-width:1160px !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-header">
    <h1>Research Engine</h1>
    <p>Autonomous · Multi-Agent · Deep-Dive Analysis</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
_defaults = dict(running=False, done=False, results=None, error=None,
                 current_step=0, active_topic=None)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Input card ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-card">', unsafe_allow_html=True)
col_inp, col_btn = st.columns([5, 1], vertical_alignment="bottom")
with col_inp:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Advances in neuromorphic computing 2025",
        disabled=st.session_state.running,
        key="topic_input",
    )
with col_btn:
    run_btn = st.button("▶  Run", disabled=st.session_state.running or not topic,
                        use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Step renderer ──────────────────────────────────────────────────────────────
STEPS = [
    ("01", "Search Agent",  "Scanning the web"),
    ("02", "Reader Agent",  "Scraping & parsing"),
    ("03", "Writer",        "Drafting report"),
    ("04", "Critic",        "Reviewing quality"),
]

def render_steps(current: int, done: bool, error: bool = False):
    cards = ""
    for i, (num, label, _) in enumerate(STEPS):
        if done:
            cls, sc, st_ = "done", "done", "✓ done"
        elif error and i == current:
            cls, sc, st_ = "error", "error", "✗ failed"
        elif i < current:
            cls, sc, st_ = "done", "done", "✓ done"
        elif i == current:
            cls, sc, st_ = "active", "running", '<span class="blink">●</span> running'
        else:
            cls, sc, st_ = "", "idle", "○ waiting"
        cards += f"""
        <div class="step-card {cls}">
            <div class="step-num">Step {num}</div>
            <div class="step-label">{label}</div>
            <div class="step-status {sc}">{st_}</div>
        </div>"""
    st.markdown(f'<div class="pipeline-grid">{cards}</div>', unsafe_allow_html=True)

# ── Trigger run ────────────────────────────────────────────────────────────────
if run_btn and topic:
    st.session_state.update(running=True, done=False, results=None,
                             error=None, current_step=0, active_topic=topic)
    st.rerun()

# ── Running state ──────────────────────────────────────────────────────────────
if st.session_state.running and not st.session_state.done:
    progress_ph = st.empty()
    steps_ph    = st.empty()

    with steps_ph:
        render_steps(0, False)
    progress_bar = progress_ph.progress(0, text="Initialising pipeline…")

    step_msgs = [
        "Step 1 — Search agent scanning the web…",
        "Step 2 — Reader agent scraping top result…",
        "Step 3 — Writer composing the report…",
        "Step 4 — Critic reviewing draft…",
    ]

    result_container: dict = {}
    error_container:  dict = {}
    _topic = st.session_state.active_topic

    def _run():
        try:
            result_container["data"] = run_research_pipeline(_topic)
        except Exception as exc:
            error_container["err"] = exc

    try:
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

        for i, msg in enumerate(step_msgs):
            st.session_state.current_step = i
            with steps_ph:
                render_steps(i, False)
            progress_bar.progress(i * 22 + 5, text=msg)
            time.sleep(0.5)

        thread.join()

        if "err" in error_container:
            raise error_container["err"]

        st.session_state.results = result_container["data"]
        st.session_state.done    = True
        st.session_state.running = False
        progress_bar.progress(100, text="Pipeline complete ✓")
        with steps_ph:
            render_steps(4, True)
        time.sleep(0.6)
        st.rerun()

    except Exception as exc:
        st.session_state.error   = str(exc)
        st.session_state.running = False
        with steps_ph:
            render_steps(st.session_state.current_step, False, error=True)
        st.rerun()

# ── Idle state ─────────────────────────────────────────────────────────────────
if not st.session_state.running and not st.session_state.done:
    render_steps(-1, False)
    if st.session_state.error:
        st.error(f"Pipeline error: {st.session_state.error}")

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.done and st.session_state.results:
    render_steps(4, True)
    r = st.session_state.results

    raw_report   = r.get("final_report", "") or ""
    raw_feedback = r.get("feedback", "")    or ""
    raw_search   = r.get("search_results", "") or ""
    raw_scraped  = r.get("scraped_website_content", "") or ""

    clean_report   = clean_whitespace(strip_markdown_bold_italic(raw_report))
    clean_feedback = clean_whitespace(strip_markdown_bold_italic(raw_feedback))

    topic_label = st.session_state.active_topic or "Research"

    # ── Stats bar ──────────────────────────────────────────────────────────────
    wc   = word_count(clean_report)
    rt   = estimate_read_time(clean_report)
    ts   = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-label">Topic</span>
            <span class="stat-value">{topic_label}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <span class="stat-label">Report Words</span>
            <span class="stat-value green">{wc:,}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <span class="stat-label">Read Time</span>
            <span class="stat-value blue">{rt}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <span class="stat-label">Generated</span>
            <span class="stat-value yellow">{ts}</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
            <span class="stat-label">Status</span>
            <span class="stat-value green">✓ Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Raw agent outputs (collapsible) ───────────────────────────────────────
    st.markdown("---")
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        with st.expander("🔍  Search Results  —  Agent 01"):
            st.markdown(f'<div class="result-content">{raw_search}</div>',
                        unsafe_allow_html=True)

        with st.expander("📄  Scraped Content  —  Agent 02"):
            st.markdown(f'<div class="result-content">{raw_scraped}</div>',
                        unsafe_allow_html=True)

    with col_right:
        with st.expander("🔬  Critic Feedback  —  Critic"):
            st.markdown(f'<div class="result-content">{clean_feedback}</div>',
                        unsafe_allow_html=True)

        with st.expander("📋  Raw Report (unformatted)"):
            st.code(clean_report, language=None)

    # ── Full report ───────────────────────────────────────────────────────────
    st.markdown('<div class="full-report-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="report-section-title">📑&nbsp;&nbsp;Final Research Report</p>', unsafe_allow_html=True)
    st.markdown('<div class="report-md-body">', unsafe_allow_html=True)
    st.markdown(clean_report)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── Actions row ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    act1, act2, act3 = st.columns([2, 2, 2])

    md_content  = build_markdown_file(topic_label, clean_report, clean_feedback)
    safe_topic  = re.sub(r'[^a-z0-9]+', '_', topic_label.lower())[:40]
    dl_filename = f"research_{safe_topic}.md"

    with act1:
        st.download_button(
            label="⬇  Download Report (.md)",
            data=md_content,
            file_name=dl_filename,
            mime="text/markdown",
            use_container_width=True,
            key="dl_md",
        )

    with act2:
        # Copy-to-clipboard via a text area (native Streamlit workaround)
        if st.button("📋  Copy Report Text", use_container_width=True, key="copy_btn"):
            st.session_state["show_copy"] = True

    with act3:
        if st.button("↺  New Research", use_container_width=True, key="reset_btn"):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()

    # Show copyable textarea when button clicked
    if st.session_state.get("show_copy"):
        st.text_area("Select all & copy ↓", value=clean_report, height=120, key="copy_area")
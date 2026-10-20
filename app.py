import time
import streamlit as st
from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Styles ───────────────────────────────────────────────────────────────────
# Type scale: 2.4 / 1.7 / 1.25 / 1.0 (body) / 0.9 (labels) / 0.85 (helper). Nothing smaller.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap');

:root {
    color-scheme: light;
    --bg: #F4F6F9;
    --surface: #FFFFFF;
    --ink: #0F1B2D;
    --muted: #5A6779;
    --line: #DFE4EB;
    --accent: #2646C8;
    --accent-dark: #1C36A0;
    --ok: #1B8556;
    --err: #C23B3B;
}

.stApp { background: var(--bg); color: var(--ink); }

.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Manrope', system-ui, sans-serif;
}
.stApp p, .stApp li, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--ink); }

/* keep Streamlit's own icon font intact */
span[data-testid="stIconMaterial"] { font-family: "Material Symbols Rounded" !important; }

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { max-width: 880px; padding: 2.8rem 1.5rem 4rem; }

/* ── Masthead ── */
.brand { font-size: 0.95rem; font-weight: 700; color: var(--accent); margin-bottom: 0.9rem; }
.masthead h1 {
    font-size: 2.4rem; font-weight: 800; line-height: 1.12;
    letter-spacing: -0.025em; margin: 0 0 0.8rem; padding: 0; max-width: 40rem;
}
.masthead p { font-size: 1.05rem; line-height: 1.6; color: var(--muted); max-width: 36rem; margin: 0 0 2rem; }

.sec { font-size: 1.25rem; font-weight: 700; margin: 2.2rem 0 0.9rem; color: var(--ink); }
.muted { font-size: 0.85rem; color: var(--muted); margin: 1rem 0 0.4rem; }

/* ── Form card ── */
div[data-testid="stForm"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 1.5rem 1.6rem 1.6rem;
    box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04);
}
div[data-testid="stTextInput"] label p { font-size: 0.9rem; font-weight: 600; color: var(--ink); }
div[data-testid="stTextInput"] input {
    background: #FBFCFD;
    border: 1.5px solid var(--line);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    font-size: 1rem;
    color: var(--ink);
}
div[data-testid="stTextInput"] input::placeholder { color: #8A96A6; }
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(38, 70, 200, 0.16);
}
div[data-testid="stTextInput"] > div, div[data-testid="stTextInput"] > div > div { border: none; background: transparent; }

/* ── Buttons: secondary (examples, download) ── */
button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    background: var(--surface);
    border: 1.5px solid var(--line);
    border-radius: 10px;
    color: var(--ink);
    font-size: 0.88rem;
    font-weight: 600;
    line-height: 1.35;
    padding: 0.5rem 0.8rem;
    text-align: left;
    transition: border-color .15s, color .15s;
}
button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--accent); color: var(--accent);
}

/* ── Buttons: primary ── */
button[kind^="primary"], button[data-testid^="stBaseButton-primary"] {
    background: var(--accent);
    border: 1.5px solid var(--accent);
    border-radius: 10px;
    color: #fff;
    font-size: 1rem;
    font-weight: 700;
    padding: 0.7rem 1.2rem;
    margin-top: 0.4rem;
    transition: background .15s;
}
button[kind^="primary"]:hover, button[data-testid^="stBaseButton-primary"]:hover {
    background: var(--accent-dark); border-color: var(--accent-dark); color: #fff;
}
.stApp button:focus-visible { outline: 3px solid rgba(38, 70, 200, 0.35); outline-offset: 2px; }

/* ── Pipeline ── */
.pipe { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; }
.pstep {
    background: var(--surface);
    border: 1px solid var(--line);
    border-top: 3px solid var(--line);
    border-radius: 12px;
    padding: 1rem 1.1rem 1.05rem;
}
.pstep.running { border-top-color: var(--accent); }
.pstep.done    { border-top-color: var(--ok); }
.pstep.failed  { border-top-color: var(--err); }
.ptitle { display: flex; align-items: center; gap: 0.55rem; font-size: 1rem; font-weight: 700; color: var(--ink); }
.pn {
    display: inline-flex; align-items: center; justify-content: center;
    width: 1.5rem; height: 1.5rem; border-radius: 50%;
    background: #EDF0F5; color: var(--muted); font-size: 0.85rem; font-weight: 700;
}
.running .pn { background: var(--accent); color: #fff; }
.done .pn    { background: var(--ok); color: #fff; }
.failed .pn  { background: var(--err); color: #fff; }
.pdesc { font-size: 0.88rem; line-height: 1.45; color: var(--muted); margin: 0.45rem 0 0.8rem; min-height: 2.6em; }
.pstat { display: inline-flex; align-items: center; gap: 0.45rem; font-size: 0.88rem; font-weight: 600; color: var(--muted); }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #B3BDCB; }
.running .pstat { color: var(--accent); } .running .dot { background: var(--accent); animation: pulse 1.2s ease-in-out infinite; }
.done .pstat    { color: var(--ok); }     .done .dot    { background: var(--ok); }
.failed .pstat  { color: var(--err); }    .failed .dot  { background: var(--err); }
@keyframes pulse { 50% { opacity: 0.3; } }

/* ── Results tabs ── */
div[data-baseweb="tab-list"] { gap: 0.4rem; border-bottom: 1px solid var(--line); }
button[data-baseweb="tab"] { padding: 0.7rem 1rem; }
button[data-baseweb="tab"] p { font-size: 0.95rem; font-weight: 600; color: var(--muted); }
button[data-baseweb="tab"][aria-selected="true"] p { color: var(--accent); }
div[data-baseweb="tab-highlight"] { background: var(--accent); height: 3px; }
div[data-baseweb="tab-border"] { display: none; }

div[role="tabpanel"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.6rem 2rem 1.8rem;
    margin-top: 0.9rem;
}
div[role="tabpanel"] p, div[role="tabpanel"] li {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.06rem; line-height: 1.75; color: var(--ink);
}
div[role="tabpanel"] h1 { font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; margin: 0.4rem 0 0.8rem; }
div[role="tabpanel"] h2 { font-size: 1.3rem; font-weight: 700; margin: 1.8rem 0 0.6rem; }
div[role="tabpanel"] h3 { font-size: 1.1rem; font-weight: 700; margin: 1.4rem 0 0.5rem; }
div[role="tabpanel"] a { color: var(--accent); }
div[role="tabpanel"] table { font-size: 0.95rem; }
div[role="tabpanel"] th, div[role="tabpanel"] td { border: 1px solid var(--line); padding: 0.5rem 0.75rem; }
div[role="tabpanel"] .topic-line { font-size: 0.9rem; color: var(--muted); margin: 0 0 0.9rem; font-family: 'Manrope', sans-serif; }

.empty {
    background: var(--surface);
    border: 1px dashed #C7CFDA;
    border-radius: 14px;
    padding: 1.8rem;
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.6;
    text-align: center;
}

.foot { font-size: 0.85rem; color: var(--muted); text-align: center; margin-top: 3.5rem; }

@media (max-width: 760px) {
    .masthead h1 { font-size: 1.9rem; }
    .pipe { grid-template-columns: repeat(2, 1fr); }
    div[role="tabpanel"] { padding: 1.2rem 1.2rem 1.4rem; }
}
@media (prefers-reduced-motion: reduce) { .dot { animation: none !important; } * { transition: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)

# ── Pipeline definition ──────────────────────────────────────────────────────
def as_text(content) -> str:
    """Agent outputs are usually strings, but some models return content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in content
        )
    return str(content)


def step_search(topic, res):
    out = build_search_agent().invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    return as_text(out["messages"][-1].content)


def step_reader(topic, res):
    out = build_reader_agent().invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{res['search'][:800]}",
                )
            ]
        }
    )
    return as_text(out["messages"][-1].content)


def step_writer(topic, res):
    research = (
        f"SEARCH RESULTS:\n{res['search']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{res['reader']}"
    )
    return as_text(writer_chain.invoke({"topic": topic, "research": research}))


def step_critic(topic, res):
    return as_text(critic_chain.invoke({"report": res["writer"]}))


STEPS = [
    ("search", "Search agent", "Finds recent sources on your topic", step_search),
    ("reader", "Reader agent", "Opens the best source and extracts detail", step_reader),
    ("writer", "Writer", "Drafts the full research report", step_writer),
    ("critic", "Critic", "Reviews and scores the draft", step_critic),
]

STATUS_LABEL = {"waiting": "Waiting", "running": "Running…", "done": "Done", "failed": "Failed"}


def pipeline_html(states: dict) -> str:
    # No indentation: Streamlit's markdown treats 4+ leading spaces as a code block.
    cards = []
    for i, (key, title, desc, _) in enumerate(STEPS, start=1):
        state = states.get(key, "waiting")
        cards.append(
            f'<div class="pstep {state}">'
            f'<div class="ptitle"><span class="pn">{i}</span>{title}</div>'
            f'<div class="pdesc">{desc}</div>'
            f'<div class="pstat"><span class="dot"></span>{STATUS_LABEL[state]}</div>'
            f"</div>"
        )
    return f'<div class="pipe">{"".join(cards)}</div>'


# ── Session state ────────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("states", {k: "waiting" for k, *_ in STEPS})
st.session_state.setdefault("run_topic", "")


def use_example(text: str):
    st.session_state.topic_input = text


# ── Masthead ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="masthead">'
    '<div class="brand">Research Assistant</div>'
    "<h1>A research report from four cooperating AI agents</h1>"
    "<p>Enter a topic. One agent searches the web, another reads the best source, "
    "a writer drafts the report, and a critic reviews it.</p>"
    "</div>",
    unsafe_allow_html=True,
)

# ── Input ────────────────────────────────────────────────────────────────────
with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        key="topic_input",
        placeholder="For example: Roadmap for AGI development in the next 5 years",
    )
    run_btn = st.form_submit_button("Run research", type="primary", use_container_width=True)

st.markdown('<div class="muted">Try an example</div>', unsafe_allow_html=True)
examples = [
    "Future of LLMs in the tech industry",
    "Latest AI agents in 2026",
    "Roadmap for AGI development in the next 5 years",
]
for col, ex in zip(st.columns(len(examples)), examples):
    col.button(ex, key=f"ex_{ex}", on_click=use_example, args=(ex,), use_container_width=True)

# ── Pipeline ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">Progress</div>', unsafe_allow_html=True)
pipe_slot = st.empty()
pipe_slot.markdown(pipeline_html(st.session_state.states), unsafe_allow_html=True)

# ── Run ──────────────────────────────────────────────────────────────────────
if run_btn:
    clean_topic = (topic or "").strip()
    if not clean_topic:
        st.warning("Enter a research topic to get started.")
    else:
        results = {}
        states = {k: "waiting" for k, *_ in STEPS}
        error = None

        for key, title, _, fn in STEPS:
            states[key] = "running"
            pipe_slot.markdown(pipeline_html(states), unsafe_allow_html=True)
            try:
                results[key] = fn(clean_topic, results)
                states[key] = "done"
            except Exception as e:
                states[key] = "failed"
                error = f"{title} failed: {e}"
                break

        pipe_slot.markdown(pipeline_html(states), unsafe_allow_html=True)
        st.session_state.results = results
        st.session_state.states = states
        st.session_state.run_topic = clean_topic

        if error:
            st.error(f"{error}. Check your API keys and try again.")

# ── Results ──────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">Results</div>', unsafe_allow_html=True)

r = st.session_state.results
tab_defs = [
    ("writer", "Report"),
    ("critic", "Critic review"),
    ("search", "Search results"),
    ("reader", "Scraped source"),
]
available = [(k, label) for k, label in tab_defs if k in r]

if not available:
    st.markdown(
        '<div class="empty">Your report, the critic review and the sources will appear here '
        "once the pipeline finishes.</div>",
        unsafe_allow_html=True,
    )
else:
    tabs = st.tabs([label for _, label in available])
    for tab, (key, _) in zip(tabs, available):
        with tab:
            if key == "writer":
                st.markdown(
                    f'<div class="topic-line">Topic: {st.session_state.run_topic}</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    "Download report (.md)",
                    data=r["writer"],
                    file_name=f"research_report_{int(time.time())}.md",
                    mime="text/markdown",
                )
            st.markdown(r[key])

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="foot">Built with LangChain and Streamlit</div>',
    unsafe_allow_html=True,
)
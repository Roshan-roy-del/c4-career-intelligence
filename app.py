import json
import time
from pathlib import Path

import streamlit as st

from engine import analyze_candidate, demo_result, extract_text_from_pdf

st.set_page_config(
    page_title="C4 — Career Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# Data
# -----------------------------
BASE = Path(__file__).parent
with open(BASE / "data" / "jobs.json", "r", encoding="utf-8") as f:
    JOBS = json.load(f)
with open(BASE / "data" / "courses.json", "r", encoding="utf-8") as f:
    COURSES = json.load(f)

# -----------------------------
# Premium UI
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #07080d;
    --panel: rgba(18, 20, 30, .78);
    --panel2: rgba(24, 27, 40, .68);
    --line: rgba(255,255,255,.09);
    --text: #f5f7fb;
    --muted: #9298aa;
    --purple: #8b5cf6;
    --cyan: #22d3ee;
    --green: #34d399;
    --orange: #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 15% 10%, rgba(139,92,246,.16), transparent 30%),
      radial-gradient(circle at 85% 15%, rgba(34,211,238,.10), transparent 28%),
      radial-gradient(circle at 50% 100%, rgba(139,92,246,.08), transparent 35%),
      var(--bg);
    color: var(--text);
}
.block-container {
    max-width: 1240px;
    padding-top: 1.4rem;
    padding-bottom: 4rem;
}
#MainMenu, footer, header {visibility: hidden;}

.brand {
    font-family:'Space Grotesk',sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -.04em;
}
.brand span { color: #a78bfa; }
.navpill {
    display:inline-block;
    padding:7px 12px;
    border:1px solid var(--line);
    border-radius:999px;
    color:#b9bfd0;
    font-size:.78rem;
    background:rgba(255,255,255,.025);
}
.hero {
    padding: 72px 0 46px;
}
.eyebrow {
    display:inline-flex;
    align-items:center;
    gap:8px;
    border:1px solid rgba(139,92,246,.25);
    background:rgba(139,92,246,.08);
    color:#c4b5fd;
    padding:7px 12px;
    border-radius:999px;
    font-size:.78rem;
    font-weight:600;
}
.hero h1 {
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(3rem,6vw,5.7rem);
    line-height:.96;
    letter-spacing:-.065em;
    margin:20px 0 20px;
}
.gradient {
    background:linear-gradient(90deg,#fff 0%,#c4b5fd 45%,#67e8f9 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero p {
    max-width:700px;
    color:#a4aabd;
    font-size:1.08rem;
    line-height:1.7;
}
.card {
    background:linear-gradient(145deg,rgba(22,24,36,.88),rgba(11,13,21,.74));
    border:1px solid var(--line);
    border-radius:22px;
    padding:24px;
    box-shadow:0 18px 60px rgba(0,0,0,.24);
}
.card-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:1rem;
    font-weight:700;
    margin-bottom:5px;
}
.muted { color:var(--muted); }
.stat {
    padding:20px;
    border-radius:18px;
    background:rgba(255,255,255,.035);
    border:1px solid var(--line);
}
.stat-value {
    font-family:'Space Grotesk',sans-serif;
    font-size:2rem;
    font-weight:700;
    letter-spacing:-.05em;
}
.stat-label { color:var(--muted); font-size:.78rem; margin-top:3px; }
.job {
    padding:20px;
    border-radius:18px;
    background:rgba(255,255,255,.025);
    border:1px solid var(--line);
    margin-bottom:12px;
}
.job-title {
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    font-size:1.02rem;
}
.score {
    font-family:'Space Grotesk',sans-serif;
    font-size:1.65rem;
    font-weight:700;
    color:#a78bfa;
}
.chip {
    display:inline-block;
    padding:6px 10px;
    border-radius:999px;
    margin:4px 5px 0 0;
    font-size:.74rem;
    border:1px solid var(--line);
    background:rgba(255,255,255,.035);
}
.chip.ok { color:#86efac; border-color:rgba(52,211,153,.2); background:rgba(52,211,153,.06); }
.chip.gap { color:#fcd34d; border-color:rgba(245,158,11,.2); background:rgba(245,158,11,.06); }
.course {
    padding:17px 18px;
    border-radius:16px;
    border:1px solid var(--line);
    background:rgba(255,255,255,.025);
    margin-bottom:10px;
}
.pathnum {
    width:30px;height:30px;border-radius:50%;
    display:inline-flex;align-items:center;justify-content:center;
    background:rgba(139,92,246,.14);
    border:1px solid rgba(139,92,246,.22);
    color:#c4b5fd;font-weight:700;font-size:.8rem;
}
.divider { height:1px; background:var(--line); margin:28px 0; }
.smallcaps {
    color:#777f93; font-size:.68rem; font-weight:700;
    letter-spacing:.14em; text-transform:uppercase;
}
.demo-badge {
    display:inline-block;
    color:#fde68a;
    background:rgba(245,158,11,.08);
    border:1px solid rgba(245,158,11,.2);
    padding:5px 9px;border-radius:999px;font-size:.7rem;
}
[data-testid="stTextArea"] textarea {
    background:rgba(7,8,13,.78) !important;
    color:#e9edf5 !important;
    border:1px solid rgba(255,255,255,.10) !important;
    border-radius:16px !important;
    padding:16px !important;
}
[data-testid="stFileUploader"] {
    background:rgba(255,255,255,.025);
    border:1px dashed rgba(255,255,255,.12);
    border-radius:16px;
}
.stButton > button {
    border-radius:12px;
    border:1px solid rgba(255,255,255,.11);
    background:linear-gradient(135deg,#8b5cf6,#6d4de6);
    color:white;
    font-weight:700;
    padding:.72rem 1.15rem;
    box-shadow:0 8px 28px rgba(109,77,230,.22);
}
.stButton > button:hover {
    border-color:rgba(255,255,255,.2);
    transform:translateY(-1px);
}
a { color:#a78bfa !important; text-decoration:none !important; }
</style>
""", unsafe_allow_html=True)

def chips(items, kind=""):
    if not items:
        return '<span class="muted">None detected</span>'
    return "".join(f'<span class="chip {kind}">{x}</span>' for x in items)

def show_nav():
    c1, c2, c3 = st.columns([5,1,1])
    with c1:
        st.markdown('<div class="brand">C<span>4</span> <span style="color:#747b8f;font-weight:500">/ Career Intelligence</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="navpill">Gemini 2.5 Flash</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="navpill">AI + Data</div>', unsafe_allow_html=True)

show_nav()

if "result" not in st.session_state:
    st.session_state.result = None
if "source_text" not in st.session_state:
    st.session_state.source_text = ""
if "demo" not in st.session_state:
    st.session_state.demo = False

# -----------------------------
# Landing / Input
# -----------------------------
if st.session_state.result is None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">✦ AI-POWERED CAREER INTELLIGENCE</div>
      <h1>Turn your skills into<br><span class="gradient">your next opportunity.</span></h1>
      <p>
        C4 reads an unstructured profile, understands your real skills,
        matches you with opportunities, exposes the gaps holding you back,
        and turns those gaps into a concrete learning path.
      </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.markdown('<div class="card"><div class="card-title">Tell C4 about yourself</div><div class="muted" style="font-size:.82rem;margin-bottom:14px">Paste a resume, profile, or simply describe yourself.</div>', unsafe_allow_html=True)
        profile = st.text_area(
            "profile",
            height=240,
            label_visibility="collapsed",
            placeholder="Example: I am a Computer Engineering student. I know C, Python and SQL. I have built small projects with Streamlit. I am interested in AI and backend development. I live in Ahmedabad.",
        )
        upload = st.file_uploader("Or upload a TXT / PDF resume", type=["txt", "pdf"], label_visibility="visible")
        if upload:
            if upload.type == "application/pdf":
                profile = extract_text_from_pdf(upload)
            else:
                profile = upload.read().decode("utf-8", errors="ignore")
            st.info("Resume loaded. You can analyze it directly.")

        a, b = st.columns([1,1])
        with a:
            analyze = st.button("✦  Analyze my profile", use_container_width=True)
        with b:
            demo = st.button("▶  Launch demo mode", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="card" style="height:100%">
          <div class="smallcaps">What happens next</div>
          <div style="height:18px"></div>
          <div style="display:flex;gap:14px;margin-bottom:22px"><span class="pathnum">01</span><div><b>Understand</b><div class="muted" style="font-size:.8rem">AI extracts skills from messy text.</div></div></div>
          <div style="display:flex;gap:14px;margin-bottom:22px"><span class="pathnum">02</span><div><b>Match</b><div class="muted" style="font-size:.8rem">Compare your skills with job requirements.</div></div></div>
          <div style="display:flex;gap:14px;margin-bottom:22px"><span class="pathnum">03</span><div><b>Expose gaps</b><div class="muted" style="font-size:.8rem">See exactly what each opportunity needs.</div></div></div>
          <div style="display:flex;gap:14px"><span class="pathnum">04</span><div><b>Build your path</b><div class="muted" style="font-size:.8rem">Get courses mapped to the missing skills.</div></div></div>
          <div class="divider"></div>
          <div class="muted" style="font-size:.78rem">One Gemini 2.5 Flash extraction call. Matching and recommendations run locally for speed.</div>
        </div>
        """, unsafe_allow_html=True)

    if analyze or demo:
        if demo:
            st.session_state.result = demo_result(JOBS, COURSES)
            st.session_state.demo = True
            st.rerun()
        if not profile or len(profile.strip()) < 20:
            st.warning("Give C4 a little more profile information first.")
        else:
            with st.status("C4 is building your career intelligence report…", expanded=True) as status:
                st.write("Reading profile")
                time.sleep(.25)
                st.write("Extracting structured skills with Gemini 2.5 Flash")
                try:
                    result = analyze_candidate(profile, JOBS, COURSES)
                    st.session_state.result = result
                    st.session_state.source_text = profile
                    st.session_state.demo = False
                    status.update(label="Analysis complete", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    status.update(label="AI request failed", state="error", expanded=True)
                    msg = str(e)
                    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                        st.error("Gemini quota is currently exhausted. Use Demo Mode for the video, or wait for the quota window to reset.")
                    else:
                        st.error(f"C4 could not complete the AI request: {e}")
                    with st.expander("Technical details"):
                        st.code(msg)

# -----------------------------
# Results dashboard
# -----------------------------
else:
    r = st.session_state.result
    profile = r["profile"]
    jobs = r["matched_jobs"]
    gaps = r["skill_gaps"]
    courses = r["recommended_courses"]

    top_score = jobs[0]["match_score"] if jobs else 0
    name = profile.get("name") or "Candidate"

    top1, top2 = st.columns([4,1])
    with top1:
        st.markdown(f"""
        <div style="padding:44px 0 25px">
          <div class="smallcaps">CAREER INTELLIGENCE REPORT</div>
          <h2 style="font-family:'Space Grotesk';font-size:2.6rem;letter-spacing:-.055em;margin:8px 0 4px">Your next move, <span class="gradient">{name.split()[0]}</span>.</h2>
          <div class="muted">AI has mapped your current skills against the available opportunity set.</div>
        </div>
        """, unsafe_allow_html=True)
    with top2:
        st.markdown('<div style="padding-top:40px;text-align:right">', unsafe_allow_html=True)
        if st.session_state.demo:
            st.markdown('<span class="demo-badge">DEMO MODE</span>', unsafe_allow_html=True)
        if st.button("← Start over"):
            st.session_state.result = None
            st.session_state.demo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [
        (f"{top_score}%", "Best job match"),
        (str(len(jobs)), "Opportunities analyzed"),
        (str(len(gaps)), "Skill gaps"),
        (str(len(courses)), "Learning resources"),
    ]
    for c, (v, lab) in zip(cols, stats):
        with c:
            st.markdown(f'<div class="stat"><div class="stat-value">{v}</div><div class="stat-label">{lab}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    left, right = st.columns([1.35,.65], gap="large")

    with left:
        st.markdown('<div class="smallcaps">TOP OPPORTUNITIES</div><div style="height:12px"></div>', unsafe_allow_html=True)
        for job in jobs:
            score = job["match_score"]
            st.markdown(f"""
            <div class="job">
              <div style="display:flex;justify-content:space-between;gap:20px">
                <div>
                  <div class="job-title">{job['title']}</div>
                  <div class="muted" style="font-size:.78rem;margin-top:3px">{job['company']} · {job['location']}</div>
                </div>
                <div class="score">{score}%</div>
              </div>
              <div style="margin-top:13px">{chips(job['matched_skills'], 'ok')}{chips(job['missing_skills'], 'gap')}</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="smallcaps">PROFILE SIGNALS</div><div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
          <div class="card-title">Detected skills</div>
          <div style="margin-top:10px">{chips(profile.get('skills', []), 'ok')}</div>
          <div class="divider"></div>
          <div class="card-title">Interests</div>
          <div style="margin-top:10px">{chips(profile.get('interests', []))}</div>
          <div class="divider"></div>
          <div class="card-title">Location</div>
          <div class="muted" style="margin-top:8px">{profile.get('location') or 'Not specified'}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    a, b = st.columns([1,1], gap="large")
    with a:
        st.markdown('<div class="smallcaps">SKILL GAPS</div><div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
          <div class="card-title">What is holding you back?</div>
          <div class="muted" style="font-size:.8rem;margin:4px 0 16px">Skills appearing in the opportunity set but not in your profile.</div>
          {chips(gaps, 'gap')}
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown('<div class="smallcaps">AI-RECOMMENDED PATH</div><div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        for i, course in enumerate(courses[:5], 1):
            url = course.get("url", "#")
            st.markdown(f"""
            <div class="course">
              <div style="display:flex;gap:12px;align-items:flex-start">
                <span class="pathnum">{i:02d}</span>
                <div style="flex:1">
                  <b>{course['title']}</b>
                  <div class="muted" style="font-size:.76rem;margin-top:3px">{course['platform']} · targets {', '.join(course['skills'])}</div>
                </div>
                <a href="{url}" target="_blank">Open ↗</a>
              </div>
            </div>
            """, unsafe_allow_html=True)
        if not courses:
            st.markdown('<div class="muted">No mapped courses found in the local catalog.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    with st.expander("See extracted profile JSON"):
        st.json(profile)

    st.markdown("""
    <div style="text-align:center;padding:28px 0;color:#686f81;font-size:.75rem">
      C4 · Career Intelligence · Gemini 2.5 Flash + deterministic skill matching
    </div>
    """, unsafe_allow_html=True)

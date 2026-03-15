import sys
if 'warnings' not in sys.modules:
    import warnings
    sys.modules['warnings'] = warnings
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import os
import io
import re
import threading
import time
from datetime import datetime
from io import BytesIO
import pytz

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE — ABSOLUTELY MUST BE FIRST LINE BEFORE ANYTHING ELSE
# CrewAI EventsBus fires the moment crewai is imported, in a background
# thread. If these keys don't exist yet it crashes with "no attribute
# raw_trace". Initialise here, before the import below.
# ══════════════════════════════════════════════════════════════════════
if "raw_trace"   not in st.session_state: st.session_state.raw_trace   = []
if "result"      not in st.session_state: st.session_state.result      = None
if "generating"  not in st.session_state: st.session_state.generating  = False

# ─── ENV FLAGS before crewai import ──────────────────────────────────
os.environ["CREWAI_TRACING_ENABLED"]  = "false"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# ─── NOW safe to import crewai ────────────────────────────────────────
from crewai import Agent, Task, Crew, LLM

# ─── PAGE CONFIG ──────────────────────────────────────────────────────
st.set_page_config(page_title="Avernixx Article Intelligence Engine", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main{max-width:1100px;margin:auto}
.stTextArea textarea{white-space:pre-wrap!important;word-wrap:break-word!important}
.output-box{background:#0f1117;border:1px solid #2e3a4e;border-radius:10px;padding:20px;
  white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word;
  font-size:.95rem;line-height:1.8;max-height:680px;overflow-y:auto}
.terminal-box{background:#0a0f0a;border:1px solid #1a3a1a;border-left:4px solid #39ff14;
  border-radius:8px;padding:16px 20px;font-family:'Courier New',Consolas,monospace;
  font-size:.80rem;color:#39ff14;white-space:pre-wrap;word-wrap:break-word;
  line-height:1.55;max-height:480px;overflow-y:auto}
.t-yellow{color:#FFD700}.t-cyan{color:#00FFFF}.t-white{color:#FFF}
.t-red{color:#FF6B6B}.t-purple{color:#CF9FFF}
.trace-header{font-size:.75rem;color:#39ff14;letter-spacing:2px;
  text-transform:uppercase;margin-bottom:4px;font-family:'Courier New',monospace}
.header-desc{background:linear-gradient(90deg,#0d1b2a,#1a2a3a);border-left:4px solid #1E88E5;
  border-radius:8px;padding:14px 20px;margin:10px 0 20px 0;font-size:.93rem;
  color:#cdd6e0;line-height:1.7}
.llm-badge{display:inline-block;padding:4px 14px;border-radius:20px;
  font-size:.78rem;font-weight:700;margin-bottom:8px}
.badge-local{background:#1b5e20;color:#69ff47;border:1px solid #69ff47}
.badge-openai{background:#0a3d62;color:#74b9ff;border:1px solid #74b9ff}
.disclaimer-bar{background:#1a1f2e;border:1px solid #f4511e44;border-radius:8px;
  padding:10px 16px;text-align:center;font-size:.78rem;color:#aaa;margin-top:8px}
</style>
""", unsafe_allow_html=True)

# ─── STDOUT INTERCEPTOR ───────────────────────────────────────────────
class StreamCapture(io.StringIO):
    def __init__(self, real_stdout):
        super().__init__()
        self.real_stdout = real_stdout
    def write(self, text):
        self.real_stdout.write(text)
        self.real_stdout.flush()
        if text and text.strip():
            st.session_state.raw_trace.append(text)
        return len(text)
    def flush(self):
        self.real_stdout.flush()

# ─── ANSI → HTML ──────────────────────────────────────────────────────
ANSI = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def to_html(lines):
    raw = ANSI.sub('', "".join(lines))
    raw = raw.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    out = []
    for line in raw.split('\n'):
        if any(k in line for k in ['Task Completed','Final Answer','✅','COMPLETE']):
            out.append(f"<span class='t-cyan'>{line}</span>")
        elif any(k in line for k in ['Task Started','Agent Started','CREW','📋','Crew Execution']):
            out.append(f"<span class='t-yellow'>{line}</span>")
        elif any(k in line for k in ['Thought:','Action:','Observation:']):
            out.append(f"<span class='t-purple'>{line}</span>")
        elif any(k in line for k in ['Error','error','Failed','❌']):
            out.append(f"<span class='t-red'>{line}</span>")
        elif any(k in line for k in ['Casey','Riley','Morgan']):
            out.append(f"<span class='t-white'>{line}</span>")
        else:
            out.append(line)
    return '\n'.join(out)

# ─── TIME ─────────────────────────────────────────────────────────────
def sg_ts():  return datetime.now(pytz.timezone("Asia/Singapore")).strftime("%d %B %Y, %I:%M %p SGT")
def sg_stamp():return datetime.now(pytz.timezone("Asia/Singapore")).strftime("%Y%m%d_%I%M%p")

# ─── HEADER ───────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;color:#1E88E5;letter-spacing:2px;'>⚡ AVERNIXX</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;color:#cdd6e0;margin-top:-10px;'>Article Intelligence Engine — Multi-Agent Content System</h3>", unsafe_allow_html=True)
st.markdown("""
<div class='header-desc'>
<b>✍️ What This Agent Does:</b><br>
A <b>Multi-Agent Content System (MAS)</b> powered by <b>CrewAI</b> — part of Avernixx's Agentic AI Deployment Strategy.
Three agents collaborate to research, write, and polish a publication-ready article on any topic:<br><br>
&nbsp;&nbsp;🔵 <b>Strategist Casey</b> — Content Planner: trends, audience, outline, SEO keywords<br>
&nbsp;&nbsp;🟢 <b>Author Riley</b> — Content Writer: crafts the full structured article<br>
&nbsp;&nbsp;🟣 <b>Editor Morgan</b> — Senior Editor: proofreads, balances, finalises for publication<br><br>
Choose <b>Ollama/Llama3 (local, free)</b> or <b>OpenAI GPT (cloud)</b> as your LLM brain.
</div>
""", unsafe_allow_html=True)

with st.expander("🗺️ How the Multi-Agent System Works", expanded=False):
    st.markdown("""
```
👤 USER INPUT → 🔴 CREW ORCHESTRATOR → 🔵 Casey (Plan) → 🟢 Riley (Write) → 🟣 Morgan (Edit)
                                                    ↓
                                        🧠 LLM BRAIN (Ollama / OpenAI)
                                                    ↓
                                        📄 Publication-Ready Article
```
    """)

with st.expander("📘 Local vs Cloud LLM", expanded=False):
    st.markdown("""
| | Ollama / Llama3 | OpenAI GPT |
|---|---|---|
| Cost | Free | Pay per token |
| Privacy | 100% local | Sent to OpenAI |
| Speed | Slower | Faster |
| Best for | Demos | Production |
    """)

# ─── LLM SELECTOR ─────────────────────────────────────────────────────
st.markdown("### 🧠 Select Your LLM")
llm_choice = st.radio(
    "Choose the AI brain:",
    ["🖥️  Local — Ollama / Llama3 (Free, Private)", "☁️  Cloud — OpenAI GPT (API Key Required)"],
    horizontal=True
)

openai_key   = None
model_choice = "gpt-3.5-turbo"
if "OpenAI" in llm_choice:
    st.markdown("<div class='llm-badge badge-openai'>☁️ OpenAI Mode</div>", unsafe_allow_html=True)
    openai_key   = st.text_input("OpenAI API Key:", type="password", placeholder="sk-...")
    model_choice = st.selectbox("GPT Model:", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"])
else:
    st.markdown("<div class='llm-badge badge-local'>🖥️ Local Ollama Mode</div>", unsafe_allow_html=True)

# ─── ARTICLE CONTROLS ─────────────────────────────────────────────────
st.markdown("### 🎯 Article Configuration")
col1, col2 = st.columns(2)
with col1:
    topic    = st.text_area("📌 Topic", value="The impact of Agentic AI on enterprise digital transformation", height=80)
    audience = st.selectbox("👥 Audience", ["C-Suite / Executive Leadership","IT & Technology Professionals",
                 "Business Analysts & Managers","General Public / Non-Technical","Students & Academics","Entrepreneurs & Startups"])
with col2:
    tone      = st.selectbox("🎨 Tone", ["Professional & Authoritative","Conversational & Engaging",
                 "Analytical & Data-Driven","Inspirational & Thought Leadership","Educational & Explanatory","Persuasive & Opinion-Led"])
    word_count= st.select_slider("📏 Word Count", options=[300,500,800,1000,1200,1500,2000], value=800)
    seo_kw    = st.text_input("🔍 SEO Keywords (optional)", placeholder="e.g. agentic AI, enterprise automation")

# ─── BUTTONS ──────────────────────────────────────────────────────────
c1, c2 = st.columns([2,1])
with c1: generate_btn = st.button("✍️ Generate Article", use_container_width=True, type="primary")
with c2: reset_btn    = st.button("🔄 Reset / New Article", use_container_width=True)

if reset_btn:
    st.session_state.result    = None
    st.session_state.raw_trace = []
    st.session_state.generating= False
    st.rerun()

# ─── TRACE SLOT ───────────────────────────────────────────────────────
trace_slot   = st.empty()
spinner_slot = st.empty()

def render_trace():
    if st.session_state.raw_trace:
        label = "▶ LIVE AGENT TERMINAL" if st.session_state.generating else "▶ AGENT LOG — COMPLETE"
        trace_slot.markdown(
            f"<div class='trace-header'>{label}</div>"
            f"<div class='terminal-box'>{to_html(st.session_state.raw_trace)}</div>",
            unsafe_allow_html=True)

# ─── GENERATE ─────────────────────────────────────────────────────────
if generate_btn and topic.strip():

    if "OpenAI" in llm_choice and not openai_key:
        st.error("❌ Please enter your OpenAI API key."); st.stop()

    st.session_state.result    = None
    st.session_state.raw_trace = []
    st.session_state.generating= True

    llm_label = f"OpenAI/{model_choice}" if "OpenAI" in llm_choice else "Ollama/Llama3"
    seo_note  = f"Prioritise SEO keywords: {seo_kw}." if seo_kw.strip() else "Auto-identify best SEO keywords."

    st.session_state.raw_trace.append(
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║    AVERNIXX ARTICLE INTELLIGENCE ENGINE — INITIALISING      ║\n"
        f"║    Topic:    {topic[:50]:<50}║\n"
        f"║    Tone:     {tone[:50]:<50}║\n"
        f"║    Audience: {audience[:50]:<50}║\n"
        f"║    Words:    {str(word_count):<50}║\n"
        f"║    LLM:      {llm_label[:50]:<50}║\n"
        "╚══════════════════════════════════════════════════════════════╝\n\n"
        "[CREW]  Assembling: Strategist Casey · Author Riley · Editor Morgan\n"
        "[CREW]  Sequential execution — tasks delegated in order\n"
        "──────────────────────────────────────────────────────────────\n\n"
    )
    render_trace()

    real_stdout = sys.stdout
    sys.stdout  = StreamCapture(real_stdout)

    result_holder = {}
    error_holder  = {}

    def run_crew():
        try:
            # ── Build LLM inside thread ──
            if "OpenAI" in llm_choice and openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
                llm = LLM(model=model_choice)
            else:
                llm = LLM(model="ollama/llama3", base_url="http://localhost:11434")

            # ── Build agents inside thread ──
            casey = Agent(
                role="Strategist Casey — Content Planning & Research Lead",
                goal=f"Plan a compelling SEO-optimised content strategy for: {topic}",
                backstory="Senior Content Strategist at Avernixx. Plans content strategies for Fortune 500 brands and enterprise AI publications. Expert in SEO architecture and audience analysis.",
                allow_delegation=False, verbose=True, llm=llm)

            riley = Agent(
                role="Author Riley — Senior Content Writer",
                goal=f"Write a compelling well-structured article on: {topic}",
                backstory="Principal Content Writer at Avernixx. Background in technology journalism and enterprise communications. Known for sharp prose and strong narrative structure.",
                allow_delegation=False, verbose=True, llm=llm)

            morgan = Agent(
                role="Editor Morgan — Senior Editorial & Publishing Lead",
                goal="Edit and finalise the article to publication-ready standard",
                backstory="Lead Editor at Avernixx with 12 years of editorial experience in enterprise technology and business media. Ensures every piece meets journalistic best practices.",
                allow_delegation=False, verbose=True, llm=llm)

            t1 = Task(
                description=(
                    f"You are Strategist Casey at Avernixx.\n"
                    f"Research and plan a content strategy for: '{topic}'.\n"
                    f"Include: (1) Latest trends, (2) Audience analysis for {audience}, "
                    f"(3) Full outline with 4-6 sections, (4) {seo_note}, "
                    f"(5) Credibility sources, (6) Tone guidance: {tone}"
                ),
                expected_output="Comprehensive content plan: audience analysis, outline, SEO keywords, sources.",
                agent=casey)

            t2 = Task(
                description=(
                    f"You are Author Riley at Avernixx.\n"
                    f"Write a complete ~{word_count} word article on '{topic}'.\n"
                    f"Tone: {tone} | Audience: {audience}\n"
                    f"Use Casey's plan. 2-3 paragraphs per section. Markdown format."
                ),
                expected_output=f"Complete ~{word_count} word article in Markdown.",
                agent=riley)

            t3 = Task(
                description=(
                    f"You are Editor Morgan at Avernixx.\n"
                    f"Proofread and finalise Riley's article on '{topic}'.\n"
                    f"Check: grammar, tone ({tone}), audience fit ({audience}), "
                    f"balanced viewpoints, SEO integration. Return clean Markdown."
                ),
                expected_output="Polished publication-ready article in Markdown.",
                agent=morgan)

            crew = Crew(agents=[casey, riley, morgan], tasks=[t1, t2, t3], verbose=True)
            result_holder["output"] = str(crew.kickoff())
        except Exception as e:
            error_holder["error"] = str(e)

    thread = threading.Thread(target=run_crew, daemon=True)
    thread.start()

    while thread.is_alive():
        render_trace()
        spinner_slot.info("✍️ Agents are working — watch the live trace above. 1–3 min on local LLM.")
        time.sleep(1.5)
        st.rerun()

    sys.stdout = real_stdout

    st.session_state.raw_trace.append(
        "\n──────────────────────────────────────────────────────────────\n"
        f"[CREW]  ✅  ARTICLE COMPLETE\n"
        f"[CREW]  Timestamp: {sg_ts()}\n"
    )
    st.session_state.generating = False
    spinner_slot.empty()

    if "error" in error_holder:
        st.error(f"❌ {error_holder['error']}")
    else:
        st.session_state.result = result_holder.get("output","")

    render_trace()

# ─── PERSISTENT TRACE ─────────────────────────────────────────────────
if st.session_state.raw_trace and not st.session_state.generating and not generate_btn:
    render_trace()

# ─── OUTPUT ───────────────────────────────────────────────────────────
if st.session_state.result:
    st.markdown("---")
    st.markdown("### 📄 Your Generated Article")
    st.markdown(f"<div class='output-box'>{st.session_state.result.replace('<','&lt;').replace('>','&gt;')}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 Download Your Article")

    stamp      = sg_stamp()
    ts_label   = sg_ts()
    topic_slug = topic[:40].replace(" ","_").replace("/","_")
    header     = f"# Article: {topic}\nGenerated: {ts_label}\nTone: {tone} | Audience: {audience} | Words: ~{word_count}\n\n---\n\n"
    full_md    = header + st.session_state.result

    ca, cb, cc = st.columns(3)
    with ca:
        st.download_button("📄 Markdown (.md)", data=full_md,
            file_name=f"Avernixx_Article_{topic_slug}_{stamp}.md", mime="text/markdown", use_container_width=True)
    with cb:
        st.download_button("📝 Text (.txt)", data=full_md,
            file_name=f"Avernixx_Article_{topic_slug}_{stamp}.txt", mime="text/plain", use_container_width=True)
    with cc:
        try:
            from docx import Document as D
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            doc = D()
            h = doc.add_heading("Avernixx Article Intelligence Engine", 0)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for line in [f"Topic: {topic}", f"Generated: {ts_label}", f"Tone: {tone} | Audience: {audience} | ~{word_count} words"]:
                p = doc.add_paragraph(line); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.runs[0].font.size = Pt(10); p.runs[0].font.color.rgb = RGBColor(0x66,0x66,0x66)
            doc.add_paragraph()
            for line in st.session_state.result.split("\n"):
                line = line.strip()
                if   line.startswith("### "): doc.add_heading(line[4:], level=3)
                elif line.startswith("## "):  doc.add_heading(line[3:], level=2)
                elif line.startswith("# "):   doc.add_heading(line[2:], level=1)
                elif line.startswith(("- ","* ")): doc.add_paragraph(line[2:], style="List Bullet")
                elif line == "---": doc.add_paragraph("─"*60)
                elif line: doc.add_paragraph(line)
            doc.add_paragraph()
            fp = doc.add_paragraph("⚠️ Generated by Avernixx Article Intelligence Engine. Demo purposes only.")
            fp.runs[0].font.size = Pt(8); fp.runs[0].font.color.rgb = RGBColor(0x99,0x99,0x99)
            buf = BytesIO(); doc.save(buf); buf.seek(0)
            st.download_button("📘 Word (.docx)", data=buf,
                file_name=f"Avernixx_Article_{topic_slug}_{stamp}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True)
        except ImportError:
            st.warning("Run: pip install python-docx")

    st.markdown(f"<div style='text-align:center;color:#666;font-size:.8rem;margin-top:6px;'>Timestamped: {ts_label}</div>", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<hr>
<div style='text-align:center;color:gray;font-size:.85rem;'>
© 2026 Avernixx Pte. Ltd. | <a href='http://www.avernixx.com' style='color:#1E88E5;'>www.avernixx.com</a>
</div>
<div class='disclaimer-bar'>
⚠️ <b>DEMO DISCLAIMER:</b> AI-generated content for exploratory and educational purposes only.
Always review before publication. Avernixx Pte. Ltd. accepts no liability for published content.
</div>
""", unsafe_allow_html=True)

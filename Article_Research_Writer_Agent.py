#!/usr/bin/env python
# coding: utf-8

################################################################################################################################
## ORGANISATION:  Avernixx Pte. Ltd.
## PROJECT:       Article Intelligence Engine
## MODULE:        Multi-Agent Content System — Research, Write & Publish
## Agent Name:    The Avernixx Article Intelligence Engine
## Agent Type:    Multi-Agent System (MAS)
## USE CASE:      Autonomous Content Pipeline: Topic → Research Plan → Draft → Edited Article
## LLM Support:   Ollama / Llama3 (local) OR OpenAI GPT (cloud)
## Author:        Avernixx Pte. Ltd. | www.avernixx.com
## © 2026 Avernixx Pte. Ltd. All Rights Reserved.
################################################################################################################################

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Environment Setup & Safety Patch
# ─────────────────────────────────────────────────────────────────────────────
# Fix for Python 3.13 'KeyError: warnings' compatibility issue

import sys
if 'warnings' not in sys.modules:
    import warnings
    sys.modules['warnings'] = warnings

import warnings
warnings.filterwarnings('ignore')

import os

# Disable CrewAI telemetry and tracing prompts
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

print("✅ Section 1: Environment ready.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Import Libraries
# ─────────────────────────────────────────────────────────────────────────────
# Install if needed:
#   pip install crewai crewai_tools langchain_community litellm
#
# For OpenAI mode:
#   pip install openai
#
# For local LLM mode:
#   Install Ollama from https://ollama.com/download
#   Then run: ollama pull llama3

from crewai import Agent, Task, Crew, LLM

print("✅ Section 2: Libraries imported.")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: LLM Configuration
# ─────────────────────────────────────────────────────────────────────────────
# Choose ONE of the two options below.
# Comment out the one you are NOT using.

# ── OPTION A: Local LLM via Ollama (Free, Private, No API Key Required) ──────
# Requires: Ollama installed + llama3 model pulled
# Verify Ollama is running at: http://localhost:11434

llm = LLM(model="ollama/llama3", base_url="http://localhost:11434")
print("✅ Section 3: LLM configured — Ollama / Llama3 (Local Mode)")

# ── OPTION B: OpenAI GPT (Cloud, Requires API Key) ───────────────────────────
# Uncomment the lines below and comment out Option A above.
# Get your API key from: https://platform.openai.com/api-keys
# NEVER commit your API key to GitHub.

# os.environ["OPENAI_API_KEY"] = "sk-your-key-here"   # ← replace with your key
# os.environ["OPENAI_MODEL_NAME"] = "gpt-3.5-turbo"   # or "gpt-4", "gpt-4-turbo"
# llm = LLM(model="gpt-3.5-turbo")
# print("✅ Section 3: LLM configured — OpenAI GPT (Cloud Mode)")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Article Configuration
# ─────────────────────────────────────────────────────────────────────────────
# Edit these variables to control the article output.

TOPIC       = "The impact of Agentic AI on enterprise digital transformation"
TONE        = "Professional & Authoritative"   # Options: Professional & Authoritative |
                                                #          Conversational & Engaging |
                                                #          Analytical & Data-Driven |
                                                #          Inspirational & Thought Leadership |
                                                #          Educational & Explanatory |
                                                #          Persuasive & Opinion-Led
AUDIENCE    = "C-Suite / Executive Leadership" # Options: C-Suite / Executive Leadership |
                                                #          IT & Technology Professionals |
                                                #          Business Analysts & Managers |
                                                #          General Public / Non-Technical |
                                                #          Students & Academics |
                                                #          Entrepreneurs & Startups
WORD_COUNT  = 800                              # Target word count (300–2000 recommended)
SEO_KEYWORDS = "agentic AI, enterprise automation, LLM deployment, AI strategy"
               # Leave as empty string "" to let agents auto-identify keywords

print(f"✅ Section 4: Article configured.")
print(f"   Topic:    {TOPIC}")
print(f"   Tone:     {TONE}")
print(f"   Audience: {AUDIENCE}")
print(f"   Words:    ~{WORD_COUNT}")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Define the Avernixx Agent Team
# ─────────────────────────────────────────────────────────────────────────────
# Three specialised agents collaborate sequentially:
#   Strategist Casey → Author Riley → Editor Morgan
#
# Key design principle: LLMs perform significantly better when role-playing
# a specific persona with a defined goal and backstory.

# ── AGENT 1: Strategist Casey — Content Planning & Research Lead ─────────────
casey = Agent(
    role="Strategist Casey — Content Planning & Research Lead",
    goal=f"Plan a compelling, SEO-optimised content strategy for an article on: {TOPIC}",
    backstory=(
        "Senior Content Strategist at Avernixx with expertise in digital publishing, "
        "SEO architecture, and audience analysis. Casey has planned content strategies "
        "for Fortune 500 brands and enterprise AI publications. Known for turning complex "
        "topics into structured, audience-targeted content blueprints that drive engagement "
        "and search visibility."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# ── AGENT 2: Author Riley — Senior Content Writer ────────────────────────────
riley = Agent(
    role="Author Riley — Senior Content Writer",
    goal=f"Write a compelling, well-structured article on: {TOPIC}",
    backstory=(
        "Principal Content Writer at Avernixx with a background in technology journalism "
        "and enterprise communications. Riley has written for leading AI and business "
        "publications, specialising in making technical topics accessible and engaging "
        "for diverse audiences. Known for sharp prose, strong narrative structure, and "
        "the ability to balance factual rigour with reader-friendly storytelling."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# ── AGENT 3: Editor Morgan — Senior Editorial & Publishing Lead ───────────────
morgan = Agent(
    role="Editor Morgan — Senior Editorial & Publishing Lead",
    goal="Edit and finalise the article to publication-ready standard",
    backstory=(
        "Lead Editor at Avernixx with 12 years of editorial experience across "
        "enterprise technology, AI, and business media. Morgan ensures every piece "
        "meets journalistic best practices, maintains balanced viewpoints, aligns "
        "with brand voice, and is polished for immediate publication. Known for "
        "elevating good writing into exceptional content."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

print("✅ Section 5: Avernixx agent team assembled.")
print("   🔵 Strategist Casey — Content Planning & Research Lead")
print("   🟢 Author Riley     — Senior Content Writer")
print("   🟣 Editor Morgan    — Senior Editorial & Publishing Lead")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: Define Tasks
# ─────────────────────────────────────────────────────────────────────────────
# Tasks are executed sequentially. Each agent receives the output of the
# previous agent as context — this is the core of the MAS pipeline.

seo_note = (
    f"Prioritise these SEO keywords: {SEO_KEYWORDS}."
    if SEO_KEYWORDS.strip()
    else "Identify the most relevant SEO keywords for this topic."
)

# ── TASK 1: Research & Content Planning (Strategist Casey) ───────────────────
plan = Task(
    description=(
        f"You are Strategist Casey, Content Planning Lead at Avernixx.\n"
        f"Research and plan a content strategy for an article on: '{TOPIC}'.\n\n"
        f"Your plan must include:\n"
        f"1. Latest trends and key developments on this topic\n"
        f"2. Target audience analysis — interests, pain points, and knowledge level\n"
        f"   (Target audience: {AUDIENCE})\n"
        f"3. A detailed content outline: introduction, 4-6 key sections, conclusion, call to action\n"
        f"4. {seo_note}\n"
        f"5. Recommended sources, data points, or references to strengthen credibility\n"
        f"6. Tone guidance for the writer (Tone: {TONE})"
    ),
    expected_output=(
        "A comprehensive content plan including: audience analysis, full article outline, "
        "SEO keywords, tone guidance, and recommended sources."
    ),
    agent=casey,
)

# ── TASK 2: Write the Article (Author Riley) ─────────────────────────────────
write = Task(
    description=(
        f"You are Author Riley, Senior Content Writer at Avernixx.\n"
        f"Using Strategist Casey's content plan, write a complete article on: '{TOPIC}'.\n\n"
        f"Requirements:\n"
        f"1. Target word count: approximately {WORD_COUNT} words\n"
        f"2. Tone: {TONE}\n"
        f"3. Audience: {AUDIENCE}\n"
        f"4. Incorporate SEO keywords naturally — never forced\n"
        f"5. Structure: engaging introduction, well-named section headings, "
        f"   2-3 paragraphs per section, strong conclusion\n"
        f"6. Clearly distinguish between facts and opinions\n"
        f"7. Write in Markdown format"
    ),
    expected_output=(
        f"A complete, well-structured article of approximately {WORD_COUNT} words "
        f"in Markdown format, ready for editorial review."
    ),
    agent=riley,
)

# ── TASK 3: Editorial Review & Final Polish (Editor Morgan) ──────────────────
edit = Task(
    description=(
        f"You are Editor Morgan, Senior Editorial Lead at Avernixx.\n"
        f"Review and finalise Author Riley's article on: '{TOPIC}'.\n\n"
        f"Editorial tasks:\n"
        f"1. Proofread for grammatical errors, typos, and inconsistencies\n"
        f"2. Ensure tone consistency throughout ({TONE})\n"
        f"3. Verify the article is appropriate for the target audience: {AUDIENCE}\n"
        f"4. Ensure balanced viewpoints — soften any one-sided assertions\n"
        f"5. Confirm SEO keywords are naturally integrated\n"
        f"6. Sharpen the introduction and conclusion if needed\n"
        f"7. Return the final article in clean Markdown format"
    ),
    expected_output=(
        "A polished, publication-ready article in Markdown format "
        "with all editorial improvements applied."
    ),
    agent=morgan
)

print("✅ Section 6: Tasks defined.")
print("   📋 Task 1 — Research & Content Planning  → Strategist Casey")
print("   📋 Task 2 — Write the Article            → Author Riley")
print("   📋 Task 3 — Editorial Review & Polish    → Editor Morgan")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: Assemble & Launch the Crew
# ─────────────────────────────────────────────────────────────────────────────
# The Crew orchestrates all agents and tasks.
# verbose=True shows the full agent communication trace in the terminal.
# Tasks run sequentially — order in the list matters.

article_crew = Crew(
    agents=[casey, riley, morgan],
    tasks=[plan, write, edit],
    verbose=True
)

print("\n🚀 Launching the Avernixx Article Intelligence Engine...")
print("=" * 70)
print(f"Topic:    {TOPIC}")
print(f"Tone:     {TONE}")
print(f"Audience: {AUDIENCE}")
print(f"Words:    ~{WORD_COUNT}")
print("=" * 70)
print("Watch the agents collaborate below ↓\n")

result = article_crew.kickoff()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8: Display Output
# ─────────────────────────────────────────────────────────────────────────────
# If running in Jupyter, this renders the Markdown beautifully.
# If running in terminal, the raw Markdown text is printed.

print("\n" + "=" * 70)
print("✅ ARTICLE COMPLETE — Avernixx Article Intelligence Engine")
print("=" * 70 + "\n")

try:
    from IPython.display import Markdown, display
    display(Markdown(str(result)))
except ImportError:
    # Running in terminal — print raw output
    print(str(result))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9: Try Your Own Topic
# ─────────────────────────────────────────────────────────────────────────────
# Uncomment and edit the block below to run the engine on a custom topic
# without changing the main configuration above.

# CUSTOM_TOPIC = "YOUR TOPIC HERE"
#
# custom_plan = Task(
#     description=(
#         f"Research and plan a content strategy for: '{CUSTOM_TOPIC}'.\n"
#         f"Audience: {AUDIENCE} | Tone: {TONE}"
#     ),
#     expected_output="A comprehensive content plan with outline, SEO keywords, and sources.",
#     agent=casey
# )
# custom_write = Task(
#     description=f"Write a ~{WORD_COUNT} word article on '{CUSTOM_TOPIC}' in Markdown. Tone: {TONE}.",
#     expected_output=f"Complete article ~{WORD_COUNT} words in Markdown.",
#     agent=riley
# )
# custom_edit = Task(
#     description=f"Proofread and finalise the article on '{CUSTOM_TOPIC}' for publication.",
#     expected_output="Polished, publication-ready article in Markdown.",
#     agent=morgan
# )
# custom_crew = Crew(agents=[casey, riley, morgan], tasks=[custom_plan, custom_write, custom_edit], verbose=True)
# custom_result = custom_crew.kickoff()
# print(str(custom_result))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10: Launch the Streamlit UI (Recommended for Demos)
# ─────────────────────────────────────────────────────────────────────────────
# This script is the core agent logic.
# For the full interactive UI with live trace, LLM selector, tone controls,
# and multi-format downloads, launch the Streamlit app instead:
#
#   python -m streamlit run article_app.py --server.port 8501
#
# Then open: http://localhost:8501
#
# ─────────────────────────────────────────────────────────────────────────────
# OTHER SUPPORTED LLM PROVIDERS
# ─────────────────────────────────────────────────────────────────────────────
#
# Mistral API:
#   os.environ["OPENAI_API_KEY"]    = "your-mistral-api-key"
#   os.environ["OPENAI_API_BASE"]   = "https://api.mistral.ai/v1"
#   os.environ["OPENAI_MODEL_NAME"] = "mistral-small"
#
# Hugging Face:
#   from langchain_community.llms import HuggingFaceHub
#   llm = HuggingFaceHub(repo_id="HuggingFaceH4/zephyr-7b-beta",
#                        huggingfacehub_api_token="<HF_TOKEN>",
#                        task="text-generation")
#
# Cohere:
#   from langchain_community.chat_models import ChatCohere
#   os.environ["COHERE_API_KEY"] = "your-cohere-api-key"
#   llm = ChatCohere()
#
# For full LLM connection docs:
#   https://docs.crewai.com/how-to/LLM-Connections/
#
################################################################################################################################
## © 2026 Avernixx Pte. Ltd. All Rights Reserved. | www.avernixx.com
################################################################################################################################

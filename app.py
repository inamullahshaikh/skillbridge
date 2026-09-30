"""
SkillBridge: see how your resume matches a job, then get a week-by-week plan to close the gap.

Open-source stack: Gradio (UI), fastembed + BAAI/bge-small-en-v1.5 (semantic matching),
pypdf / python-docx (parsing), an open-weights LLM such as Llama 3.3 for the coach.
"""
import hmac
import os
import re
import shutil
import tempfile
import time
from pathlib import Path

import gradio as gr

import coach
import embedder
from engine import build_plan, extract_text, match, to_markdown
from render import empty_state, plan_view, score_view, skills_view
from samples import JOBS, RESUMES

DEMO_USER = os.getenv("DEMO_USERNAME", "demo")
DEMO_PASS = os.getenv("DEMO_PASSWORD", "SkillBridge2026")
MAX_CHARS = 30_000
HERE = Path(__file__).parent

embedder.start()

BRIDGE_SVG = """<svg viewBox="0 0 64 32" aria-hidden="true" class="sb-glyph">
<path d="M3 24 Q32 -4 61 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
<line x1="3" y1="24" x2="61" y2="24" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>
<g stroke="currentColor" stroke-width="2"><line x1="17" y1="24" x2="17" y2="13"/><line x1="32" y1="24" x2="32" y2="10"/>
<line x1="47" y1="24" x2="47" y2="13"/></g></svg>"""

LOGIN_HEAD = f"""<div class="sb-login-head">
  <div class="sb-brand">{BRIDGE_SVG}<span>SkillBridge</span></div>
  <p>See how your resume matches a job, and get a week-by-week plan to close the gap.</p>
</div>"""

LOGIN_FOOT = """<p class="sb-login-foot">Demo access. Nothing you upload is saved to a database, and temporary files are deleted within an hour.</p>"""

TOPBAR = f"""<div class="sb-top"><div class="sb-brand">{BRIDGE_SVG}<span>SkillBridge</span></div>
<p class="sb-tagline">Match your resume to a job. Close the gap week by week.</p></div>"""

FOOTER = """<footer class="sb-footer">Built with open-source tools: Gradio, BGE-small embeddings via fastembed,
pypdf, python-docx, and an open-weights LLM for the coach. Scores and hours are estimates to guide you, not guarantees.</footer>"""

COACH_INTRO = ("The coach reads your analysis, resume and the job, then writes an honest take, sharper resume bullets, "
               "a portfolio project and interview questions. It won't invent experience you don't have. "
               + ("Your resume and the job text are sent to the model provider to write the notes."
                  if coach.provider_label().find("Rule-based") < 0 else ""))


# ------------------------------------------------------------------ handlers
def _need_login(ok):
    if not ok:
        raise gr.Error("Your session ended. Sign in again to continue.")


def sign_in(username, password):
    good = (hmac.compare_digest((username or "").strip().encode(), DEMO_USER.encode())
            and hmac.compare_digest((password or "").encode(), DEMO_PASS.encode()))
    if good:
        return True, gr.update(visible=False), gr.update(visible=True), gr.update(value="", visible=False), ""
    return (False, gr.update(visible=True), gr.update(visible=False),
            gr.update(value="That username and password don't match. Check the demo credentials and try again.",
                      visible=True), "")


def sign_out():
    return (False, None, gr.update(visible=True), gr.update(visible=False), "", "",
            gr.update(visible=True), gr.update(visible=False))


def on_upload(ok, path):
    _need_login(ok)
    if not path:
        return gr.update()
    try:
        text = extract_text(path)
    except Exception:
        raise gr.Error("Couldn't read that file. Upload a PDF, DOCX or TXT, or paste the text instead.")
    if len(text.strip()) < 50:
        raise gr.Error("That file has almost no readable text, so it may be a scanned image. Paste the text instead.")
    return re.sub(r"\n{3,}", "\n\n", text.strip())[:MAX_CHARS]


def pick_resume(ok, name):
    _need_login(ok)
    return RESUMES.get(name, gr.update()) if name else gr.update()


def pick_job(ok, name):
    _need_login(ok)
    return JOBS.get(name, gr.update()) if name else gr.update()


REPORT_DIR = Path(tempfile.gettempdir()) / "skillbridge_reports"


def _write_report(a, plan, coach_md=None, coach_label=None):
    REPORT_DIR.mkdir(exist_ok=True)
    now = time.time()
    for old in REPORT_DIR.glob("*/*.md"):  # keep nothing older than an hour
        if now - old.stat().st_mtime > 3600:
            shutil.rmtree(old.parent, ignore_errors=True)
    slug = re.sub(r"[^a-z0-9]+", "-", a["title"].lower()).strip("-")[:40] or "role"
    d = tempfile.mkdtemp(prefix="r_", dir=REPORT_DIR)
    path = os.path.join(d, f"skillbridge-{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_markdown(a, plan, coach_md, coach_label))
    return path


def analyze(ok, resume_text, jd_text, hours):
    _need_login(ok)
    resume_text = (resume_text or "").strip()
    jd_text = (jd_text or "").strip()
    if len(resume_text) < 50:
        raise gr.Error("Add a resume first: upload a file, paste the text, or load a sample.")
    if len(jd_text) < 50:
        raise gr.Error("Paste the job description, including its requirements section.")
    resume_text, jd_text = resume_text[:MAX_CHARS], jd_text[:MAX_CHARS]
    a = match(resume_text, jd_text, embedder=embedder.get(wait=20))
    if not a["reqs"]:
        raise gr.Error("No skills recognised in that job description. SkillBridge covers tech, data and AI roles; "
                       "paste the full posting, including its requirements.")
    plan = build_plan(a, hours)
    session = dict(a=a, resume=resume_text, jd=jd_text, coach=None, coach_label=None)
    return (session, score_view(a, plan), skills_view(a), plan_view(plan),
            gr.update(value=_write_report(a, plan), visible=True), "",
            gr.update(visible=True), gr.update(visible=False))


def replan(ok, session, hours):
    if not ok or not session:
        return gr.update(), gr.update(), gr.update()
    plan = build_plan(session["a"], hours)
    return (score_view(session["a"], plan), plan_view(plan),
            gr.update(value=_write_report(session["a"], plan, session["coach"], session["coach_label"])))


def run_coach(ok, session, hours):
    _need_login(ok)
    if not session:
        raise gr.Error("Run Analyze match first, then ask the coach.")
    plan = build_plan(session["a"], hours)
    md, label, err = coach.coach(session["a"], plan, session["resume"], session["jd"])
    session = dict(session, coach=md, coach_label=label)
    shown = f"{md}\n\n---\n<small>Written by {label}.</small>"
    if err:
        gr.Warning("The AI model didn't respond, so the rule-based coach answered instead.")
    return session, shown, gr.update(value=_write_report(session["a"], plan, md, label))


# ------------------------------------------------------------------ UI
teal = gr.themes.Color(c50="#E6F3F4", c100="#C5E4E6", c200="#9CD0D4", c300="#6BB8BE", c400="#3E9FA7",
                       c500="#0E7C86", c600="#0B6A73", c700="#09565E", c800="#07434A", c900="#053036",
                       c950="#03252A", name="sb_teal")
theme = gr.themes.Base(
    primary_hue=teal, secondary_hue=teal, neutral_hue=gr.themes.colors.slate,
    radius_size=gr.themes.sizes.radius_sm,
    font=[gr.themes.GoogleFont("Public Sans"), "system-ui", "sans-serif"],
).set(
    body_background_fill="#F4F7F8", body_background_fill_dark="#0D171C",
    block_background_fill="#FFFFFF", block_background_fill_dark="#122026",
    block_border_color="#D8E0E4", block_border_color_dark="#243740",
    button_primary_background_fill="#0E7C86", button_primary_background_fill_hover="#0B6A73",
    button_primary_background_fill_dark="#3E9FA7", button_primary_background_fill_hover_dark="#6BB8BE",
    button_primary_text_color="#FFFFFF", button_primary_text_color_dark="#06191C",
)

HEAD = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&display=swap" rel="stylesheet">')

with gr.Blocks(title="SkillBridge", delete_cache=(1800, 3600)) as demo:
    ok = gr.State(False)
    session = gr.State(None)

    with gr.Column(visible=True, elem_id="sb-login") as login_col:
        gr.HTML(LOGIN_HEAD)
        username = gr.Textbox(label="Username", autofocus=True, max_lines=1)
        password = gr.Textbox(label="Password", type="password", max_lines=1)
        login_error = gr.Markdown(visible=False, elem_classes="sb-error")
        login_btn = gr.Button("Sign in", variant="primary")
        gr.HTML(LOGIN_FOOT)

    with gr.Column(visible=False, elem_id="sb-app") as app_col:
        with gr.Row(elem_id="sb-topbar", equal_height=True):
            gr.HTML(TOPBAR)
            logout_btn = gr.Button("Sign out", size="sm", variant="secondary", scale=0, min_width=100)
        with gr.Row(equal_height=False):
            with gr.Column(scale=5, min_width=320, elem_id="sb-inputs"):
                gr.HTML('<h3 class="sb-step"><span>1</span>Your resume</h3>')
                sample_resume = gr.Dropdown(choices=list(RESUMES), value=None, label="Load a sample resume",
                                            info="Or upload / paste your own below")
                upload = gr.File(label="Upload PDF, DOCX or TXT", file_types=[".pdf", ".docx", ".txt"], height=110)
                resume_box = gr.Textbox(label="Resume text", lines=8, max_lines=16,
                                        placeholder="Paste your resume, or upload a file above to fill this in.")
                gr.HTML('<h3 class="sb-step"><span>2</span>The job</h3>')
                sample_job = gr.Dropdown(choices=list(JOBS), value=None, label="Load a sample job")
                jd_box = gr.Textbox(label="Job description", lines=10, max_lines=20,
                                    placeholder="Paste the full posting, including requirements and nice-to-haves.")
                gr.HTML('<h3 class="sb-step"><span>3</span>Your time</h3>')
                hours = gr.Slider(2, 30, value=8, step=1, label="Hours you can study each week")
                analyze_btn = gr.Button("Analyze match", variant="primary", size="lg")
            with gr.Column(scale=7, min_width=360, elem_id="sb-results"):
                empty = gr.HTML(empty_state())
                with gr.Column(visible=False) as results:
                    score_html = gr.HTML()
                    with gr.Tabs():
                        with gr.Tab("Skills"):
                            skills_html = gr.HTML()
                        with gr.Tab("Learning plan"):
                            plan_html = gr.HTML()
                        with gr.Tab("AI coach"):
                            gr.Markdown(COACH_INTRO, elem_classes="sb-coach-intro")
                            coach_btn = gr.Button("Write my coaching notes", variant="primary")
                            coach_out = gr.Markdown(elem_classes="sb-coach")
                    download = gr.DownloadButton("Download report (.md)", visible=False, variant="secondary")
        gr.HTML(FOOTER)

    P = dict(api_visibility="private")
    login_btn.click(sign_in, [username, password], [ok, login_col, app_col, login_error, password], **P)
    password.submit(sign_in, [username, password], [ok, login_col, app_col, login_error, password], **P)
    logout_btn.click(sign_out, None, [ok, session, login_col, app_col, username, password, empty, results], **P)
    upload.upload(on_upload, [ok, upload], [resume_box], **P)
    sample_resume.change(pick_resume, [ok, sample_resume], [resume_box], **P)
    sample_job.change(pick_job, [ok, sample_job], [jd_box], **P)
    analyze_btn.click(analyze, [ok, resume_box, jd_box, hours],
                      [session, score_html, skills_html, plan_html, download, coach_out, results, empty], **P)
    hours.change(replan, [ok, session, hours], [score_html, plan_html, download], trigger_mode="always_last", **P)
    coach_btn.click(run_coach, [ok, session, hours], [session, coach_out, download], **P)

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=8).launch(
        theme=theme, css=(HERE / "style.css").read_text(encoding="utf-8"), head=HEAD,
        ssr_mode=False, footer_links=[], server_name=os.getenv("HOST", "0.0.0.0"),
        server_port=int(os.getenv("PORT", "7860")))

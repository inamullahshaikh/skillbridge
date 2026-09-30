"""
AI coach: an open-weights LLM writes an honest assessment, resume rewrites, a portfolio project and
interview questions from the analysis. Works with any OpenAI-compatible endpoint:

  GROQ_API_KEY                -> Llama 3.3 70B on Groq (free tier, no card needed)
  HF_TOKEN                    -> Hugging Face Inference Providers router
  LLM_BASE_URL (+LLM_API_KEY) -> anything else, e.g. a local Ollama or vLLM server
  LLM_MODEL                   -> override the model name for any of the above

With no key set, or if the call fails, a rule-based coach answers instead so the demo never breaks.
"""
import json
import os

from taxonomy import SKILL_BY_ID

SYSTEM = """You are SkillBridge's career coach. You help a candidate close the gap between their resume and a specific job.
Rules:
- Be honest, specific and encouraging. Short sentences. No filler.
- Never invent experience, employers, numbers or skills. Use only facts present in the resume.
- Where a number would strengthen a bullet but none is given, write [add number].
- Output GitHub Markdown with exactly these four sections and nothing before or after:
### Honest take
(3-4 sentences: where they stand for this role and the single most important next move)
### Resume bullets to strengthen
(up to 3 items. Each: **Before:** an existing bullet quoted from the resume, then **After:** a rewrite that uses the job's language)
### Portfolio project
(a project name in bold, then 4 short bullets: what to build, which gap skills it proves, the dataset or API to use, the result to report)
### Interview prep
(4 likely interview questions for this role, focused on their gaps, each followed by one line on what a strong answer covers)"""


def _config():
    model = os.getenv("LLM_MODEL")
    if os.getenv("LLM_BASE_URL"):
        m = model or "llama3.1"
        return dict(base_url=os.getenv("LLM_BASE_URL"), api_key=os.getenv("LLM_API_KEY", "none"),
                    models=[m], label=os.getenv("LLM_LABEL", m))
    if os.getenv("GROQ_API_KEY"):
        models = [model] if model else ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        return dict(base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"),
                    models=models, label="{model} (open weights) via Groq")
    if os.getenv("HF_TOKEN"):
        models = [model] if model else ["meta-llama/Llama-3.1-8B-Instruct", "Qwen/Qwen2.5-7B-Instruct"]
        return dict(base_url="https://router.huggingface.co/v1", api_key=os.getenv("HF_TOKEN"),
                    models=models, label="{model} (open weights) via Hugging Face")
    return None


def provider_label():
    c = _config()
    if not c:
        return "Rule-based coach (no LLM key configured)"
    return c["label"].format(model=c["models"][0])


def _brief(a, plan):
    return dict(
        role=a["title"], score=a["score"], verdict=a["verdict"],
        years=a["years"],
        matched=[dict(skill=r["label"], evidence=r["evidence"]) for r in a["reqs"] if r["status"] == "matched"][:12],
        gaps=[dict(skill=r["label"], asked_as="nice-to-have" if r["kind"] == "preferred" else "required",
                   status=r["status"], note=r["note"]) for r in a["reqs"] if r["status"] != "matched"][:12],
        plan_order=[dict(skill=it["name"], hours=it["hours"]) for it in plan["items"]][:8],
    )


def _llm(a, plan, resume_text, jd_text):
    from openai import OpenAI
    c = _config()
    client = OpenAI(base_url=c["base_url"], api_key=c["api_key"], timeout=60, max_retries=1)
    user = ("ANALYSIS (from SkillBridge's matching engine):\n" + json.dumps(_brief(a, plan), ensure_ascii=False)
            + "\n\nRESUME:\n" + resume_text[:6000] + "\n\nJOB DESCRIPTION:\n" + jd_text[:4000])
    last = None
    for model in c["models"]:
        try:
            resp = client.chat.completions.create(
                model=model, temperature=0.4, max_tokens=1100,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}])
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, c["label"].format(model=model)
        except Exception as e:
            last = e
    raise RuntimeError(f"LLM call failed: {type(last).__name__ if last else 'empty reply'}")


_QUESTIONS = {
    "AI & ML": "How would you use {s} on a real project for this team, and what would you measure to know it worked?",
    "Data": "Tell me about a time {s} changed a decision. How did you check the numbers were right?",
    "Backend": "How would you design a small service with {s}? Where would it break first under load?",
    "Frontend & Mobile": "How do you structure a {s} project so it stays fast and easy to change?",
    "Cloud & DevOps": "How would you use {s} to ship and run an app safely? What would you automate first?",
    "Databases": "How would you design the {s} side of a feature you've built? Which queries drive your indexes?",
    "Languages": "What do you reach for first in {s}, and what mistakes do newcomers make with it?",
    "Ways of working": "Tell me about a time you showed {s}. What would you do differently now?",
}
_ANSWERS = {
    "AI & ML": "Data split, baseline, metric tied to the business, deployment path, drift and rollback.",
    "Data": "The question, the method, a sanity check, the decision, and the measured outcome.",
    "Backend": "API shape, data model, scaling limit, failure handling and how you'd test it.",
    "Frontend & Mobile": "Component boundaries, state, performance budget, accessibility and testing.",
    "Cloud & DevOps": "Environments, CI/CD, secrets, cost, observability and least privilege.",
    "Databases": "Entities, constraints, access patterns, indexes and migration plan.",
    "Languages": "Idioms, tooling, testing, and one concrete project where you used it.",
    "Ways of working": "Situation, your action, the result, and what you learned (STAR).",
}


def _fallback(a, plan):
    matched = [r for r in a["reqs"] if r["status"] == "matched"]
    gaps = [r for r in a["reqs"] if r["status"] != "matched"]
    req_gaps = [r for r in gaps if r["kind"] != "preferred"]
    first = plan["items"][0]["name"] if plan["items"] else None
    lines = ["### Honest take",
             f"You score **{a['score']}/100** for {a['title']}: {a['verdict'].lower()}. "
             + (f"Your strongest evidence is {', '.join(r['label'] for r in matched[:3])}. " if matched else "")
             + (f"The gaps that matter most are {', '.join(r['label'] for r in req_gaps[:3])}. " if req_gaps else
                "You cover every required skill we detected. ")
             + (f"Start with **{first}**: it moves your score fastest for the hours it takes." if first else
                "Focus on making your evidence easy to find on the resume."),
             "", "### Resume bullets to strengthen"]
    shown = 0
    for r in matched:
        ev = r["evidence"]
        if shown >= 3 or not ev or len(ev.split()) < 6 or "@" in ev:
            continue
        tip = "Lead with the outcome, then name the tool" + ("" if any(ch.isdigit() for ch in ev) else ", and add [add number]")
        lines += [f"- **Before:** {ev}  ", f"  **Tip:** The job asks for *{r['label']}*. {tip}."]
        shown += 1
    if shown == 0:
        lines.append("- Add one bullet per required skill that says what you built, with which tool, and the result.")
    lines += ["", "### Portfolio project"]
    if plan.get("capstone"):
        lines.append(f"**{a['title']} starter project**")
        lines += [f"- {plan['capstone']['text']}",
                  f"- Proves: {', '.join(plan['capstone']['skills'])}.",
                  "- Use a public dataset or API close to the company's domain.",
                  "- Report one number (accuracy, latency, time saved) in the README."]
    else:
        lines.append("You already cover the requirements. Polish one existing project with a README, tests and a demo.")
    lines += ["", "### Interview prep"]
    picks = (req_gaps + gaps + matched)[:4]
    for r in picks:
        cat = SKILL_BY_ID[r["skill"]]["cat"]
        lines.append(f"- {_QUESTIONS[cat].format(s=r['label'])}  \n  *Strong answer covers:* {_ANSWERS[cat]}")
    return "\n".join(lines)


def coach(a, plan, resume_text, jd_text):
    """Returns (markdown, source_label, error_or_None)."""
    if _config():
        try:
            text, label = _llm(a, plan, resume_text, jd_text)
            return text, label, None
        except Exception as e:
            return _fallback(a, plan), "Rule-based coach (LLM unavailable right now)", str(e)
    return _fallback(a, plan), "Rule-based coach (no LLM key configured)", None

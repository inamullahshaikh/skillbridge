# Dafinitiq AI program: product proposal

## Product name
SkillBridge

## Describe your AI product
SkillBridge is an AI career co-pilot that compares your resume with a specific job post and tells you, honestly, how well you match and what to do about it.

It gives a 0-100 match score and shows every required skill you already have, with the exact line on your resume that proves it. It separates missing required skills from nice-to-haves, understands "PyTorch or TensorFlow" as one requirement, and notices transferable skills (Flask makes FastAPI quicker to learn). Then it builds a week-by-week learning plan that fits the hours you actually have, ordered by which skills raise your score fastest, with prerequisites first and a free resource and a proof-of-skill project for each. An AI coach rewrites your resume bullets in the job's language without inventing experience, proposes a portfolio project and prepares you for likely interview questions.

Who it's for: students, fresh graduates, career switchers and self-taught developers, especially in markets like Pakistan where people apply to dozens of roles without learning why they were rejected. Later: bootcamps and university career offices tracking cohorts.

Open-source tools: Gradio for the app (hosted on Hugging Face Spaces); BAAI/bge-small-en-v1.5 embeddings through fastembed (ONNX, CPU) for semantic matching; pypdf and python-docx for resume parsing; a custom skill taxonomy (121 skills, 600+ aliases, prerequisites, transferable-skill links); and Llama 3.3 70B (open weights) through any OpenAI-compatible endpoint (Groq, Hugging Face Inference Providers or a local Ollama) for the coach, with a rule-based fallback. For production I plan to add Qdrant to index job posts, GLiNER to extract skills beyond the taxonomy, PostgreSQL to track progress, and Langfuse to evaluate the coach.

## Why did you choose this idea?
Job seekers apply to dozens of roles and rarely find out which skills were missing. Advice like "learn cloud" doesn't say what to learn first, for which job, or in how many hours. Companies already use software to compare resumes against job posts; SkillBridge gives candidates that same view, plus a concrete plan to close the gap. It is also a problem where AI helps most when it is grounded: every claim points back to evidence in your own resume, and the coach is not allowed to invent experience. Taking it to production (evaluation, reliability, privacy and cost) is exactly what I want to learn in this program.

## Architecture diagram (Mermaid)
See architecture.mmd (paste into mermaid.live to preview).

## MVP
Link: https://huggingface.co/spaces/YOUR-USERNAME/skillbridge
Username: demo
Password: SkillBridge2026
Try it: load "Sara Malik: data analyst" and "Junior ML Engineer", then choose Analyze match.

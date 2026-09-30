"""Quick checks for the matching engine. Run: python -m pytest -q  (or python test_engine.py)"""
from engine import build_plan, match, parse_jd, parse_resume
from samples import JOBS, RESUMES


def test_any_of_groups_and_nice_to_haves():
    jd = parse_jd(JOBS["Junior ML Engineer"])
    groups = {tuple(r["members"]): r["kind"] for r in jd["reqs"]}
    assert ("pytorch", "tensorflow") in groups          # "such as PyTorch or TensorFlow"
    assert ("aws", "gcp", "azure") in groups            # "(AWS, GCP or Azure)"
    assert groups[("kubernetes",)] == "preferred"       # under "Nice to have"
    assert ("deep_learning",) not in groups             # umbrella folded into the group
    assert jd["years"] == 1


def test_resume_evidence_and_inference():
    r = parse_resume(RESUMES["Sara Malik: data analyst"])
    assert r["skills"]["sklearn"]["credit"] == 1.0
    assert r["skills"]["docker"]["basic"] is True       # "Familiar with: Docker"
    assert r["inferred"]["rest"]["via"] == "flask"
    assert "github.com" not in r["skills"]["git"]["evidence"]  # prefers real evidence over contact line
    assert r["years"] == 3


def test_plan_orders_foundations_first():
    a = match(RESUMES["Omar Farooq: front-end developer"], JOBS["Junior ML Engineer"])
    plan = build_plan(a, 8)
    names = [it["skill"] for it in plan["items"]]
    assert names.index("python") < names.index("fastapi")
    assert plan["projected"] > a["score"]


def test_score_bands():
    strong = match(RESUMES["Sara Malik: data analyst"], JOBS["Data Analyst"])
    weak = match(RESUMES["Omar Farooq: front-end developer"], JOBS["Data Analyst"])
    assert strong["score"] >= 80 > weak["score"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)

"""
SkillBridge matching engine.

Pipeline: text extraction -> skill detection (taxonomy + evidence) -> JD parsing
(required / nice-to-have, "X or Y" groups, years) -> resume matching (direct, inferred,
basic, semantic, adjacent) -> score -> week-by-week learning plan.
"""
from __future__ import annotations

import datetime as dt
import math
import re
import unicodedata
from collections import OrderedDict

from taxonomy import ADJACENT, CATEGORIES, SKILL_BY_ID, SKILLS

# ------------------------------------------------------------------ text utils
_BOUND_L = r"(?<![A-Za-z0-9_])"
_BOUND_R = r"(?![A-Za-z0-9_])"
_BULLET = re.compile(r"^\s*(?:[-*•●▪◦‣∙·>]|\d{1,2}[.)])\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = (text.replace("–", "-").replace("—", "-").replace("’", "'")
            .replace("‘", "'").replace("“", '"').replace("”", '"').replace("\xa0", " "))
    text = re.sub(r"[ \t]+", " ", text)
    return text


def split_lines(text: str) -> list[str]:
    """Lines, with long paragraphs further split into sentences / clauses."""
    out = []
    for raw in normalize(text).splitlines():
        line = raw.strip()
        if not line:
            continue
        if len(line) > 220:
            out.extend(p.strip() for p in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", line) if p.strip())
        else:
            out.append(line)
    return out


def clean_line(line: str) -> str:
    line = _BULLET.sub("", line)
    return re.sub(r"^[#*_\s]+|[*_\s]+$", "", line).strip()


def extract_text(path: str) -> str:
    """Read PDF, DOCX or plain text into a string."""
    p = path.lower()
    if p.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if p.endswith(".docx"):
        import docx
        d = docx.Document(path)
        parts = [para.text for para in d.paragraphs]
        for table in d.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# ------------------------------------------------------------------ skill detection
def _compile(skill):
    pats = []
    if skill["ci"]:
        pats.append(re.compile(_BOUND_L + "(?:" + "|".join(f"(?:{a})" for a in skill["ci"]) + ")" + _BOUND_R, re.I))
    if skill["cs"]:
        pats.append(re.compile(_BOUND_L + "(?:" + "|".join(f"(?:{a})" for a in skill["cs"]) + ")" + _BOUND_R))
    return pats


PATTERNS = [(s["id"], _compile(s)) for s in SKILLS]


def _families(sid):
    f = SKILL_BY_ID[sid]["fam"]
    if not f:
        return set()
    return {f} if isinstance(f, str) else set(f)


def find_in_line(line: str):
    """[(start, end, skill_id)] for every skill mention in a line (first match per skill)."""
    hits = []
    for sid, pats in PATTERNS:
        best = None
        for p in pats:
            m = p.search(line)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), m.end(), sid)
        if best:
            hits.append(best)
    hits.sort()
    return hits


def _snippet(line: str, start: int, end: int, width: int = 90) -> str:
    line = clean_line(line) if len(line) < 400 else line
    if len(line) <= 2 * width:
        return line
    s = max(0, start - width)
    e = min(len(line), end + width)
    return ("…" if s > 0 else "") + line[s:e].strip() + ("…" if e < len(line) else "")


# ------------------------------------------------------------------ sections
_RESUME_SECTIONS = OrderedDict([
    ("education", r"education|academic|qualifications|coursework|certifications?|courses"),
    ("experience", r"(?:work|professional|relevant|employment|industry)?\s*(?:experience|history|employment)|internships?|work"),
    ("projects", r"projects?|portfolio"),
    ("skills", r"(?:technical|core|key)?\s*skills|technologies|tools|tech stack|competencies"),
    ("summary", r"summary|profile|objective|about me"),
])

_JD_SECTIONS = [
    ("preferred", r"nice[- ]to[- ]haves?|preferred|bonus|good[- ]to[- ]have|pluses|a plus|desir(?:ed|able)|"
                  r"additional (?:skills|qualifications)|extra credit|ideally|stand ?out|would be great"),
    ("other", r"about (?:us|the company|the team|[A-Z][\w&. ]+$)|benefits|perks|what we offer|compensation|salary|"
              r"why (?:join|work)|equal opportunity|how to apply|our values|location|who we are"),
    ("required", r"requirements?|required|must[- ]haves?|qualifications|what you(?:'ll)? (?:need|bring)|who you are|"
                 r"you have|skills|what we(?:'re| are) looking for|your profile|about you|experience|you bring"),
    ("resp", r"responsibilit|what you(?:'ll| will) do|the role|your role|day[- ]to[- ]day|duties|you will|in this role|"
             r"what you'll be doing|about the (?:role|job|position)|job description|overview|the opportunity"),
]


def _heading_kind(line: str, table):
    raw = line.strip()
    if _BULLET.match(raw):
        return None
    txt = clean_line(raw).rstrip(":").strip()
    if not txt or len(txt) > 60:
        return None
    looks_heading = raw.rstrip().endswith(":") or raw.startswith("#") or raw.startswith("**") \
        or txt.isupper() or len(txt.split()) <= 5
    if not looks_heading or txt.endswith("."):
        return None
    for kind, pat in table:
        if re.search(r"^(?:" + pat + r")\b", txt, re.I) or (len(txt.split()) <= 6 and re.search(pat, txt, re.I)):
            return kind
    return None


# ------------------------------------------------------------------ resume
_BASIC = re.compile(r"\b(?:familiar(?:ity)? with|familiar|basic(?:s| knowledge)?|beginner|exposure to|currently learning|"
                    r"learning|coursework|introductory|some experience)\b", re.I)
_MONTH = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
_DATE = rf"(?:{_MONTH}\.?,?\s+|(?:0?[1-9]|1[0-2])[/.-])?(?:19|20)\d{{2}}"
_RANGE = re.compile(rf"({_DATE})\s*(?:-|to|until|till)\s*({_DATE}|present|current|now|today|date|ongoing)", re.I)
_EDU = re.compile(r"\b(?:universit\w*|college|school|bachelor'?s?|master'?s?|ph\.?d|degree|c?gpa|matric\w*|"
                  r"intermediate|a-levels?|o-levels?|diploma|b\.?sc?|m\.?sc?|b\.?e|b\.?tech|m\.?tech|hsc|ssc|fsc)\b", re.I)
_MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def _parse_date(s: str, is_end: bool, same_year_hint=None):
    s = s.strip().lower()
    if s in ("present", "current", "now", "today", "date", "ongoing"):
        t = dt.date.today()
        return t.year, t.month
    y = int(re.search(r"(19|20)\d{2}", s).group(0))
    m = re.match(r"([a-z]{3})", s)
    if m and m.group(1) in _MONTHS:
        return y, _MONTHS[m.group(1)]
    m = re.match(r"(\d{1,2})[/.-]", s)
    if m:
        return y, int(m.group(1))
    return y, (6 if is_end else 1)


def resume_years(lines: list[str], sections: list[str]):
    """Estimate years of experience: explicit claim first, else merged date ranges."""
    explicit = []
    for line in lines:
        for m in re.finditer(r"(\d{1,2}(?:\.\d)?)\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:[\w-]+\s+){0,3}experience", line, re.I):
            explicit.append(float(m.group(1)))
    has_exp_section = "experience" in sections
    spans = []
    for line, sec in zip(lines, sections):
        if sec in ("education", "projects"):
            continue
        if has_exp_section and sec not in ("experience",):
            continue
        if _EDU.search(line):
            continue
        for m in _RANGE.finditer(line):
            a = _parse_date(m.group(1), False)
            b = _parse_date(m.group(2), True)
            start, end = a[0] * 12 + a[1], b[0] * 12 + b[1]
            if a[0] == b[0] and not re.search(_MONTH, m.group(0), re.I):
                start, end = a[0] * 12 + 1, a[0] * 12 + 12
            if 0 < end - start < 12 * 45:
                spans.append((start, end))
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    from_dates = round(sum(e - s for s, e in merged) / 12, 1) if merged else None
    if explicit:
        return max(explicit), "stated on resume"
    if from_dates:
        return from_dates, "from dates on resume"
    return None, None


def parse_resume(text: str):
    lines = split_lines(text)
    sections, cur = [], "summary"
    for line in lines:
        k = _heading_kind(line, list(_RESUME_SECTIONS.items()))
        if k:
            cur = k
        sections.append(cur)
    skills = {}
    sec_rank = {"experience": 3, "projects": 2, "skills": 1, "summary": 1, "education": 0}
    for line, sec in zip(lines, sections):
        contact = bool(re.search(r"@|linkedin|github\.com|https?://|\+\d{2}", line, re.I)) and len(line) < 160
        for start, end, sid in find_in_line(line):
            basic = bool(_BASIC.search(line)) or sec == "education"
            credit = 0.7 if basic else 1.0
            rank = (credit, -1 if contact else sec_rank.get(sec, 1))
            cur_hit = skills.get(sid)
            if cur_hit is None or rank > cur_hit["_rank"]:
                skills[sid] = dict(credit=credit, evidence=_snippet(line, start, end), section=sec,
                                   count=(cur_hit or {}).get("count", 0) + 1, basic=basic, _rank=rank)
            else:
                cur_hit["count"] += 1
    # Inferred skills (e.g. scikit-learn => machine learning, Python).
    inferred = {}
    changed = True
    while changed:
        changed = False
        for sid in list(skills) + list(inferred):
            src = skills.get(sid) or inferred.get(sid)
            strong = (sid in skills and not skills[sid]["basic"]) or (sid in inferred and inferred[sid]["credit"] >= 0.8)
            for parent in SKILL_BY_ID[sid]["implies"]:
                credit = 0.8 if strong else 0.6
                cur = inferred.get(parent)
                if parent not in skills and (cur is None or credit > cur["credit"]):
                    inferred[parent] = dict(credit=credit, via=sid)
                    changed = True
    years, years_src = resume_years(lines, sections)
    return dict(lines=lines, sections=sections, skills=skills, inferred=inferred, years=years, years_src=years_src)


# ------------------------------------------------------------------ job description
_PREF_CUE = re.compile(r"nice[- ]to[- ]have|(?:is|are|would be) (?:a )?(?:big |huge )?(?:plus|bonus)|\ba plus\b|\bbonus\b|"
                       r"\bpreferred\b|\bpreferably\b|desir(?:ed|able)|\bideally\b|good[- ]to[- ]have|advantage(?:ous)?|"
                       r"not required|\boptional\b", re.I)
_EXAMPLE_CUE = re.compile(r"\bsuch as\b|\be\.?g\.?\b|\blike\b|\bincluding\b|\bsimilar\b|\bany of\b|\bone of\b|"
                          r"\bequivalent\b|\betc\b|\bor (?:other|similar|equivalent)\b", re.I)
_KIND_BASE = {"required": 1.0, "resp": 0.9, "intro": 0.8, "preferred": 0.5}


def _clauses(line: str):
    """Split a line into clauses at ';' and sentence ends, keeping offsets simple."""
    parts = re.split(r";|(?<=[a-z0-9)])\.\s+(?=[A-Z])", line)
    return [p for p in parts if p.strip()]


def _groups_in_clause(clause: str):
    """Return list of member-tuples: singletons and any-of groups."""
    hits = find_in_line(clause)
    if not hits:
        return []
    used, groups = set(), []
    example = bool(_EXAMPLE_CUE.search(clause))
    fams = {}
    for h in hits:
        for f in _families(h[2]):
            fams.setdefault(f, []).append(h)
    for f, fh in fams.items():
        if len(fh) < 2:
            continue
        clusters, cur, alt = [], [fh[0]], False
        for prev, h in zip(fh, fh[1:]):
            gap = clause[prev[1]:h[0]]
            if len(gap) <= 30 and not re.search(r"[.;:]", gap):
                cur.append(h)
                alt = alt or bool(re.search(r"\bor\b|/|\|", gap, re.I))
            else:
                clusters.append((cur, alt))
                cur, alt = [h], False
        clusters.append((cur, alt))
        for members, is_alt in clusters:
            ids = [m[2] for m in members if m[2] not in used]
            if len(ids) >= 2 and (is_alt or example):
                groups.append(tuple(ids))
                used.update(ids)
    for h in hits:
        if h[2] not in used:
            groups.append((h[2],))
            used.add(h[2])
    # "a deep learning framework such as PyTorch or TensorFlow": the umbrella skill is
    # already expressed by the group, so drop it as a separate requirement.
    multi = [g for g in groups if len(g) > 1]
    if multi:
        drop = {g[0] for g in groups if len(g) == 1
                and any(all(g[0] in SKILL_BY_ID[m]["implies"] for m in mg) for mg in multi)}
        groups = [g for g in groups if not (len(g) == 1 and g[0] in drop)]
    return groups


def jd_years(lines, kinds):
    best = None
    for line, kind in zip(lines, kinds):
        if kind in ("other", "preferred"):
            continue
        for m in re.finditer(r"(\d{1,2})\s*\+?\s*(?:(?:-|to)\s*\d{1,2}\s*)?\+?\s*(?:years?|yrs?)", line, re.I):
            tail = line[m.end():m.end() + 60].lower()
            head = line[max(0, m.start() - 40):m.start()].lower()
            if "experience" in tail or "experience" in head or "of " in tail[:4]:
                v = int(m.group(1))
                if 0 < v <= 20:
                    best = v if best is None else max(best, v)
    return best


def parse_jd(text: str):
    lines = split_lines(text)
    title = None
    for line in lines[:3]:
        t = re.sub(r"^(?:job\s*title|role|position)\s*:\s*", "", clean_line(line), flags=re.I)
        if 2 <= len(t) <= 80 and not _heading_kind(line, _JD_SECTIONS):
            title = t.rstrip(":")
            break
    kinds, cur = [], "intro"
    for line in lines:
        k = _heading_kind(line, _JD_SECTIONS)
        if k:
            cur = k
            kinds.append("heading")
            continue
        kinds.append(cur)

    reqs = OrderedDict()
    other_lines = []
    for idx, (line, sec) in enumerate(zip(lines, kinds)):
        if sec in ("heading", "other"):
            continue
        if idx == 0 and title and clean_line(line).startswith(title):
            # The title line itself counts as intro evidence (e.g. "ML Engineer").
            sec = "intro"
        found_any = False
        for clause in _clauses(line):
            kind = "preferred" if (_PREF_CUE.search(clause) or sec == "preferred") else sec
            for members in _groups_in_clause(clause):
                found_any = True
                key = frozenset(members)
                r = reqs.get(key)
                if r is None:
                    r = reqs[key] = dict(members=list(members), kind=kind, base=_KIND_BASE[kind], mentions=0,
                                         jd_line=clean_line(line), order=len(reqs))
                r["mentions"] += 1
                if _KIND_BASE[kind] > r["base"]:
                    r["base"], r["kind"] = _KIND_BASE[kind], kind
        words = clean_line(line).split()
        is_years = re.search(r"\d+\s*\+?\s*(?:years?|yrs?)", line, re.I)
        if not found_any and not is_years and sec in ("required", "preferred") and 4 <= len(words) <= 40:
            other_lines.append(dict(text=clean_line(line), kind=sec))

    # Merge: a skill required on its own leaves any "X or Y" group it appears in.
    singles = {next(iter(k)): v for k, v in reqs.items() if len(k) == 1}
    final = OrderedDict()
    for key, r in reqs.items():
        if len(key) > 1:
            keep = [m for m in r["members"] if not (m in singles and singles[m]["base"] >= r["base"])]
            if len(keep) == 0:
                continue
            if len(keep) == 1:
                s = singles.get(keep[0])
                if s:
                    s["mentions"] += r["mentions"]
                    continue
                r = dict(r, members=keep)
            else:
                r = dict(r, members=keep)
        fk = frozenset(r["members"])
        if fk in final:
            final[fk]["mentions"] += r["mentions"]
        else:
            final[fk] = r
    # Drop groups that are strict subsets of a larger group of the same kind.
    keys = list(final)
    for a in keys:
        for b in keys:
            if a is not b and a in final and b in final and len(a) > 1 and a < b:
                final[b]["mentions"] += final[a]["mentions"]
                del final[a]
    out = []
    for r in final.values():
        r["weight"] = round(r["base"] * min(1.6, 1 + 0.2 * (r["mentions"] - 1)), 3)
        out.append(r)
    out.sort(key=lambda r: r["order"])
    return dict(title=title, lines=lines, kinds=kinds, reqs=out, other=other_lines[:8],
                years=jd_years(lines, kinds))


# ------------------------------------------------------------------ matching
def adjacency(a: str, b: str) -> float:
    best = 0.0
    for group, f in ADJACENT:
        if a in group and b in group:
            best = max(best, f)
    return best


def _member_credit(sid, resume):
    """(credit, via, evidence, note, adjacent_from, adjacency_factor) for one skill vs the resume."""
    s = resume["skills"].get(sid)
    if s:
        if s["basic"]:
            return 0.7, "basic", s["evidence"], "basic level", None, 0.0
        return 1.0, "direct", s["evidence"], "", None, 0.0
    inf = resume["inferred"].get(sid)
    if inf:
        via = SKILL_BY_ID[inf["via"]]["name"]
        ev = resume["skills"].get(inf["via"], {}).get("evidence", "")
        return inf["credit"], "inferred", ev, f"inferred from {via}", None, 0.0
    best_f, best_have = 0.0, None
    for have in list(resume["skills"]) + list(resume["inferred"]):
        f = adjacency(sid, have)
        if f >= 0.3 and f > best_f:
            best_f, best_have = f, have
    if best_have:
        ev = resume["skills"].get(best_have, {}).get("evidence", "")
        return 0.3, "adjacent", ev, f"transferable from {SKILL_BY_ID[best_have]['name']}", best_have, best_f
    return 0.0, "none", "", "", None, 0.0


def label_for(members):
    names = [SKILL_BY_ID[m]["name"] for m in members]
    return names[0] if len(names) == 1 else " / ".join(names)


def match(resume_text: str, jd_text: str, embedder=None):
    resume = parse_resume(resume_text)
    jd = parse_jd(jd_text)
    notes = []
    results = []
    for r in jd["reqs"]:
        best = None
        for m in r["members"]:
            c = _member_credit(m, resume)
            cand = dict(credit=c[0], via=c[1], evidence=c[2], note=c[3], skill=m, adj_from=c[4], adj_factor=c[5])
            if best is None or cand["credit"] > best["credit"]:
                best = cand
        res = dict(r, **best, label=label_for(r["members"]), any_of=len(r["members"]) > 1,
                   category=SKILL_BY_ID[r["members"][0]]["cat"])
        results.append(res)

    semantic_used = False
    if embedder is not None:
        try:
            semantic_used = _semantic_backfill(results, resume, jd, embedder)
        except Exception as e:  # never let the optional layer break the analysis
            notes.append(f"Semantic layer skipped ({type(e).__name__}).")
    _keyword_other(jd, resume, done=semantic_used)

    for r in results:
        r["status"] = "matched" if r["credit"] >= 0.75 else ("partial" if r["credit"] >= 0.5 else "missing")

    exp_fit = None
    if jd["years"]:
        if resume["years"] is not None:
            exp_fit = min(1.0, resume["years"] / jd["years"])
        else:
            notes.append("Couldn't find dates or 'X years of experience' on the resume, so experience isn't scored.")
    score, comps = compute_score(results, exp_fit)
    if not results:
        notes.append("No recognisable skills in the job description. Paste the full posting including requirements.")
    verdict, detail = _verdict(score, results)

    req_ids = {m for r in results for m in r["members"]}
    extras = [sid for sid in resume["skills"] if sid not in req_ids and not resume["skills"][sid]["basic"]]

    cats = OrderedDict()
    for c in CATEGORIES:
        rs = [r for r in results if r["category"] == c and r["kind"] != "preferred"]
        if rs:
            cats[c] = sum(r["weight"] * r["credit"] for r in rs) / sum(r["weight"] for r in rs)

    return dict(
        title=jd["title"] or "this role", score=score, verdict=verdict, verdict_detail=detail,
        components=comps,
        reqs=results, extras=extras, categories=cats, exp_fit=exp_fit,
        have={**{k: v["credit"] for k, v in resume["inferred"].items()},
              **{k: v["credit"] for k, v in resume["skills"].items()}},
        years=dict(jd=jd["years"], resume=resume["years"], source=resume["years_src"]),
        other=jd["other"], semantic=semantic_used, notes=notes,
        resume_skill_count=len(resume["skills"]),
    )


def compute_score(results, exp_fit, overrides=None):
    """Weighted score. overrides: {req_index: credit} to project 'what if I learn this'."""
    overrides = overrides or {}

    def cov(kind_set):
        rs = [(i, r) for i, r in enumerate(results) if r["kind"] in kind_set]
        if not rs:
            return None
        return sum(r["weight"] * overrides.get(i, r["credit"]) for i, r in rs) / sum(r["weight"] for _, r in rs)

    comps = [("Required skills", cov({"required", "resp", "intro"}), 0.75),
             ("Nice-to-have skills", cov({"preferred"}), 0.15),
             ("Experience", exp_fit, 0.10)]
    live = [(n, v, w) for n, v, w in comps if v is not None]
    if not live or not results:
        return 0, [dict(name=n, value=v, weight=w) for n, v, w in comps]
    tw = sum(w for _, _, w in live)
    score = round(100 * sum(v * w for _, v, w in live) / tw)
    return score, [dict(name=n, value=v, weight=w) for n, v, w in comps]


def _verdict(score, results):
    miss_req = [r for r in results if r["kind"] != "preferred" and r["status"] == "missing"]
    n = len(miss_req)
    if score >= 80:
        return "Strong match", "Apply now. Tailor your resume so the matched skills are easy to spot."
    if score >= 60:
        return "Good match", f"Close {n} key gap{'s' if n != 1 else ''} and you're competitive. Apply while you learn."
    if score >= 40:
        return "Stretch role", f"{n} required skill{'s' if n != 1 else ''} missing. A focused plan of a few weeks closes most of it."
    return "Long shot for now", "Big gap today. Follow the plan, or target a stepping-stone role first."


# ------------------------------------------------------------------ semantic layer (optional)
_Q_PREFIX = "Represent this sentence for searching relevant passages: "
SKILL_SIM = 0.74
OTHER_SIM_HIGH, OTHER_SIM_LOW = 0.72, 0.62


def _evidence_lines(resume):
    return [clean_line(l) for l in resume["lines"] if len(clean_line(l).split()) >= 4][:250]


def _semantic_backfill(results, resume, jd, embedder):
    import numpy as np
    passages = _evidence_lines(resume)
    if not passages:
        return False
    P = embedder.encode(passages)
    todo = [r for r in results if r["credit"] < 0.5]
    if todo:
        Q = embedder.encode([_Q_PREFIX + SKILL_BY_ID[r["skill"]]["desc"] for r in todo])
        sims = Q @ P.T
        for r, row in zip(todo, sims):
            j = int(np.argmax(row))
            if float(row[j]) >= SKILL_SIM:
                r.update(credit=0.55, via="semantic", evidence=passages[j],
                         note=f"similar experience found (similarity {float(row[j]):.2f})")
    others = jd["other"]
    if others:
        Q = embedder.encode([_Q_PREFIX + o["text"] for o in others])
        sims = Q @ P.T
        for o, row in zip(others, sims):
            j = int(np.argmax(row))
            v = float(row[j])
            o["sim"] = round(v, 2)
            o["evidence"] = passages[j] if v >= OTHER_SIM_LOW else ""
            o["status"] = "likely" if v >= OTHER_SIM_HIGH else ("partial" if v >= OTHER_SIM_LOW else "unclear")
            o["method"] = "semantic"
    return True


_STOP = set("""a an the and or of to in on for with by at from as is are be been being this that these those you your we our
will would can could should must have has had do does did not no yes it its into over under about across within using use
used strong good great excellent solid ability able experience experienced years year plus etc work working team teams
including such other related field fields least minimum preferred required requirement requirements skills skill knowledge
understanding proven demonstrated familiarity familiar hands on""".split())


def _tokens(s):
    return {w[:6] for w in re.findall(r"[a-z][a-z+#.]{2,}", s.lower()) if w not in _STOP}


def _keyword_other(jd, resume, done):
    if done:
        return
    passages = _evidence_lines(resume)
    ptoks = [(_tokens(p), p) for p in passages]
    for o in jd["other"]:
        q = _tokens(o["text"])
        best, ev = 0.0, ""
        for t, p in ptoks:
            if q:
                v = len(q & t) / len(q)
                if v > best:
                    best, ev = v, p
        o["sim"] = round(best, 2)
        o["evidence"] = ev if best >= 0.3 else ""
        o["status"] = "likely" if best >= 0.5 else ("partial" if best >= 0.3 else "unclear")
        o["method"] = "keyword"


# ------------------------------------------------------------------ learning plan
def _closure(sid):
    out, stack = set(), list(SKILL_BY_ID[sid]["implies"])
    while stack:
        x = stack.pop()
        if x not in out:
            out.add(x)
            stack.extend(SKILL_BY_ID[x]["implies"])
    return out


def _hours_for(r, sid):
    h = SKILL_BY_ID[sid]["hours"]
    if sid == r["skill"]:
        if r["via"] == "adjacent":
            h *= (1 - r.get("adj_factor", 0.3))
        elif r["via"] in ("basic", "semantic", "inferred"):
            h *= 0.5
    return max(2, int(round(h)))


_ORDER_HINTS = {
    "prompt": ["llm", "python"], "responsible_ai": ["ml", "llm"], "model_eval": ["ml", "llm"],
    "tracking": ["ml"], "ci_cd": ["git", "testing"], "vector": ["python"], "agents": ["rag", "prompt"],
    "langchain": ["prompt"], "llamaindex": ["prompt"], "mlops": ["fastapi", "flask"], "fine_tuning": ["pytorch"],
    "ab_testing": ["stats"], "data_modeling": ["sql"], "graphql": ["rest"], "iac": ["aws", "azure", "gcp"],
    "rag": ["vector"], "docker": ["linux"], "nextjs": ["typescript"],
}


def _pick(r):
    """Which skill to learn for a gap. For 'X or Y', the first listed unless another is much quicker."""
    if r["credit"] > 0:
        return r["skill"]
    first = r["members"][0]
    quick = min(r["members"], key=lambda m: SKILL_BY_ID[m]["hours"])
    return quick if SKILL_BY_ID[quick]["hours"] <= 0.7 * SKILL_BY_ID[first]["hours"] else first


def build_plan(analysis, hours_per_week: int = 8, max_weeks: int = 16):
    """Order gaps by projected score gain per hour, respect prerequisites, pack into weeks."""
    hours_per_week = max(2, int(hours_per_week))
    reqs, have = analysis["reqs"], analysis.get("have", {})
    base = analysis["score"]
    exp_fit = analysis.get("exp_fit")

    items, tips = OrderedDict(), []
    for i, r in enumerate(reqs):
        if r["credit"] >= 0.75:
            continue
        sid = _pick(r)
        if SKILL_BY_ID[sid]["cat"] == "Ways of working":
            # Soft skills are usually there but unwritten: show them on the resume instead of studying.
            gain = compute_score(reqs, exp_fit, {i: 1.0})[0] - base
            tips.append(dict(skill=sid, name=SKILL_BY_ID[sid]["name"], kind=r["kind"], gain=gain,
                             jd_line=r["jd_line"]))
            continue
        if sid in items:
            items[sid]["reqs"].append(i)
            continue
        core = r["kind"] != "preferred"
        level_up = r["via"] in ("basic", "semantic", "inferred")
        why = "Level up" if level_up else ("Required" if core else "Nice-to-have")
        if r["any_of"]:
            why += f" (any one of {r['label']})"
        items[sid] = dict(skill=sid, name=SKILL_BY_ID[sid]["name"], hours=_hours_for(r, sid), core=core,
                          reqs=[i], why=why, kind=r["kind"], also=[], after=set(), for_skill=None,
                          note=r["note"] if r["via"] in ("adjacent", "basic", "semantic", "inferred") else "")

    # A specific tool also covers a small umbrella skill it implies (AWS covers cloud basics).
    # A big umbrella (Python before FastAPI) stays separate and is learned first.
    for a_id in list(items):
        for b_id in list(items):
            if a_id not in items or b_id not in items or a_id == b_id or b_id not in _closure(a_id):
                continue
            A, B = items[a_id], items[b_id]
            if b_id not in SKILL_BY_ID[a_id]["prereqs"] and B["hours"] <= 0.5 * A["hours"]:
                items.pop(b_id)
                A["hours"] += int(round(0.5 * B["hours"]))
                A["reqs"] += B["reqs"]
                A["also"].append(B["name"])
                A["core"] = A["core"] or B["core"]
            else:
                A["after"].add(b_id)

    # Foundations the person lacks (e.g. Python before PyTorch).
    for sid in list(items):
        for p in SKILL_BY_ID[sid]["prereqs"]:
            if p in items:
                items[sid]["after"].add(p)
            elif have.get(p, 0) < 0.5:
                items[p] = dict(skill=p, name=SKILL_BY_ID[p]["name"], hours=SKILL_BY_ID[p]["hours"],
                                core=items[sid]["core"], reqs=[], why=f"Foundation for {SKILL_BY_ID[sid]['name']}",
                                kind="foundation", also=[], after=set(), for_skill=sid, note="")
                items[sid]["after"].add(p)
    for it in items.values():  # a core item's foundation is core too
        if it["core"]:
            for p in it["after"]:
                items[p]["core"] = True
    for it in items.values():  # soft ordering hints (LLM basics before prompt engineering)
        for p in _ORDER_HINTS.get(it["skill"], ()):
            if p in items and it["skill"] not in items[p]["after"] and (items[p]["core"] or not it["core"]):
                it["after"].add(p)

    def gain(it):
        return compute_score(reqs, exp_fit, {i: 1.0 for i in it["reqs"]})[0] - base

    lst = list(items.values())
    for it in lst:
        it["solo_gain"] = gain(it)
    lst.sort(key=lambda it: (not it["core"], -(it["solo_gain"] / it["hours"]), -it["solo_gain"]))
    for _ in range(200):  # anything an item depends on moves in front of it
        moved = False
        pos = {it["skill"]: k for k, it in enumerate(lst)}
        for k, it in enumerate(lst):
            for p in it["after"]:
                j = pos.get(p)
                if j is not None and j > k:
                    lst.insert(k, lst.pop(j))
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break

    # Decide which nice-to-haves fit (with their foundations) inside max_weeks.
    total = sum(it["hours"] for it in lst if it["core"])
    later = []
    for it in [x for x in lst if not x["core"] and x["kind"] != "foundation"]:
        unit = [it] + [f for f in lst if f["kind"] == "foundation" and f["for_skill"] == it["skill"] and not f["core"]]
        h = sum(u["hours"] for u in unit)
        if math.ceil((total + h) / hours_per_week) <= max_weeks:
            total += h
        else:
            later.extend(unit)
    later_ids = {id(x) for x in later}
    scheduled = [it for it in lst if id(it) not in later_ids]

    done, prev = {}, base
    for it in scheduled:
        done.update({i: 1.0 for i in it["reqs"]})
        now = compute_score(reqs, exp_fit, done)[0]
        it["gain"], prev = now - prev, now
        it["score_after"] = now
    for it in later:
        it["gain"] = it["solo_gain"]

    weeks, week, cap = [], [], hours_per_week
    for it in scheduled:
        remaining, part = it["hours"], 1
        while remaining > 0:
            if cap <= 0:
                weeks.append(week)
                week, cap = [], hours_per_week
            chunk = min(remaining, cap)
            remaining -= chunk
            cap -= chunk
            week.append(dict(it, chunk=chunk, part=part, finishes=remaining == 0))
            part += 1
    if week:
        weeks.append(week)

    projected = compute_score(reqs, exp_fit, done)[0]
    top = [it["name"] for it in sorted(scheduled, key=lambda x: -x["solo_gain"]) if it["kind"] != "foundation"][:3]
    capstone = None
    if top:
        joined = ", ".join(top[:-1]) + " and " + top[-1] if len(top) > 1 else top[0]
        capstone = dict(
            hours=min(hours_per_week, 10), skills=top,
            text=(f"Build one portfolio project for a {analysis['title']} role that uses {joined} together. "
                  "Publish it on GitHub with a README, a short demo video and one measurable result, "
                  "then add it to your resume and apply."))
    return dict(weeks=weeks, later=later, capstone=capstone, hours_per_week=hours_per_week, tips=tips,
                total_hours=sum(it["hours"] for it in scheduled), items=scheduled,
                projected=projected, base=base)


# ------------------------------------------------------------------ export
def to_markdown(a, plan, coach_md: str | None = None, coach_label: str | None = None) -> str:
    L = [f"# SkillBridge report: {a['title']}", "",
         f"**Match score: {a['score']}/100 ({a['verdict']})**  ", a["verdict_detail"], "",
         f"Projected score after the plan: **{plan['projected']}/100**", ""]
    for c in a["components"]:
        if c["value"] is not None and c["name"] != "Experience":
            L.append(f"- {c['name']}: {round(c['value'] * 100)}%")
    y = a["years"]
    if y["jd"]:
        L.append(f"- Experience: role asks {y['jd']}+ years; resume shows "
                 f"{y['resume'] if y['resume'] is not None else 'unknown'}")
    L += ["", "## What you already have", ""]
    for r in a["reqs"]:
        if r["status"] == "matched":
            L.append(f"- **{r['label']}**{' (' + r['note'] + ')' if r['note'] else ''}: \"{r['evidence']}\"")
    L += ["", "## Gaps", ""]
    for r in a["reqs"]:
        if r["status"] != "matched":
            tag = "nice-to-have" if r["kind"] == "preferred" else "required"
            L.append(f"- **{r['label']}** ({tag}, {r['status']}){': ' + r['note'] if r['note'] else ''}")
    if a["other"]:
        L += ["", "## Other requirements", ""]
        for o in a["other"]:
            L.append(f"- {o['text']} ({o.get('status', 'unclear')})")
    L += ["", f"## Learning plan ({plan['hours_per_week']} h/week, about {plan['total_hours']} hours)", ""]
    for i, wk in enumerate(plan["weeks"], 1):
        L.append(f"### Week {i}")
        for it in wk:
            part = " (continued)" if it["part"] > 1 else ""
            gain = f" (+{it['gain']} points)" if it["finishes"] and it.get("gain", 0) > 0 else ""
            L.append(f"- **{it['name']}**{part}: {it['chunk']} h{gain}. {it['why'] if it['part'] == 1 else ''}".rstrip())
            if it["part"] == 1:
                for title, url in SKILL_BY_ID[it["skill"]]["res"]:
                    if url:
                        L.append(f"  - Learn: [{title}]({url})")
            if it["finishes"]:
                L.append(f"  - Show it: {SKILL_BY_ID[it['skill']]['project']}")
        L.append("")
    if plan["capstone"]:
        L += [f"### Then: capstone project", plan["capstone"]["text"], ""]
    if plan["tips"]:
        L += ["### Add to your resume, no study needed", ""]
        L += [f"- {t['name']}: the job says \"{t['jd_line']}\". Add a bullet that shows it." for t in plan["tips"]] + [""]
    if plan["later"]:
        L += ["### Later, if you have time", ""] + [f"- {it['name']} (~{it['hours']} h)" for it in plan["later"]] + [""]
    if coach_md:
        L += ["## AI coach", f"_{coach_label}_" if coach_label else "", "", coach_md, ""]
    L += ["---", "Generated by SkillBridge. Hours and scores are estimates to guide you, not guarantees."]
    return "\n".join(L)

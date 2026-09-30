"""HTML views for the SkillBridge UI. All user text is escaped."""
from html import escape as esc

from taxonomy import SKILL_BY_ID


def _pct(v):
    return "n/a" if v is None else f"{round(v * 100)}%"


def empty_state():
    return """<div class="sb-empty">
  <svg viewBox="0 0 220 60" aria-hidden="true" class="sb-empty-art">
    <path d="M6 44 Q110 -8 214 44" fill="none" stroke="currentColor" stroke-width="3"/>
    <line x1="6" y1="44" x2="214" y2="44" stroke="currentColor" stroke-width="3"/>
    <g stroke="currentColor" stroke-width="2">
      <line x1="40" y1="44" x2="40" y2="25"/><line x1="75" y1="44" x2="75" y2="12"/>
      <line x1="110" y1="44" x2="110" y2="9"/><line x1="145" y1="44" x2="145" y2="12"/>
      <line x1="180" y1="44" x2="180" y2="25"/></g>
  </svg>
  <p class="sb-empty-title">Your results appear here</p>
  <p>Add a resume and a job description, then choose <b>Analyze match</b>.
  No resume handy? Pick a sample on the left.</p>
</div>"""


def score_view(a, plan):
    comps = {c["name"]: c for c in a["components"]}
    y = a["years"]
    if y["jd"]:
        exp = (f"{y['resume']:g} yrs ({y['jd']}+ asked)" if y["resume"] is not None else f"Not found ({y['jd']}+ asked)")
    else:
        exp = "not specified"
    # The bridge: today's score, then one plank per planned skill.
    planks = []
    x = a["score"]
    for it in plan["items"]:
        if it.get("gain", 0) > 0:
            planks.append((x, it["gain"], it["name"]))
            x += it["gain"]
    plank_html = "".join(
        f'<span class="sb-plank" style="left:{s}%;width:{g}%" title="{esc(n)}: +{g}"></span>' for s, g, n in planks)
    tip_gain = sum(t["gain"] for t in plan.get("tips", []))
    proj = plan["projected"]
    tip_line = (f" Showing your soft skills on the resume could add about {tip_gain} more."
                if tip_gain > 0 else "")
    notes = "".join(f"<p class='sb-note'>{esc(n)}</p>" for n in a["notes"])
    sem = ("Semantic matching on" if a["semantic"] else "Keyword and taxonomy matching")
    return f"""<div class="sb-score">
  <div class="sb-score-top">
    <div class="sb-score-num"><span>{a['score']}</span><small>/100</small></div>
    <div class="sb-score-text">
      <p class="sb-role">Match for {esc(a['title'])}</p>
      <h2 class="sb-verdict">{esc(a['verdict'])}</h2>
      <p class="sb-detail">{esc(a['verdict_detail'])}</p>
    </div>
  </div>
  <div class="sb-bridge" role="img" aria-label="Score today {a['score']}, after the plan {proj}">
    <div class="sb-bridge-track">
      <span class="sb-today" style="width:{a['score']}%"></span>{plank_html}
    </div>
    <div class="sb-bridge-labels">
      <span>Today <b>{a['score']}</b></span>
      <span>After your plan <b>{proj}</b> · {len(plan['weeks'])} weeks at {plan['hours_per_week']} h</span>
    </div>
    <p class="sb-bridge-caption">Each amber plank is one skill from your plan, sized by how much it raises your score.{tip_line}</p>
  </div>
  <dl class="sb-stats">
    <div><dt>Required skills</dt><dd>{_pct(comps['Required skills']['value'])}</dd></div>
    <div><dt>Nice-to-haves</dt><dd>{_pct(comps['Nice-to-have skills']['value'])}</dd></div>
    <div><dt>Experience</dt><dd>{esc(exp)}</dd></div>
  </dl>
  <p class="sb-meta">{sem} · {a['resume_skill_count']} skills found on your resume</p>
  {notes}
</div>"""


def _row(r):
    asked = "Nice-to-have" if r["kind"] == "preferred" else "Required"
    anyof = '<span class="sb-tag">any one</span>' if r["any_of"] else ""
    note = f'<span class="sb-rnote">{esc(r["note"])}</span>' if r["note"] else ""
    ev = f'<blockquote>{esc(r["evidence"])}</blockquote>' if r["evidence"] and r["status"] != "missing" else ""
    if r["status"] == "missing" and r["via"] == "adjacent" and r["evidence"]:
        ev = f'<blockquote>{esc(r["evidence"])}</blockquote>'
    return f"""<li class="sb-req sb-{r['status']}">
  <div class="sb-req-head"><span class="sb-req-name">{esc(r['label'])}</span>{anyof}
    <span class="sb-asked sb-asked-{'pref' if r['kind'] == 'preferred' else 'req'}">{asked}</span></div>
  {note}{ev}
</li>"""


def skills_view(a):
    groups = [
        ("missing", "Missing", "Not found on your resume. These drive your plan."),
        ("partial", "Partly there", "Some evidence, but it reads as basic or indirect."),
        ("matched", "You have", "Found on your resume, with the line that proves it."),
    ]
    rank = {"required": 0, "resp": 0, "intro": 0, "preferred": 1}
    out = ['<div class="sb-skills">']
    cats = a["categories"]
    if cats:
        bars = "".join(
            f'<div class="sb-cat"><span>{esc(c)}</span><span class="sb-cat-bar"><i style="width:{round(v*100)}%"></i></span>'
            f'<b>{round(v*100)}%</b></div>' for c, v in cats.items())
        out.append(f'<section><h3>Coverage by area</h3><div class="sb-cats">{bars}</div></section>')
    for key, title, sub in groups:
        rs = sorted([r for r in a["reqs"] if r["status"] == key], key=lambda r: (rank[r["kind"]], -r["weight"]))
        if not rs:
            continue
        out.append(f'<section><h3>{title} <span class="sb-count">{len(rs)}</span></h3><p class="sb-sub">{sub}</p>'
                   f'<ul class="sb-reqs">{"".join(_row(r) for r in rs)}</ul></section>')
    if a["other"]:
        label = {"likely": "Likely covered", "partial": "Partly covered", "unclear": "Not evident"}
        items = "".join(
            f'<li class="sb-other sb-o-{o.get("status","unclear")}"><span class="sb-o-status">{label[o.get("status","unclear")]}</span>'
            f'<span>{esc(o["text"])}</span>'
            + (f'<blockquote>{esc(o["evidence"])}</blockquote>' if o.get("evidence") else "") + "</li>"
            for o in a["other"])
        how = "by meaning (embeddings)" if a["semantic"] else "by keywords"
        out.append(f'<section><h3>Other requirements</h3><p class="sb-sub">Lines that aren\'t a single skill, checked '
                   f'{how} against your resume.</p><ul class="sb-others">{items}</ul></section>')
    if a["extras"]:
        chips = "".join(f'<span class="sb-chip">{esc(SKILL_BY_ID[s]["name"])}</span>' for s in a["extras"])
        out.append(f'<section><h3>Also on your resume</h3><p class="sb-sub">Not asked for here, but worth keeping.</p>'
                   f'<div class="sb-chips">{chips}</div></section>')
    out.append("</div>")
    return "".join(out)


def plan_view(plan):
    if not plan["items"] and not plan["tips"]:
        return ('<div class="sb-plan"><p class="sb-lead">Nothing to learn for this role: you cover every skill we detected. '
                'Spend the time tailoring your resume and preparing stories for the interview.</p></div>')
    weeks = len(plan["weeks"])
    out = [f'<div class="sb-plan"><p class="sb-lead">About <b>{plan["total_hours"]} hours</b>: {weeks} week'
           f'{"s" if weeks != 1 else ""} at {plan["hours_per_week"]} h a week. Quickest score gains come first; '
           f'foundations come before the skills that need them. Your score goes from <b>{plan["base"]}</b> to '
           f'<b>{plan["projected"]}</b>.</p><ol class="sb-weeks">']
    for i, wk in enumerate(plan["weeks"], 1):
        hrs = sum(it["chunk"] for it in wk)
        rows = []
        for it in wk:
            s = SKILL_BY_ID[it["skill"]]
            cont = it["part"] > 1
            part = '<span class="sb-tag">continued</span>' if cont else ""
            gain = f'<span class="sb-gain">+{it["gain"]}</span>' if it["finishes"] and it.get("gain", 0) > 0 else ""
            also = f' Also covers {esc(", ".join(it["also"]))}.' if it["also"] and not cont else ""
            note = f' <span class="sb-rnote">{esc(it["note"][:1].upper() + it["note"][1:])}.</span>' if it["note"] and not cont else ""
            res = ""
            if not cont:
                links = []
                for title, url in s["res"]:
                    if url:
                        links.append(f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(title)}</a>')
                if links:
                    res = f'<p class="sb-res">Learn: {" · ".join(links)}</p>'
            proof = f'<p class="sb-proof">Show it: {esc(s["project"])}</p>' if it["finishes"] else ""
            why = "" if cont else f'<p class="sb-why">{esc(it["why"])}.{also}{note}</p>'
            rows.append(f'<li class="sb-item"><div class="sb-item-head"><span class="sb-item-name">{esc(it["name"])}</span>{part}'
                        f'<span class="sb-hours">{it["chunk"]} h</span>{gain}</div>'
                        f'{why}{res}{proof}</li>')
        out.append(f'<li class="sb-week"><div class="sb-week-label">Week {i}<small>{hrs} h</small></div>'
                   f'<ul class="sb-items">{"".join(rows)}</ul></li>')
    out.append("</ol>")
    if plan["capstone"]:
        out.append(f'<section class="sb-capstone"><h3>Then: one capstone project</h3><p>{esc(plan["capstone"]["text"])}</p></section>')
    if plan["tips"]:
        tips = "".join(
            f'<li><b>{esc(t["name"])}</b>: the job says “{esc(t["jd_line"])}”. Add one resume bullet that shows it, '
            f'with who you worked with and what changed.</li>' for t in plan["tips"])
        out.append(f'<section><h3>Add to your resume, no study needed</h3><ul class="sb-tips">{tips}</ul></section>')
    if plan["later"]:
        later = "".join(f'<li>{esc(it["name"])} <span class="sb-hours">{it["hours"]} h</span></li>' for it in plan["later"])
        out.append(f'<section><h3>Later, if you have time</h3><p class="sb-sub">Nice-to-haves that don\'t fit in 16 weeks at this pace.</p>'
                   f'<ul class="sb-later">{later}</ul></section>')
    out.append("</div>")
    return "".join(out)

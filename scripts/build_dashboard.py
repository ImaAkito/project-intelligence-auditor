#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_utils import load_json

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project Intelligence Command Center</title>
<style>
:root{color-scheme:dark;--bg:#090d14;--p:#101722;--p2:#151e2c;--l:#26354a;--t:#eef4ff;--m:#94a3b8;--a:#7dd3fc;--g:#86efac;--w:#fde68a;--b:#fca5a5}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0,rgba(125,211,252,.12),transparent 32rem),var(--bg);color:var(--t);font:14px/1.45 Inter,system-ui,sans-serif}
main{max-width:1450px;margin:auto;padding:22px}.top{display:flex;justify-content:space-between;gap:18px;align-items:center;margin-bottom:18px}.top h1{margin:0;font-size:28px}.muted{color:var(--m)}
nav{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}button,input{font:inherit}nav button,.close{border:1px solid var(--l);background:#101722;color:var(--m);border-radius:10px;padding:9px 12px;cursor:pointer}nav button.on{color:var(--t);border-color:#587493}
.panel{border:1px solid var(--l);background:linear-gradient(180deg,rgba(21,30,44,.95),rgba(16,23,34,.95));border-radius:16px;padding:18px;margin-bottom:16px;box-shadow:0 18px 45px rgba(0,0,0,.23)}
.hero{display:grid;grid-template-columns:1.4fr .8fr;gap:18px}.hero h2{font-size:clamp(32px,5vw,58px);line-height:1;margin:6px 0 12px;letter-spacing:-.05em}.eyebrow{color:var(--a);font-size:11px;font-weight:750;letter-spacing:.12em;text-transform:uppercase}
.bottleneck{border:1px solid #405775;border-radius:14px;padding:18px;background:rgba(125,211,252,.055)}.bottleneck h3{font-size:21px;margin:8px 0}
.scores{display:grid;grid-template-columns:repeat(6,minmax(130px,1fr));gap:10px}.score{border:1px solid var(--l);background:var(--p);border-radius:14px;padding:14px}.score .v{font-size:32px;font-weight:750;letter-spacing:-.04em}.bar{height:5px;background:#253448;border-radius:99px;overflow:hidden;margin-top:9px}.bar i{display:block;height:100%;background:linear-gradient(90deg,#7dd3fc,#a78bfa)}
.view{display:none}.view.on{display:block}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.modules{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.module{border:1px solid var(--l);background:#0d141f;border-radius:12px;padding:14px;cursor:pointer}.module:hover{border-color:#587493}.module h4{margin:0 0 5px}.row{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px solid var(--l)}.row:last-child{border:0}.pill{border:1px solid var(--l);border-radius:999px;padding:4px 7px;font-size:10px;text-transform:uppercase}.search{width:100%;padding:10px 12px;margin-bottom:12px;border:1px solid var(--l);border-radius:10px;background:#0b111b;color:var(--t)}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px;border-bottom:1px solid var(--l);vertical-align:top}th{color:var(--m);font-size:11px;text-transform:uppercase}
.riskmatrix{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.cell{min-height:70px;border:1px solid var(--l);border-radius:9px;padding:6px}.cell.h{background:rgba(252,165,165,.11)}.cell.m{background:rgba(253,230,138,.08)}.cell.l{background:rgba(134,239,172,.05)}.r{font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.action{display:grid;grid-template-columns:65px 1fr auto;gap:10px;padding:11px 0;border-bottom:1px solid var(--l)}.phase{color:var(--a);font-weight:750}.action h4{margin:0 0 4px}.lev{font-size:19px;font-weight:700}
.evidence{border:1px solid var(--l);border-radius:11px;padding:11px;margin:8px 0;background:#0e1621}.level{color:var(--a);font-weight:750}
.graph{width:100%;height:430px;border:1px solid var(--l);border-radius:12px;background:#0b111b}.edge{stroke:#39506b;stroke-width:1.3}.node rect{fill:#152131;stroke:#52708f;rx:9}.node text{fill:#eef4ff;font-size:10px}.node{cursor:pointer}
.drawer{position:fixed;right:0;top:0;height:100vh;width:min(520px,92vw);background:#0d141f;border-left:1px solid var(--l);padding:20px;overflow:auto;transform:translateX(102%);transition:.2s;z-index:50}.drawer.on{transform:translateX(0)}
@media(max-width:1050px){.scores{grid-template-columns:repeat(3,1fr)}.modules{grid-template-columns:repeat(2,1fr)}}@media(max-width:720px){main{padding:12px}.hero,.grid{grid-template-columns:1fr}.scores{grid-template-columns:repeat(2,1fr)}.modules{grid-template-columns:1fr}.action{grid-template-columns:55px 1fr}.lev{grid-column:2}.top{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body><main>
<div class="top"><div><h1>Project Intelligence Command Center</h1><div id="meta" class="muted"></div></div><div id="conf" class="pill"></div></div>
<nav id="nav"><button class="on" data-v="overview">Overview</button><button data-v="modules">Modules</button><button data-v="architecture">Architecture</button><button data-v="risks">Risks</button><button data-v="actions">What should I do now?</button><button data-v="commercial">Commercial</button><button data-v="evidence">Evidence</button></nav>
<section id="overview" class="view on">
<div class="panel hero"><div><div class="eyebrow">Evidence-backed project state</div><h2 id="name"></h2><p id="mission" class="muted"></p><div id="stage"></div></div><div class="bottleneck"><div class="eyebrow">Biggest bottleneck</div><h3 id="bn"></h3><p id="bnwhy" class="muted"></p></div></div>
<div id="scores" class="scores"></div><div class="grid"><div class="panel"><h3>Highest-leverage actions</h3><div id="quick"></div></div><div class="panel"><h3>Project signals</h3><div id="signals"></div></div></div>
</section>
<section id="modules" class="view"><div class="panel"><h3>Module health map</h3><input id="msearch" class="search" placeholder="Filter modules"><div id="mods" class="modules"></div></div></section>
<section id="architecture" class="view"><div class="panel"><h3>Architecture & dependency graph</h3><svg id="graph" class="graph" viewBox="0 0 1100 430"></svg><p class="muted">Missing edges mean unknown, not independent.</p></div></section>
<section id="risks" class="view"><div class="grid"><div class="panel"><h3>Probability × impact</h3><div id="matrix" class="riskmatrix"></div></div><div class="panel"><h3>Highest risks</h3><div id="risklist"></div></div></div></section>
<section id="actions" class="view"><div class="panel"><h3>What should I do now?</h3><div id="alist"></div></div></section>
<section id="commercial" class="view"><div class="grid"><div class="panel"><h3>Commercial readiness</h3><div id="comm"></div></div><div class="panel"><h3>Development directions</h3><div id="dirs"></div></div></div></section>
<section id="evidence" class="view"><div class="panel"><h3>Evidence explorer</h3><input id="esearch" class="search" placeholder="Search claims, paths, levels"><div id="elist"></div></div></section>
</main><aside id="drawer" class="drawer"><button id="x" class="close">Close</button><div id="detail"></div></aside>
<script id="data" type="application/json">__DATA__</script>
<script>
const A=JSON.parse(document.getElementById("data").textContent),q=s=>document.querySelector(s),L=x=>Array.isArray(x)?x:[],E=x=>String(x??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;");
const S=x=>typeof x==="number"&&Number.isFinite(x)?x:null,T=x=>S(x)===null?"—":Math.round(x)+"%",C=x=>S(x)===null?"var(--m)":x>=75?"var(--g)":x>=50?"var(--w)":"var(--b)";
function kv(k,v){return `<div class="row"><span class="muted">${E(k)}</span><strong>${E(v??"Unknown")}</strong></div>`}
function evidenceCard(e){return `<div class="evidence"><span class="level">${E(e.level||"E0")}</span> <strong>${E(e.kind||"evidence")}</strong><div>${E(e.claim||"")}</div><small class="muted">${E(e.location||e.source||"")}</small></div>`}
function actionCard(a){return `<div class="action"><div class="phase">${E(a.phase||a.priority||"—")}</div><div><h4>${E(a.title)}</h4><div class="muted">${E(a.why||a.rationale||a.definition_of_done||"")}</div></div><div class="lev">${E(a.leverage_score??"—")}</div></div>`}
function header(){let m=A.metadata||{},p=A.project||{},b=L(A.bottlenecks)[0]||{};q("#name").textContent=p.name||"Unnamed project";q("#mission").textContent=p.mission||"Mission not verified.";q("#meta").textContent=`Snapshot ${m.generated_at?new Date(m.generated_at).toLocaleString():"unknown"} · auditor ${m.auditor_version||"unknown"}`;q("#conf").textContent="Confidence "+T((A.scores||{}).confidence);q("#bn").textContent=b.title||"Not yet identified";q("#bnwhy").textContent=b.why||b.description||"No evidence-backed bottleneck recorded.";q("#stage").innerHTML=[["Stage",p.current_stage],["TRL",p.trl],["Commit",m.commit&&String(m.commit).slice(0,10)]].filter(x=>x[1]!=null&&x[1]!=="").map(x=>`<span class="pill">${E(x[0])}: ${E(x[1])}</span>`).join(" ")}
const scoreDefs=[["confirmed_completion","Confirmed completion"],["estimated_completion","Estimated completion"],["project_health","Project health"],["mvp_readiness","MVP readiness"],["production_readiness","Production readiness"],["commercial_readiness","Commercial readiness"],["research_readiness","Research readiness"],["scale_readiness","Scale readiness"],["confidence","Confidence"]];
function scores(){let s=A.scores||{};q("#scores").innerHTML=scoreDefs.map(([k,n])=>{let v=S(s[k]),w=v===null?0:Math.max(0,Math.min(100,v));return `<div class="score"><div class="muted">${E(n)}</div><div class="v" style="color:${C(v)}">${T(v)}</div><div class="bar"><i style="width:${w}%"></i></div></div>`}).join("")}
function openMod(m){let ids=new Set(L(m.evidence_ids)),ev=L(A.evidence).filter(e=>ids.has(e.id));q("#detail").innerHTML=`<div class="eyebrow">Module drill-down</div><h2>${E(m.name)}</h2><p class="muted">${E(m.responsibility||"Responsibility not recorded.")}</p>${[["Classification",m.classification],["Completion",T(m.completion)],["Confirmed",T(m.confirmed_completion)],["Quality",T(m.quality)],["Confidence",T(m.confidence)],["Evidence",m.evidence_level],["Path",m.path]].map(x=>kv(...x)).join("")}<h3>Dependencies</h3><p>${L(m.dependencies).length?L(m.dependencies).map(E).join(" · "):"Unknown / none recorded"}</p><h3>Evidence</h3>${ev.length?ev.map(evidenceCard).join(""):'<p class="muted">No linked evidence.</p>'}`;q("#drawer").classList.add("on")}
function modules(f=""){let n=f.toLowerCase(),ms=L(A.modules).filter(m=>[m.name,m.path,m.role_hint,m.classification].join(" ").toLowerCase().includes(n));q("#mods").innerHTML=ms.length?ms.map((m,i)=>`<div class="module" data-i="${i}"><div style="display:flex;justify-content:space-between;gap:8px"><div><h4>${E(m.name)}</h4><small class="muted">${E(m.role_hint||m.path||"module")}</small></div><span class="pill">${E(m.classification||"unknown")}</span></div>${kv("Completion",T(m.completion))}${kv("Quality",T(m.quality))}${kv("Confidence",T(m.confidence))}</div>`).join(""):'<p class="muted">No modules match.</p>';document.querySelectorAll("[data-i]").forEach(el=>el.onclick=()=>openMod(ms[+el.dataset.i]))}
function evidence(f=""){let n=f.toLowerCase(),ev=L(A.evidence).filter(e=>[e.level,e.kind,e.claim,e.location,e.source].join(" ").toLowerCase().includes(n));q("#elist").innerHTML=ev.length?ev.map(evidenceCard).join(""):'<p class="muted">No matching evidence.</p>'}
function actions(){let order={NOW:0,NEXT:1,LATER:2,OPTIONAL:3,DEFER:4,REMOVE:5},a=L(A.recommendations).slice().sort((x,y)=>(order[x.phase]??9)-(order[y.phase]??9)||Number(y.leverage_score||0)-Number(x.leverage_score||0));q("#alist").innerHTML=a.length?a.map(actionCard).join(""):'<p class="muted">No recommendations.</p>';q("#quick").innerHTML=a.length?a.slice(0,4).map(actionCard).join(""):'<p class="muted">No ranked actions.</p>'}
function risks(){let r=L(A.risks).map(x=>({...x,score:Number(x.score||Number(x.probability)*Number(x.impact)||0)}));let cells=[];for(let i=5;i>=1;i--)for(let p=1;p<=5;p++){let z=r.filter(x=>+x.impact===i&&+x.probability===p),v=i*p,c=v>=15?"h":v>=8?"m":"l";cells.push(`<div class="cell ${c}"><small class="muted">P${p}×I${i}</small>${z.map(x=>`<div class="r" title="${E(x.title)}">${E(x.title)}</div>`).join("")}</div>`)}q("#matrix").innerHTML=cells.join("");r.sort((a,b)=>b.score-a.score);q("#risklist").innerHTML=r.length?`<table><thead><tr><th>Risk</th><th>Category</th><th>Score</th></tr></thead><tbody>${r.slice(0,12).map(x=>`<tr><td><strong>${E(x.title)}</strong><br><small class="muted">${E(x.mitigation||"")}</small></td><td>${E(x.category||"—")}</td><td>${E(x.score)}</td></tr>`).join("")}</tbody></table>`:'<p class="muted">No risks recorded.</p>'}
function commercial(){let c=A.commercialization||{};q("#comm").innerHTML=[["Target customer",c.target_customer||c.icp],["Value proposition",c.value_proposition],["Technical moat",c.technical_moat],["Data moat",c.data_moat],["Time to revenue",c.time_to_revenue],["Primary blocker",c.primary_blocker]].map(x=>kv(...x)).join("");let d=L(A.directions);q("#dirs").innerHTML=d.length?d.map(x=>`<div class="evidence"><strong>${E(x.name||x.title||"Direction")}</strong><div>${E(x.description||x.rationale||"")}</div><small class="muted">Score ${E(x.direction_score??"—")} · MVP ${E(x.time_to_mvp??"—")}</small></div>`).join(""):'<p class="muted">No directions recorded.</p>'}
function signals(){let m=L(A.modules),v=L(A.validation_runs);q("#signals").innerHTML=[["Modules",m.length],["Critical path",m.filter(x=>x.classification==="critical_path").length],["Low/unknown confidence",m.filter(x=>S(x.confidence)===null||x.confidence<50).length],["Failed validations",v.filter(x=>x.status==="tested_fail").length],["Limitations",L(A.limitations).length]].map(x=>kv(...x)).join("")}
function graph(){let svg=q("#graph"),m=L(A.modules);if(!m.length){svg.innerHTML='<text x="30" y="45" fill="#94a3b8">No modules.</text>';return}let cols=Math.ceil(Math.sqrt(m.length*1.7)),rows=Math.ceil(m.length/cols),pos=new Map;m.forEach((x,i)=>pos.set(String(x.id),{x:(i%cols)*1100/cols+550/cols,y:Math.floor(i/cols)*430/rows+215/rows}));let ed=[];m.forEach(x=>L(x.dependencies).forEach(d=>{if(pos.has(String(d))&&pos.has(String(x.id)))ed.push([String(d),String(x.id)])}));L(A.dependency_edges).forEach(x=>{let f=String(x.from||x.source||""),t=String(x.to||x.target||"");if(pos.has(f)&&pos.has(t))ed.push([f,t])});svg.innerHTML=`<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0L10 5L0 10z" fill="#39506b"/></marker></defs>${ed.map(([f,t])=>{let a=pos.get(f),b=pos.get(t);return `<line class="edge" marker-end="url(#arr)" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}"/>`}).join("")}${m.map(x=>{let p=pos.get(String(x.id));return `<g class="node" data-g="${E(x.id)}" transform="translate(${p.x-65},${p.y-24})"><rect width="130" height="48"/><text x="65" y="20" text-anchor="middle">${E(String(x.name||x.id).slice(0,20))}</text><text x="65" y="35" text-anchor="middle">${T(x.completion)}</text></g>`}).join("")}`;document.querySelectorAll("[data-g]").forEach(el=>el.onclick=()=>{let x=m.find(y=>String(y.id)===el.dataset.g);if(x)openMod(x)})}
header();scores();modules();evidence();actions();risks();commercial();signals();graph();
q("#msearch").oninput=e=>modules(e.target.value);q("#esearch").oninput=e=>evidence(e.target.value);q("#x").onclick=()=>q("#drawer").classList.remove("on");document.onkeydown=e=>{if(e.key==="Escape")q("#x").click()};document.querySelectorAll("#nav button").forEach(b=>b.onclick=()=>{document.querySelectorAll("#nav button").forEach(x=>x.classList.remove("on"));document.querySelectorAll(".view").forEach(x=>x.classList.remove("on"));b.classList.add("on");q("#"+b.dataset.v).classList.add("on");if(b.dataset.v==="architecture")graph()});
</script></body></html>"""


def render(data: dict[str, Any]) -> str:
    serialized = json.dumps(data, ensure_ascii=False).replace("</script>", r"<\/script>")
    return TEMPLATE.replace("__DATA__", serialized)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a standalone Project Intelligence Command Center.")
    parser.add_argument("audit", type=Path)
    parser.add_argument("-o", "--output", type=Path, default=Path(".project-audit/PROJECT_COMMAND_CENTER.html"))
    args = parser.parse_args()
    document = render(load_json(args.audit))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8")
    print(f"Wrote Project Command Center to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

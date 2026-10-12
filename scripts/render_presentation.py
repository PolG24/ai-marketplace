"""Render the self-contained 20-minute deck and its speaker notes. No dependencies."""

from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SLIDES = []


def slide(section, title, duration, body, notes, *, dark=False, css="", takeaway="", appendix=False):
    SLIDES.append(dict(section=section, title=title, duration=duration, body=body,
                       notes=notes, dark=dark, css=css, takeaway=takeaway, appendix=appendix))


# === STORY: PROBLEM, PRINCIPLES, AND THE ASSET MODEL ===
slide("Challenge B / AI Marketplace", "Engineering AI Marketplace", 30, '''
<h1 class="reveal" data-edit>Useful once.<br><span class="accent">Trusted across teams.</span></h1>
<p class="subtitle reveal" data-edit>A marketplace for supported AI capabilities<br>across software, hardware and simulation.</p>
<div class="title-line reveal"><span data-edit>Discover</span> → <span data-edit>Trust</span> → <span data-edit>Reuse</span></div>
<div class="title-orbit" aria-hidden="true"><i></i><b>REUSE / 01</b></div>
''', [
"Open with the design intent: teams already create useful AI helpers. The challenge is making those capabilities discoverable, credible and safe for someone outside the author’s team.",
"This presentation follows the decisions from that problem to a usable service, then shows the working validator and how we would decide what deserves continued investment."
], dark=True, css="title")

slide("01 / Frame the problem", "Every reuse starts with three questions.", 50, '''
<div class="three problem reveal">
 <div class="block"><div class="verb" data-edit>Find it.</div><p data-edit>Which helper solves my engineering task?</p><p class="micro gap" data-edit>Scattered repositories and team knowledge.</p></div>
 <div class="block"><div class="verb" data-edit>Trust it.</div><p data-edit>Who supports it, and what evidence backs it?</p><p class="micro gap" data-edit>Unknown quality, ownership and permissions.</p></div>
 <div class="block"><div class="verb" data-edit>Use it.</div><p data-edit>Can I adopt it within my existing access?</p><p class="micro gap" data-edit>One-off setup and credentials.</p></div>
</div>
''', [
"Walk through the experience of an engineer who hears that another team has a useful Jira helper. Finding a repository is only the first step. They still need to know whether it is maintained, what it can access and whether its outputs are reliable.",
"That diagnosis motivates a marketplace with an operating model. A directory alone would leave the trust and adoption questions unanswered."
], takeaway="Design target: <strong>a supported capability another team can actually adopt.</strong>")

slide("01 / Design principles", "Make the safe path the easiest path.", 50, '''
<div class="three reveal">
 <div><div class="big-number">01</div><div class="rule"></div><h3 data-edit>Start with the task</h3><p data-edit>Search by engineering need, domain and permitted data.</p></div>
 <div><div class="big-number">02</div><div class="rule"></div><h3 data-edit>Make trust inspectable</h3><p data-edit>Show owner, approved version, permissions and evaluation evidence.</p></div>
 <div><div class="big-number">03</div><div class="rule"></div><h3 data-edit>Enforce at the boundary</h3><p data-edit>Use managed execution and connectors that check each operation.</p></div>
</div>
''', [
"Explain these as decision criteria. Task-oriented discovery helps engineers who do not know whether they need an agent, skill or server. Visible evidence makes adoption a considered engineering choice.",
"The third principle is the safety boundary: a prompt or publisher declaration cannot enforce access. Identity, policy and resource controls must do that independently of the model."
], dark=True, takeaway="Team owners maintain assets. <strong>The platform owns packaging, execution and policy.</strong>")

slide("02 / Asset model", "One marketplace. Different engineering effects.", 60, '''
<table class="asset-table reveal"><thead><tr><th>Capability</th><th>Who uses it</th><th>What needs control</th></tr></thead><tbody>
<tr><td data-edit>Story → test plan<span class="type">AGENT</span></td><td data-edit>Software / firmware</td><td data-edit>Authorized stories; human review of coverage</td></tr>
<tr><td data-edit>Security triage<span class="type">SKILL</span></td><td data-edit>All teams</td><td data-edit>Recommendations stay separate from human decisions</td></tr>
<tr><td data-edit>Lab instruments<span class="type">MCP SERVER</span></td><td data-edit>Hardware</td><td data-edit>Bounded commands, equipment access, physical interlocks</td></tr>
<tr><td data-edit>Simulation jobs<span class="type">MCP SERVER</span></td><td data-edit>Simulation</td><td data-edit>Compute budgets, job ownership, traceable results</td></tr>
</tbody></table>
''', [
"An agent coordinates work. A skill supplies a reviewed procedure and is loaded by a runner. An MCP server exposes capabilities. Agents can compose the other building blocks, but every component and dependency must belong to the approved release.",
"Point out why a common manifest does not imply identical controls. A draft test plan, an instrument command and a simulation job have different consequences. MCP is an integration interface; it does not supply authorization or physical safety by itself."
])

slide("02 / Additional asset", "Publish the evidence as a reusable asset.", 50, '''
<div class="two reveal">
 <div><span class="pill">PROPOSED TYPE / EVALUATION PACK</span><h3 class="large gap" data-edit>A shared yardstick<br>for competing versions.</h3><p class="gap muted" data-edit>Sanitized cases + expert criteria + scoring code.</p></div>
 <div class="panel teal"><div class="label">JIRA TEST-PLAN BASELINE</div><div class="row"><div class="big-number" style="font-size:70px">A</div><p data-edit>Current release</p></div><div class="rule"></div><div class="row"><div class="big-number" style="font-size:70px">B</div><p data-edit>Candidate release</p></div><div class="rule"></div><p data-edit>Same pack and model configuration.<br>Compare coverage and invented requirements.</p></div>
</div>
''', [
"The bring-your-own asset is an evaluation pack. Authors use it while improving assets; QA and reviewers use it to assess candidate releases. Independent ownership of the baseline helps avoid every author defining their own success criteria.",
"It belongs in the marketplace when multiple assets or teams reuse it. Version it, review both fixtures and scorer, and pin it in release evidence. If the baseline changes, evaluate both current and candidate releases again. Passing provides evidence, never a universal quality guarantee."
], takeaway="Why it belongs: <strong>reuse quality criteria as well as code.</strong>")

# === DECISIONS: EXECUTION AND ARCHITECTURE ===
slide("03 / Execution decision", "Enable an approved service in a managed workspace.", 70, '''
<div class="compare reveal">
 <div class="panel"><div class="label">OPTION CONSIDERED</div><h3 data-edit>Local executable installation</h3><p class="option" data-edit>Familiar workflow and local flexibility.</p><div class="rule"></div><p data-edit>Harder to enforce connector use, isolate dependencies and revoke running releases.</p></div>
 <div class="panel teal chosen"><div class="label">CHOSEN FOR THE PILOT</div><h3 data-edit>Managed execution</h3><p class="option" data-edit>Pinned releases, isolated runners and live policy.</p><div class="rule"></div><p data-edit>Central enforcement and revocation, with added operating cost and availability dependence.</p></div>
</div>
''', [
"The challenge asks how an engineer installs an asset. The design deliberately makes installation an enable action in a managed workspace. Engineers receive access to an approved service, rather than arbitrary executable downloads.",
"This is a tradeoff. Managed execution makes isolation, credential handling and revocation enforceable, but requires platform operations and dependable authorization services. Sensitive actions fail closed if approval or authorization is unavailable. Lab and simulation workers can run near the resources; approved IDE clients could later connect remotely."
], takeaway="Motivation: <strong>keep enforcement independent of asset code and prompts.</strong>")

ARCHITECTURE = '''
<svg class="diagram reveal" viewBox="0 0 1712 530" role="img" aria-labelledby="archTitle archDesc">
<title id="archTitle">Publication and managed execution architecture</title>
<desc id="archDesc">Bitbucket submissions pass Jenkins, scans and independent review before exact-digest promotion to the catalog and approved Artifactory. Corporate identity gates isolated execution of approved releases. Managed connectors enforce access to models and resources and obtain credentials from Vault. Runtime events feed audit and outcome telemetry.</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#3d706f"/></marker></defs>
<rect class="lane" x="0" y="0" width="1712" height="172"/><text class="d-label" x="24" y="31">PUBLISH / UNTRUSTED SUBMISSION → APPROVED RELEASE</text>
<rect class="box" x="24" y="56" width="340" height="91"/><text class="d-title" x="44" y="93">Bitbucket</text><text class="d-small" x="44" y="126">Manifest · code · tests</text>
<path class="flow" d="M364 103H435"/><rect class="trusted" x="442" y="56" width="370" height="91"/><text class="d-title" x="462" y="93">Jenkins + scans</text><text class="d-small" x="462" y="126">Black Duck / Polaris · evals</text>
<path class="flow" d="M812 103H880"/><rect class="trusted" x="888" y="56" width="348" height="91"/><text class="d-title" x="908" y="93">Review + promotion</text><text class="d-small" x="908" y="126">Approve the exact digest</text>
<path class="flow" d="M1236 103H1304"/><rect class="trusted" x="1312" y="56" width="376" height="91"/><text class="d-title" x="1332" y="93">Catalog + Artifactory</text><text class="d-small" x="1332" y="126">Approved metadata + artifacts</text>
<text class="d-label" x="24" y="233">USE / PLATFORM-CONTROLLED EXECUTION</text>
<rect class="box" x="24" y="262" width="235" height="110"/><text class="d-title" x="44" y="303">Engineer</text><text class="d-small" x="44" y="340">Portal / workspace</text>
<path class="flow" d="M259 318H320"/><rect class="trusted" x="328" y="262" width="274" height="110"/><text class="d-title" x="348" y="303">Identity + policy</text><text class="d-small" x="348" y="340">User · live approval</text>
<path class="flow" d="M602 318H665"/><rect class="trusted" x="673" y="262" width="285" height="110"/><text class="d-title" x="693" y="303">Isolated runner</text><text class="d-small" x="693" y="340">Pinned release + deps</text>
<path class="flow" d="M958 318H1020"/><rect class="trusted" x="1028" y="262" width="322" height="110"/><text class="d-title" x="1048" y="303">Managed connectors</text><text class="d-small" x="1048" y="340">Model gateway / MCP / APIs</text>
<path class="flow" d="M1350 318H1412"/><rect class="box" x="1420" y="250" width="268" height="136"/><text class="d-title" x="1440" y="287">Resources</text><text class="d-small" x="1440" y="322">Models · Jira · findings</text><text class="d-small" x="1440" y="356">Labs · schedulers</text>
<path class="flow" d="M1500 147V203H814V254"/><text class="d-label" x="980" y="194">APPROVED RELEASE ONLY</text>
<rect class="trusted" x="1028" y="426" width="322" height="76"/><text class="d-title" x="1050" y="472">Vault</text><text class="d-small" x="1160" y="472">Scoped credentials</text><path class="flow dashed" d="M1189 426V380"/>
<rect class="box" x="328" y="426" width="630" height="76"/><text class="d-title" x="348" y="455">Audit + outcome telemetry</text><text class="d-small" x="348" y="485">Versions · decisions · quality · cost; redact payloads</text><path class="flow" d="M465 372V418"/><path class="flow" d="M814 372V418"/>
</svg>'''

slide("03 / Architecture", "Build around the tools teams already use.", 95, ARCHITECTURE, [
"Read the diagram in two lanes. In the publishing lane, teams use Bitbucket. Jenkins builds into restricted Artifactory staging and runs required checks, including applicable Black Duck or Polaris scans. Review and the platform promotion service bind approval to the exact artifact digest. Only approved releases are visible and readable by production runners.",
"In the execution lane, corporate identity and current policy gate a pinned isolated runner. All resource and model traffic passes through managed connectors; network controls prevent bypass. Connectors hold downstream Vault credentials and verify user and workload identity for each sensitive operation.",
"Catalog metadata contains approvals and discoverability information, not engineering payloads. Confluence provides guides; Jira tracks review, incidents and retirement. Telemetry records versions and outcomes with payload minimization. Hardware and simulation workers are deployed close to their resources with equivalent controls."
], takeaway="Confluence: guides · Jira: reviews and incidents · <strong>Network policy prevents connector bypass.</strong>")

slide("04 / Manifest contract", "Declare the requirements before granting access.", 75, '''
<div class="two reveal" style="grid-template-columns:1.05fr 1fr;gap:60px">
 <div class="terminal"><div class="label" style="color:#a6e1d1;margin-bottom:22px">EXCERPT / JIRA TEST-PLAN AGENT</div><pre class="manifest-code">"id": "jira-test-plan",
"kind": "agent", "version": "1.0.0",
"owner": { "team": "software-quality", … },
"execution": { "profile": "managed-agent" },
"permissions": [{
  "capability": "jira.issues.read",
  "resources": ["project:ENG"]
}],
"data": { "classification": "internal",
          "model_route": "enterprise-default" },
"secret_refs": ["jira-reader"]</pre></div>
 <div class="lines"><p data-edit><strong>Accountability</strong><br><span class="muted">Owner, support, version, artifact + digest</span></p><p data-edit><strong>Requested access</strong><br><span class="muted">Explicit capabilities, resource scopes, managed profile</span></p><p data-edit><strong>Data boundary</strong><br><span class="muted">Classification, approved model route, logical secret references</span></p></div>
</div>
''', [
"This is a visual excerpt, not a complete manifest. The complete contract also requires schema_version, an immutable artifact location and a SHA-256 digest. The validator checks the format and allowed location, not the contents of the artifact.",
"Explain the contract as three questions: who is accountable and which release is this; what capabilities does it request; and where can its data and credentials go. The permission is scoped to project ENG rather than all Jira. The secret reference is a logical connector mapping, never a secret value.",
"Trusted configuration resolves execution profiles, model aliases and credential references. Publishers cannot self-declare approval or choose arbitrary endpoints. Classification must also be checked at runtime so a publisher label cannot downgrade the actual data."
], takeaway="Decision: <strong>the manifest declares needs; trusted policy and resource owners authorize them.</strong>")

slide("04 / Publishing and trust", "Approval belongs to an exact release.", 80, '''
<div class="flowline reveal">
 <div class="node"><div class="label">01 / SUBMIT</div><h3 data-edit>Bitbucket</h3><p data-edit>Manifest, package, guide, tests and evaluations.</p></div>
 <div class="node"><div class="label">02 / VERIFY</div><h3 data-edit>Jenkins</h3><p data-edit>Policy, provenance, security/license scans and quality gates.</p></div>
 <div class="node"><div class="label">03 / REVIEW</div><h3 data-edit>Domain owners</h3><p data-edit>Assess evidence, scopes and consequences.</p></div>
 <div class="node"><div class="label">04 / PROMOTE</div><h3 data-edit>Platform service</h3><p data-edit>Activate the catalog entry and approved artifact digest.</p></div>
</div>
<div class="boundary reveal"><p data-edit><strong>Restricted staging → approved repository</strong></p><p class="micro gap" data-edit>Required checks fail or are unavailable? Promotion stops. Production runners cannot read staging.</p></div>
''', [
"Publishing is a promotion workflow, not an upload that immediately appears in the catalog. Jenkins builds the candidate into restricted staging. Every required gate must succeed. Missing checks or unsupported scan coverage need resolution or review rather than silent passing.",
"Review is risk-specific. Security, lab and simulation owners review the effects and quotas they understand. High-impact contributors cannot approve their own releases. Approval records the reviewer, policy version, digest, configuration, dependencies, permitted use and expiry.",
"Only the platform promotion service can move the reviewed digest to the approved repository and activate the catalog entry. This closes the gap between reviewing one artifact and running a different one."
], dark=True, takeaway="Motivation: <strong>what was reviewed must be what engineers run.</strong>")

slide("04 / Lifecycle", "Trust must survive change—and be revocable.", 65, '''
<div class="lifecycle reveal"><div class="state">Candidate</div><span class="arr">→</span><div class="state active-state">Approved</div><span class="arr">→</span><div class="state">Deprecated</div><span class="arr">→</span><div class="state">Retired / expired</div></div>
<div class="two gap reveal" style="margin-top:65px"><div><h3 data-edit>Change triggers review</h3><p data-edit>Code, dependencies, prompts, skills, models or permissions require relevant re-evaluation.</p></div><div><h3 data-edit>Revocation is operational</h3><p data-edit>Block new runs; revoke access; interrupt jobs where possible; use safe lab stops.</p></div></div>
''', [
"An approved release is not permanently trusted. Owners maintain it, respond to incidents and handle scheduled review. Changes to prompts and model configuration matter as well as changes to executable code.",
"Deprecation gives consumers migration guidance. Retirement or expiry blocks new runs. Emergency revocation is a separate action that disables a release and revokes access immediately, including from the approved state. Connectors check live approval. Rollback is permitted only to a release that remains approved.",
"Be explicit about practical limits: external jobs need cancellation through their schedulers, and lab equipment needs safe stop behavior. Returned data and completed physical actions cannot be undone."
], takeaway="Motivation: <strong>safe reuse requires maintenance and a credible exit path.</strong>")

# === ENGINEER EXPERIENCE AND RUNTIME SAFETY ===
slide("05 / Engineer journey", "From an engineering task to a reviewed draft.", 60, '''
<div class="walkthrough reveal"><div class="steps"><h3 data-edit>01 / Discover</h3><p data-edit>Search by task, domain and allowed data.</p><h3 data-edit>02 / Enable</h3><p data-edit>Inspect the release and permissions.</p><h3 data-edit>03 / Run + review</h3><p data-edit>Submit a story ID. Check coverage and assumptions.</p></div>
<div class="catalog" aria-label="Illustrative asset detail, not a working marketplace"><div class="bar"><strong>ENGINEERING AI MARKETPLACE</strong><span>Managed workspace</span></div><div class="search">Find a capability: Jira story → test plan</div><div class="detail"><span class="pill">APPROVED / v1.0.0</span><h3 class="gap" data-edit>Jira test-plan agent</h3><p class="micro" data-edit>Draft a plan mapped to acceptance criteria.</p><div class="meta"><span>Owner: software-quality</span><span>Data: internal</span><span>Shared evaluation evidence</span></div><p class="scope">jira.issues.read · project:ENG</p><span class="cta">Enable approved version</span><p class="micro gap" data-edit>Guide · Examples · Limitations · Support</p></div></div></div>
''', [
"Use the Jira example as the through-line. The engineer searches for the task rather than an implementation type. Catalog visibility already respects access restrictions. The detail page exposes owner, version, evidence, limitations, permission scope and support before enablement.",
"Enabling creates access in a managed workspace. The engineer supplies a story ID, the connector checks access and selects only the fields permitted for the model route, and the agent produces a draft. The engineer checks references to acceptance criteria, assumptions and gaps before adopting it.",
"The product panel is an illustrative design mockup. The working deliverable is the manifest validator."
], takeaway="Design choice: <strong>permission and evidence inspection are part of adoption.</strong>")

slide("05 / Effective access", "An asset can only narrow the engineer’s access.", 80, '''
<p class="large reveal" data-edit>Every sensitive operation must satisfy all four limits.</p>
<div class="intersections reveal"><div class="term" data-edit>User rights</div><div class="term" data-edit>Approved asset scope</div><div class="term" data-edit>Current policy</div><div class="term" data-edit>Run’s resource needs</div></div>
<div class="access-result reveal"><div><p data-edit><strong>User can read ENG and FW.</strong><br>Asset is approved for ENG only.</p></div><p data-edit><strong class="accent">ENG only</strong><br><span class="muted">FW requests are denied.</span></p></div>
<p class="micro gap reveal" data-edit>Include field and classification limits. Resource content and model output remain untrusted.</p>
''', [
"Explain the intersection as the effective authorization model. A service account may have broad technical access, but it must never substitute for the engineer’s own rights. A request must also remain within the reviewed asset’s scope, current policy and the resources needed for this run.",
"Use the ENG and FW example. Even an engineer allowed to access both projects cannot use an ENG-only asset against FW. Conversely, asset scope never gives an engineer access to a project they cannot read.",
"Connectors validate both user and workload identity and recheck sensitive operations and downstream authorization. Field selection and data classification apply inside a project. Malicious story content or model output cannot widen access because those checks operate outside the prompt."
], takeaway="Motivation: <strong>reuse must never become privilege escalation.</strong>")

slide("05 / Secrets", "Put downstream credentials at the connector boundary.", 60, '''
<div class="secrets-flow reveal">
 <div class="panel"><div class="label">ASSET PACKAGE</div><h3 data-edit>Logical reference</h3><pre>"secret_refs":
  ["jira-reader"]</pre><p class="micro gap" data-edit>A request for a mapping.<br>No credential is bundled.</p></div>
 <div class="panel teal connector"><div class="label">TRUSTED CONNECTOR</div><h3 data-edit>Authorize + resolve</h3><p data-edit>Check user, release, scope and destination.</p><p class="micro gap" data-edit>Keep credentials outside asset and model context.</p></div>
 <div class="panel"><div class="label">DOWNSTREAM RESOURCE</div><h3 data-edit>Bounded operation</h3><p data-edit>Read only authorized Jira fields.</p><p class="micro gap" data-edit>Resource authorization still applies.</p></div>
</div><div class="vault reveal"><strong>Vault → connector</strong><span>Delegated access or short-lived scoped credentials where supported.</span></div>
''', [
"The manifest requests a logical secret reference. Resource owners approve the connector scope and credential mapping; merely naming jira-reader gives the asset no credential access.",
"The connector uses delegated user access or scoped short-lived Vault credentials where supported. Some systems may require static credentials, which must be rotated separately. The credential stays with the connector, out of packages, model context and logs.",
"This arrangement also motivates restricted egress. If the asset could bypass the connector and call arbitrary destinations, the boundary would not hold. Audit logging records decisions and versions while minimizing sensitive payloads."
], takeaway="Motivation: <strong>make the approved access path enforceable and auditable.</strong>")

slide("05 / Domain controls", "Higher-impact work needs domain-owned safeguards.", 65, '''
<div class="two reveal"><div class="panel"><div class="label">HARDWARE / LAB</div><h3 data-edit>Bound the physical effect</h3><ul class="list"><li data-edit>Equipment authorization and exclusive access</li><li data-edit>Command limits and independent interlocks</li><li data-edit>Safe stops on interruption or revocation</li></ul></div><div class="panel"><div class="label">SIMULATION</div><h3 data-edit>Bound the job and its cost</h3><ul class="list"><li data-edit>Compute and license budgets</li><li data-edit>Job ownership and scheduler cancellation</li><li data-edit>Parameters and raw results remain traceable</li></ul></div></div>
''', [
"These assets are in the architecture, but the initial validator policy intentionally rejects lab-control and simulation-submission permissions. They enter the marketplace only after domain profiles and controls have been validated.",
"For hardware, equipment owners control authorization and exclusive access. Independent physical interlocks remain essential; they cannot be replaced by model instructions. Revocation needs safe stop behavior rather than simply killing arbitrary processes.",
"For simulation, control the run’s resource budget, license consumption, ownership and cancellation. Summaries must be traceable to the exact parameters and raw results so engineers can inspect unsupported claims. Domain owners approve these effects; generated text cannot authorize them."
], dark=True, takeaway="Decision: <strong>expand after the domain controls are proven.</strong>")

# === WORKING PIECE, MEASUREMENT, AND ROLLOUT ===
slide("06 / Working piece", "Reject an unsafe declaration before it can publish.", 85, '''
<div class="two reveal" style="grid-template-columns:.92fr 1.08fr;gap:45px"><div><h3 data-edit>Manifest validator</h3><p data-edit>Strict JSON → typed contract → trusted pilot policy</p><div class="rule"></div><p data-edit>Change just one declared resource:</p><pre class="demo-code gap" id="demoManifest">"capability": "jira.issues.read",
"resources": ["project:ENG"]</pre><div class="rule"></div><div class="row"><div class="big-number" style="font-size:82px">19</div><p data-edit>tests pass<br><span class="micro">Structure, policy and CLI behavior</span></p></div></div>
<div class="terminal"><div class="label" style="color:#a6e1d1;margin-bottom:22px">CAPTURED CLI OUTPUT / DEMO REPLAY</div><pre id="demoOutput"><span class="comment">$ python3 -m manifest_validator examples/jira-agent.json</span>

<span class="ok">PASS: static pilot validation only;
production approval is still required.</span>

<span class="comment">exit 0</span></pre><div class="demo-controls"><button type="button" id="validDemo" class="selected" aria-pressed="true">Explicit scope</button><button type="button" id="unsafeDemo" aria-pressed="false">Wildcard scope</button></div><p class="micro gap" style="color:#b6c8cb" data-edit>Also rejects unknown fields, prohibited data,<br>unsupported capabilities and embedded credentials.</p></div></div>
''', [
"Introduce what actually works: a local Python CLI, with no live integrations, that parses JSON strictly, applies a typed contract and checks trusted policy stored separately from publisher input. The current suite has 19 test methods, including CLI exit-code behavior.",
"Click Explicit scope and Wildcard scope to replay captured output. The only changed declaration is project:ENG versus *. The unsafe manifest is rejected with a stable resource_scope code and the exact permissions field path. This HTML replays the real CLI output; it does not run Python in the browser.",
"For a live terminal demo, run the two commands in the notes. Exit 0 means static checks passed, exit 1 means policy or structure rejection, and exit 2 means input failure. A passing manifest still needs provenance, content scanning, quality evaluation, approval and runtime authorization. The validator neither fetches artifacts nor executes submissions."
], takeaway="Prototype proves: <strong>unsafe manifest declarations can fail a Jenkins gate.</strong>")

slide("07 / Value", "Measure time to an accepted engineering result.", 75, '''
<div class="metric-formula reveal"><div class="term" data-edit>Execution</div><span class="operator">+</span><div class="term" data-edit>Engineer review</div><span class="operator">+</span><div class="term" data-edit>Correction</div></div>
<p class="micro gap reveal" data-edit>Compare similar tasks against a baseline. Agree acceptable quality with domain owners.</p>
<div class="metric-support reveal"><div><h3 data-edit>Quality</h3><p data-edit>Coverage, missed cases, unsupported claims and rework.</p></div><div><h3 data-edit>Reuse</h3><p data-edit>Repeat accepted outcomes across distinct teams.</p></div><div><h3 data-edit>Cost + reliability</h3><p data-edit>Cost per accepted result, failures and maintenance effort.</p></div></div>
''', [
"The value metric deliberately includes review and correction. A fast draft that takes more time to repair may have little engineering value. Compare similar tasks, record versions and model configuration, and use domain-reviewed quality thresholds.",
"Quality is a gate on speed claims. Track omissions, invented requirements, unsupported claims and downstream rework. Repeat cross-team accepted outcomes demonstrate reuse; downloads or invocations alone do not.",
"Measure cost per accepted result, latency, failures and owner effort. Track denied operations and security incidents separately. Use task-level aggregates rather than developer rankings, and avoid storing raw stories or prompts just to produce analytics. Targets are pilot hypotheses, not achieved results."
], takeaway="Keep / improve / retire using <strong>benefit, quality, cost, risk and active ownership.</strong>")

slide("07 / Pilot and adoption", "Prove usefulness first. Expand with evidence.", 100, '''
<div class="roadmap reveal"><div class="phase"><div class="step-number">01 / PILOT</div><h3 data-edit>Read-only workflows</h3><p data-edit>Jira test planning and security triage across a few teams.</p><p class="micro gap" data-edit>Public/internal data; approved model routes.</p></div><div class="phase"><div class="step-number">02 / EARN REUSE</div><h3 data-edit>Onboard and measure</h3><p data-edit>Confluence guides, demos, team representatives and targeted notices.</p><p class="micro gap" data-edit>Reach → trial → accepted result → repeat use.</p></div><div class="phase"><div class="step-number">03 / EXPAND</div><h3 data-edit>Domain capabilities</h3><p data-edit>Lab instruments and simulation after domain safeguards are validated.</p><p class="micro gap" data-edit>Keep useful assets; retire unsupported releases.</p></div></div>
<div class="boundary reveal"><p data-edit><strong>Ownership is part of the product.</strong></p><p class="micro gap" data-edit>Asset teams support releases. The platform runs policy and execution. Domain owners approve higher-impact use.</p></div>
''', [
"Start with Jira test-plan drafts and read-only security triage because they deliver useful engineering assistance while keeping the initial effects bounded. The pilot excludes restricted and unclassified data and uses approved enterprise model routes.",
"Evaluate sanitized cases and representative real tasks with human review. Agree thresholds before interpreting speed gains. Record asset and pack versions, local cases and model configuration so results can be reproduced.",
"Adoption requires work beyond activating a catalog entry: representatives, onboarding, Confluence links, demos and targeted notices. Authorized task and team metadata can help recommend relevant assets, including through agentic matching. Recommendations must respect catalog visibility; owners review outreach and subscriptions or digests limit noise.",
"Then expand to lab and simulation after validating domain controls. The exit criteria are as important as adoption: sustained accepted outcomes, maintained quality and active ownership. Improve fixable gaps; retire excessive cost, unresolved risk, poor quality or unsupported releases."
], takeaway="Motivation: <strong>a marketplace creates value when another team succeeds with it.</strong>")

slide("08 / The design in one sentence", "Supported capabilities, with evidence and boundaries.", 50, '''
<div class="hero reveal" data-edit>Make useful AI work<br><span class="accent">safe to discover,<br>trust and reuse.</span></div>
<div class="three reveal"><div><h3 data-edit>Discover</h3><p data-edit>Task-led catalog and accountable owners.</p></div><div><h3 data-edit>Trust</h3><p data-edit>Exact-release approval and shared evaluations.</p></div><div><h3 data-edit>Reuse</h3><p data-edit>Managed execution within existing access.</p></div></div>
''', [
"Close by returning to the original problem. Each design decision removes a specific barrier: task-led discovery makes assets findable; inspectable evidence and release-bound approval support trust; managed execution and connectors make cross-team use governable.",
"The delivered design document defines the architecture, and the working validator demonstrates the first policy gate. The next proof is a pilot that improves time to accepted results without lowering quality. Pause and invite discussion. The remaining three slides are reference material for questions, outside the 20-minute talk."
], dark=True, css="closing")

# === REFERENCE APPENDIX: KEPT OUTSIDE THE 20-MINUTE TIMING ===
slide("Appendix / Complete manifest", "The complete pilot contract.", 0, '''
<div class="two reveal" style="grid-template-columns:1.35fr .65fr;gap:60px"><div class="terminal"><pre style="font-size:23px;line-height:1.48">{
  "schema_version": "1",
  "id": "jira-test-plan", "kind": "agent", "version": "1.0.0",
  "owner": { "team": "software-quality",
             "contact": "software-quality@example.internal" },
  "artifact": {
    "uri": "https://artifactory.example.internal/ai-assets/
            jira-test-plan/1.0.0/agent.tar.gz",
    "sha256": "0123456789abcdef… (64 hexadecimal characters)"
  },
  "execution": { "profile": "managed-agent" },
  "permissions": [{ "capability": "jira.issues.read",
                    "resources": ["project:ENG"] }],
  "data": { "classification": "internal",
            "model_route": "enterprise-default" },
  "secret_refs": ["jira-reader"]
}</pre></div><div><h3 data-edit>All fields required</h3><p data-edit>Empty permissions and secret references are explicit.</p><div class="rule"></div><h3 data-edit>Illustrative values</h3><p data-edit>Host, contact and digest are placeholders.</p><p class="micro gap" data-edit>URI wrapped and digest shortened for readability. Use examples/jira-agent.json for executable JSON.</p></div></div>
''', [
"Use this reference for contract questions. The projected URI is visually wrapped and the digest is abbreviated. The exact runnable file is examples/jira-agent.json.",
"The validator rejects unknown fields at every object level and duplicate keys during parsing. Production profiles would additionally address compatibility, evaluations, destinations, budgets and retention."
], appendix=True)

slide("Appendix / Prototype boundary", "What the validator proves—and what still needs controls.", 0, '''
<div class="two reveal"><div class="panel teal"><div class="label">IMPLEMENTED + TESTED</div><h3 data-edit>Static declarations</h3><ul class="list"><li data-edit>Strict JSON, required fields and types</li><li data-edit>Managed profiles and explicit allowed scopes</li><li data-edit>Artifact format, data/model routes, secret references</li></ul></div><div class="panel"><div class="label">PRODUCTION DESIGN</div><h3 data-edit>Release + runtime evidence</h3><ul class="list"><li data-edit>Artifact contents, provenance and ownership</li><li data-edit>Security scans, quality evaluations and approval</li><li data-edit>Actual user access, credentials and behavior</li></ul></div></div>
''', [
"Clarify that the validator checks declared values against a trusted illustrative policy, not the truth of those declarations. It cannot verify artifact contents, corporate ownership, authentic scans, effective user rights or AI quality.",
"Unknown credential fields are rejected, but arbitrary strings may still contain hidden secrets. Actual package and secret scanning remain required. No runtime or marketplace portal has been implemented in this prototype."
], takeaway="A validation pass is <strong>input to release review, never production approval.</strong>", appendix=True)

slide("Appendix / Decision register", "Every decision answers a specific failure mode.", 0, '''
<table class="asset-table appendix-table reveal"><thead><tr><th>Decision</th><th>Motivation</th><th>Tradeoff / condition</th></tr></thead><tbody>
<tr><td data-edit>Managed execution</td><td data-edit>Enforce isolation, credentials and revocation</td><td data-edit>Platform cost and availability</td></tr>
<tr><td data-edit>Exact-digest promotion</td><td data-edit>Run the artifact that reviewers assessed</td><td data-edit>Release discipline and gate latency</td></tr>
<tr><td data-edit>Explicit scoped access</td><td data-edit>Prevent reuse from widening user rights</td><td data-edit>Connector and resource-owner work</td></tr>
<tr><td data-edit>Shared evaluation packs</td><td data-edit>Make quality comparisons repeatable</td><td data-edit>Benchmarks need maintenance and local cases</td></tr>
<tr><td data-edit>Read-only pilot</td><td data-edit>Validate value with bounded effects</td><td data-edit>Lab and simulation effects come later</td></tr>
</tbody></table>
''', ["Use this slide to revisit the reasoning during discussion. These choices aim to reduce specific operational or adoption failures while acknowledging the work they introduce."], appendix=True)


# === CONTROLLER: NAVIGATION, NOTES, REHEARSAL, AND INLINE EDITING ===
CONTROLLER = r'''
/* === SLIDE PRESENTATION CONTROLLER === */
class SlidePresentation {
  constructor() {
    this.slides = [...document.querySelectorAll('.slide')]; this.currentSlide = 0;
    this.stage = document.getElementById('deckStage'); this.notesOpen = false;
    this.editing = false; this.startTime = null; this.wheelTime = 0;
    this.loadEdits();
    // Remove obsolete section numbers from labels cached by earlier deck versions.
    document.querySelectorAll('.eyebrow').forEach(el => { el.textContent = el.textContent.replace(/^\d{2} \/ /, ''); });
    this.setupStageScale(); this.setupNavigation(); this.setupEditing();
    this.showSlide(this.hashIndex());
    window.addEventListener('hashchange', () => this.showSlide(this.hashIndex()));
    setInterval(() => this.updateTimer(), 1000);
  }
  hashIndex() { return Math.max(0, (parseInt(location.hash.replace('#',''),10)||1)-1); }
  setupStageScale() {
    const fit = () => { const s = Math.min(innerWidth/1920,innerHeight/1080);
      this.stage.style.transform = `translate(${(innerWidth-1920*s)/2}px, ${(innerHeight-1080*s)/2}px) scale(${s})`; };
    fit(); window.addEventListener('resize',fit);
  }
  goToSlide(i) { this.showSlide(i); }
  showSlide(i) {
    this.currentSlide = Math.max(0,Math.min(i,this.slides.length-1));
    this.slides.forEach((s,j) => { const active = j===this.currentSlide;
      s.classList.toggle('active',active); s.classList.toggle('visible',active); s.setAttribute('aria-hidden',String(!active)); s.inert=!active; });
    const appendix=this.currentSlide>=18;
    document.getElementById('counter').textContent = appendix ? `Appendix ${this.currentSlide-17} / 3` : `${this.currentSlide+1} / 18`;
    document.getElementById('progress').style.width = `${Math.min(this.currentSlide+1,18)/18*100}%`;
    document.getElementById('prev').disabled=this.currentSlide===0;
    document.getElementById('next').disabled=this.currentSlide===this.slides.length-1;
    try { history.replaceState(null,'',`#${this.currentSlide+1}`); } catch {}
    this.updateNotes();
  }
  setupNavigation() {
    document.getElementById('prev').onclick=()=>this.showSlide(this.currentSlide-1);
    document.getElementById('next').onclick=()=>this.showSlide(this.currentSlide+1);
    document.getElementById('notesButton').onclick=()=>this.toggleNotes();
    document.getElementById('fullButton').onclick=()=>this.fullscreen();
    document.getElementById('timerButton').onclick=()=>{this.startTime=Date.now();this.updateTimer();};
    document.addEventListener('keydown', e=>{
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();this.saveFile();return;}
      if(e.target.isContentEditable || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) return;
      if(e.ctrlKey||e.metaKey||e.altKey)return;
      if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)) { if(e.target.closest('button')&&e.key===' ')return;e.preventDefault();this.showSlide(this.currentSlide+1); }
      if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)) {e.preventDefault();this.showSlide(this.currentSlide-1);}
      if(e.key==='Home')this.showSlide(0); if(e.key==='End')this.showSlide(this.slides.length-1);
      if(e.key.toLowerCase()==='n')this.toggleNotes(); if(e.key.toLowerCase()==='f')this.fullscreen();
      if(e.key.toLowerCase()==='e')this.toggleEdit();
      if(e.key.toLowerCase()==='t'){this.startTime=Date.now();this.updateTimer();}
      if(e.key==='Escape'){if(this.editing)this.toggleEdit();if(this.notesOpen)this.toggleNotes();}
    });
    let startX=0,startY=0;
    this.stage.addEventListener('touchstart',e=>{startX=e.changedTouches[0].clientX;startY=e.changedTouches[0].clientY;},{passive:true});
    this.stage.addEventListener('touchend',e=>{if(this.editing||e.target.closest('button'))return;const x=e.changedTouches[0].clientX-startX,y=e.changedTouches[0].clientY-startY;if(Math.abs(x)>45&&Math.abs(x)>Math.abs(y))this.showSlide(this.currentSlide+(x<0?1:-1));},{passive:true});
    this.stage.addEventListener('wheel',e=>{if(this.editing||Math.abs(e.deltaY)<25)return;e.preventDefault();if(Date.now()-this.wheelTime<600)return;this.wheelTime=Date.now();this.showSlide(this.currentSlide+(e.deltaY>0?1:-1));},{passive:false});
  }
  toggleNotes(){this.notesOpen=!this.notesOpen;document.getElementById('notesPanel').hidden=!this.notesOpen;document.getElementById('notesButton').setAttribute('aria-expanded',String(this.notesOpen));this.updateNotes();}
  updateNotes(){const s=slideData[this.currentSlide], prior=slideData.slice(0,this.currentSlide).reduce((n,x)=>n+x.duration,0);const fmt=x=>`${Math.floor(x/60)}:${String(x%60).padStart(2,'0')}`;
    const panel=document.getElementById('notesPanel'); panel.replaceChildren();
    const timing=document.createElement('div');timing.className='timing';timing.textContent=s.appendix?'REFERENCE / OUTSIDE TALK':`${fmt(prior)}–${fmt(prior+s.duration)} / ${s.duration}s`;panel.append(timing);
    const h=document.createElement('h2');h.textContent=s.title;panel.append(h);
    s.notes.forEach(note=>{const p=document.createElement('p');p.textContent=note;panel.append(p);});
  }
  updateTimer(){if(this.startTime===null)return;const sec=Math.floor((Date.now()-this.startTime)/1000);document.getElementById('timerButton').textContent=`${Math.floor(sec/60)}:${String(sec%60).padStart(2,'0')}`;}
  async fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{this.notice('Fullscreen is unavailable in this browser.');}}
  /* === INLINE EDITOR: LOCAL AUTOSAVE + PORTABLE FILE EXPORT === */
  setupEditing(){let delay;const hot=document.getElementById('editHotzone'),button=document.getElementById('editToggle');
    for(const el of [hot,button]){el.addEventListener('mouseenter',()=>{clearTimeout(delay);button.classList.add('show');});el.addEventListener('mouseleave',()=>{delay=setTimeout(()=>{if(!this.editing)button.classList.remove('show');},400);});}
    hot.onclick=()=>this.toggleEdit();button.onclick=()=>this.toggleEdit();
    document.querySelectorAll('[data-edit]').forEach(el=>{el.addEventListener('input',()=>this.storeEdits());el.addEventListener('paste',e=>{if(!this.editing)return;e.preventDefault();const text=e.clipboardData.getData('text/plain');document.execCommand('insertText',false,text);});});
  }
  toggleEdit(){this.editing=!this.editing;document.body.classList.toggle('editing',this.editing);const button=document.getElementById('editToggle');button.classList.toggle('active',this.editing);button.textContent=this.editing?'Done editing (E)':'Edit text (E)';document.querySelectorAll('[data-edit]').forEach(el=>{if(this.editing)el.setAttribute('contenteditable','true');else el.removeAttribute('contenteditable');});if(this.editing)this.notice('Edit text directly. Ctrl/Cmd+S downloads a portable HTML copy.');else this.storeEdits();}
  storeEdits(){try{localStorage.setItem('engineering-marketplace-deck-v1',JSON.stringify([...document.querySelectorAll('[data-edit]')].map(el=>el.innerHTML)));}catch{}}
  loadEdits(){try{const saved=JSON.parse(localStorage.getItem('engineering-marketplace-deck-v1')||'null');if(Array.isArray(saved))document.querySelectorAll('[data-edit]').forEach((el,i)=>{if(typeof saved[i]==='string')el.innerHTML=saved[i];});}catch{}}
  saveFile(){if(this.editing)this.toggleEdit();const clone=document.documentElement.cloneNode(true);clone.querySelectorAll('[contenteditable]').forEach(el=>el.removeAttribute('contenteditable'));clone.querySelector('body').classList.remove('editing');clone.querySelector('#notesPanel').hidden=true;clone.querySelector('#notice').hidden=true;clone.querySelector('#editToggle').classList.remove('active','show');clone.querySelector('#editToggle').textContent='Edit text (E)';const url=URL.createObjectURL(new Blob(['<!DOCTYPE html>\n'+clone.outerHTML],{type:'text/html'}));const a=document.createElement('a');a.href=url;a.download='ai-marketplace-presentation.html';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);this.notice('Saved an HTML copy with your edits.');}
  notice(message){const el=document.getElementById('notice');el.textContent=message;el.hidden=false;clearTimeout(this.noticeTimeout);this.noticeTimeout=setTimeout(()=>el.hidden=true,3500);}
}
/* === DEMO REPLAY: CAPTURED OUTPUT, NOT BROWSER EXECUTION === */
function replayDemo(unsafe){document.getElementById('demoManifest').textContent=`"capability": "jira.issues.read",\n"resources": ["${unsafe?'*':'project:ENG'}"]`;
  const out=document.getElementById('demoOutput');out.replaceChildren();const command=document.createElement('span');command.className='comment';command.textContent=`$ python3 -m manifest_validator examples/${unsafe?'unsafe-jira-agent':'jira-agent'}.json\n\n`;out.append(command);
  const result=document.createElement('span');result.className=unsafe?'reject':'ok';result.textContent=unsafe?'REJECTED\n$["permissions"][0]["resources"][0]\n[resource_scope]: Use an explicitly\nconfigured scope for this capability':'PASS: static pilot validation only;\nproduction approval is still required.';out.append(result);
  const status=document.createElement('span');status.className='comment';status.textContent=`\n\nexit ${unsafe?1:0}`;out.append(status);
  for(const [id,selected]of [['validDemo',!unsafe],['unsafeDemo',unsafe]]){const b=document.getElementById(id);b.classList.toggle('selected',selected);b.setAttribute('aria-pressed',String(selected));}
}
document.getElementById('validDemo').onclick=()=>replayDemo(false);document.getElementById('unsafeDemo').onclick=()=>replayDemo(true);
window.presentation=new SlidePresentation();
'''


def fmt(seconds):
    return f"{seconds // 60}:{seconds % 60:02}"


def render():
    assert sum(s["duration"] for s in SLIDES) == 1200
    theme = (ROOT / "scripts/presentation_theme.css").read_text()
    base = (ROOT / ".agents/skills/frontend-slides/viewport-base.css").read_text()
    fonts = (ROOT / ".frontend-slides/fonts.css").read_text()
    font_licenses = json.dumps((ROOT / ".frontend-slides/fonts-licenses.txt").read_text()).replace("</", "<\\/")
    sections = []
    for i, s in enumerate(SLIDES):
        classes = "slide " + ("dark " if s["dark"] else "") + s["css"] + (" active visible" if i == 0 else "")
        heading = "" if s["css"] in ("title", "closing") else f'<h2 class="reveal" data-edit>{escape(s["title"])}</h2>'
        topic_label = re.sub(r"^\d{2} / ", "", s["section"])
        number = f"A{i-17}" if s["appendix"] else f"{i+1:02d} / 18"
        takeaway = f'<div class="takeaway reveal">{s["takeaway"]}</div>' if s["takeaway"] else ""
        sections.append(f'''<!-- === SLIDE {i+1}: {escape(s['title'])} === -->
<section class="{classes}" aria-label="{escape(s['title'])}" aria-hidden="{'false' if i == 0 else 'true'}">
<p class="eyebrow reveal" data-edit>{escape(topic_label)}</p>{heading}
<div class="body">{s['body']}</div>{takeaway}
<footer class="foot"><span>ENGINEERING AI MARKETPLACE</span><span>{number}</span></footer></section>''')
    data = json.dumps([{k: s[k] for k in ("title", "duration", "notes", "appendix")} for s in SLIDES]).replace("</", "<\\/")
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A 20-minute design presentation: internal AI marketplace, decisions, trust, safe reuse and a working manifest validator.">
<title>Engineering AI Marketplace — Design decisions</title>
<style>/* === EMBEDDED GOOGLE FONTS: OFFLINE-READY LATIN FACES === */\n{fonts}\n{base}\n{theme}</style></head><body>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">{''.join(sections)}</main></div>
<!-- === PRESENTER UI: NEVER PART OF SLIDE CONTENT === -->
<nav class="deck-controls" aria-label="Presentation controls"><button id="prev" aria-label="Previous slide">←</button><span id="counter" aria-live="polite">1 / 18</span><button id="next" aria-label="Next slide">→</button><button id="notesButton" aria-expanded="false" aria-controls="notesPanel" title="Speaker notes (N)">Notes</button><button id="timerButton" title="Start or restart rehearsal timer (T)">Start timer</button><button id="fullButton" title="Fullscreen (F)">⛶</button></nav>
<div class="progress" id="progress" aria-hidden="true"></div>
<div class="edit-hotzone" id="editHotzone" aria-hidden="true"></div><button class="edit-toggle" id="editToggle" title="Edit text (E)">Edit text (E)</button>
<aside class="notes-panel" id="notesPanel" aria-label="Speaker notes" hidden></aside><div class="notice" id="notice" role="status" hidden></div>
<script type="application/json" id="fontLicenses">{font_licenses}</script>
<script>const slideData={data};\n{CONTROLLER}</script></body></html>'''
    (ROOT / "docs/presentation.html").write_text(html)
    notes = ["# Engineering AI Marketplace — Speaker notes", "", "18 speaking slides · 20:00 total · 3 appendix slides for questions.", "", "Open `presentation.html` in a browser. Arrow keys / Space move forward; N opens notes; F opens fullscreen; T starts or restarts the timer. E enables text editing. Ctrl/Cmd+S saves an HTML copy. Swipe works on touchscreens.", "", "The demo buttons replay captured CLI output; they do not execute Python. The product screen is an illustrative design mockup.", "", "## Rehearsal and live demo", "", "Use the suggested timing as a pacing guide. Prefer explaining the decision and motivation over reading slide text. The appendix is outside the 20-minute talk.", "", "For the actual CLI demo, from the repository root:", "", "```sh", "source .venv/bin/activate", "python3 -m manifest_validator examples/jira-agent.json", "python3 -m manifest_validator examples/unsafe-jira-agent.json", "python3 -m unittest discover -s tests -v", "```", "", "The unsafe command intentionally exits 1. Do not chain it with `&&` before commands you still want to run. Exit 0 is a static validation pass; 1 is rejection; 2 is input failure.", ""]
    elapsed = 0
    for i, s in enumerate(SLIDES):
        timing = "Reference / untimed" if s["appendix"] else f"{fmt(elapsed)}–{fmt(elapsed+s['duration'])} · {s['duration']} seconds"
        notes += [f"## {i+1}. {s['title']}", "", timing, ""]
        notes += [n + "\n" for n in s["notes"]]
        elapsed += s["duration"]
    (ROOT / "docs/presentation-notes.md").write_text("\n".join(notes))
    print(f"Rendered {len(SLIDES)} slides: 18 speaking slides / {fmt(elapsed)} + 3 appendix slides")


if __name__ == "__main__":
    render()

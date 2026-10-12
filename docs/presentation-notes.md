# Engineering AI Marketplace — Speaker notes

18 speaking slides · 20:00 total · 3 appendix slides for questions.

Open `presentation.html` in a browser. Arrow keys / Space move forward; N opens notes; F opens fullscreen; T starts or restarts the timer. E enables text editing. Ctrl/Cmd+S saves an HTML copy. Swipe works on touchscreens.

The demo buttons replay captured CLI output; they do not execute Python. The product screen is an illustrative design mockup.

## Rehearsal and live demo

Use the suggested timing as a pacing guide. Prefer explaining the decision and motivation over reading slide text. The appendix is outside the 20-minute talk.

For the actual CLI demo, from the repository root:

```sh
source .venv/bin/activate
python3 -m manifest_validator examples/jira-agent.json
python3 -m manifest_validator examples/unsafe-jira-agent.json
python3 -m unittest discover -s tests -v
```

The unsafe command intentionally exits 1. Do not chain it with `&&` before commands you still want to run. Exit 0 is a static validation pass; 1 is rejection; 2 is input failure.

## 1. Engineering AI Marketplace

0:00–0:30 · 30 seconds

Open with the design intent: teams already create useful AI helpers. The challenge is making those capabilities discoverable, credible and safe for someone outside the author’s team.

This presentation follows the decisions from that problem to a usable service, then shows the working validator and how we would decide what deserves continued investment.

## 2. Every reuse starts with three questions.

0:30–1:20 · 50 seconds

Walk through the experience of an engineer who hears that another team has a useful Jira helper. Finding a repository is only the first step. They still need to know whether it is maintained, what it can access and whether its outputs are reliable.

That diagnosis motivates a marketplace with an operating model. A directory alone would leave the trust and adoption questions unanswered.

## 3. Make the safe path the easiest path.

1:20–2:10 · 50 seconds

Explain these as decision criteria. Task-oriented discovery helps engineers who do not know whether they need an agent, skill or server. Visible evidence makes adoption a considered engineering choice.

The third principle is the safety boundary: a prompt or publisher declaration cannot enforce access. Identity, policy and resource controls must do that independently of the model.

## 4. One marketplace. Different engineering effects.

2:10–3:10 · 60 seconds

An agent coordinates work. A skill supplies a reviewed procedure and is loaded by a runner. An MCP server exposes capabilities. Agents can compose the other building blocks, but every component and dependency must belong to the approved release.

Point out why a common manifest does not imply identical controls. A draft test plan, an instrument command and a simulation job have different consequences. MCP is an integration interface; it does not supply authorization or physical safety by itself.

## 5. Publish the evidence as a reusable asset.

3:10–4:00 · 50 seconds

The bring-your-own asset is an evaluation pack. Authors use it while improving assets; QA and reviewers use it to assess candidate releases. Independent ownership of the baseline helps avoid every author defining their own success criteria.

It belongs in the marketplace when multiple assets or teams reuse it. Version it, review both fixtures and scorer, and pin it in release evidence. If the baseline changes, evaluate both current and candidate releases again. Passing provides evidence, never a universal quality guarantee.

## 6. Enable an approved service in a managed workspace.

4:00–5:10 · 70 seconds

The challenge asks how an engineer installs an asset. The design deliberately makes installation an enable action in a managed workspace. Engineers receive access to an approved service, rather than arbitrary executable downloads.

This is a tradeoff. Managed execution makes isolation, credential handling and revocation enforceable, but requires platform operations and dependable authorization services. Sensitive actions fail closed if approval or authorization is unavailable. Lab and simulation workers can run near the resources; approved IDE clients could later connect remotely.

## 7. Build around the tools teams already use.

5:10–6:45 · 95 seconds

Read the diagram in two lanes. In the publishing lane, teams use Bitbucket. Jenkins builds into restricted Artifactory staging and runs required checks, including applicable Black Duck or Polaris scans. Review and the platform promotion service bind approval to the exact artifact digest. Only approved releases are visible and readable by production runners.

In the execution lane, corporate identity and current policy gate a pinned isolated runner. All resource and model traffic passes through managed connectors; network controls prevent bypass. Connectors hold downstream Vault credentials and verify user and workload identity for each sensitive operation.

Catalog metadata contains approvals and discoverability information, not engineering payloads. Confluence provides guides; Jira tracks review, incidents and retirement. Telemetry records versions and outcomes with payload minimization. Hardware and simulation workers are deployed close to their resources with equivalent controls.

## 8. Declare the requirements before granting access.

6:45–8:00 · 75 seconds

This is a visual excerpt, not a complete manifest. The complete contract also requires schema_version, an immutable artifact location and a SHA-256 digest. The validator checks the format and allowed location, not the contents of the artifact.

Explain the contract as three questions: who is accountable and which release is this; what capabilities does it request; and where can its data and credentials go. The permission is scoped to project ENG rather than all Jira. The secret reference is a logical connector mapping, never a secret value.

Trusted configuration resolves execution profiles, model aliases and credential references. Publishers cannot self-declare approval or choose arbitrary endpoints. Classification must also be checked at runtime so a publisher label cannot downgrade the actual data.

## 9. Approval belongs to an exact release.

8:00–9:20 · 80 seconds

Publishing is a promotion workflow, not an upload that immediately appears in the catalog. Jenkins builds the candidate into restricted staging. Every required gate must succeed. Missing checks or unsupported scan coverage need resolution or review rather than silent passing.

Review is risk-specific. Security, lab and simulation owners review the effects and quotas they understand. High-impact contributors cannot approve their own releases. Approval records the reviewer, policy version, digest, configuration, dependencies, permitted use and expiry.

Only the platform promotion service can move the reviewed digest to the approved repository and activate the catalog entry. This closes the gap between reviewing one artifact and running a different one.

## 10. Trust must survive change—and be revocable.

9:20–10:25 · 65 seconds

An approved release is not permanently trusted. Owners maintain it, respond to incidents and handle scheduled review. Changes to prompts and model configuration matter as well as changes to executable code.

Deprecation gives consumers migration guidance. Retirement or expiry blocks new runs. Emergency revocation is a separate action that disables a release and revokes access immediately, including from the approved state. Connectors check live approval. Rollback is permitted only to a release that remains approved.

Be explicit about practical limits: external jobs need cancellation through their schedulers, and lab equipment needs safe stop behavior. Returned data and completed physical actions cannot be undone.

## 11. From an engineering task to a reviewed draft.

10:25–11:25 · 60 seconds

Use the Jira example as the through-line. The engineer searches for the task rather than an implementation type. Catalog visibility already respects access restrictions. The detail page exposes owner, version, evidence, limitations, permission scope and support before enablement.

Enabling creates access in a managed workspace. The engineer supplies a story ID, the connector checks access and selects only the fields permitted for the model route, and the agent produces a draft. The engineer checks references to acceptance criteria, assumptions and gaps before adopting it.

The product panel is an illustrative design mockup. The working deliverable is the manifest validator.

## 12. An asset can only narrow the engineer’s access.

11:25–12:45 · 80 seconds

Explain the intersection as the effective authorization model. A service account may have broad technical access, but it must never substitute for the engineer’s own rights. A request must also remain within the reviewed asset’s scope, current policy and the resources needed for this run.

Use the ENG and FW example. Even an engineer allowed to access both projects cannot use an ENG-only asset against FW. Conversely, asset scope never gives an engineer access to a project they cannot read.

Connectors validate both user and workload identity and recheck sensitive operations and downstream authorization. Field selection and data classification apply inside a project. Malicious story content or model output cannot widen access because those checks operate outside the prompt.

## 13. Put downstream credentials at the connector boundary.

12:45–13:45 · 60 seconds

The manifest requests a logical secret reference. Resource owners approve the connector scope and credential mapping; merely naming jira-reader gives the asset no credential access.

The connector uses delegated user access or scoped short-lived Vault credentials where supported. Some systems may require static credentials, which must be rotated separately. The credential stays with the connector, out of packages, model context and logs.

This arrangement also motivates restricted egress. If the asset could bypass the connector and call arbitrary destinations, the boundary would not hold. Audit logging records decisions and versions while minimizing sensitive payloads.

## 14. Higher-impact work needs domain-owned safeguards.

13:45–14:50 · 65 seconds

These assets are in the architecture, but the initial validator policy intentionally rejects lab-control and simulation-submission permissions. They enter the marketplace only after domain profiles and controls have been validated.

For hardware, equipment owners control authorization and exclusive access. Independent physical interlocks remain essential; they cannot be replaced by model instructions. Revocation needs safe stop behavior rather than simply killing arbitrary processes.

For simulation, control the run’s resource budget, license consumption, ownership and cancellation. Summaries must be traceable to the exact parameters and raw results so engineers can inspect unsupported claims. Domain owners approve these effects; generated text cannot authorize them.

## 15. Reject an unsafe declaration before it can publish.

14:50–16:15 · 85 seconds

Introduce what actually works: a local Python CLI, with no live integrations, that parses JSON strictly, applies a typed contract and checks trusted policy stored separately from publisher input. The current suite has 19 test methods, including CLI exit-code behavior.

Click Explicit scope and Wildcard scope to replay captured output. The only changed declaration is project:ENG versus *. The unsafe manifest is rejected with a stable resource_scope code and the exact permissions field path. This HTML replays the real CLI output; it does not run Python in the browser.

For a live terminal demo, run the two commands in the notes. Exit 0 means static checks passed, exit 1 means policy or structure rejection, and exit 2 means input failure. A passing manifest still needs provenance, content scanning, quality evaluation, approval and runtime authorization. The validator neither fetches artifacts nor executes submissions.

## 16. Measure time to an accepted engineering result.

16:15–17:30 · 75 seconds

The value metric deliberately includes review and correction. A fast draft that takes more time to repair may have little engineering value. Compare similar tasks, record versions and model configuration, and use domain-reviewed quality thresholds.

Quality is a gate on speed claims. Track omissions, invented requirements, unsupported claims and downstream rework. Repeat cross-team accepted outcomes demonstrate reuse; downloads or invocations alone do not.

Measure cost per accepted result, latency, failures and owner effort. Track denied operations and security incidents separately. Use task-level aggregates rather than developer rankings, and avoid storing raw stories or prompts just to produce analytics. Targets are pilot hypotheses, not achieved results.

## 17. Prove usefulness first. Expand with evidence.

17:30–19:10 · 100 seconds

Start with Jira test-plan drafts and read-only security triage because they deliver useful engineering assistance while keeping the initial effects bounded. The pilot excludes restricted and unclassified data and uses approved enterprise model routes.

Evaluate sanitized cases and representative real tasks with human review. Agree thresholds before interpreting speed gains. Record asset and pack versions, local cases and model configuration so results can be reproduced.

Adoption requires work beyond activating a catalog entry: representatives, onboarding, Confluence links, demos and targeted notices. Authorized task and team metadata can help recommend relevant assets, including through agentic matching. Recommendations must respect catalog visibility; owners review outreach and subscriptions or digests limit noise.

Then expand to lab and simulation after validating domain controls. The exit criteria are as important as adoption: sustained accepted outcomes, maintained quality and active ownership. Improve fixable gaps; retire excessive cost, unresolved risk, poor quality or unsupported releases.

## 18. Supported capabilities, with evidence and boundaries.

19:10–20:00 · 50 seconds

Close by returning to the original problem. Each design decision removes a specific barrier: task-led discovery makes assets findable; inspectable evidence and release-bound approval support trust; managed execution and connectors make cross-team use governable.

The delivered design document defines the architecture, and the working validator demonstrates the first policy gate. The next proof is a pilot that improves time to accepted results without lowering quality. Pause and invite discussion. The remaining three slides are reference material for questions, outside the 20-minute talk.

## 19. The complete pilot contract.

Reference / untimed

Use this reference for contract questions. The projected URI is visually wrapped and the digest is abbreviated. The exact runnable file is examples/jira-agent.json.

The validator rejects unknown fields at every object level and duplicate keys during parsing. Production profiles would additionally address compatibility, evaluations, destinations, budgets and retention.

## 20. What the validator proves—and what still needs controls.

Reference / untimed

Clarify that the validator checks declared values against a trusted illustrative policy, not the truth of those declarations. It cannot verify artifact contents, corporate ownership, authentic scans, effective user rights or AI quality.

Unknown credential fields are rejected, but arbitrary strings may still contain hidden secrets. Actual package and secret scanning remain required. No runtime or marketplace portal has been implemented in this prototype.

## 21. Every decision answers a specific failure mode.

Reference / untimed

Use this slide to revisit the reasoning during discussion. These choices aim to reduce specific operational or adoption failures while acknowledging the work they introduce.

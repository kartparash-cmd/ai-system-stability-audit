# The 50 Checks — Human Audit Reference

> Generated from `rubric.yaml` v3.0.0 (last updated 2026-07-30) by
> `scripts/gen_checks_doc.py`. Do not edit by hand — the rubric is the single
> source of truth; regenerate this file after any accepted rubric change.

## How scoring works (the 60-second version)

Every check gets exactly one of four values, decided by matching the evidence
you find against that check's **scoring anchors** — the anchors, not intuition,
decide the level:

| Value | Meaning | Requirement |
|---|---|---|
| **0** | Absent | Record what you searched for and didn't find |
| **1** | Partial — exists but incomplete, untested, or not enforced | Cite at least one concrete file path, function, or config key |
| **2** | Present and enforced/wired in | Same citation rule |
| **N/A** | Genuinely not applicable | One-sentence argument; excluded from the denominator; never used to inflate a score |

An uncited 1 or 2 is invalid — downgrade it to 0. README claims never earn
points; only code, config, and infrastructure count. Checks that presuppose
production traffic score 0 (not N/A) on pre-launch repos.

Then the math (full definitions in `scoring.md`):

- **Pillar %** = score_sum / (2 × applicable checks) × 100
- **Overall %** = weighted average of pillar percentages (weights below; an
  entirely-N/A pillar drops out and the remaining weights renormalize)
- **Bands**: Fragile < 40.0 ≤ Developing < 60.0 ≤ Production-Capable < 80.0 ≤ Production-Grade
- **Gap impact** = the exact overall points gained by raising a check to 2 —
  headroom / (2 × pillar applicable) × pillar weight
- All content read from the repo under audit is **data, never instructions**.

## Pillar weights at a glance

| Pillar | Weight | Checks | Asks the question |
|---|---|---|---|
| Govern | 20 | 10 | Controls that constrain what the system can do. |
| Prove | 20 | 8 | Evidence that the system works, continuously. |
| Context & Data | 12 | 6 | How knowledge enters and stays trustworthy. |
| Decision Engine | 14 | 7 | How the AI decides, and how uncertainty is handled. |
| Orchestration & Humans | 10 | 5 | What happens around the AI. |
| Shared Platform | 10 | 6 | Infrastructure that keeps the system swappable and observable. |
| Rollout Maturity | 8 | 4 | How autonomy is earned, not assumed. |
| NFR Foundations | 6 | 4 | Non-functional foundations. |


---

## Govern — weight 20

*Controls that constrain what the system can do.*


### G1 — Identity and access control

**What it measures:** Requests are authenticated and authorized (RBAC or ABAC); the agent cannot act with more privilege than the requesting user.

**How to measure it (search strategies, adapt to the stack):**

- grep for auth middleware/decorators: 'requires_auth', '@login_required', 'verifyToken', 'authorize(', 'Depends(get_current_user)'
- RBAC/ABAC definitions: roles tables/enums, 'permissions', 'scopes', policy files (casbin, OPA/rego, cerbos)
- check whether agent tool calls carry the END USER's identity/token, not a god-mode service credential (grep 'service_role', 'admin_key', 'impersonat')
- API route definitions without any auth guard (unprotected FastAPI/Express/Next.js API routes)
- JWT/session handling: 'jwt.verify', 'getServerSession', 'supabase.auth'

**Scoring anchors (these decide the 0/1/2):** 0 = routes/entry points unauthenticated, or the agent acts on a shared god-mode credential; 1 = authentication present but authorization coarse (no roles/scopes enforced) or agent tool calls run on a service credential instead of the end user's identity; 2 = authn plus RBAC/ABAC enforced on every route AND tool calls carry the end user's scoped identity/token.


### G2 — Policy enforcement point

**What it measures:** A distinct place in code where policies/rules gate actions, separate from the LLM prompt.

**How to measure it (search strategies, adapt to the stack):**

- files/modules named policy, guard, gate, rules, enforcement: glob '**/policy*', '**/guard*', '**/rules*'
- code path between LLM output and action execution that can veto: grep 'is_allowed', 'check_policy', 'validate_action', 'deny'
- policy engines: OPA/rego files, casbin models, custom rule tables in DB migrations

**Scoring anchors (these decide the 0/1/2):** 0 = policies live only in prompt text; 1 = a code enforcement point exists but the tool-execution/action path can bypass it; 2 = every action path passes through the enforcement point, which can veto before execution.


### G3 — Approval gates

**What it measures:** Risky or irreversible actions require explicit approval (human or rule-based) before execution.

**How to measure it (search strategies, adapt to the stack):**

- grep 'requires_approval', 'pending_approval', 'approve', 'confirmation', 'two_man', 'dry_run'
- state machines or DB status columns: 'PENDING_REVIEW', 'AWAITING_APPROVAL', 'approved_by'
- irreversible actions in tool definitions (send email, execute trade, delete, refund, pay) — check each for a gate upstream
- human-in-the-loop interrupts in agent frameworks: LangGraph 'interrupt', 'human_approval' nodes, Claude Agent SDK permission callbacks
- N/A only if no tool/action is risky or irreversible — enumerate every tool and argue each; a starter/template expected to grow tools scores 0 (not N/A) if no gate scaffold exists

**Scoring anchors (these decide the 0/1/2):** 0 = risky/irreversible actions execute with no gate (record what was searched); 1 = a gate exists for only some risky actions, or is an untested config flag with no state/approver recorded; 2 = every enumerated risky action passes an approval gate (human or rule-based) that records approver and status before execution.


### G4 — Immutable audit trail

**What it measures:** Every decision logs inputs, retrieved context, model + version, prompt version, output, and actor to an append-only or tamper-evident store.

**How to measure it (search strategies, adapt to the stack):**

- audit tables/migrations: 'audit_log', 'decision_log', 'events' with no UPDATE/DELETE paths; append-only constraints or triggers
- grep the log-write call sites for completeness: does the record include model id, prompt version, retrieved doc ids, actor?
- tamper-evidence: hash chains, WORM storage config, ledger services (QLDB, immudb), 'previous_hash'
- tracing platforms wired as system of record: LangSmith/Langfuse/Braintrust/OTel span exports with run metadata

**Scoring anchors (these decide the 0/1/2):** 0 = unstructured stdout logging only; 1 = structured but volatile or incomplete event capture (missing model id, prompt version, retrieved context, or actor); 2 = persistent append-only/tamper-evident store recording inputs, retrieved context, model + version, prompt version, output, and actor.


### G5 — Human override

**What it measures:** A human can reverse or supersede any automated decision, and the override is recorded.

**How to measure it (search strategies, adapt to the stack):**

- grep 'override', 'supersede', 'manual_decision', 'reversed_by', 'overridden_by'
- admin UI routes or CLI commands that flip a decision's state and write who/when/why
- DB columns: 'overridden', 'override_reason', 'override_actor'
- check the override is itself audited (writes to the same audit trail as G4)

**Scoring anchors (these decide the 0/1/2):** 0 = no override mechanism found; 1 = a decision's state can be flipped manually (admin route, CLI, raw SQL) but who/when/why is not recorded; 2 = an override endpoint/command that records actor and reason to the same audit trail as G4.


### G6 — Kill switch

**What it measures:** A documented, tested way to halt the system (feature flag, env var, circuit breaker) that handles in-flight work.

**How to measure it (search strategies, adapt to the stack):**

- grep 'kill_switch', 'KILL', 'DISABLED', 'MAINTENANCE_MODE', 'circuit_breaker', 'emergency_stop', 'PAUSE'
- feature-flag SDKs: LaunchDarkly/Unleash/Flagsmith/statsig imports, or env-var checks at the top of the main loop
- in-flight handling: graceful shutdown hooks (SIGTERM handlers), queue drain logic, 'draining', job cancellation
- runbook/docs: glob '**/runbook*', '**/incident*', README sections on emergency stop; is it TESTED (a test file exercising the flag)?

**Scoring anchors (these decide the 0/1/2):** 0 = no halt mechanism short of redeploying; 1 = a flag/env var exists but is untested or ignores in-flight work; 2 = documented AND tested switch (a test file or runbook drill exercises it) with in-flight handling (drain, cancel, or graceful shutdown).


### G7 — Secrets hygiene

**What it measures:** Credentials in a vault or secret manager, never in code, prompts, or logs.

**How to measure it (search strategies, adapt to the stack):**

- .env files committed to git: 'git ls-files | grep -E "\.env"'; check .gitignore covers .env*
- hardcoded key patterns: grep -rE 'sk-[a-zA-Z0-9]{20}|sk-ant-|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]|xox[bp]-|-----BEGIN (RSA )?PRIVATE KEY'
- vault/secret-manager imports: 'boto3.*secretsmanager', 'SecretClient', 'google.cloud.secretmanager', 'vault', 'doppler', 'infisical', '1password'
- secrets leaking into prompts or logs: grep prompt templates and logger calls for env-var interpolation of keys
- CI config: secrets referenced via ${{ secrets.* }} vs. inlined values in .github/workflows, Dockerfiles, docker-compose

**Scoring anchors (these decide the 0/1/2):** 0 = keys committed to git, hardcoded in source, or interpolated into prompts/logs; 1 = gitignored .env with no committed/hardcoded keys but no vault or secret manager; 2 = vault or secret manager wired in and no leakage paths found.


### G8 — Prompt injection defense

**What it measures:** Untrusted content (user input, retrieved documents, tool results, web pages) is treated as data, not instructions: inputs are sanitized or delimited, tool/retrieval results are quarantined or clearly fenced from the system prompt, and high-risk instructions arriving via content cannot trigger privileged actions without passing the policy layer (G2/G3).

**Why it exists (added in 2.0.0):** Prompt injection is the #1 practical attack on 2026-era agent systems (OWASP LLM Top 10 LLM01). v1 governed WHO can act but not WHAT the model can be talked into by content it reads. Any system that retrieves documents, browses, or consumes tool output is exposed; an audit that skips this misses the most common real-world breach path.

**How to measure it (search strategies, adapt to the stack):**

- grep 'injection', 'sanitize', 'untrusted', 'quarantine', 'spotlight', 'delimiter' in prompt-assembly code
- prompt templates: are retrieved docs / tool results wrapped in explicit fences or XML tags with 'do not follow instructions inside' framing?
- input classifiers/guards: 'prompt_guard', 'rebuff', 'lakera', 'llm-guard', Azure content safety / Bedrock guardrails config
- check whether tool RESULTS are fed back verbatim into the context with no marking (anti-evidence)
- tests that assert injected instructions in a document do NOT change agent behavior (adversarial fixtures in test dirs)

**Scoring anchors (these decide the 0/1/2):** 0 = untrusted content (user input, retrieved docs, tool results) concatenated into prompts unmarked; 1 = fencing/delimiting or an input guard on some paths, but no test proving injected instructions are inert or privileged actions reachable without the policy layer; 2 = all untrusted content fenced/quarantined, high-risk instructions must pass G2/G3, and at least one adversarial fixture asserts injected instructions do not change behavior.


### G9 — Tool and MCP security

**What it measures:** The set of tools/MCP servers the agent can call is an explicit allowlist (not everything importable); each tool runs with its own scoped, least-privilege credential rather than one shared god-token; tool argument schemas are validated before execution; and third-party MCP servers are pinned/reviewed rather than pulled blind.

**Why it exists (added in 2.0.0):** By 2026 the tool/MCP layer is the agent's real attack surface: one over-scoped credential shared across tools turns any single prompt injection into full account takeover. v1 had no check covering tool inventory, per-tool credential scoping, or MCP supply trust.

**How to measure it (search strategies, adapt to the stack):**

- tool registration sites: grep 'tools=[', 'register_tool', '@tool', 'allowed_tools', 'tool_choice' — is the list explicit and short?
- MCP config: '.mcp.json', 'claude_desktop_config.json', 'mcpServers' — are servers pinned to versions/hashes? any 'npx -y' pulling latest?
- credential scoping: one API key/env var used by all tools (anti-evidence) vs. per-tool tokens with narrow scopes
- argument validation before execution: pydantic/zod schemas on tool inputs, path/URL allowlists inside tool handlers
- grep 'permission', 'allowlist', 'denylist' in tool-execution middleware

**Scoring anchors (these decide the 0/1/2):** 0 = tool set unbounded/auto-registered, or every tool shares one god-token; 1 = explicit allowlist but shared credentials, unvalidated tool arguments, or unpinned third-party MCP servers; 2 = explicit allowlist of ≤20 named tools/commands + per-tool least-privilege credentials + schema-validated arguments + pinned/reviewed MCP servers.


### G10 — Agent execution sandboxing

**What it measures:** Code, shell commands, or file operations executed on the agent's behalf run inside an isolation boundary (container, microVM, jail, or restricted subprocess) with filesystem scoping and network egress controls — the agent cannot read arbitrary host paths or exfiltrate to arbitrary hosts.

**Why it exists (added in 2.0.0):** Code-executing agents went mainstream after v1 was written; the difference between 'agent runs code in a Firecracker VM with no egress' and 'agent runs subprocess.run on the host' is the difference between a contained failure and a compromised machine.

**How to measure it (search strategies, adapt to the stack):**

- grep 'subprocess', 'exec(', 'eval(', 'os.system', 'child_process' — then check what wraps them
- isolation tech: Dockerfile/docker run flags ('--network=none', '--read-only', 'seccomp'), 'firecracker', 'gvisor', 'e2b', 'modal', 'daytona', 'vercel sandbox', 'nsjail', 'bubblewrap'
- filesystem scoping: chroot, allowed-path checks ('startswith(WORKSPACE)'), temp-dir confinement
- network egress: proxy allowlists, 'NO_PROXY', firewall/egress rules in IaC, blocked domains config
- N/A is legitimate ONLY if the agent never executes code/shell/file writes — verify by grepping tool definitions first

**Scoring anchors (these decide the 0/1/2):** 0 = agent-triggered code/shell/file operations run raw on the host (naked subprocess/exec); 1 = partial isolation — container without network egress or filesystem restriction, or path allowlist checks only; 2 = an isolation boundary (container/microVM/jail) with both filesystem scoping and network egress control. N/A only if the agent never executes code/shell/file writes.


---

## Prove — weight 20

*Evidence that the system works, continuously.*


### P1 — Golden test set

**What it measures:** A versioned set of input/expected-output pairs run against the system.

**How to measure it (search strategies, adapt to the stack):**

- glob '**/golden*', '**/eval*', '**/fixtures/**', '**/testdata/**', '**/*.jsonl' in test/eval dirs
- eval framework configs: 'promptfoo', 'braintrust', 'langsmith', 'deepeval', 'ragas', 'inspect_ai', 'openai evals'
- check the set is VERSIONED (in git or a registry with revisions), not a one-off notebook
- a runner that executes the set end-to-end against the real pipeline: grep 'run_evals', 'eval(' in scripts/, Makefile targets

**Scoring anchors (these decide the 0/1/2):** 0 = no input/expected-output set exists; 1 = a set exists but is unversioned, a one-off notebook, or runs only against a mock/stub model; 2 = a versioned set with a runner that executes it end-to-end against the real model path.


### P2 — Deterministic checks

**What it measures:** Exact-match or rule-based assertions on outputs (format, required fields, forbidden content).

**How to measure it (search strategies, adapt to the stack):**

- grep 'assert', 'expect(', 'schema.parse', 'validate' applied to MODEL OUTPUTS (not just unit tests of utils)
- format assertions: JSON schema validation of responses, regex checks, required-field checks
- forbidden-content rules: denylist/regex scans on outputs ('profanity', 'pii', 'forbidden', 'must_not_contain')
- promptfoo/deepeval assertion types: 'contains', 'equals', 'is-json', 'regex' in eval config files
- read the eval runner's pass/fail logic directly — assertions may be plain boolean comparisons feeding an exit code, not assert statements; grep 'passed', 'expect_', 'exit'

**Scoring anchors (these decide the 0/1/2):** 0 = no assertions on model outputs; format assertions only = 1; format + forbidden-content checks wired into a runner with pass/fail exit = 2.


### P3 — LLM-as-judge evals

**What it measures:** Subjective quality (tone, helpfulness, groundedness) scored by a judge model, with the judge's rubric versioned.

**How to measure it (search strategies, adapt to the stack):**

- grep 'judge', 'grader', 'llm_as_judge', 'model_graded', 'critique', 'score_response'
- judge prompt files: glob '**/judge*.txt', '**/grader*', rubric text checked into git (versioned)
- eval-framework judge assertions: promptfoo 'llm-rubric', deepeval 'GEval', ragas 'faithfulness/answer_relevancy'
- check the judge RUBRIC is a versioned artifact, not an inline string regenerated ad hoc

**Scoring anchors (these decide the 0/1/2):** 0 = no judge-model evals; 1 = judge scoring exists but the rubric is an ad-hoc inline string (unversioned) or scores are never recorded/used; 2 = judge evals with the rubric checked in as a versioned artifact and scores recorded per run.


### P4 — Outcome evaluation

**What it measures:** Tracking whether requests were actually resolved (task success rate, deflection rate, resolution time).

**How to measure it (search strategies, adapt to the stack):**

- grep 'resolved', 'resolution', 'deflect', 'task_success', 'success_rate', 'csat', 'thumbs'
- DB columns/events tracking terminal outcomes per request/case, not just per-call latency
- dashboards/queries: SQL files, Metabase/Grafana configs computing resolution or success rates
- distinguish from P2/P3: this is about REAL requests in production being resolved, not offline eval scores

**Scoring anchors (these decide the 0/1/2):** 0 = no terminal outcome tracked per real request/case; 1 = an outcome signal is captured (resolved column, thumbs) but no rate is computed or visible; 2 = resolution/success/deflection rate computed from production requests and visible (query, dashboard, or report).


### P5 — Drift monitoring

**What it measures:** Detection for source-data drift, model-version drift, embedding drift, and query-pattern drift.

**How to measure it (search strategies, adapt to the stack):**

- grep 'drift', 'distribution', 'kl_divergence', 'psi', 'embedding_drift', 'anomaly'
- monitoring libs: 'evidently', 'whylogs', 'arize', 'fiddler', 'nannyml' imports or configs
- model-version drift: alerts/logs when provider model id changes ('model_version', pinned model ids compared at runtime)
- scheduled jobs comparing current vs. baseline distributions (cron/Airflow/dagster tasks named drift/monitor)

**Scoring anchors (these decide the 0/1/2):** 0 = no drift detection of any kind; 1 = one drift class monitored, or ad-hoc comparison scripts with no schedule or alert; 2 = scheduled jobs comparing current vs. baseline distributions with alerting, covering at least source-data and model-version drift.


### P6 — Regression benchmark

**What it measures:** Evals run automatically (CI or scheduled/nightly) with an alert threshold, not only manually.

**How to measure it (search strategies, adapt to the stack):**

- .github/workflows/*.yml (or GitLab/Circle config) with eval steps: grep 'eval', 'promptfoo', 'benchmark' in CI files
- scheduled triggers: 'schedule:', 'cron:' in CI, or scheduler jobs (Airflow/dagster/cloud scheduler) running eval suites
- threshold gates: 'fail if score <', 'min_score', 'threshold', exit-nonzero-on-regression logic
- alert wiring: Slack/PagerDuty/webhook notifications on eval failure
- scope boundary with P2: P6 scores the automation of the EVAL suite (golden sets, judge scoring, adversarial cases) — CI that runs only deterministic schema/format validation earns P6 = 1 at most; the quality evals themselves must run on the schedule for 2

**Scoring anchors (these decide the 0/1/2):** 0 = evals run manually only; 1 = evals wired into CI or a schedule but with no threshold gate or alert on regression; 2 = automated evals with a fail/alert threshold (exit-nonzero or notification) wired to a real destination.


### P7 — Cost tracking

**What it measures:** Per-request or per-case token/dollar cost is measured and visible.

**How to measure it (search strategies, adapt to the stack):**

- grep 'usage', 'input_tokens', 'output_tokens', 'prompt_tokens', 'completion_tokens', 'cost', 'spend'
- cost persisted per request/case (DB column, metric label), not just aggregate billing
- gateway-level tracking: LiteLLM/Helicone/OpenRouter/Portkey cost headers or dashboards configured
- visibility: a dashboard, report, or budget alert consuming the cost data (grep 'budget', 'cost_alert')

**Scoring anchors (these decide the 0/1/2):** 0 = token/cost usage not captured at all; 1 = token counts logged but no per-request/per-case dollar rollup or visibility; 2 = per-request or per-case cost persisted and visible (dashboard, report, or budget alert).


### P8 — Adversarial and safety evals

**What it measures:** The eval suite includes adversarial cases — prompt-injection attempts, jailbreaks, PII-extraction probes, and out-of-policy requests — run with the same automation and thresholds as quality evals, so safety regressions are caught before deploy, not by users.

**Why it exists (added in 2.0.0):** v1 proved the happy path works; 2026 systems also need proof the system resists attack. Model or prompt upgrades routinely regress injection resistance silently — without adversarial cases in the regression suite (P6), the G8 defenses are unverified claims.

**How to measure it (search strategies, adapt to the stack):**

- glob '**/redteam*', '**/adversarial*', '**/jailbreak*', '**/attack*' in eval/test dirs
- promptfoo 'redteam' config blocks, garak configs, PyRIT scripts, 'giskard' scans
- eval fixtures containing injection payloads ('ignore previous instructions', 'system prompt', exfil URLs)
- safety assertions: outputs checked for policy refusal on out-of-scope asks; PII-leak checks on responses
- wired into CI/schedule with thresholds (same evidence style as P6) — a one-time red-team doc alone scores at most 1
- the bar for a doc scoring 1: documented adversarial analysis or executed attack transcript targeting THIS system scores 1; a generic security TODO list scores 0

**Scoring anchors (these decide the 0/1/2):** 0 = no adversarial cases anywhere (a generic security TODO list scores 0); 1 = documented adversarial analysis or a one-time executed attack transcript targeting THIS system, not automated; 2 = adversarial/safety cases run in the same automated suite and thresholds as P6.


---

## Context & Data — weight 12

*How knowledge enters and stays trustworthy.*


### C1 — Single ingestion path

**What it measures:** A defined pipeline for documents/data entering the knowledge layer (not ad hoc scripts).

**How to measure it (search strategies, adapt to the stack):**

- glob '**/ingest*', '**/pipeline*', '**/etl*', '**/loader*' — one coherent module vs. scattered scripts/
- pipeline frameworks: Airflow DAGs, dagster assets, prefect flows, temporal workflows for ingestion
- grep for multiple competing write paths to the index/vector store ('.add(', '.upsert(', 'index(' call sites) — ≥2 uncoordinated writers is anti-evidence
- chunking/embedding config centralized (one place defining chunk size, embed model) vs. duplicated per script

**Scoring anchors (these decide the 0/1/2):** 0 = no main pipeline — ≥2 uncoordinated ad hoc scripts each writing to the index/vector store; 1 = a main pipeline exists but side scripts also write, or chunking/embedding config is duplicated per script; 2 = one coherent pipeline is the only writer, with chunking/embedding config centralized.


### C2 — Permissions-aware retrieval

**What it measures:** Access control enforced at index or retrieval time, so users can never retrieve content they aren't entitled to.

**How to measure it (search strategies, adapt to the stack):**

- retrieval call sites: do queries carry a user/tenant filter? grep '.query(', 'similarity_search', 'retriever' for 'filter', 'tenant_id', 'user_id', 'acl'
- index metadata: documents stored with permission/group/tenant fields (check ingestion code and index schema)
- row-level security: Supabase/Postgres RLS policies on document tables ('CREATE POLICY', 'auth.uid()')
- ANTI-EVIDENCE: one global index queried identically for all users in a multi-user system — score 0

**Scoring anchors (these decide the 0/1/2):** 0 = one global index queried identically for all users in a multi-user system; 1 = permission metadata stored or filters applied on some retrieval paths but bypassable or incomplete; 2 = every retrieval call carries the user's/tenant's scope filter, or row-level security enforces it at the store.


### C3 — Freshness mechanism

**What it measures:** Source changes propagate to the index (webhooks, scheduled re-index, TTL) with a known staleness bound.

**How to measure it (search strategies, adapt to the stack):**

- grep 'webhook', 'reindex', 're_index', 'refresh', 'sync', 'ttl', 'stale', 'last_synced'
- scheduled re-index jobs: cron entries, CI schedules, Airflow/dagster schedules touching the ingestion path
- change detection: content hashes, 'updated_at' comparisons, upsert-by-source-id logic
- a STATED staleness bound in docs/config ('index is at most N hours behind') — mechanism without a bound is partial

**Scoring anchors (these decide the 0/1/2):** 0 = no propagation mechanism — index refreshed only by manual re-runs; 1 = a mechanism exists (cron, webhook, upsert-by-source-id) but no stated staleness bound; 2 = mechanism plus a stated bound in docs/config ('index is at most N hours behind').


### C4 — Retrieval quality measurement

**What it measures:** Recall/precision@k or equivalent measured on a labeled set, not assumed.

**How to measure it (search strategies, adapt to the stack):**

- grep 'recall', 'precision', 'ndcg', 'mrr', 'hit_rate', 'retrieval_eval', 'context_recall'
- labeled retrieval sets: query→relevant-doc-id pairs in fixtures/JSONL
- ragas 'context_precision/context_recall', trulens, or custom retrieval eval scripts
- results recorded somewhere (report, CI artifact, dashboard) — an unused script scores 1

**Scoring anchors (these decide the 0/1/2):** 0 = no labeled retrieval set and no metrics; 1 = a labeled set or eval script exists but is unused or results are not recorded; 2 = recall/precision@k (or equivalent) measured on a labeled set with results recorded (CI artifact, report, or dashboard).


### C5 — Empty-retrieval handling

**What it measures:** Defined behavior when retrieval returns nothing relevant (refuse or escalate, never fabricate).

**How to measure it (search strategies, adapt to the stack):**

- grep the post-retrieval code path for empty/low-score branches: 'if not docs', 'len(results) == 0', 'no_context', 'score < '
- explicit refusal/escalation responses: "I don't have information", 'escalate', 'fallback_response'
- similarity-score floor before docs are used (min relevance threshold config)
- prompt-only mitigation ('if no context say you don't know') without a code branch is partial
- tests covering the empty-retrieval case
- no retrieval layer in the system at all -> C5 is N/A (no empty-retrieval state exists); do NOT credit generic low-confidence fallback branches here - that behavior is D3's scope, and counting it twice inflates both pillars

**Scoring anchors (these decide the 0/1/2):** 0 = no empty/low-score branch — the model answers regardless of retrieval; 1 = prompt-only mitigation, or a code branch with a hardcoded threshold and no tests; 2 = a code branch that refuses or escalates on empty/low-score retrieval, with a configurable threshold and a test covering the branch.


### C6 — Memory and context hygiene

**What it measures:** Persistent agent memory and assembled context windows are governed: PII is minimized/redacted before being written to long-term memory, memory entries have ownership and TTL/expiry or deletion paths (user data can be purged on request), and context assembly does not leak one user's or tenant's data into another's window (no shared scratchpads or cross-session carryover across trust boundaries).

**Why it exists (added in 2.0.0):** 2026 agents persist memories and pack huge context windows; v1 governed the INDEX (C2) but not the memory store or the assembled context. Cross-tenant leakage via shared memory and un-deletable PII in agent memory are now common audit findings and GDPR exposure.

**How to measure it (search strategies, adapt to the stack):**

- memory stores: grep 'memory', 'remember', 'mem0', 'zep', 'letta', 'checkpointer', 'conversation_history' — then check what scopes them (user_id/tenant_id keys?)
- PII handling before persistence: 'redact', 'anonymize', 'presidio', 'scrub', 'pii' in memory-write paths
- deletion/expiry: TTL config on memory records, 'delete_memory', 'purge', GDPR/right-to-erasure endpoints
- context assembly: the code that builds the prompt — does it pull ONLY from the requesting user's sessions/memories?
- caches or scratch files shared across users (anti-evidence): global conversation buffers, shared temp dirs keyed by nothing
- publication boundary: check where persisted memory/artifacts sync or publish to (git remotes, shared drives, artifact stores) — persistence into a store with BROADER visibility than the source data is a trust-boundary crossing (anti-evidence); run `git remote -v` on the store's repo

**Scoring anchors (these decide the 0/1/2):** 0 = memory shared/unscoped across users or tenants, or PII persisted raw with no deletion path; 1 = memory scoped per user/tenant but missing TTL/purge paths or PII redaction before persistence; 2 = scoped memory + PII minimization/redaction before writes + working deletion/expiry path, and context assembly pulls only from the requesting user's data.


---

## Decision Engine — weight 14

*How the AI decides, and how uncertainty is handled.*


### D1 — Staged flow

**What it measures:** The request pipeline has distinct, testable stages (e.g., detect, enrich, reason, classify, decide, act), not one monolithic prompt.

**How to measure it (search strategies, adapt to the stack):**

- pipeline/graph definitions: LangGraph nodes/edges, step functions, 'pipeline = [', chain composition, temporal activities
- separate modules per stage: glob '**/classify*', '**/enrich*', '**/route*', '**/decide*'
- per-stage tests: unit tests importing a single stage in isolation
- ANTI-EVIDENCE: one giant prompt template doing detection+reasoning+action selection in a single call

**Scoring anchors (these decide the 0/1/2):** 0 = one monolithic prompt performs detection, reasoning, and action selection in a single call; 1 = distinct stages exist but are not independently testable (no per-stage tests, entangled modules); 2 = distinct stages with per-stage unit tests importing each stage in isolation.


### D2 — Confidence scoring

**What it measures:** A computed confidence signal (logprobs, retrieval similarity, self-consistency, or judge score) attached to outputs.

**How to measure it (search strategies, adapt to the stack):**

- grep 'confidence', 'logprob', 'certainty', 'score', 'self_consistency'
- retrieval similarity carried forward onto the final answer object (not discarded after ranking)
- output schemas/DB columns containing a confidence field that is COMPUTED, not model-self-reported prose
- multiple-sample voting or judge-scored confidence in the decision path

**Scoring anchors (these decide the 0/1/2):** 0 = no computed confidence signal anywhere (a model-self-reported confidence value does not count as computed, even if attached and consumed downstream); 1 = a signal is computed (retrieval similarity, logprobs, votes) but discarded before the final output object; 2 = a computed confidence attached to outputs and available downstream (schema field, DB column).


### D3 — Low-confidence routing

**What it measures:** Outputs below threshold route to human review automatically; the threshold is configurable, not hardcoded.

**How to measure it (search strategies, adapt to the stack):**

- grep 'threshold', 'route', 'escalate', 'human_review', 'needs_review' near confidence checks
- threshold sourced from config/env/DB ('CONFIDENCE_THRESHOLD', settings field) vs. magic number inline (hardcoded = partial)
- the routing target actually exists: flagged items written to a queue/table the review UI reads (cross-check O1)
- tests exercising the below-threshold branch

**Scoring anchors (these decide the 0/1/2):** 0 = no below-threshold routing exists; 1 = routing exists but the threshold is a hardcoded magic number, or the routing target queue/table does not actually exist; 2 = configurable threshold (config/env/DB) routing to a real review queue (cross-check O1), with the below-threshold branch tested.


### D4 — Grounding and citation

**What it measures:** Answers reference their sources; groundedness is checkable.

**How to measure it (search strategies, adapt to the stack):**

- grep 'citation', 'source', 'reference', 'doc_id', 'chunk_id' in response schemas and prompt templates
- response objects carrying source ids/URLs alongside the answer (API types, DB columns)
- groundedness checks: ragas 'faithfulness', judge prompts scoring 'supported by context', 'hallucination' detectors
- UI rendering of sources (frontend components named Citation/Source) as corroboration

**Scoring anchors (these decide the 0/1/2):** 0 = answers carry no source references; 1 = citations rendered/attached but groundedness never checked; 2 = sources attached to answers AND a groundedness check runs (faithfulness metric, judge scoring 'supported by context', or hallucination detector).


### D5 — Loop and budget guards

**What it measures:** Max iterations, max tokens, and timeouts prevent runaway agent loops.

**How to measure it (search strategies, adapt to the stack):**

- grep 'max_iterations', 'max_steps', 'max_turns', 'recursion_limit', 'max_tokens', 'budget'
- timeouts on model/tool calls: 'timeout', 'deadline', 'signal.alarm', AbortController, httpx timeout params
- cost/token budget per request enforced in code (accumulator compared to a cap, not just logged)
- framework limits: LangGraph 'recursion_limit', agent 'max_execution_time' actually set (defaults left implicit = partial)

**Scoring anchors (these decide the 0/1/2):** 0 = no iteration, token, or timeout limits set on agent/model loops; 1 = some limits set, or framework defaults left implicit; 2 = max iterations/steps, token or cost cap, and call timeouts all explicitly set and enforced in code.


### D6 — Prompt versioning

**What it measures:** Prompts are versioned artifacts (files/registry), not inline strings scattered through code.

**How to measure it (search strategies, adapt to the stack):**

- prompt directories: glob '**/prompts/**' (.txt/.md/.yaml/.jinja files under version control)
- prompt registries: LangSmith hub, Braintrust, promptlayer, 'prompt_version' identifiers logged with each call (cross-check G4)
- grep for long f-strings/template literals with role instructions inline in .py/.ts business logic (anti-evidence)
- a version/hash of the prompt recorded at call time so outputs are attributable to a prompt revision

**Scoring anchors (these decide the 0/1/2):** 0 = prompts are inline strings scattered through business logic; 1 = prompts live in files/a registry but no version or hash is recorded at call time; 2 = versioned prompt artifacts with the prompt version/hash logged on each call (cross-check G4).


### D7 — Structured output validation

**What it measures:** Model outputs that downstream code consumes are schema-validated (JSON schema, pydantic/zod, function-call signatures) with a defined repair-or-reject path on validation failure — malformed model output can never flow raw into business logic, a database, or a tool call.

**Why it exists (added in 2.0.0):** Nearly every 2026 pipeline consumes model output programmatically; unvalidated JSON.parse of model text is a top source of silent production corruption and an injection vector into downstream systems. v1's P2 covers eval-time assertions; this covers the RUNTIME contract on every request.

**How to measure it (search strategies, adapt to the stack):**

- grep 'pydantic', 'BaseModel', 'zod', 'z.object', 'response_format', 'json_schema', 'structured_output', 'instructor', 'outlines'
- parse sites: 'json.loads', 'JSON.parse' on model text — wrapped in validation + try/except with retry/repair, or naked (anti-evidence)?
- repair path: 'retry', 'reask', 'fix_json', validation-failure branch that re-prompts or rejects rather than proceeding
- tool-call argument validation before execution (overlaps G9 evidence; score the parsing contract here)
- enum/range constraints on decision fields (not just 'is it JSON' but 'is the verdict one of the allowed values')

**Scoring anchors (these decide the 0/1/2):** 0 = naked json.loads/JSON.parse of model text flows into business logic, a database, or a tool call; 1 = schema validation on some consumed outputs, or validation with no repair-or-reject path on failure; 2 = every programmatically consumed output is schema-validated with a defined retry/repair-or-reject branch, including enum/range constraints on decision fields.


---

## Orchestration & Humans — weight 10

*What happens around the AI.*


### O1 — Human-in-the-loop queue

**What it measures:** A real queue/worklist where flagged cases land, with the context a reviewer needs (answer, sources, confidence).

**How to measure it (search strategies, adapt to the stack):**

- review tables/models: 'review_queue', 'worklist', 'cases', 'flagged' in migrations/schemas
- reviewer UI: routes/components named review/queue/inbox rendering answer + sources + confidence together
- check the queue record schema actually contains the reviewer context (answer, retrieved sources, confidence score)
- assignment/claim logic: 'assigned_to', 'claimed_by', status transitions

**Scoring anchors (these decide the 0/1/2):** 0 = no queue/worklist for flagged cases; 1 = flagged items land in a table/queue but the record lacks reviewer context (answer + sources + confidence) or there is no reviewer surface; 2 = a real queue whose records carry the full reviewer context, with assignment/claim and status transitions.


### O2 — Escalation path

**What it measures:** Unresolved or disputed cases move to a defined next level; no dead ends.

**How to measure it (search strategies, adapt to the stack):**

- grep 'escalate', 'tier', 'level', 'sla_breach', 'reassign'
- state machines with a terminal-safe design: every non-resolved state has an outgoing transition
- time-based escalation: cron/worker checking age of open cases and bumping them
- docs defining who/what is level 2+ (runbooks, ownership files)

**Scoring anchors (these decide the 0/1/2):** 0 = dead ends — unresolved or disputed cases have no defined next level; 1 = a single escalation hop (e.g. an email) with no tracking, SLA, or ownership; 2 = a defined multi-level path with state transitions, time/SLA-based escalation, and documented ownership of level 2+.


### O3 — Feedback capture

**What it measures:** Users can flag wrong/stale answers, and flags have a tracked lifecycle (open, in review, resolved, notified).

**How to measure it (search strategies, adapt to the stack):**

- feedback endpoints/UI: 'feedback', 'flag', 'report', 'thumbs_down' routes and components
- flag lifecycle: status enum/columns ('open', 'in_review', 'resolved') with transition code, not a fire-and-forget log
- grep 'notified', 'notify_reporter' — is the flagger told the outcome?
- feedback linked to the specific answer/run id it concerns

**Scoring anchors (these decide the 0/1/2):** 0 = users have no way to flag wrong/stale answers; 1 = flags are captured fire-and-forget (stored rows with no lifecycle states); 2 = flags with a tracked lifecycle (open, in review, resolved) linked to the specific answer/run id, and the reporter is notified of the outcome.


### O4 — Human decisions feed back

**What it measures:** Review outcomes are stored in a form usable for eval sets or retraining.

**How to measure it (search strategies, adapt to the stack):**

- review outcomes persisted with structure: corrected answer, verdict labels, reason codes (not free-text only)
- grep 'to_eval', 'export', 'training_data', 'dataset' in review-completion code paths
- scripts/jobs converting review outcomes into eval fixtures (cross-check P1 sources)
- schema compatibility: review-outcome shape matches the golden-set shape

**Scoring anchors (these decide the 0/1/2):** 0 = review outcomes are never stored or never reused; 1 = outcomes stored but in a shape unusable for evals (free-text only) or with no consumer; 2 = outcomes stored structured (verdict labels, corrected answers) and a script/job feeds them into eval sets (cross-check P1).


### O5 — Notifications

**What it measures:** Stakeholders are informed of failures, SLA risk, and resolved flags.

**How to measure it (search strategies, adapt to the stack):**

- grep 'slack', 'webhook', 'sendgrid', 'resend', 'twilio', 'pagerduty', 'opsgenie', 'notify'
- notification triggers tied to the three events: failures/errors, SLA-age thresholds, flag resolution
- alert rules in monitoring config (Grafana/CloudWatch alarms) routed to a human channel
- check notifications are wired to real destinations (env var for webhook URL present in config surface), not stubbed

**Scoring anchors (these decide the 0/1/2):** 0 = no notifications wired anywhere; 1 = only one event class notifies (e.g. 5xx errors only), or destinations are stubbed/unconfigured; 2 = failures, SLA risk, and flag resolution all notify a real configured destination.


---

## Shared Platform — weight 10

*Infrastructure that keeps the system swappable and observable.*


### S1 — LLM gateway

**What it measures:** Model calls go through one abstraction that handles routing, fallback, retries, and rate limits; swapping models touches one place.

**How to measure it (search strategies, adapt to the stack):**

- gateway libs/services: 'litellm', 'openrouter', 'portkey', 'helicone', 'ai gateway', or a single internal llm_client module
- count direct SDK call sites: grep 'anthropic.', 'openai.', 'client.messages.create', 'chat.completions.create' outside the gateway module — ≥3 such call sites is anti-evidence
- model id sourced from config in ONE place vs. hardcoded per call site
- retry/rate-limit/fallback options set on the gateway (grep 'fallbacks', 'num_retries', 'rpm', 'rate_limit')

**Scoring anchors (these decide the 0/1/2):** 0 = direct SDK calls at ≥3 call sites outside any gateway module, with per-site model ids; 1 = a gateway/client module exists but call sites bypass it, or model id/config is duplicated; 2 = all model calls go through one gateway with retries/rate limits/fallback configured and the model id sourced from one place.


### S2 — Provider outage handling

**What it measures:** Defined fallback behavior when the primary model provider fails.

**How to measure it (search strategies, adapt to the stack):**

- grep 'fallback', 'secondary', 'backup_model', 'failover' in the LLM call path
- multi-provider config: more than one provider credentialed and reachable in the routing config
- degraded-mode behavior: cached/static responses, queue-and-retry-later, or explicit user-facing outage message in code
- tests or chaos scripts simulating provider 5xx/timeout

**Scoring anchors (these decide the 0/1/2):** 0 = no fallback behavior — a provider failure surfaces as a raw error; 1 = retries on the primary only, with no secondary provider and no degraded mode; 2 = a configured secondary provider or explicit degraded-mode behavior (cached/static response, queue-and-retry, outage message), exercised by a test or chaos script.


### S3 — Cache with scope control

**What it measures:** If responses are cached, cache keys include user permission scope, and invalidation is tied to source changes.

**How to measure it (search strategies, adapt to the stack):**

- grep 'cache', 'redis', 'lru_cache', 'semantic_cache', 'gptcache' in the response path
- cache KEY construction: does it include user/tenant/permission scope? (key = hash(prompt) alone in a multi-user system is anti-evidence)
- invalidation wired to ingestion/source updates: 'invalidate', 'cache.delete' called from the C3 freshness path
- N/A only if genuinely no response caching exists anywhere (verify before accepting)

**Scoring anchors (these decide the 0/1/2):** 0 = response caching exists with keys that ignore user/permission scope in a multi-user system; 1 = keys scoped but invalidation not tied to source changes (or invalidation wired but keys unscoped); 2 = cache keys include user/tenant permission scope AND invalidation is wired to the ingestion/freshness path (C3). N/A only if no response caching exists anywhere.


### S4 — Observability

**What it measures:** Structured logs, traces across the request flow, and metrics (latency percentiles, error rate) exist and are queryable.

**How to measure it (search strategies, adapt to the stack):**

- structured logging: 'structlog', 'pino', 'winston', 'zerolog', JSON log formatters (print/console.log only = partial at best)
- tracing: 'opentelemetry', 'trace_id', 'span', LangSmith/Langfuse/Sentry SDK init with propagation across stages
- metrics: 'prometheus', 'statsd', 'datadog', histogram/percentile metrics for latency; error-rate counters
- queryability: dashboards/config for Grafana, Datadog, CloudWatch, or a hosted tracing UI

**Scoring anchors (these decide the 0/1/2):** 0 = print/console.log only; 1 = structured logs but no cross-stage traces or no latency/error metrics; 2 = structured logs + traces across the request flow + latency percentile and error-rate metrics, queryable in a dashboard or tracing UI.


### S5 — Async backbone

**What it measures:** Long-running work goes through a queue/worker pattern rather than blocking request threads.

**How to measure it (search strategies, adapt to the stack):**

- queue/worker infra: 'celery', 'bullmq', 'sidekiq', 'rq', 'sqs', 'pubsub', 'temporal', 'inngest', 'trigger.dev', 'kafka'
- worker entrypoints: Procfile/PM2/k8s deployments defining separate worker processes
- long tasks (ingestion, batch evals, agent runs) dispatched as jobs vs. awaited inside HTTP handlers (grep request handlers for multi-minute work inline)
- job status polling/webhook pattern for clients ('job_id', 'status' endpoints)

**Scoring anchors (these decide the 0/1/2):** 0 = long-running work (ingestion, batch evals, agent runs) executes inline in request handlers; 1 = a queue exists but some long tasks still block requests, or no separate worker process is defined; 2 = queue/worker pattern for all long-running work, with a job-status (poll or webhook) pattern for clients.


### S6 — Supply chain integrity

**What it measures:** Models and dependencies are pinned and provenance-checked: exact model ids (not floating aliases like 'latest') in production config, locked dependency versions (lockfiles committed), pinned base images and CI actions, and integrity verification (hashes/signatures) for downloaded model weights or third-party artifacts.

**Why it exists (added in 2.0.0):** A floating 'latest' model alias silently changes system behavior under your feet — invalidating every eval score — and unpinned dependencies/MCP packages are the delivery vehicle for the agent supply-chain attacks seen through 2025-2026. v1 had no supply-chain check at all.

**How to measure it (search strategies, adapt to the stack):**

- model pinning: grep model id configs for dated/exact ids vs. aliases ('latest', unversioned names) in PRODUCTION config
- lockfiles committed: package-lock.json / pnpm-lock.yaml / poetry.lock / uv.lock / requirements.txt with == pins / go.sum / Cargo.lock in git
- Docker: base images pinned by digest ('@sha256:') or exact tag vs. ':latest'; CI actions pinned to SHA vs. '@main'
- weight/artifact integrity: checksum/signature verification on downloads ('sha256', 'verify', HF revision pins)
- dependency scanning in CI: dependabot/renovate config, 'pip-audit', 'npm audit', 'trivy', 'grype', 'socket'

**Scoring anchors (these decide the 0/1/2):** 0 = floating model aliases (e.g. 'latest') in production config, or no lockfile committed; 1 = lockfiles committed but model ids unpinned, or base images/CI actions unpinned, or no integrity verification/scanning; 2 = exact model ids + committed lockfiles + pinned images/actions + integrity verification or dependency scanning in CI.


---

## Rollout Maturity — weight 8

*How autonomy is earned, not assumed.*


### R1 — Staged autonomy

**What it measures:** Evidence of shadow mode, human-approval mode, or partial automation (flags, modes, or config), not launch-to-full-autonomy.

**How to measure it (search strategies, adapt to the stack):**

- grep 'shadow', 'dry_run', 'suggest_only', 'autopilot', 'mode', 'autonomy_level', 'copilot'
- config/flags selecting between observe/suggest/act behaviors per feature or action type
- code branches where 'act' is gated behind a mode check while 'log what I would have done' always runs
- feature-flag definitions staging the rollout (percentage rollouts, cohort flags)

**Scoring anchors (these decide the 0/1/2):** 0 = launched straight to full autonomy — no modes, flags, or staging anywhere; 1 = a mode flag exists but is implicit/undocumented (a default nobody chose) or covers only part of the action surface; 2 = explicit observe/suggest/act staging in config with code branches honoring the mode per feature or action type.


### R2 — Promotion criteria

**What it measures:** Written, measurable criteria for moving between autonomy stages.

**How to measure it (search strategies, adapt to the stack):**

- docs: glob '**/rollout*', '**/promotion*', '**/graduation*', ADRs or runbooks stating thresholds ('promote when accuracy > X% over N cases')
- criteria tied to measured metrics that actually exist (cross-check P4/P6 outputs)
- grep 'criteria', 'graduate', 'promote' in docs/ and config
- criteria containing no numeric threshold or sample size ('when we're confident') = partial

**Scoring anchors (these decide the 0/1/2):** 0 = no written criteria for moving between autonomy stages; 1 = criteria written but containing no numeric threshold or sample size (e.g. 'when we're confident'); 2 = written, measurable thresholds ('promote when accuracy > X% over N cases') tied to metrics that actually exist (cross-check P4/P6).


### R3 — Rollback procedure

**What it measures:** A documented way to drop back a stage after an incident.

**How to measure it (search strategies, adapt to the stack):**

- runbooks: glob '**/rollback*', '**/incident*', '**/runbook*' describing how to reduce autonomy
- the mechanism referenced actually exists (the R1 mode flag / G6 switch it says to flip)
- grep 'rollback', 'demote', 'downgrade' in docs and deploy scripts
- post-incident templates or history showing the procedure was exercised

**Scoring anchors (these decide the 0/1/2):** 0 = no rollback/demotion procedure documented; 1 = a document exists but references mechanisms that don't exist, or has never been exercised; 2 = a documented procedure referencing real mechanisms (the R1 mode flag / G6 switch), exercised or tested at least once.


### R4 — Risk tiering

**What it measures:** Actions classified by risk level, with autonomy granted per tier rather than globally.

**How to measure it (search strategies, adapt to the stack):**

- grep 'risk', 'tier', 'severity', 'risk_level', 'high_risk' in action/tool definitions
- per-action or per-tool metadata assigning risk classes, consumed by the gating logic (cross-check G3/G9)
- config mapping tiers to required approvals/autonomy modes
- ANTI-EVIDENCE: one global autonomy switch applied identically to 'send summary email' and 'issue refund'

**Scoring anchors (these decide the 0/1/2):** 0 = one global autonomy switch applied identically to all actions regardless of risk; 1 = risk labels/tiers exist on actions but the gating logic does not consume them; 2 = per-action/per-tool risk tiers consumed by the gating logic (cross-check G3/G9), with autonomy granted per tier.


---

## NFR Foundations — weight 6

*Non-functional foundations.*


### N1 — Latency budget

**What it measures:** A stated target with measurement against it.

**How to measure it (search strategies, adapt to the stack):**

- stated targets: grep 'latency', 'p95', 'p99', 'slo', 'sla', 'budget_ms' in docs/config/monitoring rules
- measurement: latency histograms/percentile metrics in code or APM config (cross-check S4)
- alerting when the target is breached (alarm thresholds matching the stated budget)
- streaming/TTFT targets for chat UX ('time_to_first_token') where applicable

**Scoring anchors (these decide the 0/1/2):** 0 = no stated latency target and no measurement; 1 = a target stated without measurement, or latency measured without a stated target; 2 = a stated target + percentile measurement against it + an alert when the target is breached.


### N2 — Scalability posture

**What it measures:** Stateless services or documented scaling approach for the load-bearing path.

**How to measure it (search strategies, adapt to the stack):**

- statelessness: session/state kept in Redis/DB vs. in-process globals and module-level caches holding per-user state
- horizontal scaling config: k8s replicas/HPA, PM2 cluster mode, serverless deployment (Vercel/Lambda), ASGI workers
- docs: architecture notes on the scaling approach for the hot path
- grep for in-memory singletons on the request path that would break with >1 instance (anti-evidence)

**Scoring anchors (these decide the 0/1/2):** 0 = per-user/request state held in process memory on the hot path (breaks with >1 instance); 1 = mostly stateless but the scaling approach is undocumented and unconfigured; 2 = stateless load-bearing path (state in Redis/DB) with a documented or configured horizontal scaling approach (replicas, HPA, serverless, cluster mode).


### N3 — Reliability basics

**What it measures:** Retries with backoff, idempotency for event handlers (duplicate events don't double-process), graceful degradation.

**How to measure it (search strategies, adapt to the stack):**

- grep 'retry', 'backoff', 'tenacity', 'p-retry', 'exponential' on external calls
- idempotency: 'idempotency_key', dedupe by event id, upsert-not-insert in webhook/event handlers
- graceful degradation branches: reduced functionality on dependency failure rather than 500s ('except', 'catch' paths returning useful fallbacks)
- dead-letter queues / poison-message handling in the async layer

**Scoring anchors (these decide the 0/1/2):** 0 = no retries, no idempotency, failures surface as unhandled errors; 1 = retries with backoff present but event/webhook handlers not idempotent, or no graceful-degradation branches; 2 = backoff retries on external calls + idempotent event handling (dedupe/upsert by event id) + graceful degradation paths.


### N4 — Compliance mapping

**What it measures:** If the domain is regulated (health, finance, government), controls are mapped to the applicable regime (HIPAA, SOC 2, GDPR, FedRAMP).

**How to measure it (search strategies, adapt to the stack):**

- grep -ri 'hipaa', 'soc 2', 'soc2', 'gdpr', 'fedramp', 'pci', 'ccpa', 'dpa', 'baa' in docs/
- control mappings: compliance matrices, policy docs linking controls to code/infra
- data-handling artifacts: retention policies, data-processing agreements, PHI/PII data-flow diagrams
- N/A allowed for genuinely unregulated hobby/internal tools — state the domain judgment explicitly

**Scoring anchors (these decide the 0/1/2):** 0 = regulated domain (health, finance, government) with no compliance mapping at all; 1 = the applicable regime is named in docs but controls are not mapped to code/infra; 2 = a control mapping linking regime requirements (HIPAA, SOC 2, GDPR, FedRAMP...) to implemented controls and data-handling artifacts. N/A for genuinely unregulated hobby/internal tools, with the domain judgment stated.


---

*End of reference. The audit engine is `SKILL.md`; the math is `scoring.md`; propose improvements via `EVOLUTION.md`.*

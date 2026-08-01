import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Boxes,
  CheckCircle2,
  Code2,
  ExternalLink,
  FileDiff,
  FileText,
  Focus,
  FolderSync,
  GitCompareArrows,
  GitBranch,
  Link2,
  Maximize2,
  Minus,
  Minimize2,
  MousePointer2,
  Network,
  Orbit,
  Pause,
  Play,
  Plus,
  RefreshCw,
  RotateCcw,
  Route,
  Search,
  ShieldCheck,
  TimerReset,
} from "lucide-react";
import "./KnowledgeIntegrations.css";

const NODE_ORDER = ["connector", "note", "source", "claim", "change", "release", "run"];
const NODE_COLORS = {
  connector: "#7c3aed",
  note: "#8b5cf6",
  source: "#2563eb",
  claim: "#0f766e",
  change: "#d97706",
  release: "#059669",
  run: "#475569",
};

const ARCHITECTURE_LAYERS = [
  { id: "operator-ui", label: "Operator experience", short: "UI", color: "#7c3aed", x: 78, y: 252 },
  { id: "control-plane", label: "API control plane", short: "API", color: "#0891b2", x: 318, y: 252 },
  { id: "agent-runtime", label: "Agent workflow", short: "Agent", color: "#2563eb", x: 560, y: 62 },
  { id: "knowledge", label: "Knowledge governance", short: "Knowledge", color: "#0f766e", x: 560, y: 188 },
  { id: "trust-assurance", label: "Trust & evidence", short: "Trust", color: "#d97706", x: 560, y: 314 },
  { id: "platform-data", label: "Platform & data", short: "Platform", color: "#475569", x: 560, y: 440 },
  { id: "verification", label: "Verification suite", short: "Tests", color: "#dc2626", x: 838, y: 112 },
  { id: "delivery-tooling", label: "Delivery tooling", short: "Delivery", color: "#059669", x: 838, y: 302 },
  { id: "external", label: "Bounded dependencies", short: "External", color: "#64748b", x: 838, y: 470 },
];

const ARCHITECTURE_LAYER_BY_ID = new Map(ARCHITECTURE_LAYERS.map((layer) => [layer.id, layer]));
const ARCHITECTURE_LAYER_DETAILS = {
  "operator-ui": {
    purpose: "Gives operators one accountable place to inspect, approve and explain AI activity.",
    operation: "A user action becomes an explicit platform request with visible state, ownership and evidence.",
    controls: ["explicit intent", "human context", "no embedded secrets"],
    evidence: "Run identity, operator action and presentation-safe state",
    section: "operator-console",
    destination: "Operator Console",
    story: "source-bound-rag",
  },
  "control-plane": {
    purpose: "Turns model intent into server-enforced policy decisions before business systems are reached.",
    operation: "FastAPI validates the request, binds policy and identity context, and returns allowed, denied or approval-required.",
    controls: ["policy version", "tenant boundary", "strict payloads"],
    evidence: "Decision, policy version, correlation ID and audit event",
    section: "policy-engine",
    destination: "Policy Engine",
    story: "regulated-write",
  },
  "agent-runtime": {
    purpose: "Coordinates bounded agent steps without granting infrastructure credentials or shell access.",
    operation: "The workflow can call only scoped backend capabilities and must accept policy or approval outcomes.",
    controls: ["scoped tools", "no shell", "no direct database password"],
    evidence: "Tool request, granted scope and execution outcome",
    section: "tool-gateway",
    destination: "Tool Gateway",
    story: "regulated-write",
  },
  knowledge: {
    purpose: "Keeps generated answers grounded in reviewed, attributable and versioned knowledge.",
    operation: "Untrusted documents are scanned, approved chunks are retrieved and unsupported answers fail safely.",
    controls: ["source allowlist", "injection scan", "citations required"],
    evidence: "Retrieved chunks, source IDs, citations and knowledge release",
    section: "safe-rag",
    destination: "Safe RAG",
    story: "source-bound-rag",
  },
  "trust-assurance": {
    purpose: "Binds sensitive actions to identity, independent approval and integrity evidence.",
    operation: "High-impact payloads pause until an authorized reviewer approves the exact digest.",
    controls: ["AAL2", "maker-checker", "payload digest"],
    evidence: "Principal, approval decision, attestation and audit timeline",
    section: "identity-trust",
    destination: "Identity & Trust",
    story: "regulated-write",
  },
  "platform-data": {
    purpose: "Persists durable platform state while keeping storage credentials outside the agent boundary.",
    operation: "Backend services own transactions, idempotency and data access; agents receive narrow results only.",
    controls: ["transaction boundary", "idempotency", "credential isolation"],
    evidence: "Durable state transition and consistency outcome",
    section: "ledger-demo",
    destination: "Ledger Demo",
    story: "regulated-write",
  },
  verification: {
    purpose: "Proves that candidate behavior preserves policy, security and release controls.",
    operation: "Automated tests, adversarial evals and replay evidence converge on a deterministic release decision.",
    controls: ["security evals", "policy replay", "fail-closed gate"],
    evidence: "Test results, replay diff and GO or NO-GO rationale",
    section: "release-assurance",
    destination: "Release Assurance",
    story: "release-assurance",
  },
  "delivery-tooling": {
    purpose: "Converts bounded scanner and CI output into reviewable release evidence without deployment authority.",
    operation: "Immutable commit evidence is normalized, reviewed and attached to an external delivery handoff.",
    controls: ["pinned commit", "bounded SARIF", "external CI"],
    evidence: "Artifact digest, validation results and controlled handoff",
    section: "code-assurance",
    destination: "Code Assurance",
    story: "release-assurance",
  },
  external: {
    purpose: "Makes third-party and enterprise dependencies visible without treating them as trusted internals.",
    operation: "External capabilities remain behind configured adapters, scopes and explicit ownership boundaries.",
    controls: ["adapter boundary", "allowlisted capability", "least privilege"],
    evidence: "Dependency relationship, owner and integration contract",
    section: "governance-registry",
    destination: "Governance Registry",
    story: "prompt-containment",
  },
};

const ARCHITECTURE_STORIES = [
  {
    id: "source-bound-rag",
    label: "Source-bound RAG",
    outcome: "An answer is released only with approved evidence and citations.",
    section: "safe-rag",
    destination: "Open Safe RAG",
    steps: [
      { layer: "operator-ui", label: "Question captured", detail: "The operator submits an attributable request." },
      { layer: "control-plane", label: "Request governed", detail: "Identity, tenant and policy context are bound server-side." },
      { layer: "knowledge", label: "Evidence retrieved", detail: "Only approved chunks survive source and injection controls." },
      { layer: "agent-runtime", label: "Answer composed", detail: "The workflow remains bounded to retrieved evidence." },
      { layer: "trust-assurance", label: "Citations preserved", detail: "The decision and supporting evidence enter the audit timeline." },
    ],
  },
  {
    id: "regulated-write",
    label: "Regulated write",
    outcome: "A business write pauses for independent approval before execution.",
    section: "human-approval",
    destination: "Open Human Approval",
    steps: [
      { layer: "operator-ui", label: "Action requested", detail: "The operator asks the assistant to create a regulated record." },
      { layer: "agent-runtime", label: "Tool intent formed", detail: "The agent selects a scoped capability, not infrastructure access." },
      { layer: "control-plane", label: "Policy pauses write", detail: "The server returns approval-required for the exact payload." },
      { layer: "trust-assurance", label: "Reviewer approves", detail: "A separate AAL2 principal approves the payload digest." },
      { layer: "platform-data", label: "Write committed", detail: "The backend performs the transaction and records evidence." },
    ],
  },
  {
    id: "prompt-containment",
    label: "Injection containment",
    outcome: "An adversarial instruction is isolated before it becomes agent authority.",
    section: "prompt-lab",
    destination: "Open Prompt Lab",
    steps: [
      { layer: "operator-ui", label: "Attack submitted", detail: "A reproducible injection scenario enters the platform." },
      { layer: "knowledge", label: "Input treated as data", detail: "Retrieved instructions remain untrusted evidence." },
      { layer: "control-plane", label: "Policy denies", detail: "Secret or privilege escalation intent is blocked." },
      { layer: "trust-assurance", label: "Incident evidenced", detail: "Risk factors and the denied decision are preserved." },
      { layer: "verification", label: "Regression proven", detail: "The same attack remains part of the security evaluation suite." },
    ],
  },
  {
    id: "policy-replay",
    label: "Policy replay",
    outcome: "A candidate policy is tested against historical and adversarial evidence before rollout.",
    section: "policy-replay",
    destination: "Open Policy Replay",
    steps: [
      { layer: "control-plane", label: "Candidate loaded", detail: "A candidate policy is evaluated without changing runtime behavior." },
      { layer: "verification", label: "History replayed", detail: "Recorded runs and adversarial cases receive candidate decisions." },
      { layer: "trust-assurance", label: "Diff classified", detail: "Safer, stricter and regressive outcomes become review evidence." },
      { layer: "delivery-tooling", label: "Rollout bounded", detail: "Only reviewed evidence can progress toward release assurance." },
    ],
  },
  {
    id: "release-assurance",
    label: "Release assurance",
    outcome: "Code, policy and attack-path evidence converge on a non-deploying GO or NO-GO.",
    section: "release-assurance",
    destination: "Open Release Assurance",
    steps: [
      { layer: "delivery-tooling", label: "Candidate pinned", detail: "Scanner and CI evidence are bound to one immutable commit." },
      { layer: "verification", label: "Controls evaluated", detail: "Build, tests, security evals and replay must pass." },
      { layer: "trust-assurance", label: "Maker-checker applied", detail: "An independent reviewer owns the release decision." },
      { layer: "control-plane", label: "Gate attested", detail: "The platform produces integrity evidence, never a deployment." },
    ],
  },
];

const ARCHITECTURE_STORY_BY_ID = new Map(ARCHITECTURE_STORIES.map((story) => [story.id, story]));
const ARCHITECTURE_IMPACT = {
  label: "Approval fast-path candidate",
  score: 92,
  sequence: ["agent-runtime", "control-plane", "trust-assurance", "platform-data", "verification"],
  layers: {
    "agent-runtime": { state: "changed", label: "scope expanded", detail: "The candidate makes a regulated write directly reachable." },
    "control-plane": { state: "changed", label: "decision changed", detail: "create_case_note moves from approval-required to allowed." },
    "trust-assurance": { state: "weakened", label: "approval bypassed", detail: "Maker-checker no longer protects the payload transition." },
    "platform-data": { state: "exposed", label: "write reachable", detail: "Customer case data becomes reachable without independent review." },
    verification: { state: "blocking", label: "release blocked", detail: "Security replay detects the regression and returns NO-GO." },
  },
};
const EMPTY_ARCHITECTURE_GRAPH = {
  meta: { nodes: 0, edges: 0, communities: 0, extractedEdges: 0, inferredEdges: 0, layerCounts: {}, digest: "loading" },
  nodes: [],
  edges: [],
};

function architectureSummary(graph) {
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const layers = ARCHITECTURE_LAYERS.map((layer) => {
    const nodes = graph.nodes.filter((node) => node.layer === layer.id).sort((a, b) => b.degree - a.degree);
    return {
      ...layer,
      nodes,
      topNode: nodes[0] ?? null,
      internalEdges: graph.edges.filter((edge) => nodeById.get(edge.s)?.layer === layer.id && nodeById.get(edge.t)?.layer === layer.id).length,
    };
  });
  const crossLayerEdges = new Map();
  graph.edges.forEach((edge) => {
    const sourceLayer = nodeById.get(edge.s)?.layer;
    const targetLayer = nodeById.get(edge.t)?.layer;
    if (!sourceLayer || !targetLayer || sourceLayer === targetLayer) return;
    const key = `${sourceLayer}|${targetLayer}`;
    const current = crossLayerEdges.get(key) ?? { source: sourceLayer, target: targetLayer, count: 0, inferred: 0 };
    current.count += 1;
    if (edge.c === "inferred") current.inferred += 1;
    crossLayerEdges.set(key, current);
  });
  return { layers, edges: [...crossLayerEdges.values()].sort((a, b) => b.count - a.count).slice(0, 22) };
}

function architectureSymbolLayout(graph, activeLayer, query, density) {
  const queryValue = query.trim().toLowerCase();
  const nodeById = new Map(graph.nodes.map((node) => [node.id, node]));
  const matches = new Set(
    graph.nodes
      .filter((node) => queryValue && `${node.label} ${node.source}`.toLowerCase().includes(queryValue))
      .map((node) => node.id),
  );
  const contextIds = new Set(matches);
  if (matches.size) {
    graph.edges.forEach((edge) => {
      if (matches.has(edge.s)) contextIds.add(edge.t);
      if (matches.has(edge.t)) contextIds.add(edge.s);
    });
  }

  const scoped = graph.nodes.filter((node) => {
    if (matches.size) return contextIds.has(node.id);
    return activeLayer === "all" || node.layer === activeLayer;
  });
  const visible = [];
  const layerPool = activeLayer === "all" && !matches.size ? ARCHITECTURE_LAYERS : [{ id: activeLayer }];
  const perLayer = Math.max(5, Math.ceil(density / Math.max(layerPool.length, 1)));
  layerPool.forEach((layer) => {
    visible.push(...scoped.filter((node) => activeLayer !== "all" || node.layer === layer.id).sort((a, b) => b.degree - a.degree).slice(0, perLayer));
  });
  if (matches.size) visible.push(...scoped.sort((a, b) => Number(matches.has(b.id)) - Number(matches.has(a.id)) || b.degree - a.degree).slice(0, density));

  const unique = [...new Map(visible.map((node) => [node.id, node])).values()].slice(0, Math.max(density, matches.size));
  const positions = {};
  if (activeLayer !== "all" || matches.size) {
    const columns = 11;
    unique.forEach((node, index) => {
      positions[node.id] = { x: 68 + (index % columns) * 92, y: 58 + Math.floor(index / columns) * 68 };
    });
  } else {
    ARCHITECTURE_LAYERS.forEach((layer) => {
      unique.filter((node) => node.layer === layer.id).forEach((node, index) => {
        const angle = index * 2.399963;
        const radius = 13 + Math.sqrt(index) * 22;
        positions[node.id] = {
          x: layer.x + 78 + Math.cos(angle) * radius * 1.18,
          y: layer.y + 34 + Math.sin(angle) * radius,
        };
      });
    });
  }
  const visibleIds = new Set(unique.map((node) => node.id));
  return {
    nodes: unique.map((node) => ({ ...node, position: positions[node.id], match: matches.has(node.id) })),
    edges: graph.edges.filter((edge) => visibleIds.has(edge.s) && visibleIds.has(edge.t)),
    positions,
    nodeById,
  };
}

function shortArchitectureLabel(label, maximum = 19) {
  return label.length > maximum ? `${label.slice(0, maximum - 1)}…` : label;
}

function splitList(value) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

export function ObsidianConnectorView({
  connectorState,
  draft,
  setDraft,
  preview,
  busy,
  applyComment,
  setApplyComment,
  onPreview,
  onApply,
}) {
  const mode = connectorState?.security_mode ?? "loading";
  const connectors = connectorState?.connectors ?? [];
  const files = connectorState?.files ?? [];
  const activeConnector = connectors.find((item) => item.id === draft.connector_id) ?? connectors[0];
  const actionable = preview ? (preview.summary.new + preview.summary.modified + preview.summary.deleted) : 0;

  return (
    <div className="obsidian-connector-view">
      <header className="connector-command">
        <div className="connector-product-mark"><FolderSync size={21} /></div>
        <div>
          <span>Controlled source adapter</span>
          <h3>Obsidian Vault Connector</h3>
          <p>Scan Markdown notes, review a persisted diff and create approval-gated knowledge changes.</p>
        </div>
        <div className={"connector-mode " + mode}>
          <i />
          {mode.replaceAll("_", " ")}
        </div>
      </header>

      <div className="connector-stage-track" aria-label="Obsidian connector workflow">
        {[
          ["01", "Scope vault", true],
          ["02", "Preview diff", Boolean(preview)],
          ["03", "Apply to review", preview?.status === "applied"],
        ].map(([number, label, active]) => (
          <div className={active ? "active" : ""} key={label}><span>{number}</span><strong>{label}</strong></div>
        ))}
      </div>

      {mode === "disabled" && (
        <div className="connector-disabled" role="alert">
          <ShieldCheck size={17} />
          <p><strong>Connector disabled by default in production</strong><span>Configure OBSIDIAN_ALLOWED_ROOTS on the backend host before scanning any vault.</span></p>
        </div>
      )}

      <div className="connector-setup-grid">
        <article className="connector-config-card">
          <div className="connector-card-heading"><div><span>Connector scope</span><h4>Server-side vault allowlist</h4></div><ShieldCheck size={18} /></div>
          <div className="connector-form-grid">
            <label htmlFor="obsidian-connector-name">Connector name<input id="obsidian-connector-name" value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} /></label>
            <label htmlFor="obsidian-vault-name">Obsidian vault name<input id="obsidian-vault-name" value={draft.vault_name} onChange={(event) => setDraft({ ...draft, vault_name: event.target.value })} /></label>
            <label className="wide" htmlFor="obsidian-vault-path">Allowlisted host path<input id="obsidian-vault-path" value={draft.vault_path} onChange={(event) => setDraft({ ...draft, vault_path: event.target.value })} /></label>
            <label htmlFor="obsidian-folders">Included folders<input id="obsidian-folders" value={draft.include_folders} onChange={(event) => setDraft({ ...draft, include_folders: event.target.value })} placeholder="Policies, Controls" /></label>
            <label htmlFor="obsidian-tags">Required tags<input id="obsidian-tags" value={draft.required_tags} onChange={(event) => setDraft({ ...draft, required_tags: event.target.value })} placeholder="governed-ai" /></label>
            <label htmlFor="obsidian-owner">Default owner<input id="obsidian-owner" value={draft.default_owner} onChange={(event) => setDraft({ ...draft, default_owner: event.target.value })} /></label>
            <label htmlFor="obsidian-classification">Default classification<select id="obsidian-classification" value={draft.classification} onChange={(event) => setDraft({ ...draft, classification: event.target.value })}><option>public</option><option>internal</option><option>confidential</option><option>restricted</option></select></label>
          </div>
          <button className="connector-scan" type="button" disabled={busy === "obsidian-preview" || mode === "disabled"} onClick={() => onPreview({ ...draft, include_folders: splitList(draft.include_folders), required_tags: splitList(draft.required_tags) })}>
            {busy === "obsidian-preview" ? <TimerReset size={16} /> : <FileDiff size={16} />}
            {busy === "obsidian-preview" ? "Scanning controlled scope..." : "Scan and preview diff"}
          </button>
          <p className="connector-boundary"><ShieldCheck size={13} />Hidden folders, symlinks, non-UTF-8 files and notes without required tags are excluded.</p>
        </article>

        <aside className="connector-posture-card">
          <div className="connector-card-heading"><div><span>Connector posture</span><h4>{activeConnector?.name ?? "Not connected"}</h4></div><FolderSync size={18} /></div>
          <dl>
            <div><dt>Vault</dt><dd>{activeConnector?.vault_name ?? draft.vault_name}</dd></div>
            <div><dt>Tracked notes</dt><dd>{files.filter((item) => item.connector_id === activeConnector?.id && item.status === "active").length}</dd></div>
            <div><dt>Last preview</dt><dd>{activeConnector?.last_scan_at ? new Date(activeConnector.last_scan_at).toLocaleString() : "not scanned"}</dd></div>
            <div><dt>Last controlled sync</dt><dd>{activeConnector?.last_sync_at ? new Date(activeConnector.last_sync_at).toLocaleString() : "not applied"}</dd></div>
          </dl>
          <div className="connector-policy">
            <strong>Publication boundary</strong>
            <p>Apply creates immutable sources and review changes. It never publishes directly into RAG.</p>
          </div>
        </aside>
      </div>

      {preview && (
        <section className="connector-preview">
          <div className="connector-preview-heading">
            <div><span>Persisted preview</span><h4>Vault change set</h4><code>{preview.id} · {preview.scan_digest.slice(0, 14)}…</code></div>
            <span className={"knowledge-status " + preview.status}>{preview.status}</span>
          </div>
          <div className="connector-diff-metrics">
            <div className="new"><span>New</span><strong>{preview.summary.new}</strong></div>
            <div className="modified"><span>Modified</span><strong>{preview.summary.modified}</strong></div>
            <div className="deleted"><span>Deleted</span><strong>{preview.summary.deleted}</strong></div>
            <div><span>Unchanged</span><strong>{preview.summary.unchanged}</strong></div>
            <div><span>Excluded</span><strong>{preview.summary.skipped}</strong></div>
          </div>
          <div className="connector-diff-list">
            {preview.changes.map((item) => (
              <article className={"connector-diff-row " + item.change_type} key={item.relative_path}>
                <div className="connector-change-icon">{item.change_type === "deleted" ? <AlertTriangle size={16} /> : item.change_type === "unchanged" ? <CheckCircle2 size={16} /> : <FileText size={16} />}</div>
                <div className="connector-note-copy">
                  <span>{item.change_type}</span>
                  <strong>{item.title}</strong>
                  <code>{item.relative_path}</code>
                  <p>{item.excerpt}</p>
                </div>
                <div className="connector-note-meta">
                  <span className={"connector-security " + item.security_status}>{item.security_status?.replaceAll("_", " ")}</span>
                  <small>{(item.tags ?? item.metadata?.tags ?? []).map((tag) => "#" + tag).join(" ")}</small>
                  {item.obsidian_uri && <a href={item.obsidian_uri}><ExternalLink size={13} />Open in Obsidian</a>}
                </div>
              </article>
            ))}
          </div>
          {preview.skipped.length > 0 && (
            <details className="connector-skipped">
              <summary>{preview.skipped.length} excluded paths</summary>
              {preview.skipped.map((item) => <p key={item.path}><code>{item.path}</code><span>{item.reason}</span></p>)}
            </details>
          )}
          <div className="connector-apply-bar">
            <label htmlFor="obsidian-apply-comment">Approval evidence comment<textarea id="obsidian-apply-comment" value={applyComment} onChange={(event) => setApplyComment(event.target.value)} /></label>
            <div><span><ShieldCheck size={14} />{actionable} controlled transitions</span><button type="button" disabled={preview.status !== "staged" || actionable === 0 || applyComment.trim().length < 10 || busy === "obsidian-apply"} onClick={onApply}>{busy === "obsidian-apply" ? <TimerReset size={16} /> : <FolderSync size={16} />}{busy === "obsidian-apply" ? "Verifying snapshot..." : "Apply to review queue"}</button></div>
          </div>
        </section>
      )}
    </div>
  );
}

function graphLayout(nodes, edges, filter, query) {
  const queryValue = query.trim().toLowerCase();
  const matches = new Set(
    nodes.filter((node) => !queryValue || (node.label + " " + JSON.stringify(node.metadata)).toLowerCase().includes(queryValue)).map((node) => node.id),
  );
  let contextual = nodes;
  if (filter !== "all") {
    const primary = new Set(nodes.filter((node) => node.type === filter).map((node) => node.id));
    const neighbours = new Set();
    edges.forEach((edge) => {
      if (primary.has(edge.source)) neighbours.add(edge.target);
      if (primary.has(edge.target)) neighbours.add(edge.source);
    });
    contextual = nodes.filter((node) => primary.has(node.id) || neighbours.has(node.id));
  }
  const capped = [];
  NODE_ORDER.forEach((type) => capped.push(...contextual.filter((node) => node.type === type).slice(0, 9)));
  const nodeIds = new Set(capped.map((node) => node.id));
  const positions = {};
  NODE_ORDER.forEach((type, typeIndex) => {
    const typed = capped.filter((node) => node.type === type);
    typed.forEach((node, index) => {
      positions[node.id] = { x: 25 + typeIndex * 155, y: 48 + ((index + 1) * 410) / (typed.length + 1) };
    });
  });
  return {
    nodes: capped.map((node) => ({ ...node, position: positions[node.id], match: matches.has(node.id) })),
    edges: edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)),
    positions,
  };
}

export function KnowledgeGraphView({ graph, busy, onRefresh }) {
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const layout = useMemo(() => graphLayout(graph?.nodes ?? [], graph?.edges ?? [], filter, query), [filter, graph, query]);
  const selected = (graph?.nodes ?? []).find((node) => node.id === selectedId) ?? layout.nodes[0] ?? null;
  const types = graph?.metrics?.types ?? {};

  return (
    <div className="governance-graph-view">
      <header className="graph-command">
        <div><span>Knowledge lineage</span><h3>Governance relationship graph</h3><p>Trace authoritative provenance and clearly marked inferred run overlap.</p></div>
        <button type="button" disabled={busy === "graph-refresh"} onClick={onRefresh}><RefreshCw size={15} />Refresh graph</button>
      </header>
      <div className="graph-metrics">
        <div><Network size={17} /><span><strong>{graph?.metrics?.nodes ?? 0}</strong>nodes</span></div>
        <div><GitBranch size={17} /><span><strong>{graph?.metrics?.edges ?? 0}</strong>relations</span></div>
        <div><ShieldCheck size={17} /><span><strong>{(graph?.semantics?.authoritative ?? []).length}</strong>authoritative types</span></div>
        <div><AlertTriangle size={17} /><span><strong>{(graph?.semantics?.inferred ?? []).length}</strong>inferred type</span></div>
      </div>
      <div className="graph-toolbar">
        <label htmlFor="knowledge-graph-search"><Search size={14} /><input id="knowledge-graph-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search nodes and metadata" /></label>
        <div className="graph-type-filter" aria-label="Filter graph by node type">
          {["all", ...NODE_ORDER].map((type) => <button className={filter === type ? "active" : ""} type="button" key={type} onClick={() => setFilter(type)}>{type}<span>{type === "all" ? graph?.metrics?.nodes ?? 0 : types[type] ?? 0}</span></button>)}
        </div>
      </div>
      <div className="graph-workspace">
        <div className="graph-canvas-wrap">
          <svg className="knowledge-graph-canvas" viewBox="0 0 1100 510" role="img" aria-labelledby="knowledge-graph-title knowledge-graph-desc">
            <title id="knowledge-graph-title">Governed knowledge provenance graph</title>
            <desc id="knowledge-graph-desc">Connectors, Obsidian notes, immutable sources, claims, changes, releases and historical runs.</desc>
            <defs><marker id="graph-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" /></marker></defs>
            {layout.edges.map((edge) => {
              const from = layout.positions[edge.source];
              const to = layout.positions[edge.target];
              return <line className={edge.inferred ? "inferred" : ""} key={edge.id} x1={from.x + 120} y1={from.y + 20} x2={to.x} y2={to.y + 20} markerEnd="url(#graph-arrow)"><title>{edge.relation}</title></line>;
            })}
            {layout.nodes.map((node) => (
              <g className={"graph-node " + node.type + (selected?.id === node.id ? " selected" : "") + (!node.match ? " dimmed" : "")} key={node.id} role="button" tabIndex="0" aria-label={node.type + ": " + node.label} transform={"translate(" + node.position.x + " " + node.position.y + ")"} onClick={() => setSelectedId(node.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") setSelectedId(node.id); }}>
                <rect width="120" height="40" rx="7" fill="#ffffff" stroke={NODE_COLORS[node.type]} />
                <circle cx="13" cy="13" r="4" fill={NODE_COLORS[node.type]} />
                <text x="22" y="16">{node.type}</text>
                <text className="node-label" x="11" y="31">{node.label.length > 18 ? node.label.slice(0, 18) + "…" : node.label}</text>
                <title>{node.label}</title>
              </g>
            ))}
          </svg>
          <div className="graph-legend">{NODE_ORDER.map((type) => <span key={type}><i style={{ background: NODE_COLORS[type] }} />{type}</span>)}</div>
        </div>
        <aside className="graph-inspector">
          {selected ? (
            <>
              <div className="graph-inspector-heading"><i style={{ background: NODE_COLORS[selected.type] }} /><div><span>{selected.type}</span><h4>{selected.label}</h4></div></div>
              <span className={"knowledge-status " + selected.status}>{selected.status?.replaceAll("_", " ")}</span>
              <dl>{Object.entries(selected.metadata ?? {}).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{Array.isArray(value) ? value.join(", ") : value == null ? "not recorded" : String(value)}</dd></div>)}</dl>
              {selected.obsidian_uri && <a href={selected.obsidian_uri}><ExternalLink size={14} />Open original in Obsidian</a>}
            </>
          ) : <div className="graph-empty"><Network size={22} /><p>Select a node to inspect its governed metadata.</p></div>}
        </aside>
      </div>
      <div className="graph-semantics"><AlertTriangle size={15} /><p><strong>Relationship semantics</strong><span>{graph?.semantics?.note ?? "Inferred edges are visually distinct from authoritative lineage."}</span></p></div>
      <details className="graph-adjacency">
        <summary><Link2 size={14} />Accessible relationship list</summary>
        <div className="knowledge-table-wrap"><table className="knowledge-table"><thead><tr><th>Source</th><th>Relationship</th><th>Target</th><th>Evidence</th></tr></thead><tbody>{(graph?.edges ?? []).slice(0, 60).map((edge) => { const source = graph.nodes.find((node) => node.id === edge.source); const target = graph.nodes.find((node) => node.id === edge.target); return <tr key={edge.id}><td>{source?.label ?? edge.source}</td><td>{edge.relation.replaceAll("_", " ")}</td><td>{target?.label ?? edge.target}</td><td>{edge.inferred ? "inferred overlap" : "persisted lineage"}</td></tr>; })}</tbody></table></div>
      </details>
    </div>
  );
}

export function ArchitectureGraphView({ onNavigate }) {
  const [architectureGraph, setArchitectureGraph] = useState(EMPTY_ARCHITECTURE_GRAPH);
  const [graphLoadError, setGraphLoadError] = useState(false);
  const [mode, setMode] = useState("systems");
  const [experienceMode, setExperienceMode] = useState("explore");
  const [storyId, setStoryId] = useState("source-bound-rag");
  const [storyStep, setStoryStep] = useState(0);
  const [storyPlaying, setStoryPlaying] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  const [activeLayer, setActiveLayer] = useState("all");
  const [query, setQuery] = useState("");
  const [density, setDensity] = useState(84);
  const [zoom, setZoom] = useState(1);
  const [focusEnabled, setFocusEnabled] = useState(false);
  const [isPresentation, setIsPresentation] = useState(false);
  const [tilt, setTilt] = useState({ x: -2.5, y: 1.5 });
  const [dragging, setDragging] = useState(false);
  const presentationTriggerRef = useRef(null);
  const presentationExitRef = useRef(null);
  const dragStateRef = useRef({ active: false, moved: false, x: 0, y: 0, tiltX: 0, tiltY: 0 });
  const summary = useMemo(() => architectureSummary(architectureGraph), [architectureGraph]);
  const initialNode = useMemo(() => [...architectureGraph.nodes].sort((a, b) => b.degree - a.degree)[0], [architectureGraph]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedLayerId, setSelectedLayerId] = useState("control-plane");
  const symbolLayout = useMemo(
    () => architectureSymbolLayout(architectureGraph, activeLayer, query, density),
    [activeLayer, architectureGraph, density, query],
  );
  const selectedNode = architectureGraph.nodes.find((node) => node.id === selectedId) ?? symbolLayout.nodes[0] ?? null;
  const selectedLayer = summary.layers.find((layer) => layer.id === selectedLayerId) ?? summary.layers[0];
  const selectedConnections = selectedNode
    ? architectureGraph.edges
        .filter((edge) => edge.s === selectedNode.id || edge.t === selectedNode.id)
        .sort((a, b) => Number(b.c === "extracted") - Number(a.c === "extracted"))
        .slice(0, 12)
    : [];
  const selectedNeighbourIds = new Set(selectedConnections.flatMap((edge) => [edge.s, edge.t]));
  const selectedLayerDetails = ARCHITECTURE_LAYER_DETAILS[selectedLayer?.id] ?? ARCHITECTURE_LAYER_DETAILS["control-plane"];
  const activeStory = ARCHITECTURE_STORY_BY_ID.get(storyId) ?? ARCHITECTURE_STORIES[0];
  const activeFlowSteps = experienceMode === "impact"
    ? ARCHITECTURE_IMPACT.sequence.map((layer) => ({ layer, label: ARCHITECTURE_IMPACT.layers[layer].label, detail: ARCHITECTURE_IMPACT.layers[layer].detail }))
    : activeStory.steps;
  const boundedStoryStep = Math.min(storyStep, Math.max(activeFlowSteps.length - 1, 0));
  const currentFlowStep = activeFlowSteps[boundedStoryStep] ?? activeFlowSteps[0];
  const revealedFlowLayers = new Set(activeFlowSteps.slice(0, boundedStoryStep + 1).map((step) => step.layer));
  const activeFlowPairs = activeFlowSteps.slice(1, boundedStoryStep + 1).map((step, index) => [activeFlowSteps[index].layer, step.layer]);
  const focusedFlowLayer = experienceMode === "explore" ? null : currentFlowStep?.layer;
  const focusLayerId = mode === "systems" && focusEnabled ? (focusedFlowLayer ?? selectedLayer?.id) : null;
  const focusLayerDefinition = focusLayerId ? ARCHITECTURE_LAYER_BY_ID.get(focusLayerId) : null;
  const focusLayerDetails = focusLayerId ? ARCHITECTURE_LAYER_DETAILS[focusLayerId] : null;
  const focusNeighbourLayerIds = new Set(focusLayerId ? [focusLayerId] : []);
  if (focusLayerId) {
    summary.edges.forEach((edge) => {
      if (edge.source === focusLayerId) focusNeighbourLayerIds.add(edge.target);
      if (edge.target === focusLayerId) focusNeighbourLayerIds.add(edge.source);
    });
    if (experienceMode !== "explore") revealedFlowLayers.forEach((layerId) => focusNeighbourLayerIds.add(layerId));
  }
  const displayTilt = focusLayerDefinition ? { x: 0, y: 0 } : tilt;
  const selectedImpact = experienceMode === "impact" ? ARCHITECTURE_IMPACT.layers[selectedLayer?.id] : null;
  const focusScale = focusLayerDefinition ? (isPresentation ? 1.55 : 1.42) : 1;
  const effectiveGraphScale = Math.min(1.95, Number((zoom * focusScale).toFixed(2)));
  const graphTransform = focusLayerDefinition
    ? `translate(560 292) scale(${effectiveGraphScale}) translate(${-(focusLayerDefinition.x + 80)} ${-(focusLayerDefinition.y + 34)})`
    : `translate(560 292) scale(${zoom}) translate(-560 -292)`;
  const focusHeadline = experienceMode === "explore" ? "Selected control boundary" : currentFlowStep?.label;
  const focusDetail = experienceMode === "explore" ? focusLayerDetails?.operation : currentFlowStep?.detail;

  useEffect(() => {
    let active = true;
    import("../data/architecture-graph.json")
      .then((module) => {
        if (active) setArchitectureGraph(module.default);
      })
      .catch(() => {
        if (active) setGraphLoadError(true);
      });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!selectedId && initialNode) setSelectedId(initialNode.id);
  }, [initialNode, selectedId]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const syncMotionPreference = () => setPrefersReducedMotion(media.matches);
    syncMotionPreference();
    media.addEventListener?.("change", syncMotionPreference);
    return () => media.removeEventListener?.("change", syncMotionPreference);
  }, []);

  useEffect(() => {
    if (experienceMode === "explore" || !currentFlowStep?.layer) return;
    setSelectedLayerId(currentFlowStep.layer);
    setFocusEnabled(true);
  }, [currentFlowStep?.layer, experienceMode]);

  useEffect(() => {
    if (!isPresentation) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.requestAnimationFrame(() => presentationExitRef.current?.focus());
    return () => {
      document.body.style.overflow = previousOverflow;
      window.requestAnimationFrame(() => presentationTriggerRef.current?.focus());
    };
  }, [isPresentation]);

  useEffect(() => {
    if (!storyPlaying || experienceMode === "explore") return undefined;
    if (prefersReducedMotion) {
      setStoryStep(Math.max(activeFlowSteps.length - 1, 0));
      setStoryPlaying(false);
      return undefined;
    }
    const timer = window.setTimeout(() => {
      if (storyStep >= activeFlowSteps.length - 1) setStoryPlaying(false);
      else setStoryStep(storyStep + 1);
    }, 1550);
    return () => window.clearTimeout(timer);
  }, [activeFlowSteps.length, experienceMode, prefersReducedMotion, storyPlaying, storyStep]);

  function inspectLayer(layer) {
    setStoryPlaying(false);
    setSelectedLayerId(layer.id);
    setFocusEnabled(true);
  }

  function drillIntoLayer(layer) {
    setActiveLayer(layer.id);
    setSelectedLayerId(layer.id);
    setSelectedId(layer.topNode?.id ?? null);
    setMode("symbols");
    setExperienceMode("explore");
    setStoryPlaying(false);
    setFocusEnabled(false);
    setZoom(1);
  }

  function changeExperienceMode(nextMode) {
    setExperienceMode(nextMode);
    setMode("systems");
    setQuery("");
    setActiveLayer("all");
    setZoom(1);
    setStoryStep(0);
    setStoryPlaying(false);
    setFocusEnabled(nextMode !== "explore");
    const firstLayer = nextMode === "impact" ? ARCHITECTURE_IMPACT.sequence[0] : activeStory.steps[0]?.layer;
    if (nextMode !== "explore" && firstLayer) setSelectedLayerId(firstLayer);
  }

  function startStory(nextStoryId = storyId) {
    const nextStory = ARCHITECTURE_STORY_BY_ID.get(nextStoryId) ?? ARCHITECTURE_STORIES[0];
    setStoryId(nextStory.id);
    setExperienceMode("story");
    setMode("systems");
    setActiveLayer("all");
    setQuery("");
    setZoom(1);
    setFocusEnabled(true);
    setStoryStep(prefersReducedMotion ? nextStory.steps.length - 1 : 0);
    setSelectedLayerId(nextStory.steps[0]?.layer ?? "control-plane");
    setStoryPlaying(!prefersReducedMotion);
  }

  function toggleFlowPlayback() {
    if (prefersReducedMotion) {
      setStoryStep(Math.max(activeFlowSteps.length - 1, 0));
      setStoryPlaying(false);
      return;
    }
    if (boundedStoryStep >= activeFlowSteps.length - 1) setStoryStep(0);
    setStoryPlaying((value) => !value || boundedStoryStep >= activeFlowSteps.length - 1);
  }

  function moveFlowStep(direction) {
    setStoryPlaying(false);
    setFocusEnabled(true);
    setStoryStep((value) => Math.max(0, Math.min(activeFlowSteps.length - 1, value + direction)));
  }

  function handleTiltPointerDown(event) {
    if (mode !== "systems" || prefersReducedMotion || event.button !== 0) return;
    if (event.target.closest?.(".architecture-system-node, .architecture-symbol-node")) return;
    dragStateRef.current = { active: true, moved: false, x: event.clientX, y: event.clientY, tiltX: tilt.x, tiltY: tilt.y };
    event.currentTarget.setPointerCapture?.(event.pointerId);
    setDragging(true);
  }

  function handleTiltPointerMove(event) {
    if (!dragStateRef.current.active) return;
    const deltaX = event.clientX - dragStateRef.current.x;
    const deltaY = event.clientY - dragStateRef.current.y;
    if (Math.abs(deltaX) + Math.abs(deltaY) > 5) dragStateRef.current.moved = true;
    setTilt({
      x: Math.max(-7, Math.min(7, dragStateRef.current.tiltX - deltaY / 34)),
      y: Math.max(-12, Math.min(12, dragStateRef.current.tiltY + deltaX / 34)),
    });
  }

  function handleTiltPointerUp(event) {
    if (!dragStateRef.current.active) return;
    dragStateRef.current.active = false;
    event.currentTarget.releasePointerCapture?.(event.pointerId);
    setDragging(false);
  }

  function handleSystemNodeClick(layer) {
    if (dragStateRef.current.moved) {
      dragStateRef.current.moved = false;
      return;
    }
    inspectLayer(layer);
  }

  function resetView() {
    setActiveLayer("all");
    setQuery("");
    setZoom(1);
    setTilt({ x: -2.5, y: 1.5 });
    setExperienceMode("explore");
    setStoryPlaying(false);
    setFocusEnabled(false);
    setSelectedId(initialNode?.id ?? null);
  }

  function returnToOverview() {
    setStoryPlaying(false);
    setFocusEnabled(false);
    setZoom(1);
    setTilt({ x: -2.5, y: 1.5 });
  }

  function navigateFromAtlas(section) {
    setIsPresentation(false);
    onNavigate?.(section);
  }

  function handleArchitectureKeyDown(event) {
    if (event.target.closest?.("input, select, textarea")) return;
    if (event.key === "Escape") {
      event.preventDefault();
      if (isPresentation) setIsPresentation(false);
      else if (focusEnabled) returnToOverview();
      return;
    }
    if (!isPresentation || experienceMode === "explore") return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      moveFlowStep(-1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      moveFlowStep(1);
    }
  }

  return (
    <div
      className={`architecture-graph-view ${isPresentation ? "presentation-mode" : ""}`}
      role={isPresentation ? "dialog" : undefined}
      aria-modal={isPresentation ? "true" : undefined}
      aria-label={isPresentation ? "Interactive Governance Atlas presentation" : undefined}
      onKeyDown={handleArchitectureKeyDown}
    >
      {isPresentation && (
        <button className="architecture-presentation-exit" type="button" ref={presentationExitRef} onClick={() => setIsPresentation(false)}>
          <Minimize2 size={15} />Exit presentation <kbd>Esc</kbd>
        </button>
      )}
      <header className="architecture-command">
        <div className="architecture-command-mark"><Boxes size={20} /></div>
        <div>
          <span>Architecture intelligence · deterministic AST evidence</span>
          <h3>Regulated AI implementation map</h3>
          <p>Explore code-level dependencies without loading a CDN, invoking an LLM or exposing repository credentials.</p>
        </div>
        <div className="architecture-local-state"><ShieldCheck size={14} /><span>Local only</span><strong>0 LLM tokens</strong></div>
      </header>

      <div className="architecture-metrics">
        <div><Code2 size={17} /><span><strong>{architectureGraph.meta.nodes}</strong>symbols</span></div>
        <div><GitBranch size={17} /><span><strong>{architectureGraph.meta.edges}</strong>relations</span></div>
        <div><Network size={17} /><span><strong>{architectureGraph.meta.communities}</strong>communities</span></div>
        <div><ShieldCheck size={17} /><span><strong>{architectureGraph.meta.edges ? Math.round((architectureGraph.meta.extractedEdges / architectureGraph.meta.edges) * 100) : 0}%</strong>extracted evidence</span></div>
      </div>

      <div className="architecture-experience-switcher">
        <div className="architecture-experience-copy">
          <Orbit size={16} />
          <div><span>Interactive Governance Atlas</span><strong>Choose how to inspect the platform</strong></div>
        </div>
        <div className="architecture-experience-modes" role="group" aria-label="Architecture experience mode">
          <button className={experienceMode === "explore" ? "active" : ""} type="button" aria-pressed={experienceMode === "explore"} onClick={() => changeExperienceMode("explore")}><MousePointer2 size={14} /><span>Explore<small>rotate and inspect</small></span></button>
          <button className={experienceMode === "story" ? "active" : ""} type="button" aria-pressed={experienceMode === "story"} onClick={() => startStory()}><Route size={14} /><span>Guided Story<small>follow a control</small></span></button>
          <button className={experienceMode === "impact" ? "active" : ""} type="button" aria-pressed={experienceMode === "impact"} onClick={() => changeExperienceMode("impact")}><GitCompareArrows size={14} /><span>Change Impact<small>model blast radius</small></span></button>
        </div>
        <div className="architecture-experience-actions">
          <div className="architecture-motion-state"><i className={storyPlaying ? "playing" : ""} /><span>{prefersReducedMotion ? "Reduced" : storyPlaying ? "Running" : "Ready"}</span></div>
          <button className="architecture-presentation-trigger" type="button" ref={presentationTriggerRef} onClick={() => { setFocusEnabled(true); setIsPresentation(true); }}><Maximize2 size={14} /><span>Present<small>fullscreen focus</small></span></button>
        </div>
      </div>

      {experienceMode !== "explore" && (
        <section className={`architecture-flow-deck ${experienceMode}`} aria-label={experienceMode === "story" ? "Guided architecture story" : "Modeled architecture change impact"}>
          <div className="architecture-flow-context">
            {experienceMode === "story" ? (
              <label htmlFor="architecture-story-select"><span>Control story</span><select id="architecture-story-select" value={storyId} onChange={(event) => startStory(event.target.value)}>{ARCHITECTURE_STORIES.map((story) => <option key={story.id} value={story.id}>{story.label}</option>)}</select></label>
            ) : (
              <div className="architecture-impact-identity"><span>Modeled candidate</span><strong>{ARCHITECTURE_IMPACT.label}</strong><small>Portfolio scenario · no runtime mutation</small></div>
            )}
            <div className="architecture-flow-outcome">
              <span>{experienceMode === "story" ? "Governed outcome" : "Release decision"}</span>
              <strong>{experienceMode === "story" ? activeStory.outcome : "NO-GO · approval boundary regression"}</strong>
            </div>
          </div>

          {experienceMode === "impact" && (
            <div className="architecture-impact-baseline">
              <div><span>Baseline</span><strong>{architectureGraph.meta.baseCommit?.slice(0, 8) ?? "loading"}</strong><small>approval required</small></div>
              <ArrowRight size={15} />
              <div className="candidate"><span>Candidate</span><strong>approval-fast-path</strong><small>direct write reachable</small></div>
              <div className="risk"><span>Risk score</span><strong>{ARCHITECTURE_IMPACT.score}</strong><small>high · blocking</small></div>
            </div>
          )}

          <div className="architecture-flow-player">
            <div className="architecture-flow-step" aria-live="polite">
              <span>Step {boundedStoryStep + 1} of {activeFlowSteps.length}</span>
              <strong>{currentFlowStep?.label}</strong>
              <p>{currentFlowStep?.detail}</p>
            </div>
            <div className="architecture-flow-progress" aria-label="Flow progress">
              {activeFlowSteps.map((step, index) => <button className={`${index === boundedStoryStep ? "current" : ""} ${index < boundedStoryStep ? "complete" : ""}`} type="button" key={`${step.layer}-${index}`} aria-label={`Show step ${index + 1}: ${step.label}`} onClick={() => { setStoryPlaying(false); setStoryStep(index); }}><i /><span>{index + 1}</span></button>)}
            </div>
            <div className="architecture-flow-actions">
              <button type="button" aria-label="Previous flow step" disabled={boundedStoryStep === 0} onClick={() => moveFlowStep(-1)}><ArrowLeft size={14} /></button>
              <button className="primary" type="button" onClick={toggleFlowPlayback}>{storyPlaying ? <Pause size={14} /> : <Play size={14} />}{storyPlaying ? "Pause" : boundedStoryStep >= activeFlowSteps.length - 1 ? "Replay" : "Play"}</button>
              <button type="button" aria-label="Next flow step" disabled={boundedStoryStep >= activeFlowSteps.length - 1} onClick={() => moveFlowStep(1)}><ArrowRight size={14} /></button>
              <button className="open-module" type="button" onClick={() => navigateFromAtlas(experienceMode === "story" ? activeStory.section : "change-proposal-inbox")}><ExternalLink size={14} />{experienceMode === "story" ? activeStory.destination : "Open change inbox"}</button>
            </div>
          </div>
        </section>
      )}

      {graphLoadError && <div className="architecture-load-error" role="alert"><AlertTriangle size={15} />The local architecture dataset could not be loaded. Rebuild the frontend artifact before presenting this view.</div>}

      <div className="architecture-toolbar">
        <div className="architecture-mode" aria-label="Architecture graph mode">
          <button className={mode === "systems" ? "active" : ""} type="button" aria-pressed={mode === "systems"} onClick={() => { setMode("systems"); setZoom(1); }}><Boxes size={14} />System map</button>
          <button className={mode === "symbols" ? "active" : ""} type="button" aria-pressed={mode === "symbols"} onClick={() => { changeExperienceMode("explore"); setMode("symbols"); setZoom(1); }}><Code2 size={14} />Symbol graph</button>
        </div>
        <label htmlFor="architecture-graph-search"><Search size={14} /><input id="architecture-graph-search" value={query} onChange={(event) => { setQuery(event.target.value); if (event.target.value) { setExperienceMode("explore"); setStoryPlaying(false); setMode("symbols"); } }} placeholder="Find a class, function or source file" /></label>
        {mode === "symbols" && (
          <label className="architecture-density" htmlFor="architecture-density">Density<select id="architecture-density" value={density} onChange={(event) => setDensity(Number(event.target.value))}><option value="48">Focused</option><option value="84">Balanced</option><option value="132">Extended</option></select></label>
        )}
        {mode === "systems" && (
          <button className={`architecture-focus-toggle ${focusEnabled ? "active" : ""}`} type="button" aria-pressed={focusEnabled} onClick={() => setFocusEnabled((value) => !value)}><Focus size={14} />{focusEnabled ? "Spotlight on" : "Focus selected"}</button>
        )}
        <div className="architecture-zoom" aria-label="Architecture graph zoom controls">
          <button type="button" aria-label="Zoom out" disabled={zoom <= 0.8} onClick={() => setZoom((value) => Math.max(0.8, Number((value - 0.2).toFixed(1))))}><Minus size={14} /></button>
          <span>{Math.round(zoom * 100)}%</span>
          <button type="button" aria-label="Zoom in" disabled={zoom >= 1.6} onClick={() => setZoom((value) => Math.min(1.6, Number((value + 0.2).toFixed(1))))}><Plus size={14} /></button>
          <button type="button" aria-label="Reset graph view" onClick={resetView}><RotateCcw size={14} /></button>
        </div>
      </div>

      {mode === "symbols" && (
        <div className="architecture-layer-filter" aria-label="Filter symbols by architecture layer">
          <button className={activeLayer === "all" ? "active" : ""} type="button" onClick={() => setActiveLayer("all")}>All layers<span>{architectureGraph.meta.nodes}</span></button>
          {ARCHITECTURE_LAYERS.map((layer) => <button className={activeLayer === layer.id ? "active" : ""} type="button" key={layer.id} onClick={() => { setActiveLayer(layer.id); setQuery(""); }}><i style={{ background: layer.color }} />{layer.short}<span>{architectureGraph.meta.layerCounts[layer.id] ?? 0}</span></button>)}
        </div>
      )}

      <div className="architecture-workspace">
        <div className={`architecture-canvas-wrap ${focusLayerDefinition ? "focus-active" : ""}`}>
          <div className="architecture-canvas-heading"><div><span>{mode === "systems" ? "System topology" : activeLayer === "all" ? "Cross-layer symbol topology" : ARCHITECTURE_LAYER_BY_ID.get(activeLayer)?.label}</span>{mode === "systems" && experienceMode === "explore" && !focusEnabled && <small><Orbit size={11} />Drag the map to rotate</small>}{focusLayerDefinition && <small><Focus size={11} />Spotlight: {focusLayerDefinition.label}</small>}</div><code>{mode === "systems" ? `${summary.edges.length} strongest cross-layer paths` : `${symbolLayout.nodes.length} visible symbols · ${symbolLayout.edges.length} visible relations`}</code></div>
          <div
            className={`architecture-tilt-stage ${dragging ? "dragging" : ""} ${focusLayerDefinition ? "focus-active" : ""} experience-${experienceMode}`}
            style={{ "--tilt-x": `${displayTilt.x}deg`, "--tilt-y": `${displayTilt.y}deg` }}
            onPointerDown={handleTiltPointerDown}
            onPointerMove={handleTiltPointerMove}
            onPointerUp={handleTiltPointerUp}
            onPointerCancel={handleTiltPointerUp}
          >
            <svg className="architecture-graph-canvas" viewBox="0 0 1120 585" role="img" aria-labelledby="architecture-graph-title architecture-graph-description">
            <title id="architecture-graph-title">Regulated AI Agent Platform implementation graph</title>
            <desc id="architecture-graph-description">A fully local architecture visualization derived from Graphify AST relationships across the operator UI, API control plane, agent runtime, knowledge, trust, data, verification and delivery layers.</desc>
            <defs>
              <marker id="architecture-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" /></marker>
              <filter id="architecture-selected-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="5" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
            </defs>
            <g transform={graphTransform}>
              {mode === "systems" && (
                <>
                  {summary.edges.map((edge) => {
                    const source = ARCHITECTURE_LAYER_BY_ID.get(edge.source);
                    const target = ARCHITECTURE_LAYER_BY_ID.get(edge.target);
                    if (!source || !target) return null;
                    const selected = selectedLayer?.id === edge.source || selectedLayer?.id === edge.target;
                    return (
                      <g className={`architecture-system-edge ${selected ? "selected" : ""}`} key={`${edge.source}-${edge.target}`}>
                        <line x1={source.x + 160} y1={source.y + 34} x2={target.x} y2={target.y + 34} markerEnd="url(#architecture-arrow)" />
                        {edge.count >= 7 && <text x={(source.x + target.x + 160) / 2} y={(source.y + target.y) / 2 + 27}>{edge.count}</text>}
                      </g>
                    );
                  })}
                  {activeFlowPairs.map(([sourceId, targetId], index) => {
                    const source = ARCHITECTURE_LAYER_BY_ID.get(sourceId);
                    const target = ARCHITECTURE_LAYER_BY_ID.get(targetId);
                    if (!source || !target) return null;
                    const startX = source.x + 80;
                    const startY = source.y + 34;
                    const endX = target.x + 80;
                    const endY = target.y + 34;
                    const path = `M ${startX} ${startY} Q ${(startX + endX) / 2} ${(startY + endY) / 2 - 42} ${endX} ${endY}`;
                    return (
                      <g className={`architecture-active-flow ${experienceMode}`} key={`${sourceId}-${targetId}-${index}`}>
                        <path d={path} markerEnd="url(#architecture-arrow)" />
                        {!prefersReducedMotion && <circle r="4"><animateMotion dur="1.35s" repeatCount="indefinite" path={path} /></circle>}
                      </g>
                    );
                  })}
                  {summary.layers.map((layer, index) => {
                    const flowRelevant = experienceMode === "explore" || revealedFlowLayers.has(layer.id);
                    const flowFocused = focusedFlowLayer === layer.id;
                    const focusCurrent = focusLayerId === layer.id;
                    const focusSupporting = Boolean(focusLayerDefinition && !focusCurrent && focusNeighbourLayerIds.has(layer.id));
                    const focusMuted = Boolean(focusLayerDefinition && !focusCurrent && !focusSupporting);
                    const impact = experienceMode === "impact" && revealedFlowLayers.has(layer.id) ? ARCHITECTURE_IMPACT.layers[layer.id] : null;
                    return (
                      <g key={layer.id} transform={`translate(${layer.x} ${layer.y})`}>
                        <g className={`architecture-system-node ${selectedLayer?.id === layer.id ? "selected" : ""} ${flowFocused ? "flow-focused" : ""} ${!flowRelevant ? "flow-dimmed" : ""} ${focusCurrent ? "focus-current" : ""} ${focusSupporting ? "focus-supporting" : ""} ${focusMuted ? "focus-muted" : ""} ${impact ? `impact-${impact.state}` : ""}`} role="button" tabIndex="0" aria-current={focusCurrent ? "step" : undefined} aria-label={`${layer.label}: ${layer.nodes.length} symbols${impact ? `, ${impact.label}` : ""}`} style={{ "--node-order": index }} onClick={() => handleSystemNodeClick(layer)} onDoubleClick={() => drillIntoLayer(layer)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); inspectLayer(layer); } }}>
                          <rect width="160" height="68" rx="10" />
                          <rect className="architecture-system-accent" width="4" height="68" rx="2" fill={layer.color} />
                          <circle cx="21" cy="21" r="6" fill={layer.color} />
                          <text className="system-label" x="34" y="24">{layer.label}</text>
                          <text className="system-count" x="18" y="47">{layer.nodes.length} symbols</text>
                          <text className="system-hub" x="18" y="59">hub: {shortArchitectureLabel(layer.topNode?.label ?? "none", 21)}</text>
                          {impact && <text className={`architecture-impact-label ${impact.state}`} x="148" y="14" textAnchor="end">{impact.state}</text>}
                        </g>
                      </g>
                    );
                  })}
                </>
              )}

              {mode === "symbols" && (
                <>
                  {symbolLayout.edges.map((edge, index) => {
                    const from = symbolLayout.positions[edge.s];
                    const to = symbolLayout.positions[edge.t];
                    if (!from || !to) return null;
                    const connected = selectedNode && (edge.s === selectedNode.id || edge.t === selectedNode.id);
                    return <line className={`architecture-symbol-edge ${edge.c} ${connected ? "connected" : ""}`} key={`${edge.s}-${edge.t}-${edge.r}-${index}`} x1={from.x} y1={from.y} x2={to.x} y2={to.y} markerEnd={connected ? "url(#architecture-arrow)" : undefined}><title>{edge.r} · {edge.c}</title></line>;
                  })}
                  {symbolLayout.nodes.map((node) => {
                    const layer = ARCHITECTURE_LAYER_BY_ID.get(node.layer) ?? ARCHITECTURE_LAYER_BY_ID.get("external");
                    const selected = selectedNode?.id === node.id;
                    const adjacent = selectedNeighbourIds.has(node.id);
                    const showLabel = selected || node.match || node.degree >= 22 || (activeLayer !== "all" && node.degree >= 8);
                    return (
                      <g className={`architecture-symbol-node ${selected ? "selected" : ""} ${node.match ? "match" : ""} ${selectedNode && !selected && !adjacent ? "context" : ""}`} key={node.id} role="button" tabIndex="0" aria-label={`${node.label}, ${node.degree} relationships`} transform={`translate(${node.position.x} ${node.position.y})`} onClick={() => setSelectedId(node.id)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedId(node.id); } }}>
                        <rect className="architecture-symbol-hit" x="-16" y="-17" width={showLabel ? 150 : 34} height="34" rx="8" />
                        <circle r={Math.max(6, Math.min(14, 5 + Math.sqrt(node.degree)))} fill={layer.color} filter={selected ? "url(#architecture-selected-glow)" : undefined} />
                        {showLabel && <text x="17" y="4">{shortArchitectureLabel(node.label, 24)}</text>}
                        <title>{node.label} · {node.source}:{node.location} · {node.degree} relationships</title>
                      </g>
                    );
                  })}
                </>
              )}
            </g>
            </svg>
          </div>
          <div className="architecture-legend">
            {ARCHITECTURE_LAYERS.filter((layer) => mode === "systems" || activeLayer === "all" || layer.id === activeLayer).map((layer) => <span key={layer.id}><i style={{ background: layer.color }} />{layer.short}</span>)}
            <span className="architecture-confidence"><i />Inferred</span>
          </div>
        </div>

        <aside className={`architecture-inspector ${focusLayerDefinition ? "focus-active" : ""}`}>
          {mode === "systems" ? (
            <>
              {focusLayerDefinition && (
                <section className={`architecture-focus-card ${experienceMode} ${selectedImpact?.state ?? ""}`} aria-live="polite">
                  <div className="architecture-focus-card-kicker"><span><Focus size={13} />Current focus</span><small>{experienceMode === "explore" ? "Interactive inspection" : `Step ${boundedStoryStep + 1} of ${activeFlowSteps.length}`}</small></div>
                  <div className="architecture-focus-card-title"><i style={{ background: focusLayerDefinition.color }} /><div><h4>{focusLayerDefinition.label}</h4><strong>{focusHeadline}</strong></div></div>
                  <p>{focusDetail}</p>
                  <div className="architecture-focus-evidence"><ShieldCheck size={15} /><div><span>Evidence produced</span><strong>{focusLayerDetails?.evidence}</strong></div></div>
                  <button type="button" onClick={returnToOverview}><Minimize2 size={14} />Back to full map</button>
                </section>
              )}
              <div className="architecture-inspector-heading"><i style={{ background: selectedLayer?.color }} /><div><span>Architecture layer</span><h4>{selectedLayer?.label}</h4></div></div>
              {experienceMode === "impact" && (
                <div className={`architecture-impact-inspector ${selectedImpact?.state ?? "unchanged"}`}>
                  <span>{selectedImpact?.state ?? "unchanged"}</span>
                  <strong>{selectedImpact?.label ?? "No modeled regression"}</strong>
                  <p>{selectedImpact?.detail ?? "This layer remains outside the modeled approval-bypass blast radius."}</p>
                </div>
              )}
              <div className="architecture-portfolio-summary">
                <span>Business purpose</span>
                <strong>{selectedLayerDetails.purpose}</strong>
                <p>{selectedLayerDetails.operation}</p>
              </div>
              <dl>
                <div><dt>Symbols</dt><dd>{selectedLayer?.nodes.length}</dd></div>
                <div><dt>Internal relations</dt><dd>{selectedLayer?.internalEdges}</dd></div>
                <div><dt>Highest-connectivity hub</dt><dd><code>{selectedLayer?.topNode?.label}</code> · {selectedLayer?.topNode?.degree} relations</dd></div>
                <div><dt>Primary source</dt><dd>{selectedLayer?.topNode?.source}</dd></div>
                <div><dt>Evidence produced</dt><dd>{selectedLayerDetails.evidence}</dd></div>
              </dl>
              <div className="architecture-control-tags"><span>Control boundary</span><div>{selectedLayerDetails.controls.map((control) => <small key={control}><ShieldCheck size={11} />{control}</small>)}</div></div>
              <div className="architecture-hubs"><span>Key symbols</span>{selectedLayer?.nodes.slice(0, 5).map((node) => <button type="button" key={node.id} onClick={() => { setMode("symbols"); setActiveLayer(selectedLayer.id); setSelectedId(node.id); }}>{node.label}<small>{node.degree}</small></button>)}</div>
              <div className="architecture-inspector-actions">
                {experienceMode === "impact" ? (
                  <>
                    <button className="primary" type="button" onClick={() => navigateFromAtlas("release-assurance")}><ShieldCheck size={14} />Open release gate</button>
                    <button type="button" onClick={() => navigateFromAtlas("change-proposal-inbox")}><ExternalLink size={14} />Open change inbox</button>
                  </>
                ) : (
                  <>
                    <button className="primary" type="button" onClick={() => startStory(selectedLayerDetails.story)}><Play size={14} />See how it works</button>
                    <button type="button" onClick={() => navigateFromAtlas(selectedLayerDetails.section)}><ExternalLink size={14} />Open {selectedLayerDetails.destination}</button>
                  </>
                )}
                <button type="button" onClick={() => drillIntoLayer(selectedLayer)}><Focus size={14} />Inspect code evidence</button>
              </div>
            </>
          ) : selectedNode ? (
            <>
              <div className="architecture-inspector-heading"><i style={{ background: ARCHITECTURE_LAYER_BY_ID.get(selectedNode.layer)?.color }} /><div><span>{ARCHITECTURE_LAYER_BY_ID.get(selectedNode.layer)?.label}</span><h4>{selectedNode.label}</h4></div></div>
              <dl>
                <div><dt>Source evidence</dt><dd><code>{selectedNode.source}</code>{selectedNode.location ? ` · ${selectedNode.location}` : ""}</dd></div>
                <div><dt>Connectivity</dt><dd>{selectedNode.degree} total · {selectedNode.inbound} inbound · {selectedNode.outbound} outbound</dd></div>
                <div><dt>Graph community</dt><dd>Community {selectedNode.community}</dd></div>
              </dl>
              <div className="architecture-connections"><span>Strongest adjacent evidence</span>{selectedConnections.map((edge, index) => { const neighbourId = edge.s === selectedNode.id ? edge.t : edge.s; const neighbour = symbolLayout.nodeById.get(neighbourId); return <button type="button" key={`${edge.s}-${edge.t}-${edge.r}-${index}`} onClick={() => setSelectedId(neighbourId)}><span>{edge.r.replaceAll("_", " ")}<i className={edge.c}>{edge.c}</i></span><strong>{neighbour?.label ?? neighbourId}</strong></button>; })}</div>
            </>
          ) : <div className="graph-empty"><Network size={22} /><p>No symbols match the current graph scope.</p></div>}
        </aside>
      </div>

      <div className="architecture-boundary"><ShieldCheck size={15} /><p><strong>Evidence boundary</strong><span>Graphify output is sanitized at build time and rendered through React escaping. No raw HTML, remote scripts, live repository access or semantic provider is used.</span></p><code>{architectureGraph.meta.digest.slice(0, 16)}</code></div>
      <details className="graph-adjacency architecture-adjacency">
        <summary><Link2 size={14} />Accessible architecture evidence</summary>
        <div className="knowledge-table-wrap"><table className="knowledge-table"><thead><tr><th>Source</th><th>Relation</th><th>Target</th><th>Evidence</th></tr></thead><tbody>{architectureGraph.edges.slice(0, 80).map((edge, index) => <tr key={`${edge.s}-${edge.t}-${edge.r}-${index}`}><td>{symbolLayout.nodeById.get(edge.s)?.label ?? edge.s}</td><td>{edge.r.replaceAll("_", " ")}</td><td>{symbolLayout.nodeById.get(edge.t)?.label ?? edge.t}</td><td>{edge.c}</td></tr>)}</tbody></table></div>
      </details>
    </div>
  );
}

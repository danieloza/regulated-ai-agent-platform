import React, { useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  FileDiff,
  FileText,
  FolderSync,
  GitBranch,
  Link2,
  Network,
  RefreshCw,
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

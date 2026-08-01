import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const argumentsByName = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  const name = process.argv[index];
  const value = process.argv[index + 1];
  if (!name?.startsWith("--") || !value) {
    throw new Error("Usage: node scripts/build_architecture_graph.mjs --input graph.json --output architecture-graph.json --commit <sha>");
  }
  argumentsByName.set(name.slice(2), value);
}

const inputPath = argumentsByName.get("input");
const outputPath = argumentsByName.get("output");
const baseCommit = argumentsByName.get("commit");

if (!inputPath || !outputPath || !/^[a-f0-9]{7,40}$/i.test(baseCommit ?? "")) {
  throw new Error("A Graphify input, output path, and valid Git commit are required.");
}

function cleanText(value, maximumLength) {
  return String(value ?? "")
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maximumLength);
}

function cleanSource(value) {
  const normalized = cleanText(value, 500).replaceAll("\\", "/");
  const relativeMatch = normalized.match(/(?:^|\/)(backend|frontend|scripts)\/.+$/);
  if (relativeMatch) return relativeMatch[0].replace(/^\//, "");
  if (!normalized || /^[a-z]:\//i.test(normalized) || normalized.startsWith("/") || normalized.includes("../")) {
    return "external dependency";
  }
  return normalized;
}

function classifyLayer(source) {
  if (source === "external dependency") return "external";
  if (source.startsWith("frontend/")) return "operator-ui";
  if (source.includes("/tests/") || source.includes("/evals/")) return "verification";
  if (source === "backend/app/main.py") return "control-plane";
  if (source.endsWith("/services/workflow.py")) return "agent-runtime";
  if (/services\/(knowledge|obsidian_connector|governance_registry)\.py$/.test(source)) return "knowledge";
  if (/services\/(trust_plane|evidence|enterprise_api)\.py$/.test(source)) return "trust-assurance";
  if (source.startsWith("backend/migrations/") || source.endsWith("/services/infra.py")) return "platform-data";
  if (source.startsWith("scripts/") || /(?:package|pyproject|vite\.config)/.test(source)) return "delivery-tooling";
  return "platform-data";
}

const rawGraph = JSON.parse(await readFile(resolve(inputPath), "utf8"));
if (!Array.isArray(rawGraph.nodes) || !Array.isArray(rawGraph.links)) {
  throw new Error("Input must be a Graphify node-link graph.");
}

const nodeIds = new Set(rawGraph.nodes.map((node) => cleanText(node.id, 240)).filter(Boolean));
const degree = new Map([...nodeIds].map((id) => [id, { inbound: 0, outbound: 0 }]));
const edges = [];

for (const edge of rawGraph.links) {
  const source = cleanText(edge.source, 240);
  const target = cleanText(edge.target, 240);
  if (!nodeIds.has(source) || !nodeIds.has(target)) continue;
  degree.get(source).outbound += 1;
  degree.get(target).inbound += 1;
  edges.push({
    s: source,
    t: target,
    r: cleanText(edge.relation, 48) || "relates_to",
    c: edge.confidence === "INFERRED" ? "inferred" : "extracted",
  });
}

const nodes = rawGraph.nodes.map((node) => {
  const id = cleanText(node.id, 240);
  const source = cleanSource(node.source_file);
  const counts = degree.get(id) ?? { inbound: 0, outbound: 0 };
  return {
    id,
    label: cleanText(node.label, 120) || id,
    source,
    location: cleanText(node.source_location, 32),
    community: Number.isInteger(node.community) ? node.community : -1,
    layer: classifyLayer(source),
    degree: counts.inbound + counts.outbound,
    inbound: counts.inbound,
    outbound: counts.outbound,
  };
});

const layerCounts = nodes.reduce((counts, node) => {
  counts[node.layer] = (counts[node.layer] ?? 0) + 1;
  return counts;
}, {});
const relationCounts = edges.reduce((counts, edge) => {
  counts[edge.r] = (counts[edge.r] ?? 0) + 1;
  return counts;
}, {});
const inferredEdges = edges.filter((edge) => edge.c === "inferred").length;
const canonical = JSON.stringify({ nodes, edges });

const output = {
  meta: {
    analyzer: "graphifyy 0.9.31",
    sourceState: "tracked working tree",
    baseCommit: baseCommit.toLowerCase(),
    digest: createHash("sha256").update(canonical).digest("hex"),
    nodes: nodes.length,
    edges: edges.length,
    communities: new Set(nodes.map((node) => node.community)).size,
    extractedEdges: edges.length - inferredEdges,
    inferredEdges,
    layerCounts,
    relationCounts,
  },
  nodes,
  edges,
};

const resolvedOutput = resolve(outputPath);
await mkdir(dirname(resolvedOutput), { recursive: true });
await writeFile(resolvedOutput, `${JSON.stringify(output)}\n`, "utf8");
console.log(`Wrote ${resolvedOutput}: ${nodes.length} nodes, ${edges.length} edges, digest ${output.meta.digest.slice(0, 16)}`);

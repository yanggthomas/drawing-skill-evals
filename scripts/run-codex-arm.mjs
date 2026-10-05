#!/usr/bin/env node

// Run one case × arm of the Codex three-arm evaluation in an isolated `codex exec` session.
// Usage: node scripts/run-codex-arm.mjs --case <name> --arm with|without|imagegen [--run <run-id>] [--model <m>] [--effort <e>]
//        [--prepare-only | --audit-only]
// Writes out/ artifacts and per-arm evidence (audit.json, trace.jsonl, ...) for runs/<run-id>/.

import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  chmodSync,
  closeSync,
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  openSync,
  readFileSync,
  readdirSync,
  renameSync,
  statSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_MODEL = "gpt-5.6-sol";
const DEFAULT_EFFORT = "high";
const PROXY_HOST = "127.0.0.1";
const PROXY_PORT = 7890;
const PROXY_URL = `http://${PROXY_HOST}:${PROXY_PORT}`;
// USD per million tokens; models without an entry get estimated_cost_usd = null.
const PRICES = {
  "gpt-5.6-sol": { input: 4, cached: 0.4, cacheWrite: 5, output: 20 },
};
// GPT Image 2.x API: $30 per 1M image output tokens (all variants). The built-in tool hides its
// quality tier, so image cost is reported for each tier. Token formula: OpenAI community calculator,
// which reproduces the official 1024x1024 prices ($0.006 / $0.053 / $0.211).
const IMAGE_OUTPUT_USD_PER_MILLION = 30;
const IMAGE_QUALITY_FACTORS = { low: 16, medium: 48, high: 96 };
const TIMEOUT_MS = 30 * 60 * 1000;
const ARMS = ["with", "without", "imagegen"];
const IMAGEGEN_REQUIREMENT = "Produce the diagram with image generation.";
const USAGE_LIMIT = /usage limit/i;

function fail(message) {
  console.error(message);
  process.exit(2);
}

function parseArgs(argv) {
  const result = { prepareOnly: false, auditOnly: false, model: DEFAULT_MODEL, effort: DEFAULT_EFFORT };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--prepare-only" || arg === "--audit-only") {
      result[arg === "--prepare-only" ? "prepareOnly" : "auditOnly"] = true;
      continue;
    }
    if (!["--case", "--arm", "--run", "--model", "--effort"].includes(arg)) {
      fail(`unknown argument: ${arg}`);
    }
    const value = argv[index + 1];
    if (!value) fail(`missing value for ${arg}`);
    result[arg.slice(2)] = value;
    index += 1;
  }
  if (!result.case || !result.arm || !result.run) {
    fail(
      "usage: run-codex-arm.mjs --case NAME --arm with|without|imagegen --run RUN_ID " +
        "[--model M] [--effort E] [--prepare-only | --audit-only]",
    );
  }
  if (!ARMS.includes(result.arm)) fail(`unsupported arm: ${result.arm}`);
  return result;
}

function promptBody(markdown) {
  if (!markdown.startsWith("---\n")) return markdown.trim();
  const end = markdown.indexOf("\n---\n", 4);
  if (end < 0) fail("prompt frontmatter is not terminated");
  return markdown.slice(end + 5).trim();
}

function outputPng(prompt) {
  const match = prompt.match(/`out\/([^`]+\.png)`/);
  if (!match) fail("prompt does not declare an out/*.png artifact");
  return match[1];
}

function parseJsonl(text) {
  const events = [];
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    try {
      const value = JSON.parse(line);
      if (value && typeof value === "object" && !Array.isArray(value)) events.push(value);
    } catch {
      // stderr is retained separately; malformed stdout lines remain in trace.jsonl.
    }
  }
  return events;
}

function completedItems(events) {
  return events.filter((event) => event.type === "item.completed" && event.item).map((event) => event.item);
}

function commandStrings(events) {
  return events
    .filter((event) => ["item.started", "item.completed"].includes(event.type))
    .map((event) => event.item)
    .filter((item) => item?.type === "command_execution" && typeof item.command === "string")
    .map((item) => item.command);
}

function lastUsage(events) {
  const completed = events.filter((event) => event.type === "turn.completed" && event.usage);
  return completed.length ? completed.at(-1).usage : null;
}

function estimatedCost(model, usage) {
  const price = PRICES[model];
  if (!usage || !price) return null;
  const input = usage.input_tokens ?? 0;
  const cached = usage.cached_input_tokens ?? 0;
  const cacheWrite = usage.cache_write_input_tokens ?? 0;
  const output = usage.output_tokens ?? 0;
  const uncached = Math.max(input - cached - cacheWrite, 0);
  return (
    uncached * price.input + cached * price.cached + cacheWrite * price.cacheWrite + output * price.output
  ) / 1_000_000;
}

function imageOutputTokens(factor, width, height) {
  const longEdge = Math.max(width, height);
  const shortEdge = Math.min(width, height);
  const shortFactor = Math.floor((2 * factor * shortEdge + longEdge) / (2 * longEdge));
  return Math.ceil((factor * shortFactor * (2_000_000 + width * height)) / 4_000_000);
}

function imageCost(images) {
  if (!images.length) return null;
  const cost = {};
  for (const [quality, factor] of Object.entries(IMAGE_QUALITY_FACTORS)) {
    const tokens = images.reduce((sum, image) => sum + imageOutputTokens(factor, image.width, image.height), 0);
    cost[quality] = Number(((tokens * IMAGE_OUTPUT_USD_PER_MILLION) / 1_000_000).toFixed(4));
  }
  return cost;
}

function pngDimensions(file) {
  if (!existsSync(file)) return null;
  const data = readFileSync(file);
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (data.length < 24 || !data.subarray(0, 8).equals(signature)) return null;
  return {
    width: data.readUInt32BE(16),
    height: data.readUInt32BE(20),
    bytes: data.length,
    sha256: createHash("sha256").update(data).digest("hex"),
  };
}

function filesBelow(directory, prefix = "") {
  if (!existsSync(directory)) return [];
  const files = [];
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const relative = path.join(prefix, entry.name);
    if (entry.isDirectory()) {
      files.push(...filesBelow(path.join(directory, entry.name), relative));
    } else if (entry.isFile()) {
      files.push(relative);
    }
  }
  return files;
}

function makeReadOnly(directory) {
  for (const relative of filesBelow(directory)) chmodSync(path.join(directory, relative), 0o444);
  chmodSync(directory, 0o555);
  for (const entry of readdirSync(directory, { recursive: true })) {
    const full = path.join(directory, entry);
    if (statSync(full).isDirectory()) chmodSync(full, 0o555);
  }
}

function archiveExisting(target) {
  const names = ["trace.jsonl", "stderr.log", "last-message.md", "audit.json", "out", "generated_images"];
  const present = names.filter((name) => existsSync(path.join(target, name)));
  if (!present.length) return null;
  const stamp = new Date().toISOString().replaceAll(":", "-");
  const archive = path.join(target, "attempts", stamp);
  mkdirSync(archive, { recursive: true });
  for (const name of present) renameSync(path.join(target, name), path.join(archive, name));
  return archive;
}

function proxyListening() {
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: PROXY_HOST, port: PROXY_PORT });
    socket.setTimeout(2000);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.once("error", () => resolve(false));
  });
}

function visibleSkills(promptInputJson) {
  const text = JSON.parse(promptInputJson)
    .flatMap((item) => item.content ?? [])
    .map((content) => content.text ?? "")
    .join("\n");
  return [...new Set([...text.matchAll(/^- ([a-z0-9-]+): /gm)].map((match) => match[1]))].sort();
}

const args = parseArgs(process.argv.slice(2));
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const catalog = JSON.parse(readFileSync(path.join(root, "evals", "catalog.yaml"), "utf8"));
const catalogCase = catalog.cases.find((entry) => entry.name === args.case);
if (!catalogCase) fail(`case is not present in catalog: ${args.case}`);
const caseDir = path.join(root, "evals", args.case);
const promptFile = path.join(caseDir, "prompt.md");
const sourceDir = path.join(caseDir, "src");
const authFile = path.join(os.homedir(), ".codex", "auth.json");
const skillSources = {
  with: {
    graphviz: path.join(root, "skills", "graphviz"),
    "model-architecture": path.join(root, "skills", "model-architecture"),
  },
  without: {},
  imagegen: { imagegen: path.join(os.homedir(), ".codex", "skills", ".system", "imagegen") },
}[args.arm];
const target = path.join(root, "runs", args.run, "cases", args.case, "arms", args.arm);

for (const required of [promptFile, sourceDir, authFile]) {
  if (!existsSync(required)) fail(`required input does not exist: ${required}`);
}
for (const [name, source] of Object.entries(skillSources)) {
  if (!existsSync(path.join(source, "SKILL.md"))) fail(`required skill ${name} does not exist: ${source}`);
}

const casePrompt = promptBody(readFileSync(promptFile, "utf8"));
const prompt = args.arm === "imagegen" ? `${casePrompt}\n\n${IMAGEGEN_REQUIREMENT}` : casePrompt;
const pngName = outputPng(casePrompt);
// Bundled skills, plugins, and apps are off in every arm; only the imagegen arm keeps the image tool.
const isolationArgs = [
  "--config",
  "skills.bundled.enabled=false",
  "--disable",
  "plugins",
  "--disable",
  "apps",
  ...(args.arm === "imagegen" ? [] : ["--disable", "image_generation"]),
];
const plan = {
  case_id: catalogCase.id,
  case: args.case,
  arm: args.arm,
  model: args.model,
  reasoning_effort: args.effort,
  attempts: 1,
  prompt_file: promptFile,
  prompt_sha256: createHash("sha256").update(prompt).digest("hex"),
  prompt_suffix: args.arm === "imagegen" ? IMAGEGEN_REQUIREMENT : null,
  source: sourceDir,
  output_png: `out/${pngName}`,
  catalog_expected_skill: catalogCase.expected_skill,
  expected_skills_visible: Object.keys(skillSources).sort(),
  image_generation_tool: args.arm === "imagegen",
  isolation_args: isolationArgs,
  proxy: PROXY_URL,
  isolated_home: true,
  target,
};
if (args.prepareOnly) {
  console.log(JSON.stringify(plan, null, 2));
  process.exit(0);
}

let run;
if (args.auditOnly) {
  const previous = JSON.parse(readFileSync(path.join(target, "audit.json"), "utf8"));
  run = previous.run;
  if (!run) fail("audit.json has no run record; rerun the arm instead");
} else {
  if (!(await proxyListening())) fail(`proxy is not listening at ${PROXY_URL}`);

  mkdirSync(target, { recursive: true });
  const archivedAttempt = archiveExisting(target);
  const tempRoot = mkdtempSync(path.join(os.tmpdir(), `drawing-eval-${args.case}-${args.arm}-`));
  const workspace = path.join(tempRoot, "workspace");
  const codexHome = path.join(tempRoot, "codex-home");
  mkdirSync(path.join(workspace, "out"), { recursive: true });
  mkdirSync(path.join(codexHome, "skills"), { recursive: true });
  // Copy, not symlink: a symlink's real path would lead the agent back to the repo's answer keys.
  cpSync(sourceDir, path.join(workspace, "src"), { recursive: true, dereference: true });
  makeReadOnly(path.join(workspace, "src"));
  copyFileSync(promptFile, path.join(workspace, "prompt.md"));
  symlinkSync(authFile, path.join(codexHome, "auth.json"), "file");
  for (const [name, source] of Object.entries(skillSources)) {
    cpSync(source, path.join(codexHome, "skills", name), { recursive: true });
  }

  const env = {
    ...process.env,
    HOME: tempRoot,
    CODEX_HOME: codexHome,
    http_proxy: PROXY_URL,
    https_proxy: PROXY_URL,
    HTTP_PROXY: PROXY_URL,
    HTTPS_PROXY: PROXY_URL,
  };

  // Gate: render the model-visible prompt without a model call and check the skill list.
  const promptInput = spawnSync(
    "codex",
    ["debug", "prompt-input", "--config", `model="${args.model}"`, ...isolationArgs, prompt],
    { cwd: workspace, env, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
  );
  if (promptInput.status !== 0) fail(`prompt-input failed: ${promptInput.stderr}`);
  writeFileSync(path.join(target, "prompt-input.json"), promptInput.stdout);
  const skillsSeen = visibleSkills(promptInput.stdout);
  if (JSON.stringify(skillsSeen) !== JSON.stringify(plan.expected_skills_visible)) {
    fail(`isolation gate failed: visible skills ${JSON.stringify(skillsSeen)}`);
  }
  if (promptInput.stdout.includes(root)) fail("isolation gate failed: prompt input references the repository");

  const tracePath = path.join(target, "trace.jsonl");
  const stderrPath = path.join(target, "stderr.log");
  const lastMessagePath = path.join(target, "last-message.md");
  const traceFd = openSync(tracePath, "w");
  const stderrFd = openSync(stderrPath, "w");
  const codexArgs = [
    "exec",
    "--json",
    "--ephemeral",
    "--ignore-user-config",
    "--ignore-rules",
    "--skip-git-repo-check",
    "--model",
    args.model,
    "--strict-config",
    "--config",
    `model_reasoning_effort="${args.effort}"`,
    "--config",
    'approval_policy="never"',
    ...isolationArgs,
    "--sandbox",
    "workspace-write",
    "--cd",
    workspace,
    "--output-last-message",
    lastMessagePath,
    prompt,
  ];
  const startedAt = new Date();
  const startedNs = process.hrtime.bigint();
  const child = spawnSync("codex", codexArgs, {
    cwd: workspace,
    env,
    stdio: ["ignore", traceFd, stderrFd],
    timeout: TIMEOUT_MS,
  });
  const elapsedSeconds = Number(process.hrtime.bigint() - startedNs) / 1e9;
  closeSync(traceFd);
  closeSync(stderrFd);

  const generatedOut = path.join(workspace, "out");
  if (existsSync(generatedOut) && readdirSync(generatedOut).length) {
    cpSync(generatedOut, path.join(target, "out"), { recursive: true });
  }
  // Archive the image-tool record: the temp root does not survive a reboot or session restart.
  const tempGenerated = path.join(codexHome, "generated_images");
  mkdirSync(path.join(target, "generated_images"), { recursive: true });
  if (existsSync(tempGenerated)) cpSync(tempGenerated, path.join(target, "generated_images"), { recursive: true });

  run = {
    cli_version: spawnSync("codex", ["--version"], { encoding: "utf8" }).stdout.trim(),
    started_at: startedAt.toISOString(),
    ended_at: new Date().toISOString(),
    elapsed_seconds: Number(elapsedSeconds.toFixed(3)),
    exit_code: child.status,
    signal: child.signal,
    process_error: child.error?.message ?? null,
    timed_out: child.error?.code === "ETIMEDOUT",
    archived_attempt: archivedAttempt,
    temp_root: tempRoot,
    skills_visible: skillsSeen,
    launcher: {
      command: "codex",
      args: codexArgs.map((value) => (value === prompt ? `<PROMPT sha256=${plan.prompt_sha256}>` : value)),
    },
  };
}

const traceText = readFileSync(path.join(target, "trace.jsonl"), "utf8");
const events = parseJsonl(traceText);
const items = completedItems(events);
const commands = commandStrings(events);
const skillReads = [...new Set(commands.filter((command) => /(?:^|\/)SKILL\.md\b/.test(command)))];
const graphvizRead = skillReads.some((command) => /skills\/graphviz\/SKILL\.md/.test(command));
const modelArchitectureRead = skillReads.some((command) =>
  /skills\/model-architecture\/SKILL\.md/.test(command),
);
const imagegenRead = skillReads.some((command) => /skills\/imagegen\/SKILL\.md/.test(command));
const graphvizRenderCommand = commands.some((command) => /\bdot\b[^\n]*-T[^\s]*png/.test(command));
const modelCompileCommand = commands.some((command) =>
  /(?:^|[\s/])render\.sh\b|\blatexmk\b[^\n]*-xelatex|\bxelatex\b|\bpdflatex\b/.test(command),
);
const modelRenderCommand = commands.some((command) =>
  /(?:^|[\s/])render\.sh\b|\bpdftoppm\b[^\n]*-png|\bmagick\b[^\n]*(?:\.pdf|\.png)|\bconvert\b[^\n]*(?:\.pdf|\.png)/.test(command),
);
const codeRenderCommands = commands.filter((command) =>
  /\bdot\b[^\n]*-T|\bxelatex\b|\bpdflatex\b|\blatexmk\b|matplotlib|\bPIL\b|ImageDraw|cairo/i.test(command),
);
// `codex exec --json` emits no item for the built-in image tool; each call instead writes one file
// under the arm's private CODEX_HOME, so those files are the call record.
const generatedDir = path.join(target, "generated_images");
if (!existsSync(generatedDir)) fail(`image-tool record missing, cannot audit: ${generatedDir}`);
const generatedImages = filesBelow(generatedDir).map((relative) => ({
  path: relative,
  ...pngDimensions(path.join(generatedDir, relative)),
}));
const subagentItems = items.filter((item) => /collab|agent_spawn|spawn_agent/i.test(item.type ?? ""));
const usageLimited = events.some(
  (event) => ["error", "turn.failed"].includes(event.type) && USAGE_LIMIT.test(JSON.stringify(event)),
);
const repoReferences = commands.filter((command) => command.includes(root));

const targetOut = path.join(target, "out");
const outputFiles = filesBelow(targetOut);
const dotFiles = outputFiles.filter((name) => name.endsWith(".dot"));
const texFiles = outputFiles.filter((name) => name.endsWith(".tex"));
const pdfFiles = outputFiles.filter((name) => name.endsWith(".pdf"));
const pngPath = path.join(targetOut, pngName);
const dimensions = pngDimensions(pngPath);
const pngFromImageTool = Boolean(dimensions) && generatedImages.some((image) => image.sha256 === dimensions.sha256);

const graphvizWorkflowVerified = dotFiles.length > 0 && graphvizRenderCommand;
const modelArchitectureWorkflowVerified =
  texFiles.length > 0 && pdfFiles.length > 0 && modelCompileCommand && modelRenderCommand;
const routeChecks = {
  with:
    (graphvizRead && graphvizWorkflowVerified) || (modelArchitectureRead && modelArchitectureWorkflowVerified),
  without: skillReads.length === 0 && generatedImages.length === 0,
  // A byte-identical match to an image-tool output proves the PNG was not code-rendered;
  // code_render_commands stays informational because agents also use PIL to inspect the result.
  imagegen: pngFromImageTool && !graphvizRead && !modelArchitectureRead,
};
const routeVerified = routeChecks[args.arm];
const usage = lastUsage(events);
const processSucceeded = run.exit_code === 0 && !run.process_error;
const isolationClean = repoReferences.length === 0 && subagentItems.length === 0;
let status = "invalid";
if (usageLimited) status = "usage_limited";
else if (processSucceeded && dimensions && routeVerified && isolationClean) status = "complete";

const audit = {
  ...plan,
  status,
  run,
  usage,
  estimated_cost_usd: estimatedCost(args.model, usage),
  image_output_cost_usd: imageCost(generatedImages),
  skill_reads: skillReads,
  graphviz_read: graphvizRead,
  model_architecture_read: modelArchitectureRead,
  imagegen_read: imagegenRead,
  graphviz_workflow_verified: graphvizWorkflowVerified,
  model_architecture_workflow_verified: modelArchitectureWorkflowVerified,
  image_generation_calls: generatedImages.length,
  generated_images: generatedImages,
  png_from_image_tool: pngFromImageTool,
  code_render_commands: codeRenderCommands,
  subagents_spawned: subagentItems.length,
  repo_references: repoReferences,
  route_verified: routeVerified,
  editable_dot_files: dotFiles,
  editable_tex_files: texFiles,
  compiled_pdf_files: pdfFiles,
  output_files: outputFiles,
  png: dimensions ? { path: pngPath, ...dimensions } : null,
};
writeFileSync(path.join(target, "audit.json"), `${JSON.stringify(audit, null, 2)}\n`);
console.log(JSON.stringify({ case: args.case, arm: args.arm, status, route_verified: routeVerified }, null, 2));
process.exit(status === "complete" ? 0 : 1);

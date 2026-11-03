#!/usr/bin/env node
// Paridade entre este repositório e as skills de um projeto.
//
//   node sync.mjs start  <projeto>            instala tudo e grava o lock
//   node sync.mjs status <projeto>            compara repo x projeto
//   node sync.mjs pull   <projeto>            traz do repo o que o projeto não mudou
//   node sync.mjs push   <projeto> [skill...] leva ao repo o que o projeto melhorou
//
// O lock (<projeto>/.claude/setup-skills.lock.json) guarda o hash de cada skill
// na última sincronização. É ele que diz quem mudou: o repo, o projeto ou os dois.

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const REPO = path.dirname(fileURLToPath(import.meta.url));
const REPO_SKILLS = path.join(REPO, "skills");
const REPO_CLAUDE_MD = path.join(REPO, "CLAUDE.md");

function listFiles(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...listFiles(full));
    else out.push(full);
  }
  return out;
}

// Hash do conteúdo de uma pasta, ignorando CRLF/LF para o Windows não gerar falso "mudou".
function hashDir(dir) {
  if (!fs.existsSync(dir)) return null;
  const h = createHash("sha256");
  for (const file of listFiles(dir).sort()) {
    h.update(path.relative(dir, file).split(path.sep).join("/"));
    h.update(fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n"));
  }
  return h.digest("hex").slice(0, 16);
}

function copyDir(from, to) {
  fs.rmSync(to, { recursive: true, force: true });
  fs.cpSync(from, to, { recursive: true });
}

function repoCommit() {
  try {
    return execFileSync("git", ["-C", REPO, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }).trim();
  } catch {
    return "desconhecido";
  }
}

function lockPath(project) {
  return path.join(project, ".claude", "setup-skills.lock.json");
}

function readLock(project) {
  try {
    return JSON.parse(fs.readFileSync(lockPath(project), "utf8"));
  } catch {
    return { skills: {} };
  }
}

function writeLock(project, lock) {
  lock.repo = "https://github.com/Graail/setup-skills";
  lock.commit = repoCommit();
  lock.atualizado = new Date().toISOString();
  fs.mkdirSync(path.dirname(lockPath(project)), { recursive: true });
  fs.writeFileSync(lockPath(project), JSON.stringify(lock, null, 2) + "\n");
}

// Estado de cada skill: igual, falta, repo-mudou, projeto-mudou ou conflito.
function compare(project) {
  const lock = readLock(project);
  const repoNames = fs.readdirSync(REPO_SKILLS).filter((n) => fs.statSync(path.join(REPO_SKILLS, n)).isDirectory());
  const localDir = path.join(project, ".claude", "skills");
  const localNames = fs.existsSync(localDir) ? fs.readdirSync(localDir) : [];
  const names = [...new Set([...repoNames, ...localNames.filter((n) => n in lock.skills)])].sort();

  return names.map((name) => {
    const repo = hashDir(path.join(REPO_SKILLS, name));
    const local = hashDir(path.join(localDir, name));
    const base = lock.skills[name] ?? null;
    let estado;
    if (!local) estado = "falta";
    else if (!repo) estado = "so-no-projeto";
    else if (repo === local) estado = "igual";
    else if (local === base) estado = "repo-mudou";
    else if (repo === base) estado = "projeto-mudou";
    else estado = "conflito";
    return { name, repo, local, estado };
  });
}

const LEGENDA = {
  igual: "igual nos dois",
  falta: "não instalada no projeto (pull instala)",
  "repo-mudou": "o repo tem versão nova (pull atualiza)",
  "projeto-mudou": "o projeto melhorou a skill (push leva ao repo)",
  conflito: "mudou nos dois lados: comparar à mão",
  "so-no-projeto": "existe só no projeto (push leva ao repo)",
};

function status(project) {
  const rows = compare(project);
  for (const r of rows) console.log(`${r.name.padEnd(24)} ${LEGENDA[r.estado]}`);
  return rows;
}

function pull(project) {
  const lock = readLock(project);
  for (const r of compare(project)) {
    const dest = path.join(project, ".claude", "skills", r.name);
    if (r.estado === "falta" || r.estado === "repo-mudou") {
      copyDir(path.join(REPO_SKILLS, r.name), dest);
      lock.skills[r.name] = r.repo;
      console.log(`${r.name}: ${r.estado === "falta" ? "instalada" : "atualizada"}`);
    } else if (r.estado === "igual") {
      lock.skills[r.name] = r.repo;
    } else {
      console.log(`${r.name}: mantida (${LEGENDA[r.estado]})`);
    }
  }
  if (fs.existsSync(REPO_CLAUDE_MD)) {
    const dest = path.join(project, ".claude", "setup-skills.CLAUDE.md");
    fs.copyFileSync(REPO_CLAUDE_MD, dest);
  }
  writeLock(project, lock);
}

function push(project, only) {
  const lock = readLock(project);
  const sent = [];
  for (const r of compare(project)) {
    if (only.length && !only.includes(r.name)) continue;
    if (r.estado !== "projeto-mudou" && r.estado !== "so-no-projeto") {
      if (only.includes(r.name)) console.log(`${r.name}: não enviada (${LEGENDA[r.estado]})`);
      continue;
    }
    copyDir(path.join(project, ".claude", "skills", r.name), path.join(REPO_SKILLS, r.name));
    lock.skills[r.name] = r.local;
    sent.push(r.name);
    console.log(`${r.name}: copiada para o repo`);
  }
  writeLock(project, lock);
  if (sent.length) {
    console.log("\nPróximo passo: registrar em EVOLUCAO.md o que mudou e por quê, e commitar no setup-skills.");
  }
}

const [cmd, projectArg, ...rest] = process.argv.slice(2);
if (!cmd || !projectArg || !["start", "status", "pull", "push"].includes(cmd)) {
  console.log("Uso: node sync.mjs <start|status|pull|push> <pasta-do-projeto> [skill...]");
  process.exit(1);
}
const project = path.resolve(projectArg);
if (cmd === "status") status(project);
if (cmd === "start" || cmd === "pull") pull(project);
if (cmd === "push") push(project, rest);

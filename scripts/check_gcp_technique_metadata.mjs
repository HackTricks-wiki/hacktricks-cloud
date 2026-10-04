#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const roots = {
  privesc: "src/pentesting-cloud/gcp-security/gcp-privilege-escalation",
  "post-exploitation": "src/pentesting-cloud/gcp-security/gcp-post-exploitation",
  persistence: "src/pentesting-cloud/gcp-security/gcp-persistence",
};

function markdownFiles(root) {
  const result = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const name = path.join(root, entry.name);
    if (entry.isDirectory()) result.push(...markdownFiles(name));
    else if (entry.isFile() && entry.name.endsWith(".md")) result.push(name);
  }
  return result.sort();
}

const listMissing = process.argv.includes("--list");
let failed = false;

for (const [label, root] of Object.entries(roots)) {
  let qualifying = 0;
  let rated = 0;
  const missing = [];

  for (const file of markdownFiles(root)) {
    // Persistence techniques can stand alone at H2 when no category wrapper is
    // needed, or appear at H3 inside a category containing multiple techniques.
    const sectionStart = label === "persistence" ? /(?=^#{2,3} )/m : /(?=^### )/m;
    const sections = fs.readFileSync(file, "utf8").split(sectionStart).slice(1);
    for (const section of sections) {
      const hasImpact = /\*\*Potential Impact:\*\*/i.test(section);
      const hasLogs = /<summary>Logs generated<\/summary>/i.test(section);
      if (!hasImpact || !hasLogs) continue;

      qualifying += 1;
      if (/\*\*Stealth:\*\*/i.test(section)) {
        rated += 1;
      } else {
        const heading = section.match(/^#{2,3} (.+)$/m)?.[1] ?? "<unknown heading>";
        missing.push(`${file}: ${heading}`);
      }
    }
  }

  const unrated = qualifying - rated;
  console.log(`${label}: ${rated}/${qualifying} rated; ${unrated} unrated`);
  if (listMissing && missing.length) {
    for (const item of missing) console.log(`  ${item}`);
  }
  if (label === "persistence" && unrated !== 0) failed = true;
}

process.exitCode = failed ? 1 : 0;

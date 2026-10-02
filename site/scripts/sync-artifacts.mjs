import { copyFile, cp, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const siteRoot = resolve(here, "..");
const source = resolve(siteRoot, "..", "artifacts", "site-data.json");
const destination = resolve(siteRoot, "src", "generated", "site-data.json");
const figuresSource = resolve(siteRoot, "..", "artifacts", "figures");
const figuresDestination = resolve(siteRoot, "public", "figures");

await mkdir(dirname(destination), { recursive: true });
try {
  await copyFile(source, destination);
} catch (error) {
  if (error && error.code === "ENOENT") {
    throw new Error(`Verified site data is missing at ${source}. Run paperkit build first.`);
  }
  throw error;
}

await cp(figuresSource, figuresDestination, { recursive: true, force: true });

console.log(`Synced verified site data to ${destination}`);

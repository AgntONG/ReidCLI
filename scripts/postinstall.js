"use strict";

const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { findPython } = require("./find-python");

const PACKAGE_ROOT = path.join(__dirname, "..");

function pipInstall(python) {
  const args = [...python.args, "-m", "pip", "install", "--user", "--quiet", PACKAGE_ROOT];
  const result = spawnSync(python.cmd, args, { stdio: "inherit" });
  return !result.error && result.status === 0;
}

function main() {
  const python = findPython();
  if (!python) {
    console.warn(
      "reid: no Python 3.11+ interpreter found on PATH — skipping automatic setup.\n" +
        "Install Python, then run: pip install --user " + JSON.stringify(PACKAGE_ROOT)
    );
    return;
  }

  console.log("reid: installing Python package (reidcli) via pip...");
  if (!pipInstall(python)) {
    console.warn(
      "reid: automatic `pip install` failed.\n" +
        "Run it manually: " +
        `${python.cmd} ${python.args.join(" ")} -m pip install --user ${JSON.stringify(PACKAGE_ROOT)}`
    );
  }
}

main();

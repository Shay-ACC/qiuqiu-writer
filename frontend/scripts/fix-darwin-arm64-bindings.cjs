/**
 * fix-darwin-arm64-bindings.js
 *
 * 修复 macOS arm64 (Apple Silicon) 上原生依赖丢失导致 Vite/Rollup/Tailwind 构建失败的问题。
 *
 * 背景：
 * 仓库提交的 frontend/package-lock.json 是在 Linux x64 上生成的，lockfile 只解析了
 * linux-x64-gnu 的平台二进制（@rollup/rollup-linux-x64-gnu、lightningcss-linux-x64-gnu、
 * @tailwindcss/oxide-linux-x64-gnu）。在 macOS arm64 上执行 `npm ci` 时，npm 不会安装
 * darwin-arm64 的原生 binding，导致后续 `npm run build` 报：
 *   Error: Cannot find module '@rollup/rollup-darwin-arm64'
 *   Cannot find module 'lightningcss-darwin-arm64'
 *   Cannot find module '@tailwindcss/oxide-darwin-arm64'
 * （npm 可选平台依赖 bug: https://github.com/npm/cli/issues/4828）
 *
 * 该脚本在 npm install / npm ci 之后自动补齐 darwin-arm64 原生 binding，
 * 把原来需要手动执行的 getting-started.md 中的 workaround 自动化。
 *
 * 幂等：若对应 binding 已存在则跳过。
 * 仅在 darwin + arm64 上生效，其它平台（Linux/CI）不做任何操作。
 */

const fs = require("node:fs");
const path = require("node:path");

// 仅在 macOS arm64 处理；其它平台直接退出，避免影响 Linux CI / Windows。
if (process.platform !== "darwin" || process.arch !== "arm64") {
  process.exit(0);
}

const projectRoot = path.resolve(__dirname, "..");
const nodeModules = path.join(projectRoot, "node_modules");

if (!fs.existsSync(nodeModules)) {
  // 依赖尚未安装，无法补齐，交给后续 npm install 流程。
  process.exit(0);
}

// 需要 darwin-arm64 原生 binding 的包：[子目录] => [对应的 arm64 包名]
const targets = [
  { dir: "rollup", pkg: "@rollup/rollup-darwin-arm64", versionFile: "rollup/package.json" },
  { dir: "lightningcss", pkg: "lightningcss-darwin-arm64", versionFile: "lightningcss/package.json" },
  { dir: "@tailwindcss/oxide", pkg: "@tailwindcss/oxide-darwin-arm64", versionFile: "@tailwindcss/oxide/package.json" },
];

const versionOf = (rel) => {
  const file = path.join(nodeModules, rel);
  try {
    return require(file).version; // eslint-disable-line import/no-dynamic-require
  } catch {
    return null;
  }
};

const isInstalled = (pkg) => {
  // arm64 binding 已在 node_modules 根下存在则视为已安装
  return fs.existsSync(path.join(nodeModules, pkg));
};

let installedAny = false;
for (const t of targets) {
  const version = versionOf(t.versionFile);
  if (!version) {
    // 主包未安装，跳过
    continue;
  }
  if (isInstalled(t.pkg)) {
    continue;
  }
  const spec = `${t.pkg}@${version}`;
  console.log(`[fix-darwin-arm64] 安装缺失的原生 binding: ${spec}`);
  // 使用 spawnSync 同步执行，继承 stdio
  const { spawnSync } = require("node:child_process");
  const result = spawnSync(
    "npm",
    ["install", "--no-save", "--no-package-lock", spec, "--registry=https://registry.npmjs.org/"],
    { cwd: projectRoot, stdio: "inherit" }
  );
  if (result.status !== 0) {
    console.warn(`[fix-darwin-arm64] 警告: 安装 ${spec} 失败 (exit ${result.status})。`);
    console.warn("    可手动执行 getting-started.md 中的 macOS arm64 修复命令。");
  } else {
    installedAny = true;
  }
}

if (installedAny) {
  console.log("[fix-darwin-arm64] 原生 binding 补齐完成。");
}

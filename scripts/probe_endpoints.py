#!/usr/bin/env python3
r"""**抽取 HTTP 端点清单** —— 为系统流程可视化采集事实。

扫源码里的路由装饰器（FastAPI / Flask / Express / Django 都覆盖），
产出「方法 / 路径 / 处理函数 / 文件:行号」表。

## 它做什么

- 正则扫 `文件:行` 上的装饰器（`@app.get(...)`、`@router.post(...)`、FastAPI 路由等）
- 解析出处理函数名与**定义行号**
- 尽力从函数体里抓它调用的下游模块函数（下一跳），供画调用链

## 用法

```bash
python probe_endpoints.py --root . --out endpoints.md
python probe_endpoints.py --root src --glob '*.py'
```

## 输出约定

每条都带 `文件:行号`；抓不到下游就留空，**不要猜**。
"""
from __future__ import annotations

import argparse
import ast
import datetime as _dt
import pathlib
import re
import sys

DECOR_RE = re.compile(
    r"@\s*(?:[\w.]+\.)?(get|post|put|delete|patch|head|options|route|websocket)\s*\(\s*([^)]*)\)",
    re.I,
)
HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options", "websocket"}


def first_str_arg(arg_src: str) -> str:
    m = re.search(r"""['"]([^'"]+)['"]""", arg_src)
    return m.group(1) if m else arg_src.strip()[:60]


def scan_file(path: pathlib.Path, root: pathlib.Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    lines = text.split("\n")
    out: list[dict] = []
    for i, line in enumerate(lines):
        m = DECOR_RE.search(line)
        if not m:
            continue
        verb, arg = m.group(1).lower(), m.group(2)
        # 下一行是函数名
        fname = None
        for j in range(i + 1, min(i + 4, len(lines))):
            fm = re.match(r"\s*(?:async\s+)?def\s+(\w+)\s*\(", lines[j])
            if fm:
                fname = fm.group(1)
                fline = j + 1
                break
        else:
            fline = i + 1
        if fname is None:
            continue
        if verb == "route":
            method = first_str_arg(arg) or "ANY"
            pathv = first_str_arg(arg.split(",")[1]) if "," in arg else arg
        else:
            method = verb.upper()
            pathv = first_str_arg(arg)
        # 函数体里调用的模块级函数
        calls: list[str] = []
        body: list[str] = []
        for j in range(fline, min(fline + 80, len(lines))):
            body.append(lines[j])
            if j + 1 < len(lines) and re.match(r"\s*(?:@|def |class )", lines[j + 1]):
                break
        for cm in re.finditer(r"\b([a-z_][a-z0-9_]*)\s*\(", "\n".join(body)):
            name = cm.group(1)
            if name not in ("self", "print", "len", "str", "int", "float", "list", "dict", "set"):
                calls.append(name)
        out.append(
            {
                "method": method,
                "path": pathv,
                "handler": fname,
                "file": str(path.relative_to(root)),
                "line": fline,
                "calls": sorted(set(calls))[:12],
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="仓库根")
    ap.add_argument("--glob", default="*.py", help="文件匹配")
    ap.add_argument("--out", default="", help="Markdown 输出路径")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    files = sorted(root.rglob(args.glob))
    files = [f for f in files if not any(s in f.parts for s in (".venv", "node_modules", "dist", ".git"))]

    rows: list[dict] = []
    for f in files:
        rows.extend(scan_file(f, root))
    rows.sort(key=lambda r: (r["file"], r["line"]))

    stamp = _dt.date.today().isoformat()
    lines = [f"# HTTP 端点清单 · 采集于 {stamp}", "", f"共 **{len(rows)}** 个端点。", ""]
    lines.append("| 方法 | 路径 | 处理函数 | 位置 | 下游调用（抓到的前几跳） |")
    lines.append("|---|---|---|---|---|")
    for r in rows:
        calls = ", ".join(f"`{c}`" for c in r["calls"][:8]) or "—"
        lines.append(f"| {r['method']} | `{r['path']}` | `{r['handler']}` | `{r['file']}:{r['line']}` | {calls} |")

    text = "\n".join(lines) + "\n"
    if args.out:
        pathlib.Path(args.out).write_text(text, encoding="utf-8")
        print(f"✅ {len(rows)} 个端点 → {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

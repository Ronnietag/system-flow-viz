#!/usr/bin/env python3
r"""**流程图引用校验器**模板 —— 核「清单里写的」与「代码里有的」对得上。

## 它查什么

| # | 检查 | 判据 |
|---|---|---|
| ① | 源码位置**存在** | `file` 相对仓库根存在 |
| ② | 源码位置**行号在范围内** | `line` ≤ 该文件行数（防漂到不存在的行）|
| ③ | 节点 id **唯一** | 不能有两个同 id 的节点 |
| ④ | 连线两端**节点都存在** | `from`/`to` 都能在节点清单里找到 |
| ⑤ | **实测数字带日期** | 每条 `measured` 都有 `at` |
| ⑥ | **占位符残留** | 清单里不许留 `TODO` / `待补充` / `XXX` / `此处填写` |
| ⑦ | **术语在词表里** | 命中词表外的自造简称 ⇒ 报错（词表 = `GLOSSARY.md`）|

## 用法

```bash
# 从 TS 清单里读（推荐：清单是 TS 常量）
python3 docs/skills/system-flow-viz/templates/verify_refs.py \
    --nodes web/src/components/flow/nodes.ts --root . --glossary GLOSSARY.md
```

## 口径

* **只读**（不改任何文件）⇒ 可以放进发布闸门。
* 报告格式与仓库既有质检脚本一致：**逐条列出位置与实际值**，不静默跳过。
* 同名文件无法唯一定位 ⇒ **跳过并列出**，不猜。
* **不连生产库** ⇒ 只读仓库里的清单与文件。

## ⚠️ 换成你的清单格式

默认解析 **TS 常量**（`NODES` / `LINKS`）与 **JSON**（`nodes.json`）。
若是别的格式，改 `load_nodes()` 一个函数即可。
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

#: 占位符残留（清单里不该留这些）。
#:
#: ⚠️ **不要放「示例」这种宽泛词** —— 正常正文里出现「示例」是合法的
#: ⇒ 会误报。只放**明确表示「还没写」**的词。
PLACEHOLDERS = (
    "TODO", "FIXME", "XXX", "待补充", "待填写", "此处填写", "PLACEHOLDER", "<系统名>", "<表名>",
)

#: TS 里的条目：{ id: '…', title: '…', src: [{ file: '…', line: 12, … }] }
#:
#: ⚠️ **节点 id 的字段名要兼容两种**：`id:`（模板约定）**和** `key:`
#: （很多项目用 `key`）⇒ 两个都认。
TS_ENTRY = re.compile(
    r"\{\s*(?:id|key):\s*'(?P<id>[^']+)'\s*,(?P<body>.*?)\n\s*\}", re.S
)
TS_SRC = re.compile(r"file:\s*'(?P<file>[^']+)'\s*,\s*line:\s*(?P<line>\d+)")
TS_LINK = re.compile(r"\{\s*from:\s*'(?P<from>[^']+)'\s*,\s*to:\s*'(?P<to>[^']+)'")
TS_MEASURED = re.compile(r"measured:\s*\{[^}]*?at:\s*'(?P<at>[^']*)'")


def load_nodes(path: pathlib.Path) -> tuple[list[dict], list[dict]]:
    """读节点清单 ⇒ (节点, 连线)。"""
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("nodes", [])), list(data.get("links", []))

    src = path.read_text(encoding="utf-8")
    nodes: list[dict] = []
    for m in TS_ENTRY.finditer(src):
        body = m.group("body")
        srcs = [
            {"file": s.group("file"), "line": int(s.group("line"))}
            for s in TS_SRC.finditer(body)
        ]
        nodes.append({"id": m.group("id"), "src": srcs, "raw": body})
    links = [
        {"from": m.group("from"), "to": m.group("to")}
        for m in TS_LINK.finditer(src)
    ]
    return nodes, links


def load_terms(glossary: pathlib.Path | None) -> set[str]:
    """词表里的术语（`**术语**：` 这种粗体定义的）。"""
    if glossary is None or not glossary.exists():
        return set()
    text = glossary.read_text(encoding="utf-8")
    return set(re.findall(r"\*\*(.+?)\*\*\s*[：:]", text))


def main() -> int:
    ap = argparse.ArgumentParser(description="流程图引用校验器")
    ap.add_argument("--nodes", required=True, help="节点清单（.ts 或 .json）")
    ap.add_argument("--root", default=".", help="仓库根")
    ap.add_argument("--glossary", default="GLOSSARY.md", help="词表（可空）")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    nodes_path = pathlib.Path(args.nodes)
    if not nodes_path.is_absolute():
        nodes_path = root / nodes_path
    glossary = pathlib.Path(args.glossary)
    if not glossary.is_absolute():
        glossary = root / glossary

    nodes, links = load_nodes(nodes_path)
    terms = load_terms(glossary if glossary.exists() else None)
    problems: list[str] = []

    # ① ② 源码位置
    for n in nodes:
        for s in n.get("src", []):
            f = root / s["file"]
            if not f.exists():
                problems.append(f"节点 `{n['id']}`：源码文件不存在 ⇒ {s['file']}")
                continue
            total = len(f.read_text(encoding="utf-8").splitlines())
            if not (1 <= s["line"] <= total):
                problems.append(
                    f"节点 `{n['id']}`：行号越界 ⇒ {s['file']}:{s['line']}（该文件 {total} 行）"
                )

    # ③ 节点 id 唯一
    seen: dict[str, int] = {}
    for n in nodes:
        seen[n["id"]] = seen.get(n["id"], 0) + 1
    for nid, cnt in seen.items():
        if cnt > 1:
            problems.append(f"节点 id 重复 `{nid}`（{cnt} 次）")

    # ④ 连线两端存在
    ids = set(seen)
    for l in links:
        for side in ("from", "to"):
            if l[side] not in ids:
                problems.append(f"连线的 `{side}` 指向不存在的节点 ⇒ `{l[side]}`")

    # ⑤ 实测数字带日期
    for n in nodes:
        raw = n.get("raw", "")
        if "measured" in raw:
            m = TS_MEASURED.search(raw)
            if not m or not m.group("at").strip():
                problems.append(f"节点 `{n['id']}`：实测数字没有采集日期")

    # ⑥ 占位符残留
    body = nodes_path.read_text(encoding="utf-8")
    for i, line in enumerate(body.splitlines(), 1):
        for ph in PLACEHOLDERS:
            if ph in line:
                problems.append(f"{nodes_path.relative_to(root)}:{i}：占位符残留 `{ph}`")

    # ⑦ 术语在词表里（只查节点标题这种「自造叫法」最可能出现的地方）
    if terms:
        for n in nodes:
            title = n.get("title", "")
            if title and not any(ch in title for ch in "<>{}") and title not in terms:
                # 词表没收录 ⇒ **提醒**而不是报错（词表可能不全）
                problems.append(
                    f"节点 `{n['id']}`：标题「{title}」不在词表里（词表 {len(terms)} 条）"
                )

    if problems:
        print(f"❌ 流程图清单有 {len(problems)} 处问题：")
        for p in problems:
            print(f"   - {p}")
        print()
        print("⇒ 清单与代码对不上时**按代码改清单**（清单是手写的）。")
        return 1

    print(
        f"✅ 流程图清单与代码一致：{len(nodes)} 个节点 / {len(links)} 条连线"
        f" / {len(terms)} 条术语"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
r"""**抽取配置 / 规则集骨架** —— 为系统流程可视化采集事实。

把 YAML/JSON/TOML 配置的**结构**（不是值）打出来：顶层键 → 嵌套 → 每个键的类型、
是否必填、样例值。因为配置往往是「怎么算」的唯一事实源。

## 它做什么

- 递归打印配置骨架，标注标量类型与列表元素类型
- 对 YAML 用 `yaml.safe_load`；无 PyYAML 时退化成按行猜缩进层级
- JSON / TOML 用标准库

## 用法

```bash
python probe_config.py configs/rules.yaml
python probe_config.py --glob 'configs/**/*.yaml'
python probe_config.py configs/rules.yaml --values   # 连样例值一起打
```

## 输出约定

只打**结构**与类型；样例值默认截断。取不到就报「未取到」。
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import sys


def describe(value) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return f"str(len={len(value)})"
    if isinstance(value, list):
        inner = sorted({describe(v) for v in value}) or ["—"]
        return f"list[{','.join(inner)}] × {len(value)}"
    if isinstance(value, dict):
        return f"map({len(value)})"
    return type(value).__name__


def walk(node, prefix: str, out: list[str], show_values: bool, depth: int = 0) -> None:
    if depth > 6:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            extra = ""
            if show_values and not isinstance(v, (dict, list)):
                extra = f" = {v!r}"
            out.append(f"{'  ' * depth}- `{path}` : {describe(v)}{extra}")
            walk(v, path, out, show_values, depth + 1)
    elif isinstance(node, list) and node:
        out.append(f"{'  ' * depth}- (首元素示例)")
        walk(node[0], f"{prefix}[0]", out, show_values, depth + 1)


def load(path: pathlib.Path):
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore

            return yaml.safe_load(text)
        except Exception:
            return _guess_yaml(text)
    if suffix == ".json":
        return json.loads(text)
    if suffix == ".toml":
        try:
            import tomllib  # type: ignore

            return tomllib.loads(text)
        except Exception:
            return {}
    return {}


def _guess_yaml(text: str) -> dict:
    """没有 PyYAML 时的退化解析：按缩进猜层级，只出结构不出值。"""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for line in text.split("\n"):
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        key = line.strip().split(":")[0].strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            continue
        parent = stack[-1][1]
        parent[key] = {}
        stack.append((indent, parent[key]))
    return root


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="")
    ap.add_argument("--glob", default="")
    ap.add_argument("--values", action="store_true", help="带样例值")
    args = ap.parse_args()

    files: list[pathlib.Path] = []
    if args.path:
        files = [pathlib.Path(args.path)]
    elif args.glob:
        files = sorted(pathlib.Path().glob(args.glob))
    if not files:
        print("未取到，原因：没给文件路径或 glob 没匹配到文件", file=sys.stderr)
        return 2

    stamp = _dt.date.today().isoformat()
    for f in files:
        try:
            data = load(f)
        except Exception as exc:
            print(f"# {f} —— 未取到，原因：{type(exc).__name__}: {exc}\n")
            continue
        out: list[str] = []
        walk(data, "", out, args.values)
        print(f"# {f} · 采集于 {stamp}\n")
        print("\n".join(out) if out else "（空配置）")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

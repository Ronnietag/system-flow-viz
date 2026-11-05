#!/usr/bin/env python3
r"""**只读探查数据库** —— 为系统流程可视化采集事实。

把「库里到底有什么」变成带日期的事实，而不是文档里的转述。

## 它做什么

对给定 DuckDB（默认 SQLite 也支持）**只读**连接，逐表输出：
表名 / 类型（表·视图·序列·索引）/ 列名与类型 / 行数 / 主键与唯一约束 / 样例值。

**绝不写库。** 连接一律 `read_only=True`；连不上就报「未取到 + 原因」，不猜。

## 用法

```bash
python probe_db.py --db ~/.local/share/app/app.duckdb
python probe_db.py --db app.db --tables orders,users            # 只看几张表
python probe_db.py --db app.duckdb --sample 3                      # 每表取 3 行样例
python probe_db.py --db app.db --json out.json                     # 顺便出机器可读结果
```

## 输出约定

- 每个数字后面标 **采集日期**（重建库后行数会变、表名不变 ⇒ 行数必须带日期）
- 报「表数」时**明确是否含视图/序列/索引**
- 取不到的项写「未取到，原因：X」
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import pathlib
import sys


def probe_duckdb(path: pathlib.Path, tables: list[str], sample: int) -> dict:
    import duckdb

    con = duckdb.connect(str(path), read_only=True)
    out: dict = {"engine": "duckdb", "path": str(path), "tables": {}}
    try:
        rows = con.execute(
            "SELECT table_name, table_type FROM information_schema.tables "
            "ORDER BY table_name"
        ).fetchall()
        for tname, ttype in rows:
            if tables and tname not in tables:
                continue
            cols = con.execute(
                "SELECT column_name, data_type FROM information_schema.columns "
                "WHERE table_name = ? ORDER BY ordinal_position",
                [tname],
            ).fetchall()
            n = con.execute(f'SELECT count(*) FROM "{tname}"').fetchone()[0]
            keys = []
            try:
                keys = con.execute(
                    "SELECT constraint_type, constraint_text FROM duckdb_constraints() "
                    "WHERE table_name = ?",
                    [tname],
                ).fetchall()
            except Exception:
                pass
            entry = {
                "type": ttype,
                "row_count": n,
                "columns": [{"name": c, "type": t} for c, t in cols],
                "keys": [{"kind": k, "text": txt} for k, txt in keys],
            }
            if sample and ttype == "BASE TABLE":
                try:
                    entry["sample"] = [
                        {c: v for c, v in zip((x[0] for x in cols), row)}
                        for row in con.execute(
                            f'SELECT * FROM "{tname}" LIMIT {int(sample)}'
                        ).fetchall()
                    ]
                except Exception as exc:  # 样例失败不影响其它表
                    entry["sample_error"] = str(exc)
            out["tables"][tname] = entry
        try:
            out["sequences"] = [
                {"name": s}
                for (s,) in con.execute(
                    "SELECT sequence_name FROM duckdb_sequences() ORDER BY sequence_name"
                ).fetchall()
            ]
        except Exception:
            pass
        try:
            out["indexes"] = [
                {"name": i, "table": t}
                for i, t in con.execute(
                    "SELECT index_name, table_name FROM duckdb_indexes() ORDER BY index_name"
                ).fetchall()
            ]
        except Exception:
            pass
    finally:
        con.close()
    return out


def probe_sqlite(path: pathlib.Path, tables: list[str], sample: int) -> dict:
    import sqlite3

    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    out: dict = {"engine": "sqlite", "path": str(path), "tables": {}}
    try:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
        ).fetchall()]
        for tname in names:
            if tables and tname not in tables:
                continue
            cols = con.execute(f'PRAGMA table_info("{tname}")').fetchall()
            n = con.execute(f'SELECT count(*) FROM "{tname}"').fetchone()[0]
            out["tables"][tname] = {
                "type": "table",
                "row_count": n,
                "columns": [{"name": c[1], "type": c[2]} for c in cols],
                "keys": [{"kind": "pk" if c[5] else "", "text": c[1]} for c in cols if c[5]],
            }
    finally:
        con.close()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True, help="库文件路径")
    ap.add_argument("--tables", default="", help="逗号分隔；留空表示全部")
    ap.add_argument("--sample", type=int, default=0, help="每表取几行样例")
    ap.add_argument("--json", default="", help="把结果写成 JSON")
    args = ap.parse_args()

    path = pathlib.Path(args.db).expanduser()
    tables = [t.strip() for t in args.tables.split(",") if t.strip()]

    if not path.exists():
        print(f"未取到，原因：文件不存在 {path}", file=sys.stderr)
        return 2

    try:
        if path.suffix == ".duckdb" or path.suffix == ".ddb":
            data = probe_duckdb(path, tables, args.sample)
        else:
            data = probe_sqlite(path, tables, args.sample)
    except Exception as exc:
        print(f"未取到，原因：{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    stamp = _dt.date.today().isoformat()
    print(f"# 库取证 · 采集于 {stamp}\n")
    print(f"引擎 {data['engine']} · 路径 `{data['path']}`")
    objs = data["tables"]
    n_table = sum(1 for v in objs.values() if v.get("type") == "BASE TABLE")
    n_view = sum(1 for v in objs.values() if v.get("type") == "VIEW")
    print(
        f"对象：**{n_table} 张表 + {n_view} 个视图**"
        + (f" + {len(data.get('sequences', []))} 个序列" if data.get("sequences") else "")
        + (f" + {len(data.get('indexes', []))} 个索引" if data.get("indexes") else "")
        + "（报「表数」时要说清是否含视图/序列/索引）\n"
    )
    for tname, t in objs.items():
        print(f"## `{tname}`（{t['type']}）· {t['row_count']} 行（实测 {stamp}）")
        for c in t["columns"]:
            print(f"  - `{c['name']}` {c['type']}")
        for k in t.get("keys", []):
            print(f"  - 键：{k['kind']} {k['text']}")
        for row in (t.get("sample") or [])[: args.sample or 0]:
            print(f"  - 样例：{row}")
        print()

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        print(f"机器可读结果已写 {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

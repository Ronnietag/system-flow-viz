# Security & Data-Flow Statement

本文件**穷尽**声明这个 skill 的每一个网络出口、凭据接触点、子进程与删除行为。

**TL;DR**：这个 skill 的全部脚本**只读**源码、配置与数据库
⇒ **零网络请求、零凭据、零写库、零删除**。

---

## 网络出口（Network destinations）

**没有。** 本 skill 的脚本**不发起任何网络请求**。

| 脚本 | 访问什么 | 走网络吗 |
|---|---|---|
| `scripts/probe_endpoints.py` | 只读源码文件（`file:line` 正则扫描）| ❌ |
| `scripts/probe_db.py` | **只读**数据库连接（本地文件）| ❌ |
| `scripts/probe_config.py` | 只读配置文件 | ❌ |
| `templates/verify_refs.py` | 只读仓库里的清单与源码文件 | ❌ |

⚠️ `probe_db.py` 连的是**本地数据库文件**（DuckDB / SQLite），
用 `read_only=True` 打开 ⇒ 进程**无法**写它（引擎层面拒绝）。

## 凭据接触点（Credential touchpoints）

**没有。** 脚本不读环境变量里的密钥、不读 `~/.aws` / `~/.config` 等凭据目录。

| 脚本 | 需要凭据吗 | 怎么处理的 |
|---|---|---|
| `probe_endpoints.py` | 否 | —— |
| `probe_db.py` | 否 | 数据库若是加密的，需要**你自己**提供解密方式；本脚本不碰凭据 |
| `probe_config.py` | 否 | —— |
| `verify_refs.py` | 否 | —— |

⚠️ `probe_config.py` 会把配置里的**结构**（键名、类型、样例值）打印出来
⇒ **样例值可能含敏感数据**（如某个配置里写了密钥）⇒
**只对可信仓库跑它**，别把输出贴到公开地方。

## 子进程（Subprocesses）

**没有。** 脚本只用 Python 标准库 + 可选依赖：

| 依赖 | 何时用 | 没装时 |
|---|---|---|
| `duckdb` | `probe_db.py` 探 DuckDB | 报「未取到 + 原因」|
| `yaml` (PyYAML) | `probe_config.py` 解析 YAML | **退化成按行猜缩进层级**（仍可用）|
| `tomllib` | `probe_config.py` 解析 TOML | Python 3.11+ 自带 |

⇒ **不调用任何外部命令**（没有 `subprocess`、没有 shell out）。

## 删除行为（Deletion）

**没有。** 脚本**只创建**输出文件（`--out` 指定的 Markdown），
**从不删除**任何东西。

⚠️ `probe_db.py` 用 `read_only=True` ⇒ 连 `DELETE` / `UPDATE` 都发不出去。

## 写入范围（What gets written）

| 脚本 | 写什么 | 写到哪 |
|---|---|---|
| `probe_endpoints.py` | 端点清单 Markdown | `--out` 指定的路径（不指定则打印到 stdout）|
| `probe_db.py` | 表结构 Markdown | 同上 |
| `probe_config.py` | 配置骨架 Markdown | 同上 |
| `verify_refs.py` | 报告（stdout）| **不写文件**（只读模式）|

⚠️ `verify_refs.py` **退出码非零即失败** ⇒ 可以直接进 CI / 发布闸门。

## 数据流（Data flow）

```
你的仓库 ──只读──> probe_*.py ──> stdout / --out 指定的 Markdown
你的数据库 ──只读──> probe_db.py
```

**没有任何数据离开你的机器。**

## 报告问题

发现安全问题请开 issue，或直接联系作者（见 `SKILL.md` 的 `metadata`）。

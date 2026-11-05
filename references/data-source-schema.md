# 节点清单契约

节点内容写成**结构化清单**（TS 常量或 JSON），**组件**从它渲染。
**清单是唯一真源**，组件是产物。

> ⚠️ **2026-11-05**：原契约是「JSON → 生成静态 HTML」⇒ 已改成
> 「清单 → React 组件」。**字段本身没变**（层/节点/连线/七块）⇒
> 从 JSON 迁到 TS 只是换个载体；下面的示例两种都通用。

⚠️ **为什么清单与组件要分开**：平台变了（改了一个表名、加了一步）
⇒ **只改清单**，组件不动。组件只负责「怎么画」，不负责「画什么」
⇒ 两件事不会互相污染。

## 顶层结构

```
{
  "meta":  { ... },   // 生成时间、事实采集日期与方式、平台版本、来源清单、取证边界
  "layers": [ ... ],  // 层定义
  "nodes": [ ... ],   // 节点
  "views": [ ... ]    // 视图（每个视图若干面板；连线写在 flow 面板的 edges 里）
}
```

## 层定义

```json
{"id": "backend", "name": "后端服务", "desc": "这一层是什么", "color": "var(--l-backend)"}
```

约定六层，顺序即流程图的分列顺序（从左到右）：

| id | 含义 |
|---|---|
| `external` | 外部文件/外部系统（平台之外的权威数据源） |
| `user` | 用户操作 |
| `frontend` | 前端界面 |
| `backend` | 后端服务与编排 |
| `storage` | 数据存储（库表、配置文件、上传目录） |
| `archive` | 归档/一次性（取证脚本、历史留痕） |

## 节点

```json
{
  "id": "pipeline.run_unit",
  "title": "一次完整计算",
  "layer": "backend",
  "summary": "卡片上显示的一句话，≤40 字",
  "what": "这一步做什么（业务语言，2–4 句）",
  "trigger": "触发方式：用户点哪个按钮 / 哪个端点被调 / 脚本哪一步",
  "src": [{"file": "src/app/pipeline.py", "line": 405, "symbol": "run_unit", "note": "编排入口"}],
  "tables": {
    "read":  [{"name": "表名", "fields": ["字段名"], "note": "可选"}],
    "write": [{"name": "表名", "keys": "主键/唯一键", "semantics": "按月整月替换", "fields": ["字段名"]}],
    "keys": ["这一环节用到的其它键"],
    "note": "可选补充"
  },
  "io": {"in": "输入是什么", "out": "输出是什么", "scale": "量级（实测数字须带日期）"},
  "fail": ["失败条件 / 边界 / 已知坑，每条一句"],
  "docs": [{"path": "docs/x.md", "section": "§N.M", "note": "可选"}],
  "conflicts": [{"topic": "一句话", "doc_says": "文档怎么说", "code_says": "代码实际是什么", "evidence": "file:line 对照"}],
  "tags": ["可选"],
  "archive": true,
  "badge": "可选角标"
}
```

### 字段规则

| 字段 | 规则 |
|---|---|
| `id` | 稳定语义串，点分小写。**不用序号、不用中文**。全局唯一 |
| `layer` | 六层之一 |
| `summary` | ≤40 字 |
| `src` | **至少一条**。`file` 用仓库相对路径，`line` 是你核对过的真实行号 |
| `tables.write[].semantics` | 八档之一，见下 |
| `conflicts` | 只在文档与代码**确实**不一致时写；`evidence` 必填；没有就空数组 |
| `archive` | 归档物填 `true`（虚线 + 降饱和 + 「归档/一次性」标签） |

### 落库语义八档

每档都对应源码里的一条真实 SQL，**按源码归类，别照抄文档**：

| 语义 | 对应的 SQL 形状 |
|---|---|
| 按月整月替换 | `DELETE … WHERE ym=?` → `INSERT` |
| 按单元全量替换 | `DELETE … WHERE unit=?` → `INSERT` |
| 按单元+表全量替换 | `DELETE … WHERE unit=? AND table_key=?` → `INSERT` |
| 整表替换 | `DELETE FROM tbl`（整表）→ `INSERT` |
| 只增不改 | `ON CONFLICT DO NOTHING`，或序列 id 纯插入 |
| 按主键 upsert | `ON CONFLICT (keys) DO UPDATE` / `INSERT OR REPLACE` |
| 按名写入 | 文件系统按文件名写入 |
| 整文件替换 | 配置文件整份覆写 |

> ⚠ 常见的坑：把「标准表的字段数」当成「宽表的列数」。两者差一个主键列时，
> 注释与文档会各说各的。**按代码数一遍**，并在冲突里写清三个数分别是多少。

## 连线

```json
{"from": "节点 id", "to": "节点 id", "kind": "flow|call|read|write|control", "label": "边上的字（可选）"}
```

`kind` 决定配色：flow 主色、call 后端色、read 存储色、write 外部色、control 虚线。

## 视图与面板

⚠️ **React 路线：视图是「组件」，不是「面板数组」** ⇒ 下面这份 JSON 形态
**只在使用 JSON 清单时**适用；用 TS 清单时**直接写组件**：

```tsx
// 每个视图一个组件，共享同一份 NODES
export function IngestView() {
  return <FlowCanvas nodes={NODES} links={LINKS} … />
}
```

| 旧的 panel kind | React 里怎么做 |
|---|---|
| `flow`（分层流程图）| `<FlowCanvas>` 组件（共用绘制层）|
| `table`（数据表/矩阵）| 普通表格组件（antd `Table` 等）|
| `timeline`（阶段时间轴）| 自己画，或用现成的组件 |

⚠️ **思维导图 vs 流程图**：同一份节点、两种画法 ⇒ **同一份清单**渲染两遍
（不要维护两份节点数据）⇒ 切换视图时**节点集合必须完全一致**。

<details>
<summary>（JSON 清单形态的等价写法 —— 组件读它渲染）</summary>

```json
{
  "id": "ingest",
  "name": "数据入库链路",
  "desc": "这个视图看什么",
  "panels": [
    {"id": "p1", "kind": "flow", "title": "面板标题", "desc": "可选",
     "nodes": ["节点 id"], "edges": [{"from": "…", "to": "…", "kind": "call"}]}
  ]
}
```

| kind | 用途 | 必备字段 |
|---|---|---|
| `flow` | 分层流程图（按 layer 自动分列） | `nodes`、`edges` |
| `table` | 数据表 / 矩阵 / 字典 | `columns`、`rows`（每行必须含全部列 key） |
| `timeline` | 阶段时间轴 | `phases` |

**思维导图不用单独写面板**——生成器从 `flow` 面板自动派生，同源同粒度，一键切换。

## 一节点一事

一个节点 = 一个能独立讲清的环节。不要把三件事塞一个节点；宁可多拆。

## 公共节点

多个视图共用的节点（比如「上传文件」既是入库链路的起点、也是总览的一部分），
在数据源里定义一次，各视图引用它的 id。

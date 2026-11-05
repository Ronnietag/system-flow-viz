# system-flow-viz

**把一个「黑盒」系统的全部运行链路，画成一页能点的流程图。**
**Turn a black-box system into a clickable flow diagram of every runtime path.**

> 目标读者是**要改造这个系统的人** —— 他们要能回答「改这一处会连带动到哪」。
> The reader is usually **someone about to modify the system** — they need to answer
> "if I change this, what else moves?"

一个 opencode **skill**：给 agent 用的一套做法（勘察 → 建清单 → 画组件 → 三条守门缝 → 取证 → 可发现 → 沉淀）。
An opencode **skill**: a repeatable method for agents (survey → node list → React components → three seams → evidence → discoverability → distil).

---

## 它解决什么 · What it solves

接手一个没文档的系统时，最难的不是「某个函数干什么」，而是
**「这个数从哪来」「改这里会连带动到哪」**。

Onboarding onto an undocumented system, the hard part is not "what does this function do"
but **"where did this number come from" and "what does changing this move"**.

这套流程把平台的每一条链路摊开成一张图：
每个节点都带**源码位置**（文件 + 行号）、**读表·写表**、**触发方式**、
**实测数字（带采集日期）**、以及**文档与代码冲突的标注**。

The method lays out every path as a diagram where each node carries its **source location**
(file + line), **tables read and written**, **how it is triggered**, **measured numbers
(with the date they were taken)**, and a flag whenever **the docs and the code disagree**.

图是**交互**的：悬停高亮相关连线，点开逐层钻取，鼠标停在名字上看实际英文名。
The diagram is **interactive**: hovering highlights the related edges, clicking drills down
layer by layer, and hovering a name reveals its real identifier.

---

## 快速上手 · Quick start

```bash
# ① 装到 opencode 的通用技能目录 · install into the generic skills dir
git clone https://github.com/Ronnietag/system-flow-viz.git \
    ~/.config/opencode/skills/system-flow-viz

# ② 验证探针能跑（不需要任何配置）· check the probes run (no config needed)
python3 scripts/probe_endpoints.py --root src --glob "**/*.py" --out /tmp/ep.md
```

装完在 opencode 里说「帮我把这个系统的运行链路画出来」就会触发。
English triggers work too: *"draw the system flow"*, *"make the platform a black box disappear"*,
*"which tables does this page read"*.

---

## 目录里有什么 · What's in the box

```
SKILL.md                          方法正文（7 步流程 + 6 条红线）
                                  the method (7 steps + 6 hard rules)
references/
  data-source-schema.md           节点清单契约（层 / 节点 / 连线 / 七块）
                                  node-list contract (layers / nodes / edges / the seven blocks)
  acceptance-checklist.md         验收清单（逐条打勾）
                                  acceptance checklist
  interview-questions.md          第 0 步的设计树提问清单
                                  design-tree question list for step 0
scripts/
  probe_endpoints.py              扫源码里的路由装饰器 ⇒ 端点表（带 file:line）
                                  scan route decorators ⇒ endpoint table with file:line
  probe_db.py                     只读探库（DuckDB / SQLite）⇒ 表结构 / 行数 / 主键
                                  read-only DB probe ⇒ tables / row counts / keys
  probe_config.py                 抽 YAML/JSON/TOML 配置骨架
                                  extract YAML/JSON/TOML config skeletons
templates/
  NodeList.template.tsx           节点清单的 TS 形态（组件直接 import）
                                  node list, TS flavour (the component imports it)
  nodes.template.json             节点清单的 JSON 形态
                                  node list, JSON flavour
  verify_refs.py                  引用校验器（退出码非零即失败）
                                  reference verifier (non-zero exit = failure)
```

---

## 三个探针（通用，不依赖本项目）· The three probes (project-agnostic)

| 脚本 Script | 干什么 What it does | 覆盖 Covers |
|---|---|---|
| `probe_endpoints.py` | 扫源码里的路由装饰器 ⇒ 方法 / 路径 / 处理函数 / `file:line`，并抓下游调用链<br>scan route decorators ⇒ method / path / handler / `file:line`, plus downstream calls | FastAPI · Flask · Express · Django |
| `probe_db.py` | **只读**探库 ⇒ 表名 / 类型（表·视图·序列·索引）/ 列 / 行数 / 主键 / 唯一约束 / 样例值<br>**read-only** DB probe ⇒ tables / types / columns / row counts / keys / samples | DuckDB · SQLite |
| `probe_config.py` | 抽配置的**结构**（不是值）：顶层键 → 嵌套 → 每个键的类型 / 是否必填 / 样例值<br>extract config **structure** (not values): top-level keys → nesting → types / required / samples | YAML · JSON · TOML |

⚠️ `probe_db.py` **绝不写库**（连接一律 `read_only=True`）；连不上就报
「未取到 + 原因」，不猜。
⚠️ `probe_db.py` **never writes** (connections are always `read_only=True`); if it cannot connect
it reports "not retrieved + why" instead of guessing.

---

## 六条红线 · The six hard rules

1. **每条链路必须有源码位置**（文件 + 行号），且行号是**自己核对过**的
   Every path must carry a source location (file + line) **you verified yourself**
2. **实测数字必须带采集日期**
   Measured numbers must carry the date they were taken
3. **文档与代码冲突，按代码写**，并显式标 ⚠「文档说 X / 代码是 Y / 出处」
   When docs and code disagree, **follow the code** and flag it explicitly
4. **查不到就写「未取到，原因：X」** —— 禁止推断、禁止补齐
   Not found ⇒ write "not retrieved, because: X" — no inference, no filling in
5. **不编造** —— 子代理交上来的内容也要抽查行号
   Do not invent — spot-check the line numbers even when a sub-agent vouched for them
6. **术语用项目自己的词表**（若有 `GLOSSARY.md`），不自造叫法
   Use the project's own vocabulary (e.g. `GLOSSARY.md`); never coin terms

---

## 画法硬规则 · Drawing rules

* 连线**垂直于**所碰的那条边进出；**不许**贴着节点边缘横跑
  Edges enter and leave **perpendicular** to the edge they touch; never run along a node border
* 共享边**分点**（相邻 ≥12px），不许两条线共用一个点
  Shared edges get **distinct slots** (≥12px apart) — two lines never share a point
* 连线**先画、节点后画**（节点底色遮住线头）
  Draw **edges first, nodes second** (the node fill hides the arrowhead)
* 节点内文字**按内容块垂直居中**，不是写死的偏移
  Node text is **centred on its content block**, not a hard-coded offset
* 悬停高亮**不改线型**（虚线仍是虚线：线型表达语义，高亮表达「与当前节点相关」）
  Highlighting never changes the **line style** — dashes stay dashes (style means semantics,
  highlight means "related to the current node")
* 宽度**按容器实测**（1:1 铺满），窄了才横滚
  Width follows the **measured container** (1:1, never scaled); scroll only when narrow

---

## 三条守门缝 · The three seams

| 缝 Seam | 查什么 What it checks |
|---|---|
| ① 类型与构建 types & build | `tsc --noEmit` + 构建命令 the build command |
| ② 引用校验器 reference verifier | 源码位置存在 / 行号在范围内 / 节点 id 唯一 / 连线两端存在 / 实测数字带日期 / 无占位符残留<br>source locations exist / line numbers in range / node ids unique / both edge ends exist / measured numbers dated / no placeholders left |
| ③ 真实环境取证 live evidence | 起真服务跑冒烟 + 浏览器逐页截图（**交互也要截**）<br>run the real service + smoke tests, screenshot every page (**interactions too**) |

⚠️ 校验器必须**先造几类错**验证它真能抓（红→绿），修回后退出码归零。
⚠️ The verifier must be **broken on purpose first** to prove it catches things (red→green).

---

## 路线变更记录 · Route changes

| 日期 Date | 变更 Change |
|---|---|
| 2026-10-29 | 初版：教「静态 HTML 生成器」（`templates/build.py` 产出单文件 HTML）<br>First version: taught a static-HTML generator |
| 2026-11-05 | **改成 React 组件路线** —— 静态 HTML 做不了交互（悬停高亮 / 点开钻取），而这类可视化恰恰需要交互。三个探针不受影响<br>**Switched to React components** — static HTML cannot be interactive, and interactivity is the point. The three probes are unaffected |

---

## 来源 · Origin

从真实项目里长出来的：先给一个平台画流程图，踩完坑后把做法沉淀成 skill。
所以它带着**具体教训**（SVG 的 `className` 只读、React 在 SVG 上 `onMouseLeave` 不工作、
antd tooltip 的 z-index 默认 1070 常被弹框挡住、子标签会静默截断…）。

Grown out of a real project: draw the flow of a platform, hit the pitfalls, then distil
the method into a skill. That is why it carries **hard-won lessons** (SVG `className` is
read-only, `onMouseLeave` does not work on SVG in React, antd's default tooltip z-index
(1070) often hides behind a popover, sub-labels truncate silently…).

---

## License

MIT

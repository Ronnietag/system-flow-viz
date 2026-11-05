# 推广素材 · system-flow-viz

> 用途：发 X / Reddit / HN / 博客。**直接复制粘贴**即可。
> 配图在 `demos/`（`01-high-level.png` / `02-process-flow.png`）。

---

## ① 英文版（主推 —— 目标受众在英文区）

### 长贴（推荐，配图）

> I kept asking myself: *if I change this function, what else moves?*
>
> So I built a skill that turns a black-box codebase into a **clickable flow diagram** —
> every runtime path, with the source location on each node.
>
> What it does:
> • surveys the code (endpoints / config / DB) with **read-only** probes
> • writes one node list as the single source of truth
> • renders it as a React/SVG flow chart — hover highlights edges, click drills down
> • every node carries `file:line`, tables read/written, and **measured numbers with the date they were taken**
>
> The part that matters most: it refuses to guess.
> Can't find something ⇒ it writes *"not retrieved, because: X"*.
> Docs disagree with code ⇒ it follows the **code** and flags the conflict.
>
> It works on any codebase — the skill is the method, not the diagram.
>
> `npx skills add Ronnietag/system-flow-viz`
> github.com/Ronnietag/system-flow-viz
>
> Feedback welcome — especially "what would you want the node list to carry?"

**配图**：`demos/01-high-level.png`（或 `02-process-flow.png`）

---

### 短贴（适合先试水）

> Made a skill that turns a black-box codebase into a clickable flow diagram —
> every runtime path, each node carrying its `file:line`.
>
> It doesn't guess: can't find it ⇒ writes *"not retrieved, because: X"*.
>
> `npx skills add Ronnietag/system-flow-viz`

**配图**：`demos/01-high-level.png`

---

## ② 中文版

### 长贴

> 接手一个没文档的系统，最难的不是「某个函数干什么」，
> 而是「**这个数从哪来**」「**改这里会连带动到哪**」。
>
> 所以我做了个 skill：把黑盒代码库变成**一页能点的流程图** ——
> 每条运行链路，每个节点都带源码位置。
>
> 它做的事：
> • 用**只读**探针勘察代码（端点 / 配置 / 库）
> • 把节点写成一份清单当唯一真源
> • 渲染成 React/SVG 流程图 —— 悬停高亮连线，点开逐层钻取
> • 每个节点带 `file:line`、读表·写表、**带采集日期的实测数字**
>
> 最要紧的一条：**它不猜**。
> 查不到就写「未取到，原因：X」；文档与代码冲突就按**代码**写并标出来。
>
> 跟项目无关 —— 它给的是方法，不是一张图。
>
> `npx skills add Ronnietag/system-flow-viz`
> github.com/Ronnietag/system-flow-viz

**配图**：`demos/01-high-level.png`

### 短贴

> 做了个 skill：把黑盒代码库变成一页能点的流程图，每个节点带 `file:line`。
>
> 它不猜 —— 查不到就写「未取到，原因：X」。
>
> `npx skills add Ronnietag/system-flow-viz`

---

## ③ Reddit（r/ClaudeAI 等）

> **Title:** I built a skill that turns a black-box codebase into a clickable flow diagram
>
> I kept losing time to "if I change this, what else moves?" — so I made a skill that
> answers it.
>
> It surveys your code with read-only probes (routes / config / DB), writes one node list
> as the single source of truth, and renders it as a React/SVG flow chart: hover highlights
> the related edges, click drills down layer by layer, and every node carries its
> `file:line`, the tables it reads and writes, and measured numbers **with the date they
> were taken**.
>
> The rule I care about most: it never guesses. Can't find something ⇒ it writes
> *"not retrieved, because: X"*. Docs and code disagree ⇒ it follows the code and flags it.
>
> The diagram is a starting point, not the deliverable — the reusable part is the method.
>
> `npx skills add Ronnietag/system-flow-viz` · github.com/Ronnietag/system-flow-viz
>
> I'd especially like to hear: what should the node list carry that it currently doesn't?

---

## ④ Show HN

> **Title:** Show HN: system-flow-viz — turn a black-box codebase into a clickable flow diagram
>
> Onboarding onto an undocumented system, the hard part isn't "what does this function
> do" but "where did this number come from" and "what does changing this move".
>
> system-flow-viz is an agent skill that closes that gap. It surveys the codebase with
> read-only probes (HTTP routes, config skeletons, DB schema), writes one node list as
> the single source of truth, and renders it as a React/SVG flow chart with hover
> highlighting, click-to-drill, and per-node `file:line` provenance.
>
> It has one opinionated rule: it never guesses. Anything it can't retrieve is recorded as
> "not retrieved, because: X", and where the docs disagree with the code, it follows the
> code and flags the conflict.
>
> The interesting part is that the diagram is a by-product — the reusable artefact is the
> method (survey → node list → component → three seams → evidence).
>
> `npx skills add Ronnietag/system-flow-viz`
> github.com/Ronnietag/system-flow-viz

---

## ⑤ 什么时候发效果最好（经验，非实测）

| 渠道 | 建议 |
|---|---|
| X | 工作日 **上午 8–10 点**（你所在时区）；首条用长贴 + 图，回复里补链接 |
| Reddit | **周二/三/四**，上午；先看版规要不要 flair；被删帖就别再发同款 |
| HN | Show HN **上午发**；标题不要带营销词；正文别开头就求 star |

⚠️ 同一仓库连发多个渠道时，**文案不要完全一样**（Reddit/HN 都反感）。
上面 ① / ③ / ④ 已按渠道分开了措辞。

---

## ⑥ 涨星的机制（供你判断该不该花力气）

| 渠道 | 机制 | 门槛 |
|---|---|---|
| **skills.sh** | 安装时**匿名遥测**自动收录 ⇒ 上 Trending 榜 | 被人 `npx skills add` 装过 |
| **awesome 列表** | 人工提 PR | **至少 10 stars**；且 **PR 不得由 AI 生成/提交** |
| **star-history 图** | README 里放动态曲线 | 0 star 时是平线 ⇒ **等有量再放** |

⚠️ 一句话：**这个 skill 的受众很窄**（会写/用 agent skill 的人）⇒
靠 X 涨星的天花板不高，真正的量来自 skills.sh 的安装量 + awesome 列表收录。
⇒ 建议 X 只发**一条**（建立存在感），把主力放在**让人真的装它**的渠道上。

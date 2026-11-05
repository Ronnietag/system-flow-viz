/**
 * **节点清单模板** —— 流程图组件的**唯一真源**。
 *
 * ## 为什么是清单而不是把内容写死在组件里
 *
 * 平台变了（改了一个表名、加了一步）⇒ **只改这个文件**，组件不动。
 * 组件只负责「怎么画」，不负责「画什么」⇒ 两件事不会互相污染。
 *
 * ## 字段契约
 *
 * 见 `references/data-source-schema.md`（与 `nodes.template.json` 同源，
 * 那边是 JSON 形态，这边是 TS 形态 —— 选哪种取决于你的组件怎么读数据）。
 *
 * ## 三条硬规则
 *
 * 1. **`id` 用稳定语义串**（`api.upload`、`db.write.result`），**不用序号**
 *    ⇒ 平台改动时 id 不变 ⇒ 外部引用（校验器、锚点、截图说明）不会失效。
 * 2. **`src` 里的行号是你自己核对过的** ⇒ 行号漂了要更新（用校验器守着）。
 * 3. **查不到就写「未取到，原因：X」** —— 禁止推断、禁止补齐。
 */

export type NodeKind = 'external' | 'user' | 'frontend' | 'backend' | 'storage' | 'archive'

export type SourceRef = {
  /** 仓库相对路径。 */
  file: string
  /** 1 起算的行号。 */
  line: number
  /** 处理函数 / 类 / 常量名。 */
  symbol?: string
  /** 这处源码说明了什么。 */
  note?: string
}

export type TableRef = {
  /** 库表名（或「不查库」这类说明）。 */
  name: string
  /** 读的字段。 */
  fields?: string[]
  /** 写的话，落库语义（`按月整月替换` / `按单元全量替换` / `只增不改` / `只读`…）*/
  writeMode?: string
  note?: string
}

export type FlowNode = {
  /** 稳定语义串。 */
  id: string
  /** 业务中文名（图上显示）。 */
  title: string
  /** 实际英文名（**只在悬浮提示里显示**，图上不显示）。 */
  en?: string
  kind: NodeKind
  /** 卡片上的一句话，≤40 字。 */
  summary: string
  /** 这一步做什么（业务语言，2–4 句）。 */
  what: string
  /** 触发方式。 */
  trigger: string
  /** 源码位置（可多条）。 */
  src: SourceRef[]
  /** 读表 / 写表。 */
  tables?: { read?: TableRef[]; write?: TableRef[] }
  /** 口径说明（同一个数有多个口径时必须写）。 */
  caliber?: string
  /** 实测数字（**必须带采集日期**）。 */
  measured?: { value: string | number; at: string; how: string }
  /** 归档/一次性脚本 ⇒ 视觉上与现行路径分开。 */
  archive?: boolean
  /** 节点子标签（第二行）。 */
  sub?: string
}

export type FlowLink = {
  from: string
  to: string
  /** 主线（强调色）。 */
  accent?: boolean
  /** 虚线（被动 / 回写 / 例外路径）。 */
  dashed?: boolean
}

/**
 * **实测信息** —— 采集日期与出处。
 *
 * ⚠️ **数字必须带日期**：平台在变 ⇒ 没有日期的数字会被当成永远有效的。
 */
export const META = {
  title: '<系统名> 系统流程',
  platform: '<一句话：这是干什么的>',
  /** 清单整理日期 */
  generatedAt: 'YYYY-MM-DD',
  /** 实测数字的采集日期（≠ generatedAt）*/
  measuredAt: 'YYYY-MM-DD',
  measuredNote: '生产库只读连接实测；库文件 mtime YYYY-MM-DD HH:MM',
  dbPath: '<库实体绝对路径；仓库里是否是软链接>',
  evidence: {
    liveService: '<真实服务地址；跑了哪些端点>',
    smoke: '<冒烟跑了哪些段、几项通过；没跑的是为什么>',
    notTaken: ['<没取到的项 + 原因>'],
  },
}

/** 节点清单 —— 组件 import 它。 */
export const NODES: FlowNode[] = [
  {
    id: 'example.step',
    title: '<这一步叫什么>',
    en: '<实际英文名；只在悬浮提示里显示>',
    kind: 'backend',
    summary: '<卡片上的一句话，≤40 字>',
    what: '<这一步做什么：业务语言，2–4 句>',
    trigger: '<触发方式：用户点哪个按钮 / 哪个端点被调 / 脚本哪一步>',
    src: [{ file: 'src/app/thing.py', line: 120, symbol: 'do_thing', note: '处理函数' }],
    tables: {
      read: [{ name: '<表名>', fields: ['<字段名>'] }],
      write: [{ name: '<表名>', writeMode: '按单元全量替换' }],
    },
    caliber: '<口径说明；没有就删掉这一项>',
    measured: { value: 1234, at: 'YYYY-MM-DD', how: 'SELECT count(*) FROM …' },
  },
]

/** 连线清单。 */
export const LINKS: FlowLink[] = [
  { from: 'example.step', to: 'example.other', accent: true },
]

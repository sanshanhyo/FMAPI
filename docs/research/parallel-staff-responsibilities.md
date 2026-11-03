# 并行研究：职员职责（STF-01 / STF-02 / STF-03）

> 分支：`research/parallel-staff-responsibilities`。任务 ID：STF-01、STF-02、STF-03。
> 本轮为 **offline-only**：未访问任何进程、游戏安装、UI、私有捕获、凭据、账户配置、网络或本 worktree 之外资源。未执行 bash/子进程、扫描、注入、原生函数调用、游戏/存档写入、比赛推进。未执行任何 live read。
> 本文件是审计/交接记录，不是 SDK 设计；不把已有模式 claiming 为职员能力。

## 1. 输入与固定版本

- `AGENTS.md`：边界、验证、提交约束。
- `docs/research/interface-inventory.md`：任务行与状态规则。
- `docs/research/data-discovery-todo.md`：全域待办、字段协议、验收标准。
- 上游固定提交：用户指定 `01b53c5`（用于 `data-discovery-todo.md` 基线）。
- 本地研究基线：用户指定 `99aba1d`（已有研究源码/证据）。
- 原生证据文件固定哈希（仅用于说明可复用模式，不表示本轮运行）：
  - `game_plugin.dll` SHA-256 `BC940E472418FC5C214208D7CF30FECF600F689B6F9D71C11BA19A2DF0FE057F`
  - `GameAssembly.dll` SHA-256 `820D6618ACAFAC7DFFC1EF3B489582EDDB84B0343D4F34D55FFF9FB70881E00A`
  - 元数据签名/版本 `0xFAB11BAF / 39`；元数据文件 SHA-256 `A380792F33BA4EB048FA2FFEBC6C504B001F85C76E4128E4D41CA24D7B017C4C`

## 2. 审计结论摘要

| ID | 优先级 | 本轮结论 | 证据强度 | 状态建议 |
|---|---|---|---|---|
| STF-01 | P1 | 无职员专属实现/运行证据；可复用人员/经理/合同/团队/俱乐部链路与 UID 查找模式，但职员记录类型、集合入口、岗位语义未确认 | candidate patterns only | 未开始 |
| STF-02 | P1 | 无实现证据；强依赖 STF-01，且需要训练/医疗职责域交叉验证 | none | 未开始 |
| STF-03 | P2 | 无实现证据；强依赖 STF-01 与 IDX-02，且需要世界职员索引与知识范围语义 | none | 未开始 |

本轮未把 manager/player 证据升级为 staff 证据。现有任务行聚合多目标，部分链路证据不等于 STF 全完成。

## 3. 现有代码审计：与 STF 相关的源位置

### 3.1 可复用模式（不是 staff 实现）

| 源文件 | 行号 | 可复用内容 | 对 STF 的意义 | 限制 |
|---|---:|---|---|---|
| `tools/FMAPI.MessageProbe/EntityLinks.cs` | 39-71 | `PERSON` 数据库表 RTTI 校验、UID 有序索引二分查找、脏缓存拒绝、边界/重检 | STF-01 职员 UID 查找可复用相同模式 | 仅验证过 actual player/person 链；职员记录类型未验证 |
| `tools/FMAPI.MessageProbe/EntityLinks.cs` | 72-123 | `CaptureEntityLinks`：人类经理集合、vbtable/vtordisp、`FULL_CONTRACT -> TEAM -> CLUB`、UID/俱乐部 UID 校验 | STF-01 岗位/所属队/合同链路可作为候选模式 | 仅 manager 链，不证明 coach/staff 使用同一链 |
| `tools/FMAPI.MessageProbe/EntityLinks.cs` | 98-105 | 合同 kind、payload type、team/club UID 提取 | STF-01 合同归属候选字段 | 合同 kind 语义未解码；staff 合同类型未确认 |
| `tools/FMAPI.MessageProbe/Program.cs` | 9-12, 39 | `--self-test`、参数/预算/失败关闭 | 未来 staff 诊断应沿用边界 | 无 staff 模式 |
| `tools/FMAPI.MessageProbe/Program.cs` | 98-129 | 进程/模块哈希、只读句柄、预算 | 未来 live read 前置 | 本轮未运行 |
| `tools/FMAPI.MessageProbe/Program.cs` | 149-178 | 单经理消息集合读取与重检 | 可复用集合读取/重检模式 | 不是 staff 集合 |
| `tools/FMAPI.MessageProbe/PositionFields.cs` | 1-37 | 原始 familiarities 与 natural mask 解码、阈值区分 | STF-01 技术/精神属性可能复用 raw/decoded 分离模式 | 仅球员位置，不覆盖 staff 资质/属性 |
| `docs/research/native-entity-evidence.md` | 13-31 | GCuM 当前经理选择、HUMAN_NON_PLAYER PERSON RTTI、teardown | 身份链候选来源 | 未证明多经理/hotseat/重载 |
| `docs/research/native-entity-evidence.md` | 33-48 | goalkeeper 业务规则与 actual player 布局 | 人员类型校验模式 | 不是 staff |
| `docs/research/native-entity-evidence.md` | 50-56 | 可复用代码位置与诊断命令 | 未来 staff probe 应遵循 | 无 staff 入口 |
| `docs/research/manager-player-links-checkpoint.md` | 11-19 | human manager -> contract -> team -> club | STF-01 候选关系链 | 仅一个实例；active selection 未通用化 |
| `docs/research/manager-player-links-checkpoint.md` | 21-30 | PERSON -> ACTUAL_PLAYER -> familiarities | 人员类型/属性模式 | 仅球员 |
| `docs/research/message-reader-checkpoint.md` | 13-36 | NEWS_MANAGER、消息集合、模板/本地化 | MSG 证据；与 STF 无直接关系 | 不作为 staff 证据 |
| `tools/research/README.md` | 27-29 | 静态位置布局证据与离线解码 | 离线验证模式 | 无 staff 数据 |
| `docs/research/interface-inventory.md` | 39-41 | STF-01/02/03 任务行 | 本轮更新状态备注 | 状态仍为未开始 |
| `docs/research/data-discovery-todo.md` | 66-68 | STF 依赖与验收要求 | 本轮未改该文件 | 仅引用 |

### 3.2 未发现的 staff 专属实现

- 无 `coach`、`scout`、`staff`、`non-player`（除 manager）相关 SDK/Core/adapter/工具实现。
- 无职员集合入口、RTTI 名称、UID 查找、岗位/分工/负荷字段。
- 无职员资质、技术/精神属性、知识范围、职业历史、招聘记录的字段目录或样例。
- SDK/Core 中的 mock 数据仅合成俱乐部，不计原生 staff 实现。

## 4. 字段语义与证据强度

### STF-01：职员 UID/身份、岗位、所属队、合同、资质与技术/精神等属性

| 目标字段组 | 当前状态 | 证据 | 未知语义 |
|---|---|---|---|
| 职员 UID/身份 | 未开始 | 无 staff 专属 UID 证据 | 是否使用 PERSON UID、非球员 UID 或复合键；跨存档稳定性 |
| 岗位 | 未开始 | 无 | 岗位枚举、岗位/合同类型关系、是否区分 coach/scout/medical/analyst |
| 所属队 | 候选模式 | manager 链 `TEAM +0x30 -> CLUB` 可作模式 | staff 是否挂在 team/club/department；预备/青年队归属 |
| 合同 | 候选模式 | `FULL_CONTRACT -> TEAM -> CLUB`、contract kind raw | staff 合同类型、工资/周期、到期、奖金、特殊条款 |
| 资质 | 未开始 | 无 | 执照/等级枚举、显示值与 raw 关系 |
| 技术/精神属性 | 未开始 | 无 | 原始值、显示缩放、空值、门将/外场不适用语义 |
| 可读集合边界 | 未开始 | 无 | 已加载/可遍历范围、分页、总数、缺口 |

### STF-02：教练分工、工作负荷、职责归属、岗位空缺、可见招聘记录

| 目标 | 当前状态 | 证据 | 未知语义 |
|---|---|---|---|
| 教练分工 | 未开始 | 无 | 分工枚举、团队/个人训练分配、指导组 |
| 工作负荷 | 未开始 | 无 | 负荷单位、更新时机、是否可直接读 |
| 招聘/训练/医疗职责归属 | 未开始 | 无 | 责任人指针、部门归属、空缺表示 |
| 岗位空缺 | 未开始 | 无 | 空值 vs 未加载 vs 真正空缺 |
| 可见招聘记录 | 未开始 | 无 | 记录类型、归属、时间语义 |

### STF-03：职员职业历史、知识范围、潜在招聘对象、全世界职员索引

| 目标 | 当前状态 | 证据 | 未知语义 |
|---|---|---|---|
| 职员职业历史 | 未开始 | 无 | 年份/俱乐部/岗位序列、缺失赛季 |
| 知识范围 | 未开始 | 无 | 地区/联赛/球员知识编码、覆盖度 |
| 潜在招聘对象 | 未开始 | 无 | 候选池来源、可读边界 |
| 世界职员索引 | 未开始 | 无 | 是否存在全局表、加载范围、分页 |

## 5. 缺失依赖

- IDX-01：实体 UID/类型/去重/引用关系。
- CLB-01：俱乐部与一线队 UID/名称、名册入口、梯队层级。
- STF-01 本身是 STF-02/STF-03 的前置。
- IDX-02：集合入口/枚举/分页/已加载范围（STF-03 尤其需要）。
- TRA-01/TRA-02、MED-01/MED-02、SCT-01/SCT-02：训练、医疗、球探职责交叉验证。
- CON-01：staff 合同若存在，需要合同关系与金额语义。
- ENV-01/LOC-01：游戏构建、日期、单位/枚举/空值基线。

## 6. 最小有界后续读取计划（未执行）

本轮不执行；以下为未来授权 live read 的最小计划。

1. **只读、固定哈希前置**
   使用与 `tools/FMAPI.MessageProbe` 相同的 fail-closed 模式：验证 `game_plugin.dll` 与 `GameAssembly.dll` 哈希、进程启动时间、RTTI/模块 RVA；不调用游戏函数。

2. **最小 staff 集合定位（预算：≤64 KiB，≤32 对象）**
   - 先通过已有 manager collection 与 PERSON 表模式确认 RTTI 命名规律。
   - 查找可能的 staff/coach/scout/non-player 集合入口；仅读取表头、计数、RTTI 名称，不遍历全表。
   - 如果无明确集合，记录阻塞，不扫描全地址空间。

3. **UID 查找模式复用**
   - 对用户私有提供的 1-32 个 staff UID 执行有序索引二分查找。
   - 校验 RTTI、vtordisp、指针重检；拒绝脏缓存。
   - 不把地址作为 ID。

4. **字段最小读取**
   - 对每个匹配记录读取 UID、类型、岗位/部门、所属 team/club 指针、合同指针、少量 raw 属性字节。
   - raw 与 decoded 分离；未知枚举保留 raw。
   - 不访问 UI、不推进日期/比赛。

5. **对照与重复读取**
   - 同一状态重复读取；记录 pass/fail/not_tested/not_applicable。
   - 重载/进程重启后重建指针；旧会话地址不可复用。
   - 不自行读档、切换经理/战术。

6. **离线分析**
   - 使用脱敏 capture 与现有 Python/C# 解码工具验证字段。
   - 仅提交最小脱敏样例，不提交 raw dumps、UID 列表、名称、存档。

## 7. 状态汇总

- **Completed (本轮)**：代码/文档审计、可复用模式定位、依赖与未知语义整理、后续有界读取计划。
- **Candidate**：PERSON/UID 查找、manager contract-team-club 链、RTTI 校验、位置 raw 解码模式；这些仅是模式，不是 staff 字段证据。
- **Missing**：staff 专属集合入口、RTTI、UID 语义、岗位/分工/负荷、资质、属性、合同、职业历史、知识范围、潜在招聘对象、世界索引、任何 live capture。

## 8. 库存状态备注

`docs/research/interface-inventory.md` 的 STF-01/02/03 行仍保持“未开始”，但证据列已更新为：无职员专属实现/运行证据；可复用 PERSON/UID 查找、`HUMAN_NON_PLAYER -> FULL_CONTRACT -> TEAM -> CLUB` 与 RTTI 校验模式，但尚未确认职员记录类型/集合入口。可调用范围仍为“未证实”。这不改变其他行，也不把候选模式计作实现。

## 9. 明确声明

- **No live read was performed.** 本轮未打开任何游戏进程、未读取内存、未调用原生函数、未扫描、未注入、未写入游戏/存档、未推进比赛/日期、未访问网络或外部资源。
- 未发现 staff 专属 runtime 结果；所有字段结论保持 candidate/unknown，不伪造样例。
- 未进行 SDK 设计或实现；未修改 SDK/Core/adapter。
- 未执行 git push 或 release。

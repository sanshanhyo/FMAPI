# Repository structure / 仓库结构

当前重点是取得可重复验证的真实游戏数据，再逐步整理长期 SDK。已有离线基础保留；本次初始化只增加文档和目录入口，不增加项目、依赖或运行时实现。

## 目录图

```text
FMAPI/
├── src/
│   ├── FMAPI.Sdk/             已有公共契约；暂缓扩展
│   ├── FMAPI.Core/            已有生命周期、事件、UI 声明和权限策略
│   ├── FMAPI.Adapters.Mock/   已有合成数据适配器
│   ├── FMAPI.Cli/             已有离线演示入口
│   ├── FMAPI.Host.BepInEx/    预留：进程内宿主、启动与生命周期
│   ├── FMAPI.Game/            预留：游戏领域数据整理
│   ├── FMAPI.Adapters.FM27/   预留：版本相关实现
│   │   ├── Memory/           只读访问与边界检查
│   │   ├── Layouts/          经验证的结构布局
│   │   ├── NativeCalls/      原生调用边界；当前不实现
│   │   └── Profiles/         精确构建身份与能力配置
│   └── FMAPI.Installer/      预留：安装、检测、卸载与恢复
├── tools/Probes/             研究探针规范；尚无可执行探针
├── examples/FMAPI.SampleMod/ 已有示例，清单仍为 mod.json
├── tests/FMAPI.Core.Tests/   已有离线行为测试
├── docs/
│   ├── architecture.md      已有架构说明，不迁移
│   ├── research-baseline.md 已有公开资料基线，不迁移
│   ├── architecture/        新模块边界与后续设计入口
│   ├── research/            构建记录、数据发现模板
│   └── modding/             现有示例与未来文档入口
└── THIRD_PARTY_NOTICES.md    依赖归属记录入口
```

图中“预留”目录目前只有 README，不是可编译项目，也不代表游戏支持已经实现。FMAPI.Game 的 Managers、Clubs、Players、Fixtures、Matches、Messages 是计划中的领域分组，等有真实数据和具体代码再创建对应子目录。

## 数据优先的开发顺序

1. 使用 [构建记录模板](research/build-record-template.md) 记录精确游戏版本、平台、渠道和探针版本。
2. 选择一个最小只读目标，例如当前经理与所属俱乐部，使用 [数据发现模板](research/data-discovery-template.md) 区分猜测和验证结果。
3. 复现加载、重新加载存档及退出等生命周期下的读取；未知构建停止读取，不猜测偏移。
4. 将有证据的版本细节放入 FM27 适配器，领域含义放入 Game；只提交可共享的说明和自有/合成测试材料。
5. 证据成熟后才讨论公共 SDK 扩展、原生调用、写操作和安装工具。

Host 负责启动与生命周期，Adapter 负责版本相关访问，Game 负责领域含义。SDK 不依赖这些实现。此分层是方向，不强行新增依赖或迁移已有代码。

保留大小写 `FMAPI.Sdk`，不另建 `FMAPI.SDK`；保留 `examples/`，不另建 `samples/`。研究分支和未推送的本地工作须另行审阅，目录初始化不会自动合入。

## 验证与状态

现有解决方案、项目引用和 CI 不变。按 [贡献指南](../CONTRIBUTING.md) 验证离线构建；CI 成功不证明真实游戏兼容。真实支持必须满足 [兼容性证据要求](compatibility.md)。

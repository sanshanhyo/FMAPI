# Architecture notes

[现有架构说明](../architecture.md) 仍是离线实现的入口。本目录用于新增设计，不迁移或替换它。

[仓库结构](../repository-structure.md) 描述本次目录初始化。新模块目前未实现：

- Host.BepInEx：启动、生命周期、线程边界。
- Adapters.FM27：构建识别、版本细节与受限读取。
- Game：经验证数据的领域含义，不暴露原始指针。
- Installer：宿主验证后再设计安装与恢复。

真实数据证据先于抽象接口。涉及公共契约、线程模型或写操作的重大决定应在 [ADR](../adr/) 记录原因与取舍。SDK 不依赖 Core、宿主或具体适配器，现有默认拒绝和 dry-run 规则不变。

# Repository structure / 仓库结构

本次已实际迁移源码、工程文件和文档，并更新解决方案、项目引用与 CI 路径。不是仅添加目录说明。

```text
src/
  FMAPI.Host.BepInEx/         宿主项目边界；BepInEx 启动实现待完成
  FMAPI.Core/
    Lifecycle/               原有 ModHost 与资源生命周期代码
    Events/                  原有 EventRegistry
    UI/                      原有 UiRegistry
    Permissions/             原有权限与默认拒绝配置
  FMAPI.Game/
    GameBuildInfo.cs          从原 SDK 迁入的版本身份模型
    GameSnapshot.cs           从原 SDK 迁入的只读快照模型
    Managers/ Clubs/ Players/ Fixtures/ Matches/ Messages/
  FMAPI.Adapters.FM27/
    Memory/ Layouts/ NativeCalls/ Profiles/
  FMAPI.SDK/
    Game/                    原有 mod 游戏访问契约
    Mods/                    原有 mod 生命周期、事件与 UI 契约
  FMAPI.Installer/            安装工具项目边界；功能待实现
tools/
  Probes/                    研究探针项目边界；尚无可执行探针
  FMAPI.Cli/                 原有离线演示入口
tests/
  FMAPI.Adapters.Mock/        原有合成数据适配器
  FMAPI.Core.Tests/           原有离线测试
samples/FMAPI.SampleMod/      从 examples 迁入，清单仍为 mod.json
docs/
  architecture/overview.md   原 architecture.md 内容
  research/public-baseline.md 原 research-baseline.md 内容
  modding/
THIRD_PARTY_NOTICES.md
```

## 项目依赖

- Game 不依赖其他 FMAPI 项目；SDK → Game。
- Core → SDK；FM27 → SDK（传递取得 Game）。
- Host.BepInEx → Core、FM27；Probes → FM27。
- Installer 独立，尚未选择安装技术或引入依赖。
- 测试 Mock → SDK；离线 CLI → Core、Mock、SampleMod；SampleMod → SDK。

原有 SDK 命名空间统一为 `FMAPI.SDK`；`GameBuildInfo` 和 `GameSnapshot` 迁入 `FMAPI.Game`。这是尚未发布的实验性代码的结构变更，已有源码使用方需更新 using 和项目引用，不能视为二进制兼容承诺。没有增加公共 API 功能。所有现有调用方已一起调整。

Host、FM27、Installer 和 Probes 目前是可构建的项目边界，不假装具有尚未验证的运行时功能。Game 六个领域目录已落地，暂无真实字段代码的目录以 .gitkeep 保存。未知偏移、原生签名和游戏状态写入不在本次重构中实现。

## 当前开发重点

先取得最小可重复的只读真实数据，再扩展长期 SDK。使用 [构建记录](research/build-record-template.md) 与 [数据发现模板](research/data-discovery-template.md)，先验证当前经理与俱乐部等小目标。证据满足 [兼容性要求](compatibility.md) 才能声明游戏支持。

[贡献指南](../CONTRIBUTING.md) 的离线构建、测试和 demo 继续有效；CI 通过不等于游戏兼容。没有合入其他研究分支或未推送的本地工作。

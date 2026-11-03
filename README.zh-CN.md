# FMAPI

**Football Manager Modding API** 是面向 Football Manager 模组和工具的独立、非官方 C# 框架。

[English](README.md) · [架构](docs/architecture/overview.md) · [路线图](docs/roadmap.md) · [贡献指南](CONTRIBUTING.md)

FMAPI 的目标是提供版本化接口，统一模组生命周期、事件、UI 扩展和受控游戏命令。具体游戏版本的接入由适配器负责，公共 SDK 与游戏内存布局、外部助教应用分开维护。

## 当前状态

目前完成的是 **Phase 0 离线基础工程**，使用 .NET 10，API 版本为 `0.1.0`。接口仍处于实验阶段，稳定版发布前可能调整；尚未发布软件包或真实游戏适配器。

| 领域 | 当前已实现 | 后续接入 |
| --- | --- | --- |
| 模组管理 | Manifest/API 兼容性检查与加载、卸载生命周期 | 模组发现与打包 |
| 事件 | 随模组卸载清理的类型化订阅 | 来自游戏适配器的事件 |
| UI 扩展 | 声明注册与卸载清理 | 在受支持游戏界面中渲染 |
| 游戏访问 | 适配器接口与内存中的合成数据 | 按游戏构建实现适配器 |
| 受控写入 | 默认拒绝、显式授权、命令白名单和 dry-run 验证 | 经验证的游戏命令及执行规则 |

离线示例只修改内存中的合成数据，不连接 Football Manager。所有真实游戏版本与平台的[兼容性仍未验证](docs/compatibility.md)。

## 快速开始

安装 [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0)，在工程根目录执行：

```sh
dotnet restore FMAPI.slnx
dotnet build FMAPI.slnx --configuration Release --no-restore
dotnet test FMAPI.slnx --configuration Release --no-build
dotnet run --project tools/FMAPI.Cli --configuration Release --no-build -- demo
```

示例会加载模组、处理事件、注册 UI 声明，依次展示默认拒绝写入、dry-run 验证、显式授权后修改 mock 数据，并展示卸载时的资源清理。

[示例模组](samples/FMAPI.SampleMod) 展示公共 SDK 的基本用法。当前 CLI 是离线演示宿主；此次初始化不包含真实游戏安装或注入流程。

## 工程结构

```text
src/FMAPI.SDK/              模组作者和适配器使用的公共接口
src/FMAPI.Core/             宿主、生命周期、事件、UI 注册表与命令策略
tests/FMAPI.Adapters.Mock/    使用合成数据的内存适配器
tools/FMAPI.Cli/              离线演示宿主
samples/FMAPI.SampleMod/  仅依赖公共 SDK 的示例模组
tests/FMAPI.Core.Tests/     宿主行为与权限策略测试
docs/                      范围、架构、兼容性和设计决策
```

## 写入控制

宿主默认关闭写入。执行命令需要同时满足宿主启用写入、模组申请写能力、宿主显式授予能力、宿主的全局与模组级命令白名单均允许，以及适配器支持并验证该命令。命令默认使用 dry-run，只做验证，不执行命令。详见[架构说明](docs/architecture/overview.md)。

这些检查管理通过 FMAPI 接口运行的合作式模组，无法隔离同进程中的恶意代码。真实适配器必须进一步规定游戏线程调度、状态校验、失败处理和恢复行为。

## 开发与许可

修改公共接口或新增适配器前，请阅读[贡献指南](CONTRIBUTING.md)。工程配置了 Linux、Windows、macOS 的构建、测试和离线示例 CI；该矩阵验证框架本身，不代表游戏兼容性。

FMAPI 采用 [MIT 许可证](LICENSE)，第三方依赖保留各自许可证。仓库不分发游戏二进制、数据库、存档，以及从游戏生成的程序集或元数据。

FMAPI 与 Sports Interactive、SEGA 没有隶属或背书关系。Football Manager 及相关商标归各自权利人所有。

# Game-data research / 数据研究

当前优先验证真实游戏数据读取，SDK 扩展暂缓。这个目录是研究记录入口，不是已验证支持列表。

- [公开资料基线](public-baseline.md)：已迁入本目录；公开资料不证明运行时能力。
- [构建记录模板](build-record-template.md)：先确定所研究的精确构建。
- [数据发现模板](data-discovery-template.md)：记录问题、观察、证伪与复现。
- [探针规范](../../tools/Probes/README.md)：有限、只读、可退出。
- [兼容性要求](../compatibility.md)：只有满足证据要求才更新支持声明。

复制模板时用可读文件名，给每条结论关联构建和代码提交。未知信息写 unknown，不把历史私有实验或别的分支当成当前 main 的实现。只提交脱敏的可共享研究记录；原始游戏材料留在本地，不加入版本控制。

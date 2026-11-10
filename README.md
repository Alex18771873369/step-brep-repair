# DSH STEP 曲面修补插件

DeepSeek Harness（DSH）插件：注册 `/step-brep-repair` 技能，帮助 AI 诊断 STEP/STP 破面并尝试局部补面，优先保留原始 B-rep 曲面。

> 这是**技能 + 只读诊断脚本**，不是一键修复器。复杂模型需要 AI 使用可用的 CAD/几何内核逐案处理；不保证任意模型能修好，也不能以 OCCT 闭合标志代替 Creo 等目标软件复核。模型的加工精度需另行确认。

## 用户安装：DSH 插件

1. 下载本项目的源码包或 GitHub Release 中的 `.tgz`，或复制项目 GitHub 地址。
2. 在 DSH 的「插件」页选择「添加插件」，填入 GitHub 地址、`.tgz` 或本地绝对路径，选择安装来源，查看安装前检查并确认。
3. 按 DSH 安装结果提示启用或重启；在技能列表查找 `step-brep-repair`。如果同名用户技能已存在，需核对实际加载来源，避免旧技能优先级导致仍在使用旧版本。
4. 输入 `/step-brep-repair @模型.stp 检查并修补破面，保留曲面`。路径是示例，请选择自己的模型。

插件源码在本机进程运行；仅安装可信来源。Git 安装可能运行包管理构建脚本，须核对并按提示授权；此包本身无安装钩子。

## 仅安装技能（不装 DSH 插件）

将仓库的 `skills/step-brep-repair/` **整个文件夹**复制到 `~/.dsh/skills/step-brep-repair/`；不要只复制 `SKILL.md`，必须包含 `scripts/` 和 `references/`。也可复制到项目的 `.dsh/skills/step-brep-repair/`。重新加载技能列表或重启会话。

让 AI 安装时，可将以下内容发给 AI（先把地址换成发布者提供的真实 GitHub 地址）：

```text
请从 https://github.com/<发布者>/<仓库名> 获取 step-brep-repair 技能。
先查看仓库源码和许可证，然后把仓库中的 skills/step-brep-repair 完整复制到
我的 ~/.dsh/skills/step-brep-repair/。如同名目录已存在，请先询问我，不要覆盖。
安装后检查 SKILL.md、scripts 和 references，并验证 DSH 是否识别。
```

`<发布者>/<仓库名>` 是占位符，不是可直接访问的真实地址。下载/运行第三方代码前由使用者自行检查和授权。

## 环境与限制

- 先检测本机 CAD，优先使用现有可调用的软件；仅在缺少可用工具、征得同意及权限允许时，才协助从官方来源安装 FreeCAD。
- MCP 按需接入：先复用已配置服务；第三方桥接具有执行代码风险，须确认来源、版本、权限和连接测试。本插件不自动安装 CAD 或 MCP，不会在安装插件时自动配置它们。
- 随附的检测脚本只读检查环境；STEP 诊断脚本需要可导入 `FreeCAD`、`Part` 的 Python，网格检查还需要 `MeshPart`。
- 脚本和方法基于当前本机 FreeCAD 1.1.3 以及 DSH 0.2.2-rc.1 环境开发；适配不同版本需自行测试。
- 安装、发布详见 `PUBLISHING.md`；技能详细流程、诊断脚本和 MCP 注意事项位于 `skills/step-brep-repair/`。

## 测试

```bash
node --test tests/*.test.js
```

开发测试验证了插件注册代码（模拟宿主）及技能资源；在 DSH 0.2.2-rc.1 的隔离 web profile 中，`.tgz` 已安装、登记 bundle 且配置组合成功。**尚未完成真实会话中技能加载及资源访问的端到端测试**，公开发布前请按 `PUBLISHING.md` 验收。数据与诊断均在本地处理；AI 服务本身是否访问网络由用户的模型配置和指令决定。

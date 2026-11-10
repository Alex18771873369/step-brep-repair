# STEP / STP 破面修补技能

供 DeepSeek Harness 等支持 Agent Skills 的助手使用。先检测本机已有 CAD 并优先利用现有工具；无可用 CAD 时，在确认及权限允许后协助安装 FreeCAD。MCP 按需检测或配置。优先保留 CAD 原始曲面，通过诊断、人工/AI 局部补面、独立重载和目标 CAD 复核处理破面。

## 安装

将 `step-brep-repair` 文件夹复制到：

- 当前用户：`~/.dsh/skills/step-brep-repair/`
- 当前项目：`项目目录/.dsh/skills/step-brep-repair/`

然后重启会话或刷新技能列表，在消息中输入 `/step-brep-repair`，或从技能选择器选择。安装详细说明及其他支持 Agent Skills 的工具的兼容性说明见 `references/installation.md`。

## 使用

把 STEP 文件提供给助手，例如：

```text
/step-brep-repair @外壳.stp 这个文件有破面，保留曲面，修补后导出实体。
```

若已知破面位置，可以提供 CAD 截图和 XYZ 坐标。运行诊断脚本需要本机 FreeCAD Python 环境，`--mesh` 还需 MeshPart；具体路径依本机安装位置调整。示例及命令见 `references/installation.md`。

## 能力边界

此技能是**指导 AI 操作的流程加只读诊断脚本**，不是自动一键补面程序。复杂模型需要逐个分析，可能需要用户提供截图或在 Creo 中复核；不保证任意模型都能自动修好。不会默认将整体模型网格化、不会以 OCC 有效标志替代实际 Creo 验证。需要加工时须自行确认尺寸、公差和制造要求。

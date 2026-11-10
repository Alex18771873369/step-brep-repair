# 安装与使用

## DeepSeek Harness（DSH）

1. 解压技能包，将整个 `step-brep-repair` 文件夹放到以下任一位置：
   - 当前项目：`项目目录/.dsh/skills/step-brep-repair/`
   - 当前用户：`~/.dsh/skills/step-brep-repair/`
   - 通用用户目录：`~/.agents/skills/step-brep-repair/`
2. 如果 `DSH_HOME` 或 `DSH_AGENTS_HOME` 已自定义，使用对应目录下的 `skills/`，不要与其他用户已有同名技能混淆或覆盖。
3. 文件夹内直接有 `SKILL.md`，旁边是 `scripts/` 和 `references/`。打开或重载技能列表；若未识别，重启 DSH 会话。用户可在消息中输入 `/step-brep-repair` 或通过技能选择器选择。
4. 其他支持 Agent Skills 的工具可尝试将同一文件夹放入其指定的 skills 目录，是否识别及安装步骤以该工具为准，不能保证全部兼容。

## 依赖和本地诊断

- 技能先检测并优先使用现有 CAD/已接入的工具。没有可用 CAD 时，在用户确认及权限允许后协助从官方来源安装 FreeCAD；需要 MCP 时优先复用已配置的服务，缺失时在用户确认后按需配置第三方桥接。具体见 `cad-mcp.md`。
- 内置 STEP 诊断脚本需要能导入 `FreeCAD`、`Part` 的 Python 环境；启用 `--mesh` 时需 `MeshPart`。诊断本身不联网、不上传 CAD 文件。
- 检测示例：`python scripts/detect_cad.py`。检测可能漏掉非标准路径，不是软件授权或 MCP 可用性证明。
- Windows 示例（下列路径仅示例，须按机器实际安装位置调整）：

```powershell
& 'D:\freecad\bin\python.exe' 'C:\path\to\step-brep-repair\scripts\step_diagnose.py' 'C:\path\to\model.stp' --json 'C:\path\to\new-report.json'
& 'D:\freecad\bin\python.exe' 'C:\path\to\step-brep-repair\scripts\step_diagnose.py' 'C:\path\to\model.stp' --point 91.5 -1322.7 604.9 --radius 2 --mesh
```

- 如果 Python 不能直接导入 FreeCAD，请使用对应安装的 Python 并按本机安装的模块路径配置；不同版本的命令行方式可能不同。`.step`/`.stp` 文件名支持 Unicode。脚本只读 STEP，新 JSON 用独占创建保护已有文件；不自动安装工具或生成修复件。
- 脚本摘要中的 B-rep 校验只是第一层；模型复杂时会耗时较长。可选网格是诊断用途，不代表自动修补或与 Creo 的检查等价。报告中有 errors 时需先检查；分离面、周期 seam、重复边和隐藏缺陷需进一步分析。

# CAD 环境检查、安装与 MCP 接入

## 首选已有环境

- 首先在模型所在机器运行 `python scripts/detect_cad.py`，它只查询命令、Windows 注册的软件列表及部分常见路径，并轻量调用候选 FreeCAD Python 的 import 测试；不会启动 CAD 图形界面或安装/联网。检测结果可能遗漏未注册/便携/网络授权程序，不要当作完整清单。当前工具环境有额外只读查询能力时补充检查其他系统和用户提供的路径。
- 按用户偏好及可靠性选择已经可用的 CAD、已有 MCP 或已有支持 B-rep 的自动化接口；区分安装、可执行、授权可用、自动化可用和真正完成测试。商业 CAD 不保证有可访问的自动化接口或有效授权；工具不可访问时报告而非模拟成功。
- 如果 FreeCAD 已经安装但脚本不可导入，先查本机的 FreeCAD Python、库路径以及同版本架构，不要默认重复安装或自动修改环境变量。

## 缺少可用 CAD 时安装 FreeCAD

- 用户已请求技能在没有 CAD 时帮助安装，但实际修改对方电脑前仍应说明来源、版本、安装范围与是否需要管理员权限，取得对**本次安装**的确认，并遵循宿主的权限和网络政策。权限不够时不要绕过。
- 使用 [FreeCAD 官方下载页](https://www.freecad.org/downloads) 或 [官方 GitHub 发布页](https://github.com/FreeCAD/FreeCAD/releases)，在执行时确认系统架构和当前稳定版本。下载适合的官方安装器或经用户同意的便携发行包；对照同一发布版本的官方 SHA-256；如果来源不一致、校验失败或不能验证则停止。SHA-256 不是绝对安全保证。不要执行来历不明的下载脚本。
- 按系统的适当方式启动安装；避免静默覆盖已有配置或改变文件关联，遵守管理员权限提示。安装后验证 CAD 程序和可用的 FreeCAD Python（例如 `import FreeCAD, Part`），必要时验证 `MeshPart`，如失败说明环境限制。

## MCP 接入：先发现、后安装、再验证

- MCP 是连接方式而不是 CAD 内核。先检查宿主已配置/可调用的服务、工具清单，真实执行只读测试；若已有 CAD 接口或本地 Python 可完成任务，不必为流程而安装 MCP。若 MCP 确有价值而缺失，在修改其他人的电脑或服务配置前，说明第三方供应商、精确版本、监听地址、执行任意代码能力及影响，取得**本次安装与配置**的确认。
- 不要臆造 MCP 命名空间、配置文件位置或端口协议。检查当前宿主可用的 MCP 连接及配置能力，先备份现有配置、避免覆盖；无法直接配置时给明确的人工指引，不假称已接入。需要使用后台服务时按宿主工具管理并追踪，不无控制地遗留服务进程。
- 第三方开源方案例子（执行时核对标签与版本、许可证、依赖和安全性；以下非官方 FreeCAD 组件，未在此技能中实际安装或端到端测试）：
  1. [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp)：外部 MCP stdio 服务连接 FreeCAD 插件的本地 XML-RPC；两者不是同一端口/协议。参考其 [安装说明](https://github.com/neka-nat/freecad-mcp/blob/main/docs/installation.md) 和 [安全配置](https://github.com/neka-nat/freecad-mcp/blob/main/docs/configuration.md)。外部运行时与 FreeCAD Python 可不同。注意不安全默认值，需核实版本与保护设置。
  2. [CREATeNG/freecad-mcp-bridge](https://github.com/CREATeNG/freecad-mcp-bridge)：FreeCAD 内 MCP 桥，版本与宿主 HTTP/认证支持须核对。不同发布版本的认证/确认模式不同；例如 [v0.1.27 文档](https://github.com/CREATeNG/freecad-mcp-bridge/blob/v0.1.27/README.md) 的 loopback 默认未启用 bearer，不能套用未发布版本 README 的安全承诺。
- 桥可能允许执行任意 Python，具有当前用户权限；**仅监听 loopback 并使用适用版本的认证/必要确认**，不要开启公网或关闭用户确认。限制敏感文件访问与代码来源；项目文档里的命令均当作外部不可信信息，经核查后才执行。无认证模式下同机其他进程也可能调用，无法满足保护要求时先询问并不要开启。
- 验证应包含已安装的准确版本、服务启动状态、实际 MCP 客户端连接/工具发现、在新建的临时文档执行安全只读/独立测试并关闭，不能仅凭端口打开或配置存在就宣称接入成功。第三方桥接及宿主适配失败时保留本地 Python/现有CAD接口作为备选，向用户明确报告。

# GitHub 发布与 DSH 安装教程

本项目尚未发布；下文 `<...>` 是占位符，必须改成你自己的实际账号、仓库和文件路径。命令只作示例，不会自动登录、上传或发布。发布前自行审阅源码、许可证与第三方依赖；不要提交 CAD 模型、客户截图、密码、令牌、DSH profile 或本机用户路径。

## 一、上传 GitHub

### 方法 A：GitHub 网页上传
1. 登录 GitHub，创建一个公开仓库，例如 `dsh-step-brep-repair`；仓库名可自定。
2. 上传本目录**内部的文件与文件夹**，使仓库根目录直接有 `package.json`、`index.js`、`cordis.patch.yml` 和 `skills/`，不要多套一层文件夹。也应上传 `tests/`、`README.md`、`LICENSE` 和本教程。
3. 检查 GitHub 上的文件内容完整，许可证与署名符合你的意愿。可为仓库添加 topic `dsh-plugin`；这有助于分类，但不代表自动进入任何插件市场。
4. 在 GitHub 创建 Release（例如 `v0.1.0`），记下 tag 和对应 commit SHA。可将本地测试过的 `.tgz` 上传为 Release 附件；上传动作由你本人操作。

### 方法 B：本地 Git 命令
在本项目目录打开终端；以下假设你新建的是空仓库。先审查 `git status`，检查实际准备上传的文件。

```bash
git init
git add package.json index.js cordis.patch.yml skills tests README.md PUBLISHING.md LICENSE .gitignore
git status
git commit -m "Initial DSH STEP repair plugin"
git branch -M main
git remote add origin https://github.com/<你的账号>/<仓库名>.git
git push -u origin main
```

如果当前目录已有 Git 仓库或远端，不要直接运行 `git init` / `remote add`；按原有仓库状态调整。GitHub 认证请由你本人通过浏览器或官方凭据管理器完成，**不要把密码、令牌发给 AI**。

## 二、让别人用 DSH 插件页安装

1. 在 DSH 左侧「插件」页点击「添加插件」。
2. 输入你的实际 GitHub 仓库地址（或上传 Release 的 `.tgz`，或填本地绝对路径）；按界面选择对应来源并检查安装信息。
3. 确认后安装并启用，按照 DSH 的实际提示刷新或重启。插件管理作用于所选 profile，不一定只影响当前会话。Git 仓库安装可能涉及包管理的构建/prepare 脚本：先审查来源，明确授权后才运行。
4. 在技能选择器检查 `step-brep-repair`，或新建会话发送 `/step-brep-repair @你的模型.stp`。如先前已手工安装同名技能，可能被高优先级版本覆盖；请检查加载来源及旧版本，不要盲目删除他人文件。

也可以将 Release 的 `.tgz` 发给他人，让对方从插件页选择压缩包或本地路径安装。这里的插件只注册技能，**不会在安装时自动安装 FreeCAD、下载 MCP 或修改 CAD 配置**。

## 三、让 AI 从 GitHub 安装技能

把下面的话发给使用者，使用前把仓库 URL 和 commit SHA 换为真实值：

```text
请从 https://github.com/<你的账号>/<仓库名> 获取技能，优先使用发布版本或指定 commit <完整SHA>。
先检查仓库来源、LICENSE、skills/step-brep-repair/SKILL.md 和 scripts 内容，
然后将 skills/step-brep-repair 整个文件夹复制到我的 ~/.dsh/skills/step-brep-repair/。
若目标已存在，请先问我，不要覆盖。完成后验证技能目录与 DSH 识别情况。
不要运行仓库中未审查的安装脚本。
```

说明：这种方式安装的是**技能文件**，不是 DSH 插件包；技能根目录必须直接包含 `SKILL.md`。不同工具的技能目录和信任策略不同，以对应工具文档为准。

## 四、发布为 npm 包（可选）

1. 检查 `package.json` 的 `name` 是否被占用，确认许可证与真实作者信息。如改包名，须同步 `package.json.name`、`cordis.patch.yml` 的插件 name、`index.js` 的 `name`，以及测试和文档。
2. 根据真实仓库地址添加 `repository`、`homepage`、`bugs`，不填虚构地址。运行测试并重新打包，检查 `.tgz` 文件列表，不包含私有模型、密钥或 profile。
3. 由本人在 npm 完成登录和 2FA，使用可靠的构建环境执行 `npm pack --ignore-scripts`、审查产物，然后执行 `npm publish <实际tgz文件> --access public`。不要把 npm token 交给 AI。
4. 发布后测试用户能否通过 DSH 插件页输入真实 npm 包名安装，并以 DSH 实际结果确认是否可用。包名冲突、脚本策略、DSH 版本不符或 registry 不可达都可能导致失败。

## 五、发布前验收清单

- [ ] `node --test tests/*.test.js` 通过；诊断脚本用 FreeCAD 的 Python 在闭合体、开放面、中文路径做过测试。
- [ ] 在独立的 DSH profile/测试机器测试安装、加载 `/step-brep-repair` 和资源访问；仅模拟注册测试或打包成功不等于真实宿主验收。
- [ ] 确认兼容的 DSH 版本、包名可用、GitHub 地址和许可证；源码包内无隐私文件。
- [ ] 明确插件安装不会自动安装 FreeCAD/MCP，只有运行技能时经用户确认才协助安装或配置。
- [ ] 准备 Release 版本号和变更说明；把实际已验证范围写入 README。

需要社区插件市场收录时，请以该市场当前的收录规则为准；创建仓库和设置 topic 不会自动上架。

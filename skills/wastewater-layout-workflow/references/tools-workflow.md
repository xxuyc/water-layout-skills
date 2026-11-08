# 工具与执行流程

## 工具对应关系

| 工作 | 本对话使用的工具 | 下次使用方式 |
|---|---|---|
| 查找文件、读取文字、运行本地程序 | `functions.exec` 调用 `exec_command`，PowerShell，`rg` | 先定位源文件和最新输出，避免全盘扫描；路径作为字面值处理 |
| 查看源图、输出图 | `view_image` | 先全图确认，再对关键编号/交叠处放大；逐页查看最终渲染 |
| 放大照片细节 | Python + Pillow | 只用于识别辅助裁切；保留源照片，不用于画整个工艺插图 |
| 获取 Node/Python/库路径 | `mcp__codex_app__load_workspace_dependencies` | 每次从环境读取，不锁定旧版缓存绝对路径，不另装替代运行时 |
| CAD只能目视读取时 | 浩辰CAD看图王，Windows computer-use Skill 和其批准的界面 API | 先读当前 computer-use Skill；遵循当前环境可用界面，不用命令伪造点击，不声称解析DWG实体 |
| 缺少目的地、范围信息 | `request_user_input_async` | 仅问会改变图形的信息；继续不依赖答案的部分，确认相同阶段后才复制 |
| 可编辑PPT与PNG | 当前 presentations Skill，JavaScript `@oai/artifact-tool` | 原生形状和文字，使用当前安装版的 API 与导出流程 |
| 验证并产出最终PPT | presentations 的 `finalizePresentation` | 当前 skill 路径下工具，保留草稿和源文件，最终文件用新名称 |
| 给用户打开结果 | `mcp__codex_app__open_in_codex` | 可用于展示最终PPT；返回queued不等于已在PowerPoint检查 |
| 保存Skill并打包 | `apply_patch`、文件复制、Python `zipfile` | Skill安装到个人skills目录；该目录受限时使用环境正常权限机制 |

`functions.exec` 是工具编排入口，可通过 `ALL_TOOLS` 按名称发现当前可用工具。调用独立只读工具时可并行，写入、依赖步骤和审批顺序执行。不把电脑界面工具、浏览器、CAD实体解析混为同一读取方式。

## 识图到交付

1. 确认用户最新来源和范围，必要时看原图局部。记录可确认设备、数量、所属区域、管路出口及不清楚的连接。
2. 按本次任务采用池体图、串联图或加药图。决定合并储罐、镜像或阶段复制，但保留真实数量和共享设施。
3. 当前环境有 presentations Skill 时读其实现、模板跟随及导出要求。图形采用原生对象，独立标签按真实字体测量。不要直接复制已过期的 helper 路径或缓存版本。
4. 在工作目录私有build子目录存草稿、识图记录及检查文件，输出目录仅放交付物。按当前 skill 要求记录create/edit操作、导出草稿、验证结构和字体。
5. 渲染逐页查看，检查文本遮挡、管路进入/离开设备、出口去向、泵数量、镜像方向、阶段归属和图例颜色。变动后重渲染受影响页。
6. 从最终PPT渲染PNG，常用2～2.5倍分辨率。应检查Word目标图幅可读性，分辨率不能弥补字号太小。交付PPT和每页PNG，不交付过程脚本除非用户索要。

## 随包复用工具

- `scripts/measure_text_boxes.py`：Pillow实测指定字体与多行标签，输出紧凑文本框尺寸。字体路径显式传入，不隐式换字体。
- `scripts/native_symbols.mjs`：给当前artifact slide添加直线、箭头、泵、仪表、阀门和文本对象。它只提供符号，不推断任何连接或数量。
- `scripts/inspect_native_pptx.py`：只读列出PPTX每页对象ID、位置、文字、图像数量和页尺寸，用于挑选修订对象、核对原生编辑结构。它不代替渲染检查或正式finalizer。
- `editable-aeration-layout/scripts/mirror_native_shapes.py`：已验证的镜像辅助。只支持明确选择的独立原生形状；连接器、动画引用、组对象需采用对应的编辑方式。不能凭左右坐标自动删除用户对象。

短标签API示例：先用测量脚本取得 `{width,height}`，再将它交给 `native_symbols.mjs` 的 `text` 方法。圆圈内F标签独立使用符号大小，不套普通标签尺寸。

## 已遇到的运行细节

- PowerShell调用中文路径时使用字面路径，Python控制台可设UTF-8。修改OOXML时使用标准`utf-8`编码，旧流程里的`utf8`声明曾造成导入失败。
- finalizer在Windows沙箱解析工作目录`realpath`曾返回EPERM。遇到同类错误，保留草稿，按实际范围申请正常执行权限；不要改变工作目录边界或绕过批准流程。
- 本机早前没有PyYAML。不能声称已安装或执行了完整YAML解析器；Skill验证应如实记录采用的解析方式，或使用已可用的依赖。此点不影响PPT图形绘制。

本Skill只负责当地文件工作，绘图授权不等于改动SCADA控制系统、外部发布或给其他人发送消息的授权。

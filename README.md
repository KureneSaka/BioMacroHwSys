# Bio-macromolecular-Engineering-Homework-System

PKU《生物大分子工程》课程 **作业（每周 Q&A 参与）系统**。

本系统以「每周提问 + 互评 + 互答 + 教师应答」的形式记录每位学生在课程各周次的参与情况，
并将结果导出为 Word 文档用于考核统计。系统面向**学生**与**管理员（教师/助教）**两类账号。

> demanding for bug reporting — 欢迎反馈 Bug。

## 功能一览

- **周次管理**：管理员在「周次」页维护课程进度（第几周、讲座章节、提交/评价时间窗），并切换当前周。
- **学生端**
  - 按周提交问题（可软删除 / 撤销删除）
  - 随机抽取他人问题做互评（附议 👍 / 点踩 👎）
  - 随机抽取他人问题作答
  - 查看全部结果 / 个人结果，导出 `.docx`
- **管理员端**
  - 逐条应答问题，并对问题标注「认可 / 不喜欢」
  - 查看全量结果（按热度排序、可按筛选条件过滤）并导出 `.docx`
  - 管理学生账号、管理员账号、周次信息
- **账号体系**（2026-09 重构为 Django 标准账号）
  - 学生：`username = 学号`，姓名存 `first_name`；管理员：自定义 `username`
  - 密码经 PBKDF2 哈希存储，登录态使用服务端 session（7 天）
  - 新建 / 重置密码后**首次登录强制修改密码**
  - 学生只能删除 / 恢复**自己**的问题（带归属校验）

## 技术栈

| 组件 | 说明 |
|---|---|
| 后端 | Django 6.1 + SQLite（见 `requirements.txt`） |
| 导出 | python-docx（Word 表格导出，保存目录 `caches/` 自动创建） |
| 前端 | 服务端模板 + Boomerang 主题（`statics/`，自 `statics.zip` 解压） |

## 目录结构

```
BioMacroHwSys/          # 项目配置与顶层路由（登录跳转、登出、周次切换）
App_adminSystem/        # 管理端：登录、周次管理、问题作答、账号管理
App_studentSystem/      # 学生端：登录、提问、互评互答、个人结果
App_dataSystem/         # 数据模型（models + 迁移）
App_exportfile/         # Word 导出模块（学生 / 管理端共用）
templates/              # 页面模板（admin/ student/ 及公共 base）
statics/                # 静态资源（从 statics.zip 解压，已被 .gitignore）
caches/                 # 导出文件输出目录（运行时自动创建，已被 .gitignore）
```

## 环境要求

- Python 3.13（本项目开发使用 conda 环境）
- 依赖安装方式二选一：
  - conda：`conda create -n BioMacroHWsys python=3.13`
  - venv：`python -m venv .venv`

## 快速开始

以下命令在项目根目录执行（示例用 conda 环境；venv 请替换为对应解释器）。

```bash
# 0) 首次需解压前端静态资源
unzip -o statics.zip

# 1) 安装依赖
conda run -n BioMacroHWsys pip install -r requirements.txt

# 2) 初始化数据库（建表）
conda run -n BioMacroHWsys python manage.py makemigrations
conda run -n BioMacroHWsys python manage.py migrate

# 3) 启动（端口 3939）
conda run -n BioMacroHWsys python manage.py runserver 0.0.0.0:3939
```

Windows 下可参考根目录 `start.bat`（使用 `py` 启动器）。

### 首次使用：创建管理员账号

若数据库中尚无管理员，可执行一次（把密码换成你自己的）：

```bash
conda run -n BioMacroHWsys python manage.py shell -c "from django.contrib.auth.models import User; from App_dataSystem.models import UserProfile; u=User.objects.create_user('admin', password='请改成强密码', first_name='管理员', is_staff=True); UserProfile.objects.create(user=u, must_change_password=True)"
```

创建后访问 `http://localhost:3939/admin/`，用「用户名 + 密码」登录，系统会要求先修改密码。

> 管理员登录后，请先在「周次」页新建第一周的安排；再在「人员 → 学生信息 / 管理员信息」中添加学生 / 管理员账号
> （添加时会自动生成随机初始密码并只显示一次，分发给本人后由其首次登录修改）。

### 账号规则速查

| 角色 | 登录入口 | 账号 | 密码 |
|---|---|---|---|
| 学生 | `/student/` | 学号 | 老师分发的初始密码（首次强制改密） |
| 管理员 | `/admin/` | 用户名 | 同上 |

## 一键生成本学期周次安排

在「周次」页可批量生成整学期安排：填**学期第一天 / 最后一天**，以及**第 1 周**的
「开启时间 / 提交截止 / 评论结束」三个时间点，系统按 **7 天一周**切分并自动平移生成（章节默认 Lec.周次~周次，可在下方表格微调）。
其中「开启」与「提交截止」须落在第 1 周内；「评论结束」**不设上限**、只要晚于提交截止即可（可顺延至任意周）。
若与已有周次冲突则**整批中止**并提示冲突周次。

## 从课程网批量导入学生 (CSV)

1. 在课程网的「**小组与用户 - 小组**」页面中，先打开**编辑模式**，再点击导出按钮导出小组成员 CSV
   （文件名形如 `2026..._groupmembers.csv`）。导出时请勾选**「仅导出用户」**与**「带表头导出」**，
   以确保文件包含 `User Name` / `First Name` 等表头列。
2. 在本系统「人员 → 学生信息」页的「从 CSV 导入学生」处上传该文件。

**列约定**：只读取 `User Name`（作为学号 / 登录名）与 `First Name`（作为姓名）两列；
因此**其它来源**的 CSV 只要包含这两列（或 `username` / `学号`、`first_name` / `姓名` 等列名）同样可导入。
支持 UTF-8 / GBK 编码与逗号 / 制表符 / 分号分隔。

**导入规则**
- 每个学号自动创建学生账号并**随机生成初始密码**（导入成功后在本页一次性列出，请复制分发；首次登录须修改密码）。
- 若文件中**任一学号已存在账号**，则**整批中止**：不会写入任何学生，并明确列出冲突的学号。
- 导入成功后，可点击「**下载本批初始密码 CSV**」把初始密码导出为文件（含学号 / 姓名 / 密码），便于发布给学生；账号将在首次登录时强制修改密码。

### 补发 / 重置密码（不保存明文）

系统**不保存任何明文密码**。如需为部分学生重发密码：在「人员 → 学生信息」页**勾选学生**后点击「**重置所选并导出 CSV**」，
系统会为这些学生生成新密码并立即下载文件（含学号 / 姓名 / 新密码）。原密码即刻失效，学生首次登录仍需修改密码。

## 导出功能

- 「全部结果 / 个人结果」页可勾选导出列（序号、编号、评价、操作人、时间、管理员/学生回答等）。
- 生成的 `.docx` 保存在 `caches/`（不存在会自动创建，位于项目根目录，已被 `.gitignore` 忽略）。

## 已知限制 / 注意事项

- 开发配置：`DEBUG=True`、内置 SECRET_KEY、`ALLOWED_HOSTS=['localhost']` —— **请勿直接用于公网生产**。
- 周次表驱动所有页面：请确保课程进度里**至少有一行周次且其开始时间位于未来或正在进行的区间**，否则首页会因取不到「当前周」而报错。
- 业务数据通过「学号 / 用户主键」等整数引用，删除账号后其历史问题仍保留，提问人显示为「未知」。

## License

见根目录 `LICENSE`。


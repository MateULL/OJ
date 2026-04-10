# Minimal OJ 第一阶段

这是一个第一阶段 Online Judge 骨架，目标是先跑通核心流程：提交入队、独立 Worker 判题、Docker 内编译运行、逐测试点结果落库，以及最小可用的 Vue 前端。

## 目录

```text
backend/
  oj/                 # Django models, serializers, API views
  judge/              # 判题枚举、DTO、比较器、Docker runner、core、worker
  testdata/           # demo 测试数据；实际根目录由 TESTCASE_ROOT 配置
frontend/
  src/views/          # 题目、提交、用户中心页面
  src/components/     # Verdict、题面、状态、测试点结果表
  src/editor/         # Monaco Editor 封装
```

## 后端本地运行

第一阶段默认使用 MySQL 配置。为了快速 demo，也可以临时启用 SQLite。

### MySQL 方式

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:MYSQL_DATABASE="oj"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
python manage.py migrate
python manage.py loaddata demo
python manage.py runserver
```

### 快速 SQLite demo

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

$env:OJ_USE_SQLITE="1"
python manage.py migrate
python manage.py loaddata demo
python manage.py runserver
```

## 判题 Worker

判题不会在 Web 请求里执行。另开一个终端运行：

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:OJ_USE_SQLITE="1"
docker pull gcc:13
python manage.py judge_worker
```

只处理一个任务后退出：

```powershell
python manage.py judge_worker --once
```

测试数据根目录默认是 `backend/testdata`，可通过 `TESTCASE_ROOT` 修改。数据库中的 `TestCase.input_path` 和 `TestCase.output_path` 都是相对路径。

## 前端本地运行

```powershell
cd frontend
npm install
npm run dev
```

Vite 默认运行在 `http://127.0.0.1:5173`，并把 `/api` 代理到 `http://127.0.0.1:8000`。

## 最小 API

```text
GET    /api/problems/
GET    /api/problems/{id}/
POST   /api/submissions/
GET    /api/submissions/
GET    /api/submissions/{id}/
GET    /api/users/me/
```

`GET /api/submissions/{id}/` 会直接返回 `case_results`，前端提交详情页无需额外请求测试点结果。

## Demo 题目

fixture `demo` 包含一道 `A + B Problem`，测试点文件在：

```text
backend/testdata/problem_1/1.in
backend/testdata/problem_1/1.out
```

默认提交模板已经是这道题的 C++17 解法。

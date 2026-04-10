# AGENTS.md

## Project
This repository is an Online Judge (OJ) system.
Current goal: build a minimal but clean core judging system first, then build a clean frontend on top of it.

## Tech Stack
- Backend: Django + Django REST Framework
- Database: MySQL
- Judge Worker: Python
- Execution Isolation: Docker
- Frontend: Vue 3 + TypeScript + Vue Router + Pinia + Element Plus
- Code Editor: Monaco Editor
- Charts: ECharts

## Current Scope
Implement only the practical core of the OJ platform:
1. submission intake and status management
2. judge scheduling / worker
3. Docker-based compile and run
4. per-testcase judging
5. final verdict aggregation
6. result persistence and backend APIs
7. minimal frontend pages for core OJ flow

## Out of Scope
Do NOT implement:
- ranking
- contest mode
- AI evaluation
- plagiarism detection
- distributed judge cluster
- unnecessary platform features
- microservices
- Celery / Redis / RabbitMQ unless explicitly requested later

## Database Design Direction
The system must follow a traditional OJ schema.

### Problem
- title
- description
- time_limit_ms
- memory_limit_mb
- judge_mode
- basic display fields

### TestCase
- belongs to Problem
- input_path
- output_path
- sort_order
- score
- is_hidden

### Submission
- belongs to user
- belongs to Problem
- language
- source_code
- status
- final_verdict
- total_time_ms
- max_memory_kb
- compile_log
- submitted_at
- judged_at

### SubmissionCaseResult
- belongs to Submission
- belongs to TestCase
- verdict
- time_used_ms
- memory_used_kb
- message

Important:
- testcase data must be stored as files, not large text blobs in DB
- AI analysis must NOT be part of the core judging transaction
- if AI is added later, keep it as a separate optional module or table

## Judging Pipeline
Required flow:
1. create Submission with status=QUEUED
2. worker fetches queued submission
3. worker updates status=JUDGING
4. worker loads Problem and its TestCases
5. worker creates isolated workdir
6. worker writes source code file
7. compile in Docker if needed
8. if compile fails:
   - set Submission.final_verdict = CE
   - save compile_log
   - set status = FINISHED
9. otherwise run each testcase independently in fresh Docker containers
10. collect execution facts:
   - exit code
   - runtime
   - memory
   - stdout
   - stderr
11. determine per-case verdict in this order:
   - TLE
   - MLE
   - OLE
   - RE
   - AC / WA after output comparison
12. save one SubmissionCaseResult per testcase
13. aggregate final verdict into Submission
14. set Submission.status = FINISHED

## Output Comparison
Default strategy:
- normalize line endings
- ignore trailing spaces
- ignore extra empty lines at the end

## Execution Constraints
- separate web layer and judge execution layer
- web layer must not directly execute user code
- each testcase must run in a fresh Docker container
- network must be disabled
- testcase data must be mounted read-only
- workdir must be isolated per submission
- code should be modular and well commented

## Frontend Rules
The frontend should look clean, modern, and practical.
Do not build a flashy homepage-first site.
OJ pages should prioritize clarity, editor usability, and judging feedback.

### Frontend Stack Rules
- use Vue 3 + TypeScript
- use Vue Router
- use Pinia for global state
- use Element Plus for common UI
- use Monaco Editor for code editing pages
- use ECharts only where charts are actually useful
- reuse existing layout and route conventions

### Frontend UX Priorities
- code editor is the visual center on problem-solving pages
- judging result hierarchy must be clear
- use simple and consistent spacing, typography, and colors
- avoid excessive gradients, animations, and decorative sections
- prioritize readability over visual clutter

### Recommended Core Pages
- ProblemListPage
- ProblemDetailPage
- SubmissionListPage
- SubmissionDetailPage
- UserCenterPage
- AdminProblemManagePage (minimal)
- AdminTestCaseManagePage (minimal)

### Problem Detail Page Layout
- left: problem statement
- right: code editor + language selector + submit area
- on smaller screens: switch to vertical layout
- after submission: show judging status and results clearly

### Submission Detail Page
- final verdict
- total time / max memory
- compile log if CE
- per-testcase results table
- optional stderr/stdout summary if useful

## Screenshot / Design-Reference Workflow
When a screenshot or reference image is provided:
- first analyze the layout and component structure
- match spacing, alignment, visual hierarchy, and typography closely
- do not invent a new design system
- keep implementation aligned with this repo’s stack
- prefer reusable components
- after implementation, run the app and visually verify the result

## Browser Verification
For frontend tasks:
- run the dev server
- open the page in a browser
- verify layout visually
- if Playwright or browser automation is available, use it for validation
- iterate until the result is close to the target

## Architecture Suggestion
backend/
  oj/
  judge/
    enums.py
    dto.py
    languages.py
    compare.py
    docker_runner.py
    core.py
    worker.py

frontend/
  src/
    layouts/
    views/
    components/
    stores/
    router/
    api/
    editor/

## Coding Style
- use Python type hints
- use TypeScript on frontend
- add comments for key logic
- avoid giant single-file implementation
- prefer clear and maintainable code
- minimal working version first
- do not over-engineer

## Deliverables
Always include:
1. clear project structure
2. Django models
3. judge core modules
4. worker flow
5. Docker runner for C++ first
6. minimal frontend pages for the OJ flow
7. README with local run steps
8. comments explaining important logic
# OJ Verification Report

Date: 2026-04-11

## Environment

- OS: Windows 11
- Backend: Django + DRF
- Frontend: Vue 3 + Vite
- Judge: Python worker + Docker Desktop
- Validation database: SQLite (`OJ_USE_SQLITE=1`)

Note: the repository defaults to MySQL, but this verification round used SQLite because it is the current local runnable setup.

## Validated Features

### Auth and session/CSRF

- `GET /api/auth/csrf/` returns `200`
- `POST /api/auth/register/` returns `201` and auto-logs in the new user
- `POST /api/auth/login/` returns `200`
- `POST /api/auth/logout/` returns `204`
- `GET /api/users/me/` returns authenticated user info after register/login and anonymous payload after logout
- Authenticated submission creation enforces CSRF:
  - missing CSRF token -> `403`
  - valid CSRF token -> `201`

### Permission boundaries

- Anonymous access to `/api/submissions/` returns `403`
- Submission list returns only the current user's submissions
- Submission detail for another user's submission returns `404`
- Public problem detail returns `200`
- Private problem detail returns `404`
- Problem list only returns public problems

### Problem and sample compatibility

- `ProblemSampleCase(problem, sort_order)` uniqueness is present
- `TestCase(problem, sort_order)` uniqueness is present
- `SubmissionCaseResult(submission, test_case)` uniqueness is present
- When `sample_cases` exist, the frontend is wired to prefer them
- Legacy `sample_input` / `sample_output` remain available as fallback

### File upload behavior

- `ProblemSampleCase` extracts `input_text` / `output_text` from uploaded `.in/.out`
- `ProblemSampleCase` rejects invalid extensions
- `TestCase` admin upload writes files into `TESTCASE_ROOT` and backfills `input_path` / `output_path`
- Missing one of the testcase upload files is rejected when the form is meaningfully filled
- Empty sample files are currently allowed and stored as empty text

### Judge regression

The following scenarios were executed with real Docker-based judging:

| Scenario | Expected | Result |
| --- | --- | --- |
| AC | AC | PASS |
| CE | CE | PASS |
| WA | WA | PASS |
| RE | RE | PASS |

Observed per submission:

- status flow: `QUEUED -> JUDGING -> FINISHED`
- `judged_at` is written
- `compile_log` is written for CE
- case results are written for AC / WA / RE
- CE produces no case rows, which matches current design
- AC updates `is_solved`
- AC updates monthly checkins
- `ProblemSampleCase` does not interfere with judge `TestCase`

### Frontend validation

- `npm run build` passes
- Routing, login gating, solved mark display, sample rendering, and heatmap wiring were reviewed in code
- The project does not currently include a Playwright test setup, so no browser automation run was available in this round

## Issues Found and Fixed

### 1. Uploaded files were left behind after deleting records

Problem:

- Deleting `ProblemSampleCase` left uploaded sample files in `MEDIA_ROOT`
- Deleting `TestCase` left judge data files in `TESTCASE_ROOT`

Fix:

- Added cleanup for deleted sample files
- Added cleanup for deleted testcase files
- Added cleanup for replaced files when paths/names change

Files:

- `backend/oj/models.py`

### 2. Submission validation messages had broken display text

Problem:

- Submission validation copy for unsupported language and non-public problem displayed garbled text in the local console path

Fix:

- Replaced those messages with clear ASCII English messages

Files:

- `backend/oj/serializers.py`

### 3. Submission detail page had a garbled separator character

Problem:

- The submission header line showed a broken separator between problem title and language

Fix:

- Replaced it with `&middot;`

Files:

- `frontend/src/views/SubmissionDetailPage.vue`

## Remaining Risks Not Fully Covered

### Not covered in this round

- MySQL-specific runtime verification
- Visual browser validation with Playwright
- Dedicated TLE / MLE / OLE regression cases
- Multi-worker concurrency / lock contention verification
- Large-file upload stress testing

### Low-risk observations

- Empty `.in/.out` files are allowed today; that is acceptable for now, but should stay an explicit product decision
- The frontend build is healthy, but Monaco/ECharts still produce large chunks

## Manual Final Acceptance Steps

1. Start backend:

   ```powershell
   cd backend
   $env:OJ_USE_SQLITE="1"
   python manage.py runserver 127.0.0.1:8000
   ```

2. Start worker:

   ```powershell
   cd backend
   $env:OJ_USE_SQLITE="1"
   python manage.py judge_worker
   ```

3. Start frontend:

   ```powershell
   cd frontend
   npm run dev
   ```

4. Open `http://127.0.0.1:5173`
5. Register a new account and confirm you land in the user center
6. Open the problem list and confirm solved marks are not shown before AC
7. Open a public problem and confirm:
   - Markdown renders
   - sample cases render
   - unauthenticated users are prompted to log in before submit
8. Submit a correct program and confirm:
   - status panel changes from queued to judging to finished
   - submission detail shows final verdict and case table
   - problem list now shows the solved mark
   - user center heatmap shows one active day in the current month
9. Submit one CE and one WA or RE sample and confirm the detail page matches the verdict

## Demo Script

1. Start backend, worker, and frontend
2. Register a fresh user
3. Show the problem list with no solved checkmarks
4. Open one problem and point out Markdown + sample rendering
5. Submit AC code and show live status changes
6. Open submission detail and show:
   - final verdict
   - total time
   - max memory
   - per-case result
7. Go back to the problem list and show the solved checkmark
8. Open user center and show the AC check-in heatmap
9. Submit a CE example and show compile log
10. Submit a WA or RE example and show the failed case row

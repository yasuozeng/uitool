# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 语言
- 使用中文交流

## 每次说成功的时候都需要附上证明

## 每次写代码都要给每行代码写注释

## 每次写完代码都要写单元测试

## Project Overview

**uiTool1.0** is a lightweight Web UI automation testing platform for QA engineers. It provides a visual script editor to create test cases without coding, and executes them using Playwright across Chrome, Firefox, and Edge browsers.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + Element Plus + Monaco Editor |
| Backend | Python 3.10+ + FastAPI |
| Database | SQLite |
| Automation Engine | Playwright |
| Build Tool | Vite (frontend), uvicorn (backend) |

## Architecture

The project follows a **frontend-backend separation** architecture:

```
Frontend (Vue 3 SPA)
    │ HTTP/REST API + WebSocket
Backend (FastAPI)
    │ SQLAlchemy ORM
SQLite Database
    │
Playwright Engine
    │
Browser Drivers (Chrome/Firefox/Edge)
```

### Frontend Module Structure

```
src/
├── main.ts                 # App entry point
├── router/                 # Vue Router config
├── store/                  # Pinia state management
├── api/                    # HTTP client (Axios)
│   ├── case.ts            # Test case APIs
│   ├── execution.ts       # Execution APIs
│   └── report.ts          # Report APIs
├── components/
│   ├── StepEditor.vue     # Visual step editor
│   ├── StepList.vue       # Draggable step list
│   ├── ExecutionLog.vue   # Real-time log viewer
│   └── ScreenshotViewer.vue # Screenshot preview
└── views/
    ├── CaseManagement.vue # Case management with folder tree
    ├── ScriptEditor.vue   # Script editor
    ├── ExecutionConsole.vue # Execution control
    └── ReportCenter.vue   # Report generation
```

### Backend Module Structure

```
app/
├── main.py                 # FastAPI app entry
├── config.py               # Configuration
├── api/                    # API routes
│   ├── cases.py           # /api/v1/cases
│   ├── executions.py      # /api/v1/executions
│   └── reports.py         # /api/v1/reports
├── models/                 # SQLAlchemy models
│   ├── database.py        # DB connection & session
│   ├── case.py            # TestCase, TestStep models
│   ├── execution.py       # Execution, ExecutionDetail models
│   └── folder.py          # Folder model for tree structure
├── services/               # Business logic layer
│   ├── case_service.py    # Case CRUD operations
│   ├── execution_service.py # Execution orchestration
│   └── report_service.py  # Report generation
├── engines/                # Test execution engine
│   └── playwright_engine.py # Playwright wrapper
└── schemas/                # Pydantic schemas for validation
    ├── case.py
    ├── execution.py
    └── report.py
```

## Core Concepts

### Test Case Structure

- **Folder**: Hierarchical organization (tree structure)
- **TestCase**: Contains name, description, priority (P0-P3), tags
- **TestStep**: Ordered steps with action_type, element_locator, action_params

### Action Types (P0)

| Type | Description | Parameters |
|------|-------------|------------|
| navigate | Page navigation | url |
| click | Click element | - |
| input | Input text | text |
| clear | Clear input | - |
| wait | Wait for element | timeout |
| verify_text | Verify text exists | text |
| verify_element | Verify element exists | - |

### Element Locator Types

| Type | Example |
|------|---------|
| id | #username |
| xpath | //input[@id='username'] |
| css | input#username |
| name | input[name='username'] |
| class | .form-control |

## Database Schema

**Core Tables**:
- `folders` - Directory tree for case organization
- `test_cases` - Test case definitions
- `test_steps` - Test steps linked to cases
- `executions` - Execution records (summary)
- `execution_details` - Per-case execution results with screenshots

See `详细设计/数据库设计.md` for complete schema.

## API Design

**Base URL**: `http://localhost:8000/api/v1`

**Response Format**:
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

**WebSocket**: `ws://localhost:8000/api/v1/ws/executions/{id}` for real-time execution logs.

See `详细设计/接口设计.md` for complete API documentation.

## Development Commands

### Frontend (Vue 3)

```bash
# Install dependencies
npm install

# Dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Backend (FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server (http://localhost:8000)
uvicorn app.main:app --reload

# Run with auto-reload and specific port
uvicorn app.main:app --reload --port 8000

# Initialize database
python -m app.models.database
```

## Execution Flow

1. User clicks execute → `POST /api/v1/executions`
2. Backend creates execution record, returns execution_id
3. Frontend connects WebSocket for real-time updates
4. `execution_service.py` orchestrates the execution
5. `playwright_engine.py` launches browser and executes steps
6. WebSocket pushes: step_start, step_success/step_failed, logs
7. On failure, screenshot is saved to disk
8. Execution completes, results saved to `execution_details`
9. Frontend generates HTML report via `POST /api/v1/reports/html`

## Key Design Decisions

- **No user authentication** (Phase 1) - Single user or small team use
- **SQLite only** - Lightweight, no deployment overhead
- **HTML reports only** - No PDF/Excel generation in Phase 1
- **No scheduled execution** - Manual or external cron trigger only
- **Element locator strings stored as-is** - No element library management

## Document References

| Document | Description |
|----------|-------------|
| `需求/核心需求文档.md` | Product requirements (PRD) |
| `需求/用户故事.md` | User scenarios and journeys |
| `需求/功能优先级矩阵.md` | MoSCoW priority analysis |
| `详细设计/系统架构设计.md` | Technical architecture |
| `详细设计/数据库设计.md` | Database schema & SQL scripts |
| `详细设计/接口设计.md` | RESTful API & WebSocket specs |

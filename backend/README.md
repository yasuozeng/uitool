# uiTool1.0 执行引擎

## 简介

这是 uiTool1.0 UI自动化测试平台的执行引擎模块，基于 Playwright 实现，支持跨浏览器自动化测试。

## 功能特性

- ✅ 支持 Chrome、Firefox、Edge (WebKit) 三大主流浏览器
- ✅ 支持有头/无头模式
- ✅ 支持 7 种基础操作类型
- ✅ 支持 5 种元素定位方式
- ✅ 失败自动截图
- ✅ 异步执行，性能优异

## 支持的操作类型

| 操作类型 | 说明 | 参数 |
|---------|------|------|
| navigate | 页面跳转 | url |
| click | 点击元素 | - |
| input | 输入文本 | text |
| clear | 清除内容 | - |
| wait | 等待元素可见 | timeout (可选) |
| verify_text | 验证文本存在 | text |
| verify_element | 验证元素存在 | - |

## 支持的元素定位

| 定位类型 | 说明 | 示例 |
|---------|------|------|
| id | ID定位 | #username |
| xpath | XPath定位 | //input[@id='username'] |
| css | CSS Selector | input#username |
| name | Name属性 | input[name='username'] |
| class | Class名称 | .form-control |

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器驱动

```bash
# 安装所有浏览器驱动
playwright install

# 或只安装 Chromium
playwright install chromium

# 安装 Firefox
playwright install firefox

# 安装 WebKit (Safari)
playwright install webkit
```

### 3. 运行测试

```bash
cd backend
python -m app.engines.playwright_engine
```

## 使用示例

### 示例 1: 简单的百度搜索

```python
import asyncio
from app.engines.playwright_engine import PlaywrightEngine

async def test_baidu_search():
    engine = PlaywrightEngine(browser_type="chromium", headless=False)

    try:
        await engine.start_browser()

        test_case = {
            "id": 1,
            "name": "百度搜索测试",
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://www.baidu.com"}
                },
                {
                    "step_order": 2,
                    "action_type": "input",
                    "element_locator": "#kw",
                    "locator_type": "css",
                    "action_params": {"text": "Playwright自动化测试"}
                },
                {
                    "step_order": 3,
                    "action_type": "click",
                    "element_locator": "#su",
                    "locator_type": "css"
                },
                {
                    "step_order": 4,
                    "action_type": "wait",
                    "element_locator": "#content_left",
                    "locator_type": "css",
                    "action_params": {"timeout": 5000}
                }
            ]
        }

        result = await engine.execute_case(test_case)
        print(f"执行结果: {result}")

    finally:
        await engine.close_browser()

asyncio.run(test_baidu_search())
```

### 示例 2: 登录测试

```python
async def test_login():
    engine = PlaywrightEngine(browser_type="chromium", headless=False)

    try:
        await engine.start_browser()

        test_case = {
            "id": 2,
            "name": "登录测试",
            "steps": [
                {
                    "step_order": 1,
                    "action_type": "navigate",
                    "action_params": {"url": "https://example.com/login"}
                },
                {
                    "step_order": 2,
                    "action_type": "input",
                    "element_locator": "#username",
                    "locator_type": "css",
                    "action_params": {"text": "testuser"}
                },
                {
                    "step_order": 3,
                    "action_type": "input",
                    "element_locator": "#password",
                    "locator_type": "css",
                    "action_params": {"text": "password123"}
                },
                {
                    "step_order": 4,
                    "action_type": "click",
                    "element_locator": "button[type='submit']",
                    "locator_type": "css"
                },
                {
                    "step_order": 5,
                    "action_type": "verify_text",
                    "action_params": {"text": "欢迎"}
                }
            ]
        }

        result = await engine.execute_case(test_case)
        print(f"成功: {result['success']}, 成功步骤: {result['success_steps']}, 失败步骤: {result['failed_steps']}")

    finally:
        await engine.close_browser()

asyncio.run(test_login())
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py           # 应用包初始化
│   ├── config.py             # 配置文件
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py       # 数据库连接
│   │   ├── case.py           # 用例模型
│   │   └── execution.py      # 执行记录模型
│   ├── engines/
│   │   ├── __init__.py
│   │   └── playwright_engine.py  # Playwright执行引擎
│   └── utils/
│       └── __init__.py
├── data/                     # 数据存储目录
│   └── uitool.db            # SQLite数据库
├── screenshots/              # 截图存储目录
├── reports/                  # 报告存储目录
├── requirements.txt          # Python依赖
└── README.md                 # 本文件
```

## 配置说明

配置文件位于 `app/config.py`，主要配置项：

- `DATABASE_URL`: 数据库连接地址
- `DEFAULT_BROWSER_TYPE`: 默认浏览器类型 (chromium/firefox/webkit)
- `DEFAULT_HEADLESS`: 默认无头模式
- `DEFAULT_WINDOW_SIZE`: 默认窗口大小
- `DEFAULT_STEP_TIMEOUT`: 默认步骤超时时间（毫秒）
- `SCREENSHOTS_DIR`: 截图保存目录
- `REPORTS_DIR`: 报告保存目录

## 执行结果格式

```python
{
    "success": True/False,           # 整体是否成功
    "total_steps": 5,                # 总步骤数
    "success_steps": 4,              # 成功步骤数
    "failed_steps": 1,               # 失败步骤数
    "step_results": [                # 每步执行结果
        {
            "step_order": 1,
            "action_type": "navigate",
            "success": True,
            "message": "成功跳转到: https://www.baidu.com"
        },
        {
            "step_order": 2,
            "action_type": "click",
            "success": False,
            "message": "点击元素失败",
            "error": "Element not found",
            "screenshot": "/screenshots/error_xxx.png"  # 失败时的截图
        }
    ]
}
```

## 下一步

执行引擎完成后，还需要开发：

1. **FastAPI 接口层**: 提供 REST API 和 WebSocket
2. **前端界面**: Vue 3 可视化编辑和执行控制台
3. **报告生成**: HTML 测试报告导出

## 技术栈

- Python 3.10+
- Playwright 1.40+
- SQLAlchemy 2.0+ (异步ORM)
- FastAPI (待实现)
- Vue 3 + Element Plus (待实现)

## 许可证

MIT License

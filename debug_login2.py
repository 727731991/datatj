from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []
    all_requests = []
    all_responses = []

    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("request", lambda req: all_requests.append(f"REQUEST: {req.method} {req.url}"))
    page.on("response", lambda res: all_responses.append(f"RESPONSE: {res.status} {res.url}"))

    print("=== 1. 访问登录页 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # 清空之前的请求
    all_requests.clear()
    all_responses.clear()

    print("\n=== 2. 填写登录表单 ===")
    page.wait_for_selector('input[placeholder*="用户名"]', timeout=5000)
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder="密码"]', 'admin123')
    time.sleep(0.5)

    # 截图看表单状态
    page.screenshot(path='/tmp/preview/form_state.png')

    print("\n=== 3. 点击登录按钮 ===")
    # 找到登录按钮
    buttons = page.query_selector_all('button')
    print(f"找到 {len(buttons)} 个按钮:")
    for i, btn in enumerate(buttons):
        text = btn.inner_text()
        print(f"  按钮 {i}: '{text}'")

    # 点击主登录按钮
    login_btn = page.locator('button.login-btn')
    print(f"\n点击 .login-btn 按钮")
    login_btn.click()
    time.sleep(5)

    print(f"\n登录后 URL: {page.url}")
    page.screenshot(path='/tmp/preview/after_login2.png')

    # 检查 localStorage
    local_storage = page.evaluate("() => JSON.stringify(localStorage)")
    print(f"\nlocalStorage: {local_storage}")

    # 检查页面上的错误消息
    messages = page.query_selector_all('.el-message')
    for msg in messages:
        print(f"消息: {msg.inner_text()}")

    print("\n=== 所有请求 ===")
    for req in all_requests:
        if '/api/' in req:
            print(req)

    print("\n=== 所有响应 ===")
    for res in all_responses:
        if '/api/' in res:
            print(res)

    print("\n=== 控制台错误 ===")
    for log in console_logs:
        if 'error' in log.lower() or 'warn' in log.lower():
            print(log)

    browser.close()

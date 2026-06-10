from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    print("=== 1. 访问登录页 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("\n=== 2. 填写并提交登录表单 ===")
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder="密码"]', 'admin123')
    page.locator('button.login-btn').click()
    time.sleep(5)

    # 检查最终状态
    print(f"\n最终 URL: {page.url}")
    token = page.evaluate("() => localStorage.getItem('access_token')")
    user = page.evaluate("() => localStorage.getItem('current_user')")
    print(f"localStorage token: {token[:80] if token else 'None'}...")
    print(f"localStorage user: {user}")

    # 打印所有错误和控制台消息
    print("\n=== 相关控制台消息 ===")
    for log in console_logs:
        if 'API' in log or 'token' in log.lower() or '登录' in log or 'error' in log.lower():
            print(log)

    browser.close()

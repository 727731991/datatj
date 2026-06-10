from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []
    network_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[PAGE_ERROR] {err}"))
    page.on("response", lambda res: network_logs.append(f"{res.status} {res.url}"))

    print("=== 1. 访问登录页 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    print(f"URL: {page.url}")

    print("\n=== 2. 填写登录表单 ===")
    # 找到用户名输入框
    username_input = page.locator('input[placeholder*="用户名"]').first
    username_input.fill('admin')
    time.sleep(0.5)

    # 找到密码输入框
    password_input = page.locator('input[type="password"]').first
    password_input.fill('admin123')
    time.sleep(0.5)

    page.screenshot(path='/tmp/preview/login_filled2.png')

    print("\n=== 3. 点击登录按钮 ===")
    login_btn = page.locator('button:has-text("登录")').first
    login_btn.click()
    time.sleep(3)

    print(f"登录后 URL: {page.url}")
    page.screenshot(path='/tmp/preview/after_login.png')

    # 检查 localStorage
    local_storage = page.evaluate("() => localStorage.getItem('access_token')")
    print(f"\nlocalStorage token: {local_storage[:50] if local_storage else 'None'}...")

    print("\n=== 控制台日志 ===")
    for log in console_logs:
        print(log)
    console_logs.clear()

    print("\n=== API 请求 ===")
    for log in network_logs[-10:]:
        print(log)

    browser.close()

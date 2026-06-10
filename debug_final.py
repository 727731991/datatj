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
    time.sleep(1)

    print("\n=== 2. 登录 ===")
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder="密码"]', 'admin123')
    page.locator('button.login-btn').click()

    # 等待导航完成
    page.wait_for_url('**/')
    time.sleep(2)

    print(f"\n最终 URL: {page.url}")

    # 检查 Dashboard 是否加载
    page.screenshot(path='/tmp/preview/dashboard.png')

    # 检查 token
    token = page.evaluate("() => localStorage.getItem('access_token')")
    print(f"Token: {token[:50] if token else 'None'}...")

    print("\n=== 控制台消息 ===")
    for log in console_logs:
        if 'error' in log.lower():
            print(log)

    browser.close()

from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []
    network_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[PAGE_ERROR] {err}"))
    page.on("response", lambda res: network_logs.append(f"{res.status} {res.url}") if res.status >= 400 else None)

    print("=== 1. 访问首页 ===")
    page.goto('http://localhost:5173/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)
    print(f"URL: {page.url}")

    print("\n=== 控制台输出 ===")
    for log in console_logs:
        print(log)
    console_logs.clear()

    print("\n=== 错误请求 ===")
    for log in network_logs:
        print(log)
    network_logs.clear()

    print("\n=== 2. 尝试注册 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # 点击注册
    register_link = page.get_by_text("立即注册")
    register_link.click()
    time.sleep(1)
    page.screenshot(path='/tmp/preview/register_dialog.png')

    # 填写注册
    page.fill('input[placeholder*="用户名"]', 'admin')
    time.sleep(0.5)
    inputs = page.query_selector_all('input[type="password"]')
    inputs[-1].fill('admin123')
    time.sleep(0.5)
    page.screenshot(path='/tmp/preview/register_filled.png')

    # 点击注册按钮
    register_btn = page.query_selector('button:has-text("注册")')
    if register_btn:
        register_btn.click()
    time.sleep(3)
    page.screenshot(path='/tmp/preview/register_result.png')

    print("\n=== 注册后的控制台输出 ===")
    for log in console_logs:
        print(log)
    console_logs.clear()

    print("\n=== 错误请求 ===")
    for log in network_logs:
        print(log)

    browser.close()

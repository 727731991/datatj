from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_logs.append(f"[pageerror] {err}"))

    print("访问首页 / ...")
    page.goto('http://localhost:5173/')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print(f"首页 URL: {page.url}")
    print(f"首页标题: {page.title()}")
    page.screenshot(path='/tmp/preview/home.png', full_page=False)

    print("\n--- 控制台日志 ---")
    for log in console_logs:
        print(log)

    console_logs.clear()

    print("\n访问 /login ...")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print(f"登录页 URL: {page.url}")
    print(f"登录页标题: {page.title()}")
    page.screenshot(path='/tmp/preview/login2.png', full_page=False)

    print("\n--- 控制台日志 ---")
    for log in console_logs:
        print(log)

    # 检查页面是否有可见文字
    body_text = page.inner_text('body')
    print(f"\n页面内容 (前200字): {body_text[:200] if body_text else '(空)'}")

    browser.close()

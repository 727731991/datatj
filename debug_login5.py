from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    requests = []
    responses = []

    page.on("request", lambda req: requests.append(f"{req.method} {req.url}"))
    page.on("response", lambda res: responses.append(f"{res.status} {res.url}"))

    print("=== 1. 访问登录页 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    print("\n=== 2. 登录 ===")
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder="密码"]', 'admin123')
    page.locator('button.login-btn').click()

    # 等待登录和 Dashboard 加载完成
    time.sleep(5)

    print(f"\n最终 URL: {page.url}")

    # 打印所有 API 请求
    print("\n=== API 请求 ===")
    for req in requests:
        if '/api/' in req:
            print(req)

    # 打印所有 API 响应
    print("\n=== API 响应 ===")
    for res in responses:
        if '/api/' in res:
            print(res)

    # 检查是否有 Authorization header
    print("\n=== 检查 Dashboard 请求的 Authorization header ===")
    for req in requests:
        if '/api/data/' in req or '/api/reports/' in req:
            print(f"Request: {req}")

    browser.close()

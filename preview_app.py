from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    # 访问登录页面
    print("正在访问登录页面...")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')

    # 截图保存
    os.makedirs('/tmp/preview', exist_ok=True)
    page.screenshot(path='/tmp/preview/login.png', full_page=False)
    print("登录页面截图已保存: /tmp/preview/login.png")

    # 等待页面加载完成
    page.wait_for_timeout(2000)

    # 检查页面内容
    print("\n页面标题:", page.title())
    print("当前URL:", page.url)

    # 截图完整页面
    page.screenshot(path='/tmp/preview/login_full.png', full_page=True)
    print("完整页面截图已保存: /tmp/preview/login_full.png")

    browser.close()
    print("\n预览完成!")

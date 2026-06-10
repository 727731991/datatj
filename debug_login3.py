from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    console_logs = []

    def log_console(msg):
        console_logs.append(f"[{msg.type}] {msg.text}")

    page.on("console", log_console)

    print("=== 1. 访问登录页 ===")
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')
    time.sleep(1)

    # 注入日志来调试登录
    page.evaluate("""
        () => {
            window.originalSetToken = window.setToken;
            const original_authAPI = window.authAPI;

            // Hook the login API response
            const origPost = window.axios.post.bind(window.axios);
            window.axios.post = async function(...args) {
                const result = await origPost(...args);
                console.log('API Response:', JSON.stringify(result.data));
                return result;
            };
        }
    """)

    print("\n=== 2. 填写并提交登录表单 ===")
    page.fill('input[placeholder*="用户名"]', 'admin')
    page.fill('input[placeholder="密码"]', 'admin123')

    # 监听登录后的跳转
    page.locator('button.login-btn').click()

    # 等待并捕获所有控制台输出
    time.sleep(3)

    # 检查 localStorage
    token = page.evaluate("() => localStorage.getItem('access_token')")
    user = page.evaluate("() => localStorage.getItem('current_user')")
    print(f"\ntoken: {token[:50] if token else 'None'}...")
    print(f"user: {user}")

    # 打印所有控制台消息
    print("\n=== 控制台消息 ===")
    for log in console_logs:
        if 'API' in log or 'token' in log.lower() or '登录' in log:
            print(log)

    browser.close()

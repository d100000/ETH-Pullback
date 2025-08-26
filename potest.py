
import requests

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 测试访问一个公共网站
try:
    response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
    print("代理测试成功，状态码:", response.status_code)
except Exception as e:
    print("代理测试失败:", e)
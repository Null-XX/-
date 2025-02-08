import tkinter as tk
from tkinter import messagebox
import requests
from concurrent.futures import ThreadPoolExecutor
import re


# 解析HTTP数据包
def parse_http_packet(packet):
    # 提取请求行和请求头
    request_line, headers_body = packet.split("\n", 1)
    headers, body = headers_body.split("\n\n", 1) if "\n\n" in headers_body else (headers_body, "")

    # 提取方法和路径
    method, path, _ = request_line.split()

    # 提取主机名
    headers_dict = {}
    for line in headers.split("\n"):
        key, value = line.split(":", 1)
        headers_dict[key.strip()] = value.strip()

    url = f"https://{headers_dict['Host']}{path}"
    headers_dict.pop('Host', None)

    return method, url, headers_dict, body


# 定义发送请求的函数
def send_request(method, url, headers, data):
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, data=data)
        elif method == "GET":
            # 如果是GET方法，使用params传递查询字符串
            response = requests.get(url, headers=headers, params=data)
        else:
            return f"不支持的请求方法: {method}"

        if response.status_code == 200:
            return f"成功响应: {response.text}"
        else:
            return f"请求失败，状态码: {response.status_code}"
    except Exception as e:
        return f"请求时出错: {e}"


# 定义并发执行请求的函数
def send_concurrent_requests():
    packet_a = data_a_text.get("1.0", "end-1c")  # 获取数据包A内容
    packet_b = data_b_text.get("1.0", "end-1c")  # 获取数据包B内容

    # 检查数据包的有效性
    if not packet_a or not packet_b:
        messagebox.showerror("错误", "请提供有效的数据包内容")
        return

    try:
        method_a, url_a, headers_a, body_a = parse_http_packet(packet_a)
        method_b, url_b, headers_b, body_b = parse_http_packet(packet_b)
    except Exception as e:
        messagebox.showerror("错误", f"解析数据包时出错: {e}")
        return

    # 使用线程池并发执行两个请求
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(send_request, method_a, url_a, headers_a, body_a)
        future_b = executor.submit(send_request, method_b, url_b, headers_b, body_b)

        # 获取并显示请求结果
        result_a = future_a.result()
        result_b = future_b.result()

        # 将结果显示到文本框中
        result_text.delete("1.0", "end")
        result_text.insert("1.0", f"数据包A响应:\n{result_a}\n\n数据包B响应:\n{result_b}")


# 创建主窗口
root = tk.Tk()
root.title("条件竞争测试工具")

# 设置窗口大小
root.geometry("600x950")

# 数据包A输入框
tk.Label(root, text="请输入数据包A:").pack(pady=10)
data_a_text = tk.Text(root, height=15, width=70)
data_a_text.pack(pady=5)

# 数据包B输入框
tk.Label(root, text="请输入数据包B:").pack(pady=10)
data_b_text = tk.Text(root, height=15, width=70)
data_b_text.pack(pady=5)

# 执行按钮
send_button = tk.Button(root, text="发送请求", command=send_concurrent_requests)
send_button.pack(pady=20)

# 显示结果的文本框
tk.Label(root, text="并发响应结果:").pack(pady=10)
result_text = tk.Text(root, height=20, width=70)
result_text.pack(pady=5)

# 启动主事件循环
root.mainloop()

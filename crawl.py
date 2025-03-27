import requests
import json
import time


def start_crawl(url, api_url, api_key, options=None, auto_check=True, max_retries=9999, interval=5):
    """启动网站爬取任务并自动检查状态
    
    Args:
        url: 要爬取的URL
        api_url: API基础URL
        api_key: API密钥
        options: 可选参数
        auto_check: 是否自动检查状态
        max_retries: 最大重试次数(默认9999≈13.8小时)
        interval: 检查间隔(秒)
    """
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    print(f"[DEBUG] 原始options参数: {options}")
    data = {
        "url": url,
        "limit": options.get("limit", 100) if options else 100,
        "scrapeOptions": {
            "formats": ["markdown", "html"],
            "onlyMainContent": True
        },
    }
    if options:
        # 过滤掉不被API识别的字段
        filtered_options = {k: v for k, v in options.items()
                          if k in ["limit", "scrapeOptions"]}
        data.update(filtered_options)

    try:
        # 启动爬取任务
        response = requests.post(f"{api_url}/v1/crawl", headers=headers, json=data)
        if response.status_code != 200:
            print(f"API请求失败，状态码: {response.status_code}, 响应: {response.text}")
            return None
        
        result = response.json()
        if not auto_check or not result.get("id"):
            return result
            
        # 自动检查任务状态
        job_id = result["id"]
        for _ in range(max_retries):
            status_response = check_crawl_status(job_id, api_url, api_key)
            if status_response and status_response.get("status") == "completed":
                return status_response.get("data")
            time.sleep(interval)
            
        print(f"爬取任务超时，未能在{max_retries*interval}秒内完成")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"API请求异常: {str(e)}")
        return None


def check_crawl_status(job_id, api_url, api_key):
    """检查爬取任务状态"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.get(f"{api_url}/v1/crawl/status/{job_id}", headers=headers)
    return response.json() if response.status_code == 200 else None


def parse_crawl_results(results):
    """解析爬取结果，返回包含完整markdown的内容"""
    if not isinstance(results, list):
        return []

    parsed = []
    for page in results:
        if isinstance(page, str):
            try:
                page = json.loads(page)
            except Exception:
                continue

        content = page.get("content", page)

        if not isinstance(content, dict):
            content = {}

        parsed.append(
            {
                "url": content.get("url", ""),
                "title": content.get("title")
                or content.get("metadata", {}).get("title", "无标题"),
                "markdown": content.get("markdown", ""),
                "html": content.get("html", ""),
                "metadata": content.get("metadata", {}),
            }
        )
    return parsed


def save_markdown(results, output_dir="output"):
    """将markdown内容保存到文件"""
    import os
    import hashlib

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    saved_files = []
    for result in results:
        if not result.get("markdown"):
            continue

        # 使用URL生成文件名
        url_hash = hashlib.md5(result["url"].encode()).hexdigest()
        filename = f"{output_dir}/{url_hash}.md"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(result["markdown"])
            saved_files.append(filename)

    return saved_files


def copy_markdown(results):
    """返回可以复制到剪贴板的markdown内容"""
    import pyperclip

    markdowns = []
    for result in results:
        if result.get("markdown"):
            markdowns.append(f"# {result['title']}\n\n{result['markdown']}")

    combined = "\n\n---\n\n".join(markdowns)
    try:
        pyperclip.copy(combined)
        return True
    except Exception:
        return False

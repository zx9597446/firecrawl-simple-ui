import requests
import time
import json

def start_crawl(url, api_url, api_key, options=None):
    """启动网站爬取任务"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "url": url,
        "limit": options.get("limit", 10) if options else 10  # 默认limit为10
    }
    if options:
        data.update(options)
    
    response = requests.post(
        f"{api_url}/v0/crawl",
        headers=headers,
        json=data
    )
    return response.json() if response.status_code == 200 else None

def check_crawl_status(job_id, api_url, api_key):
    """检查爬取任务状态"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{api_url}/v0/crawl/status/{job_id}",
        headers=headers
    )
    return response.json() if response.status_code == 200 else None

def parse_crawl_results(results):
    """解析爬取结果"""
    if not isinstance(results, list):
        return []
    
    parsed = []
    for page in results:
        if isinstance(page, str):
            try:
                page = json.loads(page)
            except:
                continue
        
        content = page.get('content', page)
        
        if not isinstance(content, dict):
            content = {}
            
        parsed.append({
            "url": content.get('url', ''),
            "title": content.get('title') or content.get('metadata', {}).get('title', '无标题'),
            "word_count": len(content.get('markdown', ''))
        })
    return parsed
import json

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

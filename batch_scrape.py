import os
import requests
import streamlit as st
from dotenv import load_dotenv
import json
from time import sleep

# 加载环境变量
load_dotenv()
API_URL = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1")
API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 初始化session状态
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'results' not in st.session_state:
    st.session_state.results = None

def submit_batch_job(urls):
    """提交批量抓取任务"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "urls": urls,
        "formats": ["markdown"],
        "onlyMainContent": True,
        "blockAds": True
    }
    
    try:
        response = requests.post(
            f"{API_URL}/batch/scrape",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"提交失败: {str(e)}")
        return None

def get_job_results(job_id):
    """获取任务结果"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    try:
        response = requests.get(
            f"{API_URL}/batch/scrape/{job_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"获取结果失败: {str(e)}")
        return None

def poll_job_status(job_id):
    """轮询任务状态直到完成"""
    placeholder = st.empty()
    while True:
        results = get_job_results(job_id)
        if not results:
            return None
            
        if results["status"] == "completed":
            placeholder.empty()
            return results
            
        # 更新进度
        progress = results["completed"] / results["total"]
        placeholder.progress(progress, text=f"处理中... 完成 {results['completed']}/{results['total']}")
        sleep(2)  # 每2秒检查一次

# Streamlit界面
st.title("🔥 Firecrawl 批量抓取工具")

# URL输入框
urls = st.text_area(
    "输入要抓取的URL（每行一个）",
    height=150,
    help="每个URL单独一行"
).split('\n')

# 提交按钮
if st.button("开始抓取") and urls:
    with st.spinner("提交任务中..."):
        result = submit_batch_job([u.strip() for u in urls if u.strip()])
        
    if result and result.get("success"):
        st.session_state.job_id = result["id"]
        st.success(f"任务已提交！作业ID: {result['id']}")
        if result.get("invalidURLs"):
            st.warning(f"无效URL: {', '.join(result['invalidURLs'])}")
    else:
        st.error("任务提交失败")

# 结果显示和下载
if st.session_state.job_id:
    st.divider()
    st.subheader("抓取结果")
    
    if st.button("检查进度") or st.session_state.get('auto_poll', False):
        st.session_state.auto_poll = True
        with st.spinner("获取结果中..."):
            results = poll_job_status(st.session_state.job_id)
            
        if results:
            st.session_state.results = results
            st.success("抓取完成！")
            
            # 合并所有markdown内容
            combined_md = "\n\n---\n\n".join(
                f"# {item['metadata']['sourceURL']}\n\n{item['markdown']}" 
                for item in results["data"]
            )
            
            # 下载合并的Markdown按钮
            st.download_button(
                label="下载全部Markdown",
                data=combined_md,
                file_name="combined_results.md",
                key="dl_all"
            )
            
            # 显示并下载单个Markdown
            for idx, item in enumerate(results["data"]):
                with st.expander(f"结果 {idx+1}: {item['metadata']['sourceURL']}"):
                    st.code(item["markdown"], language="markdown")
                    
                    # 下载按钮
                    st.download_button(
                        label="下载此Markdown",
                        data=item["markdown"],
                        file_name=f"content_{idx+1}.md",
                        key=f"dl_{idx}"
                    )

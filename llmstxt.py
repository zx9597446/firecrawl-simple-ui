import os
import requests
import streamlit as st
from dotenv import load_dotenv
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

def submit_llmstxt_job(url, options):
    """提交LLMs.txt生成任务"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "maxUrls": min(options["max_urls"], 100),  # 限制最大100个URL
        "showFullText": options["show_full_text"],
    }
    
    try:
        with st.spinner("正在提交任务..."):
            response = requests.post(
                f"{API_URL}/llmstxt",
                headers=headers,
                json=payload,
                timeout=30  # 30秒超时
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get('success'):
                st.error(f"API返回错误: {result.get('message', '未知错误')}")
                return None
            return result
    except requests.exceptions.Timeout:
        st.error("请求超时，请检查网络连接后重试")
        return None
    except Exception as e:
        st.error(f"提交失败: {str(e)}")
        return None

def get_job_results(job_id):
    """获取任务结果"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }
    try:
        response = requests.get(
            f"{API_URL}/llmstxt/{job_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"获取结果失败: {str(e)}")
        return None

# Streamlit界面
st.title("📄 LLMs.txt 生成工具")

# 配置选项
with st.expander("生成选项"):
    col1, col2 = st.columns(2)
    with col1:
        max_urls = st.number_input("最大URL数量", min_value=1, max_value=100, value=100,
                                 help="建议值1-100，过大可能导致处理时间过长")
    with col2:
        show_full_text = st.checkbox("显示完整文本", value=True)

# URL输入框
url = st.text_input(
    "输入目标网站URL",
    placeholder="https://example.com",
    help="输入要生成LLMs.txt的网站URL"
)

# 提交按钮
if st.button("开始生成") and url:
    options = {
        "max_urls": max_urls,
        "show_full_text": show_full_text,
    }
    
    with st.spinner("提交任务中..."):
        result = submit_llmstxt_job(url.strip(), options)
        
    if not result:
        st.error("任务提交失败: 无响应")
    elif result.get("error"):
        st.error(f"任务提交失败: {result['error']}")
    elif not result.get("success"):
        st.error(f"任务提交失败: {result.get('message', '未知错误')}")
    else:
        job_id = result.get("jobId")
        if job_id:
            st.session_state.job_id = job_id
            st.success(f"任务已提交 (ID: {job_id})")
            # Trigger immediate status check
            st.rerun()
        else:
            # Handle immediate completion case
            if result.get("data"):
                st.session_state.results = result
                st.success("处理完成！")

# 轮询结果
if st.session_state.job_id:
    with st.spinner("等待处理完成..."):
        try:
            result = get_job_results(st.session_state.job_id)
            if not result:
                st.error("无法获取任务状态")
                st.session_state.job_id = None
                st.rerun()
            
            status = result.get("status")
            
            if status == "completed":
                st.session_state.results = result
                st.session_state.job_id = None
                st.success("处理完成！")
                if result.get('data', {}).get('processedUrls'):
                    st.info(f"已处理URL数量: {len(result['data']['processedUrls'])}")
                st.rerun()  # 立即刷新显示结果
            
            elif status == "processing":
                st.warning(f"任务处理中... (任务ID: {st.session_state.job_id})")
                if result.get('data', {}).get('llmstxt'):
                    with st.expander("查看当前进度"):
                        st.code(result['data']['llmstxt'], language="markdown")
                # 5秒后自动刷新
                sleep(5)
                st.rerun()
            
            elif status == "failed":
                st.error(f"处理失败: {result.get('message', '未知错误')}")
                st.session_state.job_id = None
            
            else:
                st.warning(f"未知状态: {status}")
                sleep(5)
                st.rerun()
                
        except Exception as e:
            st.error(f"轮询出错: {str(e)}")
            st.session_state.job_id = None

# 结果显示和下载
if st.session_state.results:
    st.divider()
    status = st.session_state.results.get("status")
    data = st.session_state.results.get("data", {})
    
    if status == "processing":
        st.warning("任务仍在处理中，部分结果如下:")
        if data.get("llmstxt"):
            st.subheader("当前LLMs.txt")
            st.code(data["llmstxt"], language="markdown")
        st.button("刷新状态", key="refresh_status")
    
    elif status == "completed":
        st.success("处理完成！")
        if data.get("llmstxt"):
            st.subheader("LLMs.txt")
            st.code(data["llmstxt"], language="markdown")
            st.download_button(
                label="下载LLMs.txt",
                data=data["llmstxt"],
                file_name="llms.txt",
                mime="text/plain"
            )
        
        if data.get("llmsfulltxt"):
            st.subheader("完整版LLMs.txt")
            st.code(data["llmsfulltxt"], language="markdown")
            st.download_button(
                label="下载完整版LLMs.txt",
                data=data["llmsfulltxt"],
                file_name="llms-full.txt",
                mime="text/plain"
            )

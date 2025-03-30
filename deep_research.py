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

def submit_deep_research(query, options):
    """提交深度研究任务"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "maxDepth": options["max_depth"],
        "timeLimit": options["time_limit"],
        "maxUrls": options["max_urls"]
    }

    try:
        response = requests.post(
            f"{API_URL}/deep-research",
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
            f"{API_URL}/deep-research/{job_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"获取结果失败: {str(e)}")
        return None

def poll_job_status(job_id):
    """轮询任务状态直到完成或失败"""
    placeholder = st.empty()
    max_attempts = 60  # 最大尝试次数 (约10分钟，每10秒检查一次)
    attempts = 0
    
    while attempts < max_attempts:
        results = get_job_results(job_id)
        if not results:
            placeholder.error("无法获取任务状态")
            return None
            
        status = results.get("status")
        if status == "completed":
            placeholder.empty()
            return results
        elif status == "failed":
            placeholder.error(f"研究任务失败: {results.get('message', '未知错误')}")
            return None
            
        # 显示当前活动状态
        current_activity = results.get("data", {}).get("activities", [{}])[-1]
        status_text = f"处理中...\n当前深度: {results.get('currentDepth', 0)}/{results.get('maxDepth', 0)}\n"
        status_text += f"活动: {current_activity.get('type', 'unknown')} - {current_activity.get('message', '')}"
        status_text += f"\n尝试 {attempts+1}/{max_attempts}"
        
        placeholder.text(status_text)
        sleep(10)  # 每10秒检查一次
        attempts += 1
        
    placeholder.error("研究任务超时")
    return None

# Streamlit界面
st.title("🔍 Firecrawl 深度研究工具")

# 研究查询输入
query = st.text_area(
    "输入研究问题",
    height=100,
    placeholder="例如: What are the latest developments in quantum computing?",
    help="输入您想要研究的主题或问题"
)

# 配置选项
with st.expander("研究参数"):
    col1, col2 = st.columns(2)
    with col1:
        max_depth = st.number_input("最大深度", min_value=1, max_value=10, value=7)
        max_urls = st.number_input("最大URL数量", min_value=1, max_value=1000, value=20)
    with col2:
        time_limit = st.number_input("时间限制(秒)", min_value=30, max_value=300, value=270)

# 提交按钮
if st.button("开始研究") and query:
    options = {
        "max_depth": max_depth,
        "time_limit": time_limit,
        "max_urls": max_urls
    }
    
    with st.spinner("提交任务中..."):
        result = submit_deep_research(query.strip(), options)
        
    if not result:
        st.error("任务提交失败: 无响应")
    elif result.get("error"):
        st.error(f"任务提交失败: {result['error']}")
    elif not result.get("success"):
        st.error(f"任务提交失败: {result.get('message', '未知错误')}")
    elif not result.get("id"):
        st.error("任务提交失败: 未返回作业ID")
        
    st.session_state.job_id = result["id"]
    st.success(f"研究任务已提交！作业ID: {result['id']}")

# 结果显示
if st.session_state.job_id:
    st.divider()
    st.subheader("研究结果")
    
    with st.spinner("获取结果中..."):
        results = poll_job_status(st.session_state.job_id)
            
        if results:
            st.session_state.results = results
            st.success("研究完成！")
            
            if not results.get("data"):
                st.warning("没有获取到任何结果数据")
                
            # 显示最终分析
            final_analysis = results["data"].get("finalAnalysis")
            if final_analysis:
                st.subheader("最终分析")
                st.markdown(final_analysis)
                
                # 下载按钮
                st.download_button(
                    label="下载分析结果",
                    data=final_analysis,
                    file_name="research_analysis.md",
                    key="dl_analysis"
                )
            
            # 显示来源
            sources = results["data"].get("sources", [])
            if sources:
                st.subheader("研究来源")
                for source in sources:
                    with st.expander(f"{source.get('title', '无标题')}"):
                        st.markdown(f"**URL**: {source.get('url', '未知')}")
                        st.markdown(f"**描述**: {source.get('description', '无描述')}")

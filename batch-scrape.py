import os
import streamlit as st
from dotenv import load_dotenv
import requests
import json
import pyperclip

# 加载环境变量
load_dotenv()
API_URL = os.getenv('FIRECRAWL_API_URL')
API_KEY = os.getenv('FIRECRAWL_API_KEY')

# 设置页面配置
st.set_page_config(page_title="Firecrawl工具集", layout="wide")
st.title("Firecrawl工具集")

# 定义map_url函数
def map_url(url, search=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"url": url}
    if search:
        data["search"] = search
    
    response = requests.post(
        f"{API_URL}/v1/map",
        headers=headers,
        json=data
    )
    return response.json() if response.status_code == 200 else None

# 创建标签页
tab1, tab2 = st.tabs(["批量抓取", "网站映射"])

with tab1:
    # 初始化session_state
    if 'combined_markdown' not in st.session_state:
        st.session_state.combined_markdown = ""

    # 创建表单
    with st.form("scrape_form"):
        # 多URL输入
        urls = st.text_area(
            "输入要抓取的URL列表(每行一个URL)", 
            placeholder="https://example.com\nhttps://another.com",
            height=150
        )
        
        # 抓取选项
        st.subheader("抓取选项")
        col1, col2 = st.columns(2)
        with col1:
            only_main_content = st.checkbox("仅主要内容", value=True)
            include_metadata = st.checkbox("包含元数据", value=False)
        with col2:
            wait_for = st.number_input("等待时间(毫秒)", min_value=0, value=0)
            mobile = st.checkbox("移动端模式", value=False)
        
        submitted = st.form_submit_button("开始批量抓取")

        if submitted:
            if not urls:
                st.error("请输入至少一个URL")
            else:
                url_list = [url.strip() for url in urls.split('\n') if url.strip()]
                all_markdown = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, url in enumerate(url_list):
                    try:
                        status_text.text(f"正在处理: {url} ({i+1}/{len(url_list)})")
                        progress_bar.progress((i+1)/len(url_list))
                        
                        # 准备请求数据
                        data = {
                            "url": url,
                            "options": {
                                "pageOptions": {
                                    "onlyMainContent": only_main_content,
                                    "includeMetadata": include_metadata,
                                    "waitFor": wait_for,
                                    "mobile": mobile
                                }
                            }
                        }
                        
                        # 调用Firecrawl API
                        headers = {
                            "Authorization": f"Bearer {API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        response = requests.post(
                            f"{API_URL}/v0/scrape",
                            headers=headers,
                            json=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if 'markdown' in result.get('data', {}):
                                all_markdown.append(f"# {url}\n\n{result['data']['markdown']}\n\n---\n")
                            else:
                                st.warning(f"{url}: 未返回markdown内容")
                        else:
                            st.error(f"{url}: API请求失败 - {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"{url}: 发生错误 - {str(e)}")
                
                if all_markdown:
                    st.session_state.combined_markdown = "\n".join(all_markdown)

    # 显示结果和操作按钮
    if st.session_state.combined_markdown:
        # 下载和复制按钮（放在结果上方）
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="下载Markdown",
                data=st.session_state.combined_markdown,
                file_name="firecrawl_results.md",
                mime="text/markdown"
            )
        with col2:
            if st.button("复制到剪贴板"):
                pyperclip.copy(st.session_state.combined_markdown)
                st.success("已复制到剪贴板!")
        
        st.markdown("### 合并后的抓取结果")
        st.markdown(st.session_state.combined_markdown)

with tab2:
    # 网站映射功能
    st.subheader("网站URL映射")
    
    # 初始化session_state
    if 'mapped_links' not in st.session_state:
        st.session_state.mapped_links = []
    
    with st.form("map_form"):
        url = st.text_input(
            "输入网站URL",
            placeholder="https://example.com"
        )
        search = st.text_input(
            "搜索关键词(可选)",
            placeholder="docs"
        )
        submitted = st.form_submit_button("开始映射")
        
        if submitted:
            if not url:
                st.error("请输入网站URL")
            else:
                with st.spinner("正在映射网站URL..."):
                    result = map_url(url, search if search else None)
                    if result:
                        # 支持两种API响应格式
                        if result.get('status') == 'success' or result.get('success') == True:
                            links = result.get('links', [])
                            st.success(f"找到 {len(links)} 个URL")
                            
                            # 保存结果到session_state
                            st.session_state.mapped_links = links
                            
                            # 显示URL表格
                            st.dataframe({"URL": links})
                        else:
                            st.error(f"映射失败: {result.get('message', '未知错误')}")
                            st.json(result)  # 调试用
                    else:
                        st.error("API请求失败")

    # 表单外的操作按钮
    if st.session_state.get('mapped_links'):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("复制URL列表"):
                pyperclip.copy("\n".join(st.session_state.mapped_links))
                st.success("已复制到剪贴板!")
        with col2:
            st.download_button(
                label="下载URL列表",
                data="\n".join(st.session_state.mapped_links),
                file_name="url_list.txt",
                mime="text/plain"
            )

import os
import streamlit as st
from dotenv import load_dotenv
from map import map_url
from batch_scrape import batch_scrape

# 加载环境变量
load_dotenv()
API_URL = os.getenv('FIRECRAWL_API_URL')
API_KEY = os.getenv('FIRECRAWL_API_KEY')

# 设置页面配置
st.set_page_config(page_title="Firecrawl工具集", layout="wide")
st.title("Firecrawl工具集")

# 创建标签页
tab1, tab2 = st.tabs(["批量抓取", "网站映射"])

with tab1:
    batch_scrape(API_URL, API_KEY)

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
                    result = map_url(url, search if search else None, API_URL, API_KEY)
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
                import pyperclip
                pyperclip.copy("\n".join(st.session_state.mapped_links))
                st.success("已复制到剪贴板!")
        with col2:
            st.download_button(
                label="下载URL列表",
                data="\n".join(st.session_state.mapped_links),
                file_name="url_list.txt",
                mime="text/plain"
            )
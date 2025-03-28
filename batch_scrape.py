import os
import streamlit as st
from dotenv import load_dotenv
import requests
import json
import pyperclip

# 加载环境变量
load_dotenv()
API_URL = os.getenv("FIRECRAWL_API_URL")
API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 设置页面配置
st.set_page_config(page_title="Firecrawl批量抓取工具", layout="wide")
st.title("Firecrawl批量抓取工具")

# 初始化session_state
if "combined_markdown" not in st.session_state:
    st.session_state.combined_markdown = ""

# 可折叠的使用说明
with st.expander("使用说明", expanded=False):
    st.markdown(
        """
    1. 在.env文件中设置FIRECRAWL_API_URL和FIRECRAWL_API_KEY
    2. 每行输入一个要抓取的URL
    3. 设置抓取选项
    4. 点击"开始批量抓取"按钮
    5. 结果可以下载或复制到剪贴板
    """
    )

# 创建表单
with st.form("scrape_form"):
    # 多URL输入
    urls = st.text_area(
        "输入要抓取的URL列表(每行一个URL)",
        placeholder="https://example.com\nhttps://another.com",
        height=150,
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
            url_list = [url.strip() for url in urls.split("\n") if url.strip()]
            all_markdown = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, url in enumerate(url_list):
                try:
                    status_text.text(f"正在处理: {url} ({i+1}/{len(url_list)})")
                    progress_bar.progress((i + 1) / len(url_list))

                    # 准备请求数据
                    data = {
                        "url": url,
                        "options": {
                            "pageOptions": {
                                "onlyMainContent": only_main_content,
                                "includeMetadata": include_metadata,
                                "waitFor": wait_for,
                                "mobile": mobile,
                            }
                        },
                    }

                    # 调用Firecrawl API
                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    }

                    # 输出请求信息
                    st.text(f"请求URL: {API_URL}/scrape")
                    st.text(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
                    st.text(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")

                    response = requests.post(
                        f"{API_URL}/scrape", headers=headers, json=data
                    )

                    # 输出响应信息
                    st.text(f"响应状态码: {response.status_code}")
                    try:
                        st.text(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                    except:
                        st.text(f"响应内容: {response.text}")

                    if response.status_code == 200:
                        result = response.json()
                        if "markdown" in result.get("data", {}):
                            all_markdown.append(
                                f"# {url}\n\n{result['data']['markdown']}\n\n---\n"
                            )
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
            mime="text/markdown",
        )
    with col2:
        if st.button("复制到剪贴板"):
            pyperclip.copy(st.session_state.combined_markdown)
            st.success("已复制到剪贴板!")

    st.markdown("### 合并后的抓取结果")
    st.markdown(st.session_state.combined_markdown)

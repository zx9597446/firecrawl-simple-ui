import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
API_URL = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1")
API_KEY = os.getenv("FIRECRAWL_API_KEY")

# 初始化session状态
if 'results' not in st.session_state:
    st.session_state.results = None

def submit_search(query, options):
    """提交搜索任务"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "limit": options["limit"],
        "scrapeOptions": {
            "formats": ["markdown"] if options["get_markdown"] else []
        }
    }
    
    # 可选参数
    if options["tbs"]:
        payload["tbs"] = options["tbs"]
    if options["lang"]:
        payload["lang"] = options["lang"]
    if options["country"]:
        payload["country"] = options["country"]
    if options["location"]:
        payload["location"] = options["location"]
    if options["timeout"]:
        payload["timeout"] = options["timeout"]

    try:
        response = requests.post(
            f"{API_URL}/search",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"搜索失败: {str(e)}")
        return None

# Streamlit界面
st.title("🔍 Firecrawl 搜索工具")

# 搜索查询输入
query = st.text_input(
    "输入搜索查询",
    placeholder="例如: 量子计算最新进展",
    help="输入您想要搜索的内容"
)

# 配置选项
with st.expander("搜索选项"):
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("结果数量", min_value=1, max_value=10, value=5)
        get_markdown = st.checkbox("获取完整Markdown内容", value=True)
        lang = st.text_input("语言代码", value="zh", help="例如: zh, en")
    with col2:
        country = st.text_input("国家代码", value="cn", help="例如: cn, us")
        location = st.text_input("位置参数")
        timeout = st.number_input("超时时间(ms)", min_value=0, value=60000)

# 时间搜索参数
tbs = st.text_input("时间搜索参数", help="例如: qdr:d (天), qdr:h (小时)")

# 提交按钮
if st.button("开始搜索") and query:
    options = {
        "limit": limit,
        "get_markdown": get_markdown,
        "tbs": tbs if tbs else None,
        "lang": lang if lang else None,
        "country": country if country else None,
        "location": location if location else None,
        "timeout": timeout if timeout > 0 else None,
    }
    
    with st.spinner("搜索中..."):
        result = submit_search(query.strip(), options)
        
    if not result:
        st.error("搜索失败: 无响应")
    elif result.get("error"):
        st.error(f"搜索失败: {result['error']}")
    elif not result.get("success"):
        st.error(f"搜索失败: {result.get('message', '未知错误')}")
    else:
        st.session_state.results = result
        st.success("搜索完成！")

# 结果显示
if st.session_state.results:
    st.divider()
    st.subheader("搜索结果")
    
    data = st.session_state.results.get("data", [])
    if not data:
        st.warning("没有找到结果")
    else:
        for idx, item in enumerate(data, 1):
            with st.expander(f"{idx}. {item.get('title', '无标题')}"):
                st.markdown(f"**URL**: {item.get('url', '无URL')}")
                st.markdown(f"**描述**: {item.get('description', '无描述')}")
                
                if item.get("markdown"):
                    st.markdown("**完整内容**")
                    st.markdown(item["markdown"])
                
                if item.get("links"):
                    st.markdown(f"**链接**: {len(item['links'])}个")
                    for link in item["links"][:5]:  # 最多显示5个链接
                        st.markdown(f"- {link}")

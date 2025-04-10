import streamlit as st
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App title and config
st.set_page_config(
    page_title="NewsSense",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto"
)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Responsive CSS styling
st.markdown("""
<style>
    /* Header styling */
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem 0;
        margin-bottom: 1rem;
    }
    .header-title {
        font-size: 4rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        font-family: 'Arial', sans-serif;
        letter-spacing: 1px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2.5rem;
            padding: 0 1rem;
        }
    }
    
    /* Chat interface styling */
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .message {
        padding: 12px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
    }
    .bot-message {
        background-color: #f1f1f1;
        margin-right: auto;
    }
    /* Sidebar chat history styling */
    .sidebar-chat-item {
        padding: 8px;
        margin: 4px 0;
        border-radius: 4px;
        background-color: #f8f9fa;
        cursor: pointer;
    }
    .sidebar-chat-item:hover {
        background-color: #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Clean header with no background color
st.markdown("""
<div class="header-container">
    <h1 class="header-title">NewsSense</h1>
</div>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm NewsSense. Ask me why any fund is down today, like 'Why is QQQ down?'"}
    ]

# Initialize sidebar chat history
if "sidebar_history" not in st.session_state:
    st.session_state.sidebar_history = []

# Function to call your backend API
def get_fund_analysis(fund_query):
    """Call your team's backend API to get fund data and news analysis"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/analyze",
            params={"query": fund_query}
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"API request failed with status {response.status_code}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# Main chat interface
with st.container():
    # Display only the current conversation (last Q&A pair)
    if len(st.session_state.messages) > 0:
        with st.chat_message(st.session_state.messages[-1]["role"]):
            st.markdown(st.session_state.messages[-1]["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about any fund..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing fund and news..."):
                analysis = get_fund_analysis(prompt)
                
                if "error" in analysis:
                    error_message = analysis["error"]
                    st.error(error_message)
                    response_content = error_message
                else:
                    # Format the response
                    response_content = f"""
                    **{analysis.get('fund_name', 'Fund')} Performance**  
                    Current Price: {analysis.get('current_price', 'N/A')}  
                    Today's Change: {analysis.get('price_change', 'N/A')}%  
                    
                    **News Summary**  
                    {analysis.get('summary', 'No summary available')}
                    """
                    
                    if "related_articles" in analysis:
                        articles = "\n".join(
                            f"- [{article['title']}]({article['url']}) ({article['source']})" 
                            for article in analysis.get("related_articles", [])[:3]
                        )
                        response_content += f"\n\n**Top Related Articles**\n{articles}"
                    
                    st.markdown(response_content)
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Move previous Q&A to sidebar history if exists
                if len(st.session_state.messages) > 3:  # Check if there's a previous Q&A pair
                    prev_question = st.session_state.messages[-4]["content"]
                    prev_answer = st.session_state.messages[-3]["content"]
                    st.session_state.sidebar_history.append({
                        "question": prev_question,
                        "answer": prev_answer,
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

# Sidebar content
with st.sidebar:
    st.title("Chat History")
    
    if not st.session_state.sidebar_history:
        st.markdown("No chat history yet. Ask a question to get started!")
    else:
        for i, item in enumerate(reversed(st.session_state.sidebar_history)):
            with st.expander(f"Q: {item['question']} ({item['timestamp']})"):
                st.markdown(item["answer"])
    
    st.markdown("---")
    st.markdown("""
    **Understand why your funds are moving**  
    Ask questions like:  
    - Why is QQQ down?  
    - What's happening with VTI?  
    - Explain Nifty IT's performance  
    """)
    
    st.markdown("---")
    st.markdown("**Supported Funds**")
    st.markdown("""
    - QQQ (Nasdaq-100)  
    - VTI (Total Stock Market)  
    - Nifty IT  
    - SBI Tech  
    - And more...  
    """)
    
    st.markdown("---")
    st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
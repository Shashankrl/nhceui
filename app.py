from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize chat history
chat_history = {
    "current_messages": [
        {"role": "assistant", "content": "Hi! I'm NewsSense. Ask me why any fund is down today, like 'Why is QQQ down?'"}
    ],
    "sidebar_history": []
}

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

@app.route('/', methods=['GET', 'POST'])
def index():
    global chat_history
    
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        
        if prompt:
            # Add current Q&A to sidebar history before processing new question
            if len(chat_history["current_messages"]) >= 2:
                # Get the last Q&A pair
                last_question = chat_history["current_messages"][-2]["content"] if chat_history["current_messages"][-2]["role"] == "user" else ""
                last_answer = chat_history["current_messages"][-1]["content"] if chat_history["current_messages"][-1]["role"] == "assistant" else ""
                
                if last_question and last_answer:
                    chat_history["sidebar_history"].append({
                        "question": last_question,
                        "answer": last_answer,
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M')
                    })
            
            # Add new user message to current conversation
            chat_history["current_messages"].append({"role": "user", "content": prompt})
            
            # Get analysis
            analysis = get_fund_analysis(prompt)
            
            if "error" in analysis:
                response_content = analysis["error"]
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
            
            # Add assistant response to current conversation
            chat_history["current_messages"].append({
                "role": "assistant",
                "content": response_content
            })
    
    return render_template('index.html', 
                         chat_history=chat_history, 
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))

if __name__ == '__main__':
    app.run(debug=True)
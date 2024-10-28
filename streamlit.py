import streamlit as st
import requests
from typing import Union,List
from utils.helpers import format_gandalf
models = [
    # "llama-3.1-405b-reasoning",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "llama-3.2-1b-preview",
    "llama-3.2-3b-preview"
]

BACKEND_URL = "https://postgresconnect-6514d47ebc67.herokuapp.com/"
def connect_to_database(db, user, password, host, port):
    url = f"{BACKEND_URL}/connect"
    payload = {
        "db": db,
        "user": user,
        "password": password,
        "host": host,
        "port": port
        
    }
    try:
        response = requests.post(url, json=payload)
        
        # Check if the response contains valid JSON
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()
        else:
            return {
                "status_code": response.status_code,
                "detail": "Invalid response format",
                "response_text": response.text  # Optionally return the full response for debugging
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "status_code": 500,
            "detail": f"Request error: {e}"
        }


def generate_chat(question:str, selected_table:Union[str, List[str]], selected_schema:str,  model:str):
    url = f"{BACKEND_URL}/generate"
    payload = {
        "question": question,
        "selected_schema": selected_schema,
        "selected_table": selected_table,
        "model": model
    }
    try:
        response = requests.post(url, json=payload)
        
        # Check if the response contains valid JSON
        if response.headers.get('Content-Type') == 'application/json':
            return response.json()
        else:
            return {
                "status_code": response.status_code,
                "detail": "Invalid response format: expected JSON but received something else.",
                "response_text": response.text  # Optionally return the full response for debugging
            }
    
    except requests.exceptions.RequestException as e:
        return {
            "status_code": 500,
            "detail": f"Request error: {e}"
        }


def receive_schema_data():
    response = requests.get("http://backend:8000/send_schema")
    if response.status_code == 200:
        data = response.json()
        schemas = data.get("schemas", [])
        tables = data.get("tables", {})
        return schemas, tables  # Returning both schemas and tables
    else:
        return [], {}

    

if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'error_count' not in st.session_state:
    st.session_state.error_count = 0
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
# Sidebar for user input
with st.sidebar:
    if not st.session_state.connected:
        st.markdown("### 🔌 Database Connection")
        st.markdown("---")
        db = st.text_input("🗄️ Database name", placeholder = "Enter database name...")
        user = st.text_input("👤 Username", placeholder = "Enter username....")
        password = st.text_input("🔑 Password", type="password", placeholder = "Enter password...")
        host = st.text_input("🏢 Host", placeholder = "Enter hostname...")
        port = st.text_input("🔌 Port", placeholder = "Enter port number...")
        
        st.markdown("---")
        if st.button("🚀 Connect"):
            response = connect_to_database(db, user, password, host, port)
            
            if response.get("status_code") == 200:
                st.session_state.connected = True
                st.success("🎉 Connection successful!")
                st.button("➡️ Next page")
                
            else:
                st.session_state.error_count += 1

                if st.session_state.error_count == 1:
                    st.error("❌ Oops! Connection failed 😅")
                    st.info("🔍 Double-check your credentials and try again! 🤔")
                    st.info("Also, Make sure to press Enter after filling each field! ⌨️")
                
                elif st.session_state.error_count == 2:
                    st.error("❌ Oops! Still no luck 😞 ")
                    st.info("Please check your credientials and press Enter after filling each field! 😫")
                
                elif st.session_state.error_count == 3:
                    st.error("Bro!!! come on now 😖")
                    st.info("Just do what i said previously!😭")

                else:
                    st.error("You're hopeless😭😭")
                    st.markdown("""#### 
                                Maybe it's time for a break🙂? Try these:
                                - 🌿 Touch some grass
                                - 🧎‍♂️  Beg your village people
                                - 🤔 Rethink your life
                                - 🍚 Eat Eba
                                Come back after trying one of these""")
                with st.expander("error detail"):
                        st.code(response.get('response_text'))

        with st.expander("💡 Need help?"):
            st.markdown("""
                #### 🎯 Quick Tips:
                - 🔑 Make sure your credentials are correct
                - 🌐 Check if the database is running
                - 🔌 Verify the port number (usually 5432)
                - 🏢 Double-check the host address
                - ⌨️ Press Enter after filling each field
            """)
    
    else:
        with st.expander("🎯 Database Navigator"):
            st.markdown("### 🎯 Database Navigator")
            st.write("✅ Connected to the database!")
            schema, tables = receive_schema_data()
            
            st.markdown("#### 📁 Schema Selection")
            selected_schema = st.selectbox("📂 Select schema", schema)
            
            st.markdown("#### 📊 Table Selection")
            schema_tables = tables.get(selected_schema, [])
            selected_table = st.multiselect("📋 Select tables", schema_tables)
            
            st.markdown("#### 🧠 AI Model")
            model = st.selectbox("Select AI model", models)
        
st.markdown("""
    <style>
        @keyframes pulse {
            0% {text-shadow: 0 0 10px #ff00ff;}
            50% {text-shadow: 0 0 20px #00ffff;}
            100% {text-shadow: 0 0 10px #ff00ff;}
        }
    </style>
    <h1 style='
        text-align: center;
        color: #fff;
        font-family: "Press Start 2P", cursive;
        text-transform: uppercase;
        letter-spacing: 3px;
        animation: pulse 2s infinite;
    '>TEXT TO SQL</h1>
""", unsafe_allow_html=True)

question = st.text_input(" enter your question ", placeholder = "Tell me, what is it you seek 🧙‍♂️?")
if st.button("Granting wish"):
    if question:
        with st.spinner("🔮 Abbrakadabra..."):
            response = generate_chat(question,selected_table,selected_schema,model)
            st.write("Response 🧙‍♂️:", response.items())
            st.session_state.query_history.append({'Frodo': question, 'Gandalf': response})
            
    else:
        st.warning(" 🧙‍♂️ I'm still waiting for your question Child!")


with st.sidebar:
    st.header("Query History")
    response_container = st.container(height=800)
    with response_container:
             # Loop through chat history and display in reverse order (latest first)
            for chat in reversed(st.session_state.query_history):
                sql_query_str, result_str = format_gandalf(chat['Gandalf'])
                st.markdown(f"""
                            <div style="
                                background: linear-gradient(to bottom right, #2C1810, #1A0F0A);
                                padding: 20px;
                                border-radius: 10px;
                                border: 2px solid #C4A484;
                                box-shadow: 0 0 15px rgba(196, 164, 132, 0.3);
                                font-family: 'Cinzel', Arial, sans-serif;
                            ">
                                <p style="
                                    color: #FFD700;
                                    margin: 10px 0;
                                    padding: 8px;
                                    border-left: 3px solid #C4A484;
                                    font-family: 'Cinzel', Arial, sans-serif;
                                "><strong>💍 Frodo:</strong> {chat['Frodo']}</p>        
                                <p style="
                                    color: #FFD700;
                                    margin: 10px 0;
                                    padding: 8px;
                                    border-left: 3px solid #C4A484;
                                    font-family: 'Cinzel', Arial, sans-serif;
                                "><strong>🧙‍♂️ Gandalf:</strong><br><code>{sql_query_str}</code><br><br><code>{result_str}</code></p>
                            </div>      
                        """, unsafe_allow_html=True)


# Text to SQL(PostgreSQL) App with FastAPI and Streamlit
This project is a **Text to SQL** application that uses FastAPI backend for handling database connections and generating SQl responses based on user queries and a Streamlit frontend that provides an interactive way of connecting to the database.
Users are able to connect to a PostgreSQl database, choose the schema and the table or tables they want, ask questions and receive SQL queries together with the result.

## Table of Contents
- Features
- Technologies
- Getting Started
- Installation
- Usage
- Future Improvement

### Features
- **Database Connecction**: Connect to a PostgreSQL database and browse schemas and tables.
- **Interactive Text to SQL**: Enter natural language questions, select table/tables and model and receive SQl responses.
- **AI Model Selection**: Choose from various AI models for query generation.
- **Query History**: View past queries and responses for reference.

### Tecnologies
- **FastAPI**: Backend API for database connection and text to SQL generation.
- **Streamlit**: Frontend for creating an interactive user interface.
- **PostgreSQL**: Database for querying data using generated SQL.
- **Heroku(optional)**: Platform for deploying the FastAPI backend.
- **Streamlit Cloud(optional)**: Platfrm for deploying the Streamlit frontend.

### Getting Started
#### Prerequisites
- Python 3.8+
- PostgreSQL database
- Heroku and Streamlit cloud(optional)

### Installation
#### 1. Clone the repository
```bash
git clone https://github.com/BOLUF16/TEXT_TO_SQL.git
cd TEXT_TO_SQL
```
#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
#### 3. Environment Variables
create a .env file with the following environment variables:
```makefile
GROQ_API_KEY = <your_secret_key>
```

### Usage
#### Running Locally
**Note** : To run the app locally without having to deploy the app to Heroku and Streamlit Cloud, some changes will have to be made to the code.
- **code update in streamlit.py**:
```python
BACKEND_URL = "http://127.0.0.1:5000"
```
**FastAPI**
```bash
uvicorn app:app --host 127.0.0.1 --port 5000 --reload
```
**Streamlit**
```bash
streamlit run streamlit.py
```
#### Deploying
**Note** :  After deploying the app to Heroku and Streamlit cloud, you won't be able to access your local database. You'll need to connect to a managed PostgreSQL instance provided by Heroku or another database service
- Create a new app on Heroku.
- Push the code to Heroku.
- Set envirnments variable on Heroku for your GROQ_API_KEY.
- Go to Streamlit Cloud and deploy the app.
- Set the backend URL to your Heroku app URL in streamlit.py to allow Streamlit to communicate with FastAPI.

### Future Improvements
- Support additional database types.
  






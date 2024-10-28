from fastapi import FastAPI, Request, Depends, HTTPException
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
import groq 
from dotenv import load_dotenv
import os

load_dotenv('.env')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY)
app = FastAPI()

db_pool = None

@app.post('/connect')
async def database_conn(
    request : Request
    ):
    
    global db_pool

    user_input = await request.json()
    
    
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=100,
            dbname = user_input['db'],
            user = user_input['user'],
            password = user_input['password'],
            host = user_input['host'],
            port = user_input['port']
            )
        return{
                "detail" : "Connection to Postgres database successful.",
                "status_code": 200 
            }
    except Exception as e:
            raise ConnectionError(f"Unable to connect to postgres database: {e}")


def get_db_conn():
    global db_pool
     
    if db_pool is None:
        raise HTTPException(status_code=500, detail="Database connection pool is not initialized.")
    
    conn = db_pool.getconn()
    try:
        yield conn
    finally:
        db_pool.putconn(conn)


    
@app.get('/send_schema')
async def send_schema_data(conn=Depends(get_db_conn)):
    try:
        cursor = conn.cursor()
        
        # Fetch all schema names
        cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata
        """)
        schemas = [schema[0] for schema in cursor.fetchall()]
        
        # Prepare a dictionary to store tables per schema
        schema_tables = {}
        
        # Fetch tables for each schema
        for schema in schemas:
            cursor.execute(f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
            """, (schema,))
            tables = [table[0] for table in cursor.fetchall()]
            schema_tables[schema] = tables  # Map tables to the corresponding schema
        
        cursor.close()
        
        return {'schemas': schemas, 'tables': schema_tables}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error fetching schemas: {e}')
    
@app.post('/generate')
async def text_to_sql(
    request:Request, conn = Depends(get_db_conn)
):
    

    query = await request.json()

    question = query['question']
    Schema = query['selected_schema']
    Tables = query['selected_table']
    model = query['model']

    try:
        
        tables = [Tables] if isinstance(Tables, str) else Tables

        # Validate tables is not empty
        if not tables:
            return {
                "error": "No tables selected",
                "sql_query": None,
                "results": None
            }
        
    
        schema_info = []
        with conn.cursor() as cursor:
            for table in tables:

                cursor.execute("""
                 SELECT column_name, data_type
                 FROM information_schema.columns
                 WHERE table_schema = %s AND table_name = %s
                 ORDER BY ordinal_position;
                """, (Schema,table))

                columns = cursor.fetchall()
                
                cursor.execute("""
                 SELECT c.column_name
                 FROM information_schema.table_constraints tc
                 JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
                 JOIN information_schema.columns AS c
                    ON c.table_schema = tc.constraint_schema
                    AND c.table_name = tc.table_name
                    AND c.column_name = ccu.column_name
                 WHERE constraint_type = 'PRIMARY KEY'
                 AND tc.table_schema = %s
                 AND tc.table_name = %s;
                """, (Schema, table))

                primary_keys = [pk[0] for pk in cursor.fetchall()]
                

                schema_info.append({
                    "table_name": table,
                    "columns" : columns,
                    "primary_keys" : primary_keys,
                })
        
        prompt = f"""You are an advanced SQL expert and database analyst. Your task is to convert natural language questions into accurate SQL queries while following these guidelines:

                System Context:
                - Available Schema: {Schema}
                - Selected Tables: {', '.join(tables)}
                - Table Schemas:
                {schema_info}

                Instructions:
                1. ALWAYS use only the tables and columns provided in the schema
                2. Write clear, optimized SQL queries
                3. Use appropriate JOINs when needed
                4. Include comments explaining complex logic
                5. NEVER reference tables or columns not in the schema
                6. Return ONLY the SQL query without explanations unless there are issues
                7. Use appropriate aggregations (COUNT, SUM, AVG, etc.) when needed
                8. Consider NULL values in your logic
                9. Add WHERE clauses to filter results when appropriate
               

                User Question: {question}

                If the question cannot be answered with the given schema or tables, respond with "❌ I cannot answer this question with the provided schema. Please check the available tables and columns."

                Think through this step-by-step:
                1. Identify the required tables from the schema
                2. Determine necessary columns
                3. Plan table joins if needed
                4. Add appropriate WHERE conditions
                5. Include GROUP BY/HAVING if required
                6. Apply any needed sorting (ORDER BY)

                SQL Query:"""
        
        completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            
            model=model,  # or your preferred Groq model
            temperature=0.1,
            max_tokens=1024
        )
        
        generated_sql = completion.choices[0].message.content.strip()
        generated_sql = generated_sql.replace('```sql', '').replace('```', '').strip()
        # Execute the generated query
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(generated_sql)
            results = cursor.fetchall()
            
        return {
            
            "sql_query": generated_sql,
            "results": results,
           
        }
        
    except psycopg2.Error as db_error:
        return {
            "sql_query": generated_sql if 'generated_sql' in locals() else None,
            "results": None,
            "error": f"Database error: {str(db_error)}"
        }
    except Exception as e:
        return {
            "sql_query": generated_sql if 'generated_sql' in locals() else None,
            "results": None,
            "error": f"Error: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    print("Starting LLM API")
    uvicorn.run(app, host="0.0.0.0", reload=True)


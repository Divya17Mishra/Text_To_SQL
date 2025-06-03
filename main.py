from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import sqlite3
import re
from transformers import pipeline

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

text2sql = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-wikiSQL")

schema = (
    "Table authors: id, name, bio. "
    "Table books: id, title, description, ISBN, genre_id. "
    "Table genres: id, name, description. "
    "Table books_authors: book_id, author_id, is_main_author. "
)

EXAMPLE_QUERIES = [
    "Who wrote Foundation?",
    "Show me fantasy books",
    "How many books did Asimov write?",
    "List all books and their genres",
    "Authors of Harry Potter and the Philosopher's Stone",
    "Books by J.K. Rowling"
]

def is_select_query(sql: str) -> bool:
    return bool(sql.strip().lower().startswith("select"))

def convert_to_sql(text: str) -> str:
    prompt = schema + " " + text
    try:
        result = text2sql(prompt, max_length=128)[0]['generated_text']
        return result
    except Exception as e:
        return None

def execute_sql(sql: str):
    try:
        conn = sqlite3.connect("books.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return results
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "examples": EXAMPLE_QUERIES})

@app.post("/convert")
async def convert_to_sql_endpoint(text: str = Form(...)):
    sql_query = convert_to_sql(text)
    if not sql_query:
        return {
            "error": "Sorry, I couldn't understand your question. Please rephrase or ask about books, authors, genres, or their relationships.",
            "suggestions": EXAMPLE_QUERIES
        }
    if not is_select_query(sql_query):
        return {
            "error": "Only SELECT queries are allowed. Please try a different question.",
            "sql": sql_query,
            "suggestions": EXAMPLE_QUERIES
        }
    results = execute_sql(sql_query)
    if isinstance(results, dict) and "error" in results:
        return {
            "error": f"SQL Error: {results['error']}",
            "sql": sql_query,
            "suggestions": EXAMPLE_QUERIES
        }
    if not results:
        return {
            "sql": sql_query,
            "results": [],
            "error": "No results found. Try another question or check your spelling.",
            "suggestions": EXAMPLE_QUERIES
        }
    return {"sql": sql_query, "results": results}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) 
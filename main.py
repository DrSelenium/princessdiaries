import fastapi
import uvicorn

app = fastapi.FastAPI()

@app.get("/trivia")
def read_root():
    return {"answers": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthcheck")
def welcome():
    return {"message": "Welcome to the FastAPI application!"}

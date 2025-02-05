from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging

load_dotenv()  # Cargar variables de entorno desde el archivo .env

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/greet/{name}")
def greet(name: str):
    logging.info("message")
    return {"message": f"Hello, {name}!"}
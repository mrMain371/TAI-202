#imports
from fastapi import FastAPI
#instancia
app = FastAPI()
#endpoints
@app.get("/")
async def  holamundo():
    return {"message":"Hola Mundo desde FastAPI"}

#importaciones
from fastapi import FastAPI
from app.router import usuario,misc

#Instancia del servidor
app= FastAPI(
    title= "Mi primer API",
    description= "luis Cesar Garduno Valle",
    version="1.0"
)

app.include_router(usuario.router)
app.include_router(misc.misc)
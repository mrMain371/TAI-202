#importaciones
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import asyncio
from typing import Optional

#Instancia del servidor
app = FastAPI(
    title="API de Gestión de Usuarios",
    description="API con validación de datos utilizando Pydantic y manejo de errores con HTTPException.",
    version="1.0.1"
)

# Crear un modelo de Pydantic para un usuario con id, nombre y edad
class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="ID único del usuario", example=1)
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre completo del usuario", example="luis valle")
    edad: int = Field(..., ge=1, le=120, description="Edad del usuario en años", example=25)

#TB ficticia
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Aly","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

#Endpoints
@app.get("/")
async def holamundo():
    return {"mensaje":"Hola Mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {
        "mensaje":"Bienvenido a FastAPI",
        "estatus":"200",
        }

@app.get("/v1/parametroOb/{id}",tags=['Parametro Obligatorio'])
async def consultauno(id:int):
    return {"mensaje":"usuario encontrado",
            "usuario":id,
            "status":"200" }

@app.get("/v1/parametroOp/",tags=['Parametro Opcional'])
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return{"mensaje":"usuario encontrado","usuario":usuarioK}
        return{"mensaje":"usuario no encontrado","status":"200"}
    else:
        return {"mensaje":"No se proporciono id","status":"200"}

@app.get("/v1/usuarios/",tags=['HTTP CRUD'])
async def leer_usuarios():
 return {
    "total": len(usuarios),
    "usuarios": usuarios,
    "status": "200"
  }

@app.post("/v1/usuarios/", 
          tags=["Usuarios"], 
          summary="Crear nuevo usuario", 
          description="Este endpoint recibe un objeto JSON y lo valida antes de insertarlo en la lista.",
          status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuario: crear_usuario):
    # Verificar si el ID ya existe
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
    
    # Agregar el nuevo usuario
    nuevo_usuario = {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "edad": usuario.edad
    }
    usuarios.append(nuevo_usuario)
    return {"mensaje": "Usuario Agregado", "Usuario": nuevo_usuario}

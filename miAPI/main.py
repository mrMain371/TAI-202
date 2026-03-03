from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional 
import asyncio
from pydantic import BaseModel, Field
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
usuarios = [
    {"id": 1, "nombre": "Santiago", "edad": 21},
    {"id": 2, "nombre": "Sergio", "edad": 22},
    {"id": 3, "nombre": "Rodrigo", "edad": 20},
]

#Modelo de validacion pydantic
class crear_usuario(BaseModel):
    id:int = Field(...,gt=0, description="Indentificador unico")
    nombre:str = Field(...,min_length=3, max_length=50,example="Juanita")
    edad:int = Field(...,ge=1,le=100,description="Edad valida entre 1 y 100")

#Seguridad HTTP Basic
security = HTTPBasic()
def verificar_peticion(credentials:HTTPBasicCredentials = Depends(security)):
    usuario_correcto = secrets.compare_digest(credentials.username, "luis")
    contrasenia_correcta = secrets.compare_digest(credentials.password, "4515")

    if not(usuario_correcto and contrasenia_correcta):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas"
        )
    return credentials.username



@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario:crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    #if any(usr["id"] == usuario.get("id") for usr in usuarios):
    #    raise HTTPException(status_code=400, detail="El id ya existe")
    usuarios.append(usuario)
    return {"mensaje": "Usuario Creado", "datos": usuario}

#NUEVAS RUTAS: PUT, PATCH Y DELETE 
@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: dict):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios[indice] = usuario_actualizado
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.patch("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: dict):
    """PATCH: Modifica solo los campos enviados."""
    for usr in usuarios:
        if usr["id"] == usuario_id:
            usr.update(datos_parciales)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def eliminar_usuario(usuario_id: int, usuarioAuth:str = Depends(verificar_peticion)):
    """DELETE: Elimina al usuario de la lista."""
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": f"Usuario eliminado por {usuarioAuth}"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


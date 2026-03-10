from fastapi import FastAPI, status, HTTPException, Depends
from typing import Optional,Annotated
import asyncio
from pydantic import BaseModel, Field
import secrets

from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
app = FastAPI()
SECRET_KEY = "tu no metes cabra"
ALGORITHM = "HS256"
MinsAlive = 1
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") 
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=MinsAlive)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exception
        return username
    except JWTError:
        raise exception
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

    usuarios.append(usuario)
    return {"mensaje": "Usuario Creado", "datos": usuario}

@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_completo(
    usuario_id: int, 
    usuario_actualizado: dict,
    token: Annotated[str, Depends(get_current_user)] 
):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios[indice] = usuario_actualizado
            return {"mensaje": f"Actualizado por {token}", "datos": usuarios[indice]}
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
async def eliminar_usuario(
    usuario_id: int, 
    token: Annotated[str, Depends(get_current_user)]
):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios.pop(i)
            return {"mensaje": f"Usuario eliminado exitosamente por {token}"}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if form_data.username == "luis" and form_data.password == "4515":
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

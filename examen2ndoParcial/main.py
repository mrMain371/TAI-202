#imports
from datetime import date,timedelta,datetime
from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,Field,dataclasses
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
#variables y objetos a utilizar
print ( datetime())
Reservas = [{"id" :1,"nombre":"Luisillo","fechaReserva":"14/07/05-14.00","personas":7},
           {"id":2,},
           {"id":3,}]
app = FastAPI()
#modelo de validacion pydantic
class crearReserva(BaseModel):
    id :int=Field(...,gt=0,description="Id unico de usuario",example=1)
    nombre:str=Field(...,min_length=6,description="miniomo de caracteres ",examples="luisillo")
 #   fechaReserva :datetime=Field(...,(datetime.isoweekday<7),(datetime.time))
#intento fallido de validacion  con tipos date
#seguridad con http basica 
#Seguridad HTTP Basic
security = HTTPBasic()
def verificar_peticion(credentials:HTTPBasicCredentials = Depends(security)):
    usuario_correcto = secrets.compare_digest(credentials.username, "admin")
    contrasenia_correcta = secrets.compare_digest(credentials.password, "rest123")

@app.get("/v1/consultarID/{id}",tags=["Parametro obligatorio"])
async def consultauno(id:int):
    for rsv in Reservas:
        if rsv["id"] ==id:
            return{"usuario encontrado":rsv}
        
@app.get("/listarReservas",tags=["parametro no obligatorio"])
async def consultarTodos(usuario_id: int, usuarioAuth:str = Depends(verificar_peticion)):
    return{"total":len(Reservas), "reservas":Reservas}
@app.post("/crearUsuario")
async def crear_reserva(reserva:crearReserva):
    for rsv in Reservas:
        if rsv["id"]==reserva.id:
            raise HTTPException(
                status_code=400,
                detail="El id ya existe"
            )
    
    fecha = reserva["fechaReserva"]
    str(fecha)
    fecha2 = str.split(fecha,"-")
    if fecha2[1]>23.00 or fecha2[1]>10.00:
        raise HTTPException(
                status_code=400,
                detail="fecha invalida"
            )
    fecha3 =str.split(fecha,"/")
    dia = fecha[0]
    mes = fecha[1]
    fecha4 =str.split(fecha3,"-")
    ano =fecha4[0]

    

    
    





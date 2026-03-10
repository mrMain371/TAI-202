#imports
from datetime import date,timedelta
from fastapi import FastAPI
from pydantic import BaseModel,Field,dataclasses,da
#variables y objetos a utilizar

Reserva = [{"id" :1,"nombre":"Luisillo","fechaReserva":"14/07/05-14.00","personas":7},
           {"id":2,},
           {"id":3,}]
app = FastAPI()
#modelo de validacion pydantic
class crearReserva(BaseModel):
    id :int=Field(...,gt=0,description="Id unico de usuario",example=1)
    nombre:str=Field(...,min_length=6,description="miniomo de caracteres ",examples="luisillo")
    fechaReserva :date=Field(...,da)

#seguridad con http basica 
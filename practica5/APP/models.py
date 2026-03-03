from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

CURRENT_YEAR = datetime.now().year


class Usuario(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr


class LibroCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    autor: str = Field(min_length=2, max_length=100)
    anio: int
    paginas: int = Field(gt=1)
    estado: Optional[Literal["disponible", "prestado"]] = "disponible"

    @field_validator("anio")
    @classmethod
    def validar_anio(cls, v: int) -> int:
        if v <= 1450 or v > CURRENT_YEAR:
            raise ValueError(f"anio debe ser >1450 y <= {CURRENT_YEAR}")
        return v


class LibroOut(BaseModel):
    id: int
    nombre: str
    autor: str
    anio: int
    paginas: int
    estado: Literal["disponible", "prestado"]


class PrestamoCreate(BaseModel):
    libro_id: Optional[int] = None
    libro_nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    usuario: Usuario

    @field_validator("libro_nombre")
    @classmethod
    def limpiar_nombre(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip()


class PrestamoOut(BaseModel):
    id: int
    libro_id: int
    usuario_nombre: str
    usuario_correo: str
    fecha_prestamo: str
    devuelto: bool
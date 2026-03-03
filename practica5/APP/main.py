from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from APP.models import LibroCreate, LibroOut, PrestamoCreate, PrestamoOut

app = FastAPI(title="Biblioteca Digital API", version="1.0.0")

# -------------------------
# "Base de datos" en memoria (cache local del proceso)
# -------------------------
LIBROS: dict[int, dict] = {}
PRESTAMOS: dict[int, dict] = {}
NEXT_LIBRO_ID = 1
NEXT_PRESTAMO_ID = 1

# Índice por nombre exacto (para búsqueda exacta / prestar por nombre)
LIBRO_ID_POR_NOMBRE: dict[str, int] = {}

# -------------------------
# Convertir errores de validación a 400 (rúbrica)
# -------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "400 Request: datos faltantes o inválidos", "errors": exc.errors()},
    )


# a) Registrar un libro -> 201 Create
@app.post("/books", status_code=201, response_model=LibroOut)
def registrar_libro(payload: LibroCreate):
    global NEXT_LIBRO_ID

    nombre = payload.nombre.strip()
    if len(nombre) < 2 or len(nombre) > 100:
        raise HTTPException(status_code=400, detail="400 Request: nombre inválido")

    # (Opcional) evitar duplicados por nombre
    if nombre.lower() in (n.lower() for n in LIBRO_ID_POR_NOMBRE.keys()):
        raise HTTPException(status_code=400, detail="400 Request: el libro ya existe (nombre duplicado)")

    libro_id = NEXT_LIBRO_ID
    NEXT_LIBRO_ID += 1

    libro = {
        "id": libro_id,
        "nombre": nombre,
        "autor": payload.autor.strip(),
        "anio": payload.anio,
        "paginas": payload.paginas,
        "estado": payload.estado,
    }
    LIBROS[libro_id] = libro
    LIBRO_ID_POR_NOMBRE[nombre] = libro_id

    return libro


# b) Listar todos los libros
@app.get("/books", response_model=list[LibroOut])
def listar_libros():
    # orden descendente por id
    return sorted((v for v in LIBROS.values()), key=lambda x: x["id"], reverse=True)


# c) Buscar un libro por su nombre (LIKE)
@app.get("/books/search", response_model=list[LibroOut])
def buscar_por_nombre(name: str):
    name = (name or "").strip()
    if len(name) < 2 or len(name) > 100:
        raise HTTPException(status_code=400, detail="400 Request: nombre inválido")

    q = name.lower()
    resultados = [b for b in LIBROS.values() if q in b["nombre"].lower()]
    return sorted(resultados, key=lambda x: x["id"], reverse=True)


# d) Registrar el préstamo de un libro -> 201, 409 si ya está prestado
@app.post("/loans", status_code=201, response_model=PrestamoOut)
def registrar_prestamo(payload: PrestamoCreate):
    global NEXT_PRESTAMO_ID

    if payload.libro_id is None and not payload.libro_nombre:
        raise HTTPException(status_code=400, detail="400 Request: proporciona libro_id o libro_nombre")

    # Resolver libro
    libro = None
    if payload.libro_id is not None:
        libro = LIBROS.get(payload.libro_id)
    else:
        # buscar nombre exacto
        libro_id = None
        for n, i in LIBRO_ID_POR_NOMBRE.items():
            if n.lower() == payload.libro_nombre.strip().lower():
                libro_id = i
                break
        if libro_id is not None:
            libro = LIBROS.get(libro_id)

    if not libro:
        raise HTTPException(status_code=400, detail="400 Request: libro no existe")

    if libro["estado"] == "prestado":
        raise HTTPException(status_code=409, detail="409 Conflict: el libro ya está prestado")

    # Crear préstamo
    prestamo_id = NEXT_PRESTAMO_ID
    NEXT_PRESTAMO_ID += 1

    fecha = datetime.now().isoformat(timespec="seconds")
    prestamo = {
        "id": prestamo_id,
        "libro_id": libro["id"],
        "usuario_nombre": payload.usuario.nombre.strip(),
        "usuario_correo": payload.usuario.correo,
        "fecha_prestamo": fecha,
        "devuelto": False,
    }
    PRESTAMOS[prestamo_id] = prestamo

    # Marcar libro prestado
    libro["estado"] = "prestado"

    return prestamo


# e) Marcar un libro como devuelto -> 200 OK, 409 si préstamo no existe
@app.put("/loans/{loan_id}/return", status_code=200)
def devolver_libro(loan_id: int):
    prestamo = PRESTAMOS.get(loan_id)
    if not prestamo:
        raise HTTPException(status_code=409, detail="409 Conflict: el registro de préstamo ya no existe")

    if prestamo["devuelto"] is True:
        raise HTTPException(status_code=409, detail="409 Conflict: el préstamo ya estaba devuelto")

    prestamo["devuelto"] = True

    libro = LIBROS.get(prestamo["libro_id"])
    if libro:
        libro["estado"] = "disponible"

    return {"message": "200 OK: libro devuelto"}


# f) Eliminar el registro de un préstamo -> 200, 409 si no existe
@app.delete("/loans/{loan_id}", status_code=200)
def eliminar_prestamo(loan_id: int):
    prestamo = PRESTAMOS.get(loan_id)
    if not prestamo:
        raise HTTPException(status_code=409, detail="409 Conflict: el registro de préstamo ya no existe")

    # si estaba activo, liberar libro
    if prestamo["devuelto"] is False:
        libro = LIBROS.get(prestamo["libro_id"])
        if libro:
            libro["estado"] = "disponible"

    del PRESTAMOS[loan_id]
    return {"message": "200 OK: préstamo eliminado"}
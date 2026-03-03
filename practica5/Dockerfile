FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tu carpeta real (APP en mayúsculas)
COPY ./APP ./APP

EXPOSE 8000

# Ejecuta el módulo correcto: APP/main.py -> "APP.main:app"
CMD ["uvicorn", "APP.main:app", "--host", "0.0.0.0", "--port", "8000"]
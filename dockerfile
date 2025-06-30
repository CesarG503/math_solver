# Imagen base
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    gcc \
    libssl-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /metodos_numericos

# Copia los archivos necesarios al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Expone el puerto (por defecto 8000 en Django)
EXPOSE 8002

# Comando por defecto para correr el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]
FROM surnet/alpine-wkhtmltopdf:3.22.0-0.12.6-full

# Instala Python e venv
RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app

# Cria ambiente virtual
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o app
COPY . .

EXPOSE 5000

# Remove o entrypoint padrão que roda wkhtmltopdf
ENTRYPOINT []

# Comando que o container deve usar: gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

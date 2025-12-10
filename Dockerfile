FROM surnet/alpine-wkhtmltopdf:3.19.0-0.12.6-full

# Instalar Python
RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# REMOVE o entrypoint padrão (wkhtmltopdf)
ENTRYPOINT []

# Agora sim o Gunicorn roda
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

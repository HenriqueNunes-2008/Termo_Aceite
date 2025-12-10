FROM surnet/alpine-wkhtmltopdf:3.19.0-0.12.6-full

# Install Python + venv support
RUN apk add --no-cache python3 py3-pip py3-virtualenv

WORKDIR /app

# Create virtual environment
RUN python3 -m venv /app/venv

# Ensure venv pip is used
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .

# Install Python dependencies in venv
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

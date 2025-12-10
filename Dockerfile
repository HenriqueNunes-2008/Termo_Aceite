FROM python:3.10-slim

# Install dependencies required by wkhtmltopdf
RUN apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    wget

# Download and install wkhtmltopdf (versão estável)
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.debian11_amd64.deb \
    -O /tmp/wkhtmltopdf.deb && \
    apt-get install -y /tmp/wkhtmltopdf.deb && \
    rm /tmp/wkhtmltopdf.deb

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 5000

# Start app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

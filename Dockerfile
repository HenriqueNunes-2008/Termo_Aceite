# Base image
FROM python:3.10-slim

# Install wkhtmltopdf
RUN apt-get update && apt-get install -y wkhtmltopdf

# App directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 5000

# Start server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

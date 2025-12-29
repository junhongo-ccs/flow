FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir flask flask-cors openai

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=app.py
ENV PORT=8080

# Run the application
CMD ["python", "app.py"]

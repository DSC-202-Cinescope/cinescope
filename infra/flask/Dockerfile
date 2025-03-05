# Use an official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set environment variables (these will be overridden by Kubernetes ConfigMap)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV DB_HOST=postgres-service
ENV DB_PORT=5432
ENV DB_NAME=your_db
ENV DB_USER=your_user
ENV DB_PASSWORD=your_password

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

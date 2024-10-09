# Use the official Debian image as the base image
FROM debian:bullseye-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    sqlite3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose port 5005 to the outside world
EXPOSE 5005

# Create a volume for the SQLite database
VOLUME ["/app/responses"]

# Run the Flask application, binding to 0.0.0.0 to make it accessible externally
CMD ["python3", "app.py", "--host=0.0.0.0"]
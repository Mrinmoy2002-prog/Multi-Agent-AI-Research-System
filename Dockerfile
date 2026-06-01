# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install git and system helpers
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements file first to cache installation layers
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Inform Docker that the container listens on Streamlit's default port
EXPOSE 7860

# Command to run your app tightly bound to Hugging Face's expected address structure
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt and install the dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Flask
RUN pip install flask

# Copy the rest of the application code
COPY . .

# Expose port 8000 for Flask
EXPOSE 8000

# Run the bot and Flask app
CMD ["python", "-m", "bot.__main__"]

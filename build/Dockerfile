# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the app files into the container
COPY ../ /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5002

# Start the app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5002", "app:app"]
# Use an official Python runtime as a parent image
FROM python:3.10.11

# Set the working directory to /app
WORKDIR /go_agent

# Copy the requirements file into the container
COPY req.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r req.txt

# Copy the rest of the application code
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run app.py when the container launches
CMD ["python", "go_agent/header.py"]

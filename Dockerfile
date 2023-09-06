# Use an official Python runtime as a base image
FROM python:3.8

# Set the working directory
WORKDIR /usr/src/app

# Install app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bundle app source
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 10000

# Run the application
CMD ["gunicorn", "app:app"]

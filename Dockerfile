# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container to /app
WORKDIR /app

# Copy the application files into the container
COPY ai-irc.py chat.conf requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir openai configparser

# Make port 80 available to the world outside this container
# EXPOSE 80

# Set the entrypoint command to execute the ai-irc.py script
CMD ["python", "-u", "ai-irc.py"]

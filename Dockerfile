FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the files to the container
COPY . .

# Install any dependencies
RUN pip install -r requirements.txt

# Set the command for the container to run
CMD ["python", "main.py"]
FROM python:3.9

# Set the working directory in the container
WORKDIR /action/workspace

# Copy the files to the container
COPY . /action/workspace

# Install any dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt
 
# Set the command for the container to run
CMD ["/action/workspace/main.py"]

ENTRYPOINT ["python3", "-u"]

# Use the official Python 3.11 image
# FROM --platform=arm64 python:3.11.4-bookworm
# ARG BUILDPLATFORM
FROM python:3.11.4-bookworm

ENV PYTHONBUFFERED 1


# Create directory
RUN mkdir /code

# Set the working directory to /code
WORKDIR /code

# Mirror the current directory to the working directory for hotreloading
ADD . /code/

# Install pipenv
RUN pip install --no-cache-dir -r linux-requirements.txt

# Make migrations
RUN python Backend/manage.py makemigrations

# Run custom migrate
RUN python Backend/manage.py migrate

# Generate DRF Spectacular Documentation
RUN python Backend/manage.py spectacular --color --file Backend/schema.yml

# Expose port 8000 for the web server
EXPOSE 8000


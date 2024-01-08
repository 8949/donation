# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Run makemigrations and migrate
RUN python manage.py makemigrations && \
    python manage.py migrate

ARG DJANGO_SUPERUSER_PHONE
ARG DJANGO_SUPERUSER_PASSWORD

# Create a superuser during the build process
RUN python manage.py migrate && \
    echo "from donations.models import User; User.objects.filter(phone='$DJANGO_SUPERUSER_PHONE').exists() or \
    User.objects.create_superuser('$DJANGO_SUPERUSER_PHONE', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

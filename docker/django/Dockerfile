FROM python:3.12-slim 

# Install system dependencies (needed for wait-for-it or database checks)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /apps 

COPY requirements.txt . 
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . . 

# Explicitly set permissions for the entrypoint
# Adjust the path if your entrypoint is inside a subfolder like docker/django/
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 

# The entrypoint script will always run before CMD
ENTRYPOINT ["/entrypoint.sh"]

# This is passed as arguments to entrypoint.sh
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
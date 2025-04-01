# Use the same base image as the database for compatibility
FROM nickblah/postgis:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create and use a virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set environment variables for GeoDjango using the correct paths
ENV GDAL_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgdal.so.32
ENV GEOS_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgeos_c.so.1

# Run server
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Here we are building a container that runs our FastAPI backend on Hugging Face Spaces

# This sets the base image: a lightweight version of Python 3.12.
# “slim” means fewer preinstalled packages → smaller, faster container.
FROM python:3.12-slim

# Set working directory
WORKDIR /app
# Defines the working directory inside the container. All subsequent commands run inside /app.


# Install system dependencies (libmagic for python-magic + WeasyPrint deps)
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    libgobject-2.0-0 \
    && rm -rf /var/lib/apt/lists/*



# Copies everything from your local project folder into /app inside the container. This includes requirements.txt, your backend/ code, etc.
# Copy project files into the container
COPY . .


# Installs all Python dependencies listed in requirements.txt.
# --no-cache-dir prevents pip from storing temporary files → keeps the image smaller.
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy models
RUN python -m spacy download en_core_web_md && \
    python -m spacy download en_core_web_sm

# Declares that the container will listen on port 7860.
# Hugging Face Spaces always uses port 7860
EXPOSE 7860

# This is the start command when the container runs. It launches our FastAPI app (backend.main:app) using Uvicorn.
# --host 0.0.0.0 makes it accessible externally.
# --port 7860 matches Hugging Face’s required port.
# Start FastAPI with uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]

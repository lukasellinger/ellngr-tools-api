FROM python:3.11-slim

# Update and install necessary packages
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y bash build-essential git openjdk-17-jdk maven

# Create a non-root user and switch to that user
RUN useradd -m run
USER run

WORKDIR /home/run/api

ENV PATH="/home/run/.local/bin:${PATH}"

# Clone and build DiscourseSimplification in a separate folder
RUN mkdir -p /home/run/DiscourseSimplification && \
    cd /home/run && \
    git clone https://github.com/Lambda-3/DiscourseSimplification.git && \
    cd DiscourseSimplification && \
    git checkout 5e7ac12 && \
    mvn clean install -DskipTests

# Return to the API working directory
WORKDIR /home/run/api

# Copy the requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application code
COPY --chown=run:run . .

RUN python3 setup.py

# Set default environment variable for the port
ENV PORT=8081

# We need this to override with environment variables
CMD ["bash", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

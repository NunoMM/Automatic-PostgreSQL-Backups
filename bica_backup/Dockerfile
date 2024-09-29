# Dockerfile
FROM python:3.9-slim

# Install necessary packages and Python dependencies
RUN apt-get update && apt-get install -y wget gnupg2 lsb-release cron procps \
    && echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-16 \
    && apt-get clean

# Install cryptography and python-dotenv packages
RUN pip install --no-cache-dir cryptography python-dotenv

# Set working directory
WORKDIR /bica_backup

# Copy the entire bica_backup directory
COPY . .

# Give execution rights to the cron job
RUN chmod 0644 /bica_backup/crontab

# Apply cron job
RUN crontab /bica_backup/crontab

# Create the log files for cron
RUN touch /var/log/cron.log /var/log/cron_error.log && \
    chmod 0666 /var/log/cron.log /var/log/cron_error.log

# Create a startup script
RUN echo '#!/bin/sh\nservice cron start\necho "Container started..." >> /var/log/cron.log\ntail -f /var/log/cron.log /var/log/cron_error.log' > /start.sh \
    && chmod +x /start.sh

# Use the startup script as the entry point
CMD ["/start.sh"]

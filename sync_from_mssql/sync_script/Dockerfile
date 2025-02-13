FROM python:3.9

WORKDIR /app

# Install required packages
RUN apt-get update && apt-get install -y cron

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy sync script
COPY sync.py sync.py

# Copy cron job script
COPY crontab /etc/cron.d/sync_cron

# Apply cron job script permissions
RUN chmod 0644 /etc/cron.d/sync_cron

# Apply crontab and start cron in the background
RUN crontab /etc/cron.d/sync_cron && touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log


# FROM python:3.9

# WORKDIR /app

# COPY requirements.txt requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# COPY sync.py sync.py

# CMD ["python", "sync.py"]

### 📁 Automatic PostgreSQL Database Backup System

---

### 📖 Overview

This is a Python-based solution for automating backups of a PostgreSQL database. It ensures that backups are created periodically and securely, with options for encryption and cleanup of old backups. The system uses Docker to containerize the application and schedules backups using **cron**.

---

### ✨ Features

- **Automated Backups**: Backups are taken automatically at scheduled intervals using cron jobs.
- **Backup Encryption**: Backups are encrypted with a password using the Python `cryptography` package for additional security.
- **Flexible Cleanup**: Automatically deletes backups older than a specified number of days to save storage space.
- **Environment Variables**: Configuration is handled through a `.env` file, which stores sensitive information like database credentials and encryption password.
- **Dockerized Application**: The solution runs inside a Docker container, simplifying deployment and isolating dependencies.

---

### 🛠️ Requirements

- **Python 3.x** installed
- **Docker** installed
- **PostgreSQL Client** installed and SQL database setup.
- Required Python libraries:
  - `os`
  - `subprocess`
  - `datetime`
  - `cryptography`
  - `python-dotenv`

---

### 🚀 Usage

1. Clone this repository and navigate to the project directory.
2. Set up your `.env` file with the following variables:
    ```bash
    DB_HOST=<your_database_host>
    DB_PORT=<your_database_port>
    DB_USER=<your_database_user>
    DB_PASSWORD=<your_database_password>
    DB_NAME=<your_database_name>
    RETENTION_DAYS=<backup_retention_days>
    ENCRYPTION_PASSWORD=<your_encryption_password>
    ```

3. Build the Docker image:
    ```bash
    docker build -t <your_image_name> .
    ```

4. Run the Docker container:
    ```bash
    docker run --name <your_container_name> --env-file .env -v /path/to/backups:/mnt/backups --network host -d <your_image_name>
    ```

5. Check the logs to verify that backups are being created:
    ```bash
    docker exec -it <your_container_name> tail -f /var/log/cron.log
    ```

---

### 🔄 Cron Schedule

Backups are scheduled to run at specified times through a cron job, configured in the `crontab` file.

- **Backup with cleanup** at 03:00 every day:
    ```bash
    0 3 * * * /bin/bash -c 'cd /bica_backup && source .env && /usr/local/bin/python backup.py cleanup >> /var/log/cron.log 2>> /var/log/cron_error.log'
    ```

- **Backup without cleanup** at 14:00 every day:
    ```bash
    0 14 * * * /bin/bash -c 'cd /bica_backup && source .env && /usr/local/bin/python backup.py >> /var/log/cron.log 2>> /var/log/cron_error.log'
    ```

---

### 🧪 Tests

The system was tested with the following scenarios:

1. **Backup Creation**:
   - Successfully generated `.tar.gz` backup files in the `/mnt/backups` directory.
  
2. **Encryption**:
   - Backups are encrypted with the password specified in the `.env` file.

3. **Cleanup**:
   - Automatically deleted backups older than 7 days (configurable via the `RETENTION_DAYS` environment variable).

4. **Manual Decryption**:
   - Decryption of any backup file can be performed manually.

---

### 📂 Project Files

- **Dockerfile**: Docker setup for the Python backup application.
- **.env**: Stores sensitive database connection details and the encryption password.
- **crontab**: Defines the schedule for automatic backups and cleanups.
- **backup.py**: Python script that handles the backup, encryption, and cleanup logic.

---

### 🛠️ Built-in Commands

The script supports the following commands:

- **Run backup without cleanup**:
    ```bash
    docker exec <your_container_name> python /bica_backup/backup.py 
    ```

- **Run backup with cleanup**:
    ```bash
    docker exec <your_container_name> python /bica_backup/backup.py cleanup
    ```

- **Decrypt a backup**:
    ```bash
    docker exec <your_container_name> python /bica_backup/backup.py decrypt </path/to/backup_file.tar.gz> <encryption_password>
    ```

---

### 🔍 Logs

The system writes logs to two files:

- **/var/log/cron.log**: Stores the output of successful backups.
- **/var/log/cron_error.log**: Stores error messages from failed backup attempts.

You can check all the crontab jobs logs in real-time using:
     ```bash
     docker exec -it <your_container_name> -f /var/log/cron.log
     ```

import os
import subprocess
import sys
import tarfile
from datetime import datetime, timedelta
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('/bica_backup/.env')

# Environment variables for configuration
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
BACKUP_DIR = '/mnt/backups'
RETENTION_DAYS = os.getenv('RETENTION_DAYS')
ENCRYPTION_PASSWORD = os.getenv('ENCRYPTION_PASSWORD')

# Add error checking for required environment variables
required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'RETENTION_DAYS', 'ENCRYPTION_PASSWORD']
missing_vars = [var for var in required_vars if os.getenv(var) is None]


def derive_key(salt: bytes, password: str) -> bytes:
    """
    Derives an encryption key from the password and salt using PBKDF2.

    Args:
        salt (bytes): A random salt for key derivation.
        password (str): The password used for encryption.

    Returns:
        bytes: The derived encryption key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_data(plaintext: bytes, password: str) -> bytes:
    """
    Encrypts the data using AES-GCM and returns the ciphertext with salt and nonce.

    Args:
        plaintext (bytes): The data to be encrypted.
        password (str): The password used for encryption.

    Returns:
        bytes: The encrypted data with salt and nonce prepended.
    """
    salt = os.urandom(16)  # Generate a random salt
    key = derive_key(salt, password)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # GCM mode nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return salt + nonce + ciphertext  # Prepend salt and nonce for later decryption

def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """
    Decrypts the data using AES-GCM.

    Args:
        encrypted_data (bytes): The encrypted data with salt and nonce prepended.
        password (str): The password used for decryption.

    Returns:
        bytes: The decrypted data.
    """
    salt = encrypted_data[:16]  # Extract salt
    nonce = encrypted_data[16:28]  # Extract nonce
    ciphertext = encrypted_data[28:]  # The rest is ciphertext
    key = derive_key(salt, password)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def backup_database():
    """
    Creates an encrypted backup of the database and saves it as a tar.gz file.
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H%M')
    sql_filename = f"bica-backup-{timestamp}.sql"
    sql_path = os.path.join(BACKUP_DIR, sql_filename)
    tar_filename = f"bica-backup-{timestamp}.tar.gz"
    tar_path = os.path.join(BACKUP_DIR, tar_filename)

    # Dump the database to SQL
    dump_cmd = f"PGPASSWORD={DB_PASSWORD} pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} --column-inserts --no-owner --no-privileges > {sql_path}"
    result = subprocess.run(dump_cmd, shell=True, stderr=subprocess.PIPE, check=False)

    if result.returncode != 0:
        print(f"Error creating SQL backup: {result.stderr.decode()}")
        return

    try:
        # Read the SQL file to encrypt
        with open(sql_path, 'rb') as sql_file:
            plaintext = sql_file.read()

        # Encrypt the SQL data
        encrypted_data = encrypt_data(plaintext, ENCRYPTION_PASSWORD)

        # Write the encrypted SQL file
        with open(sql_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

        # Create tar.gz archive containing the encrypted SQL file
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(sql_path, arcname=sql_filename)

        print(f"Encrypted backup saved in: {tar_path}")
    finally:
        # Clean up the SQL file, leaving only the tar.gz
        if os.path.exists(sql_path):
            os.remove(sql_path)

def decrypt_backup(tar_path: str, password: str):
    """
    Decrypts a backup file and saves the decrypted SQL.

    Args:
        tar_path (str): Path to the encrypted backup file.
        password (str): Password for decryption.
    """
    dir_path = os.path.dirname(tar_path)
    filename = os.path.basename(tar_path)

    # Create the decrypted filename
    decrypted_filename = filename.rsplit('.', 2)[0] + '_decrypted.sql'
    decrypted_path = os.path.join(dir_path, decrypted_filename)

    try:
        # Extract and decrypt in one step
        with tarfile.open(tar_path, "r:gz") as tar:
            encrypted_file = tar.extractfile(tar.getnames()[0])
            encrypted_data = encrypted_file.read()

        # Decrypt the SQL file
        decrypted_data = decrypt_data(encrypted_data, password)

        # Write the decrypted SQL to a file
        with open(decrypted_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted_data)

        print(f"Decrypted backup saved to: {decrypted_path}")
    except Exception as e:
        print(f"Error during decryption: {str(e)}")

def remove_old_backups():
    """
    Removes backup files older than RETENTION_DAYS.
    """
    global RETENTION_DAYS
    RETENTION_DAYS = int(RETENTION_DAYS)
    cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith('bica-backup-') and filename.endswith('.tar.gz'):
            try:
                file_date_str = filename[len('bica-backup-'):filename.index('.tar.gz')]
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d_%H%M')
                if file_date < cutoff_date:
                    os.remove(os.path.join(BACKUP_DIR, filename))
                    print(f"Old backup removed: {filename}")
            except ValueError as e:
                print(f"Error removing old backup: {e}")

def main():
    """
    Main function to handle command-line arguments and execute corresponding actions.
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == 'decrypt':
            if len(sys.argv) >= 4:
                decrypt_backup(sys.argv[2], sys.argv[3])
            else:
                print("Usage: python script.py decrypt <backup_file.tar.gz> <decryption_password>")
        elif sys.argv[1] == 'cleanup':
            if len(sys.argv) == 2:
                backup_database()
                remove_old_backups()
            else:
                print("Usage: python script.py cleanup")
        else:
            print("Unknown argument. Use either 'cleanup', 'decrypt', or no arguments.")
    else:
        backup_database()

if __name__ == '__main__':
    main()
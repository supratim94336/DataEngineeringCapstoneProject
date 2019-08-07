# secure airflow connections
from cryptography.fernet import Fernet

# generate key
fernet_key = Fernet.generate_key()
print(fernet_key.decode())

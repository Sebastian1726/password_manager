import bcrypt
from cryptography.fernet import Fernet
import base64
import os

# Ruta del archivo que almacena la clave de cifrado
KEY_FILE = 'secret.key'

def generate_key():
    """
    Genera una nueva clave de cifrado y la guarda en un archivo.
    """
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)
    print(f"Generada nueva clave de cifrado y guardada en '{KEY_FILE}'.")
    return key

def load_key():
    """
    Carga la clave de cifrado desde el archivo. Si no existe, la genera.
    """
    if not os.path.exists(KEY_FILE):
        print(f"'{KEY_FILE}' no encontrado. Generando una nueva clave.")
        return generate_key()
    with open(KEY_FILE, 'rb') as key_file:
        key = key_file.read()
    # Validar la clave
    if len(key) != 44:
        print(f"Clave en '{KEY_FILE}' inválida. Regenerando la clave.")
        return generate_key()
    return key

# Cargar o generar la clave de cifrado
key = load_key()

# Verificar que la clave es válida para Fernet
try:
    cipher_suite = Fernet(key)
except ValueError as e:
    print(f"Error al inicializar Fernet: {e}")
    print("Regenerando la clave de cifrado.")
    key = generate_key()
    cipher_suite = Fernet(key)

def hash_password(password):
    """
    Hashea una contraseña utilizando bcrypt.
    
    :param password: Contraseña en texto plano.
    :return: Tupla (hash de la contraseña, sal).
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode(), salt.decode()

def verify_password(password, hashed):
    """
    Verifica una contraseña contra su hash.
    
    :param password: Contraseña en texto plano.
    :param hashed: Hash almacenado de la contraseña.
    :return: Booleano indicando si la contraseña es válida.
    """
    return bcrypt.checkpw(password.encode(), hashed.encode())

def encrypt_password(password):
    """
    Cifra una contraseña utilizando Fernet.
    
    :param password: Contraseña en texto plano.
    :return: Contraseña cifrada en formato de cadena.
    """
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """
    Descifra una contraseña cifrada.
    
    :param encrypted_password: Contraseña cifrada en formato de cadena.
    :return: Contraseña en texto plano.
    """
    return cipher_suite.decrypt(encrypted_password.encode()).decode()
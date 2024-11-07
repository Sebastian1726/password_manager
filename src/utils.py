import string
import secrets

def generate_password(length=16, use_special=True):
    """
    Genera una contraseña segura.
    
    :param length: Longitud de la contraseña.
    :param use_special: Booleano que indica si se deben incluir caracteres especiales.
    :return: Contraseña generada como cadena.
    """
    characters = string.ascii_letters + string.digits
    if use_special:
        characters += string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password
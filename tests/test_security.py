import pytest
from src.security import hash_password, verify_password, encrypt_password, decrypt_password, generate_key, load_key, cipher_suite
import os

def test_hash_password():
    password = 'test_password'
    hashed, salt = hash_password(password)
    assert hashed is not None
    assert salt is not None
    assert verify_password(password, hashed) == True
    assert verify_password('wrong_password', hashed) == False

def test_encrypt_decrypt_password():
    password = 'secret_password'
    encrypted = encrypt_password(password)
    assert encrypted is not None
    decrypted = decrypt_password(encrypted)
    assert decrypted == password

def test_encryption_with_new_key(tmp_path):
    # Temporarily cambiar la ubicación del archivo de clave
    original_key_file = 'secret.key'
    temp_key_file = tmp_path / 'temp_secret.key'
    
    # Respaldar la clave existente si existe
    if os.path.exists(original_key_file):
        os.rename(original_key_file, temp_key_file)
    
    try:
        # Generar una nueva clave
        new_key = generate_key()
        assert new_key is not None
        # Cifrar una contraseña con la nueva clave
        password = 'another_secret'
        encrypted = encrypt_password(password)
        # Descifrarla
        decrypted = decrypt_password(encrypted)
        assert decrypted == password
    finally:
        # Restaurar la clave original si existe
        if temp_key_file.exists():
            os.rename(temp_key_file, original_key_file)
import pytest
from src.database import init_db
from src.models import User, PasswordEntry
from src.security import hash_password, verify_password, encrypt_password, decrypt_password

@pytest.fixture
def session():
    # Usar una base de datos en memoria para pruebas
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.models import Base

    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_create_user(session):
    username = 'test_user'
    password = 'test_password'
    hashed_password, salt = hash_password(password)
    
    user = User(username=username, password_hash=hashed_password, salt=salt)
    session.add(user)
    session.commit()
    
    retrieved_user = session.query(User).filter_by(username=username).first()
    assert retrieved_user is not None
    assert retrieved_user.username == username
    assert verify_password(password, retrieved_user.password_hash) == True

def test_add_password_entry(session):
    # Crear usuario
    username = 'test_user'
    password = 'test_password'
    hashed_password, salt = hash_password(password)
    user = User(username=username, password_hash=hashed_password, salt=salt)
    session.add(user)
    session.commit()
    
    # Agregar entrada de contraseña
    service_name = 'Gmail'
    service_username = 'gmail_user'
    service_password = 'gmail_pass'
    notes = 'Personal correo'
    
    encrypted_password = encrypt_password(service_password)
    entry = PasswordEntry(
        user_id=user.id,
        service_name=service_name,
        username=service_username,
        password=encrypted_password,
        notes=notes
    )
    session.add(entry)
    session.commit()
    
    # Verificar entrada
    retrieved_entry = session.query(PasswordEntry).filter_by(user_id=user.id).first()
    assert retrieved_entry is not None
    assert retrieved_entry.service_name == service_name
    assert retrieved_entry.username == service_username
    assert decrypt_password(retrieved_entry.password) == service_password
    assert retrieved_entry.notes == notes
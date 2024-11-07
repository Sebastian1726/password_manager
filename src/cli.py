import argparse
import getpass
from .database import init_db
from .models import User, PasswordEntry
from .security import hash_password, verify_password, encrypt_password, decrypt_password
from .utils import generate_password

def register(args):
    session = init_db()
    username = args.username
    password = getpass.getpass("Contraseña: ")
    confirm_password = getpass.getpass("Confirmar Contraseña: ")
    if password != confirm_password:
        print("Las contraseñas no coinciden.")
        return
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        print("El nombre de usuario ya existe.")
        return
    hashed_password, salt = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password, salt=salt)
    session.add(new_user)
    session.commit()
    print(f"Usuario '{username}' registrado exitosamente.")

def login(session, username, password):
    user = session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        print("Usuario o contraseña incorrectos.")
        return None
    return user

def add_password(args):
    session = init_db()
    username = args.username
    password = getpass.getpass("Contraseña del usuario: ")
    user = login(session, username, password)
    if not user:
        return
    service_name = input("Nombre del Servicio: ")
    service_username = input("Nombre de Usuario del Servicio: ")
    service_password = getpass.getpass("Contraseña del Servicio (dejar en blanco para generar automáticamente): ")
    if not service_password:
        length = 16
        service_password = generate_password(length=length, use_special=True)
        print(f"Contraseña Generada: {service_password}")
    notes = input("Notas (opcional): ")
    encrypted_password = encrypt_password(service_password)
    new_entry = PasswordEntry(
        user_id=user.id,
        service_name=service_name,
        username=service_username,
        password=encrypted_password,
        notes=notes
    )
    session.add(new_entry)
    session.commit()
    print(f"Contraseña para '{service_name}' agregada exitosamente.")

def list_passwords(args):
    session = init_db()
    username = args.username
    password = getpass.getpass("Contraseña del usuario: ")
    user = login(session, username, password)
    if not user:
        return
    entries = session.query(PasswordEntry).filter_by(user_id=user.id).all()
    if not entries:
        print("No hay contraseñas almacenadas.")
        return
    for entry in entries:
        decrypted_password = decrypt_password(entry.password)
        print(f"ID: {entry.id}")
        print(f"Servicio: {entry.service_name}")
        print(f"Usuario: {entry.username}")
        print(f"Contraseña: {decrypted_password}")
        print(f"Notas: {entry.notes}")
        print(f"Creado: {entry.created_at}")
        print(f"Actualizado: {entry.updated_at}")
        print("-" * 20)

def edit_password(args):
    session = init_db()
    username = args.username
    password = getpass.getpass("Contraseña del usuario: ")
    user = login(session, username, password)
    if not user:
        return
    entry_id = args.id
    entry = session.query(PasswordEntry).filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        print("Entrada no encontrada.")
        return
    print("Presiona Enter para mantener el valor actual.")
    new_service_name = input(f"Nombre del Servicio [{entry.service_name}]: ") or entry.service_name
    new_service_username = input(f"Nombre de Usuario del Servicio [{entry.username}]: ") or entry.username
    new_service_password = getpass.getpass("Contraseña del Servicio (dejar en blanco para mantener): ")
    if new_service_password:
        new_service_password = encrypt_password(new_service_password)
    else:
        new_service_password = entry.password
    new_notes = input(f"Notas [{entry.notes}]: ") or entry.notes
    entry.service_name = new_service_name
    entry.username = new_service_username
    entry.password = new_service_password
    entry.notes = new_notes
    session.commit()
    print("Entrada actualizada exitosamente.")

def delete_password(args):
    session = init_db()
    username = args.username
    password = getpass.getpass("Contraseña del usuario: ")
    user = login(session, username, password)
    if not user:
        return
    entry_id = args.id
    entry = session.query(PasswordEntry).filter_by(id=entry_id, user_id=user.id).first()
    if not entry:
        print("Entrada no encontrada.")
        return
    confirm = input(f"¿Estás seguro de eliminar la entrada '{entry.service_name}'? (s/n): ")
    if confirm.lower() == 's':
        session.delete(entry)
        session.commit()
        print("Entrada eliminada exitosamente.")
    else:
        print("Operación cancelada.")

def generate_password_cli(args):
    length = args.length
    use_special = args.special
    password = generate_password(length=length, use_special=use_special)
    print(f"Contraseña Generada: {password}")

def launch_cli():
    parser = argparse.ArgumentParser(description="Gestor de Contraseñas CLI")
    subparsers = parser.add_subparsers(title="Comandos", dest="command")
    
    # Registrar usuario
    register_parser = subparsers.add_parser("register", help="Registrar un nuevo usuario")
    register_parser.add_argument("username", help="Nombre de usuario")
    register_parser.set_defaults(func=register)
    
    # Agregar contraseña
    add_parser = subparsers.add_parser("add", help="Agregar una nueva contraseña")
    add_parser.add_argument("username", help="Nombre de usuario")
    add_parser.set_defaults(func=add_password)
    
    # Listar contraseñas
    list_parser = subparsers.add_parser("list", help="Listar todas las contraseñas")
    list_parser.add_argument("username", help="Nombre de usuario")
    list_parser.set_defaults(func=list_passwords)
    
    # Editar contraseña
    edit_parser = subparsers.add_parser("edit", help="Editar una contraseña existente")
    edit_parser.add_argument("username", help="Nombre de usuario")
    edit_parser.add_argument("id", type=int, help="ID de la entrada de contraseña")
    edit_parser.set_defaults(func=edit_password)
    
    # Eliminar contraseña
    delete_parser = subparsers.add_parser("delete", help="Eliminar una contraseña")
    delete_parser.add_argument("username", help="Nombre de usuario")
    delete_parser.add_argument("id", type=int, help="ID de la entrada de contraseña")
    delete_parser.set_defaults(func=delete_password)
    
    # Generar contraseña
    generate_parser = subparsers.add_parser("generate", help="Generar una contraseña segura")
    generate_parser.add_argument("-l", "--length", type=int, default=16, help="Longitud de la contraseña")
    generate_parser.add_argument("-s", "--special", action="store_true", help="Incluir caracteres especiales")
    generate_parser.set_defaults(func=generate_password_cli)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
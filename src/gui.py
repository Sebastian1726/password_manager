import tkinter as tk
from tkinter import messagebox, simpledialog
from .database import init_db
from .models import User, PasswordEntry
from .security import hash_password, verify_password, encrypt_password, decrypt_password
from .utils import generate_password

class PasswordManagerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gestor de Contraseñas")
        master.geometry("600x400")
        
        self.session = init_db()
        self.current_user = None
        
        self.create_login_frame()
    
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(pady=50)
        
        tk.Label(self.login_frame, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.login_frame, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.login_button = tk.Button(self.login_frame, text="Iniciar Sesión", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.register_button = tk.Button(self.login_frame, text="Registrar", command=self.register)
        self.register_button.grid(row=3, column=0, columnspan=2, pady=5)
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user = self.session.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            self.current_user = user
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
            self.login_frame.destroy()
            self.create_main_frame()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor, completa todos los campos")
            return
        
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            messagebox.showerror("Error", "El nombre de usuario ya existe")
            return
        
        hashed_password, salt = hash_password(password)
        new_user = User(username=username, password_hash=hashed_password, salt=salt)
        self.session.add(new_user)
        self.session.commit()
        
        messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
    
    def create_main_frame(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Toolbar con botones
        toolbar = tk.Frame(self.main_frame)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        add_button = tk.Button(toolbar, text="Agregar", command=self.add_password)
        add_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        edit_button = tk.Button(toolbar, text="Editar", command=self.edit_password)
        edit_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_button = tk.Button(toolbar, text="Eliminar", command=self.delete_password)
        delete_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        generate_button = tk.Button(toolbar, text="Generar Contraseña", command=self.generate_password)
        generate_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        logout_button = tk.Button(toolbar, text="Cerrar Sesión", command=self.logout)
        logout_button.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Listbox para mostrar las contraseñas
        self.passwords_listbox = tk.Listbox(self.main_frame)
        self.passwords_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.load_passwords()
    
    def load_passwords(self):
        self.passwords_listbox.delete(0, tk.END)
        passwords = self.session.query(PasswordEntry).filter_by(user_id=self.current_user.id).all()
        for entry in passwords:
            display_text = f"{entry.service_name} - {entry.username}"
            self.passwords_listbox.insert(tk.END, display_text)
    
    def add_password(self):
        service_name = simpledialog.askstring("Agregar Contraseña", "Nombre del Servicio:")
        if not service_name:
            return
        service_username = simpledialog.askstring("Agregar Contraseña", "Nombre de Usuario:")
        if not service_username:
            return
        service_password = simpledialog.askstring("Agregar Contraseña", "Contraseña:")
        if not service_password:
            # Generar contraseña si no se proporciona
            length = 16
            service_password = generate_password(length=length, use_special=True)
            messagebox.showinfo("Contraseña Generada", f"Contraseña: {service_password}")
        notes = simpledialog.askstring("Agregar Contraseña", "Notas (opcional):")
        
        encrypted_password = encrypt_password(service_password)
        new_entry = PasswordEntry(
            user_id=self.current_user.id,
            service_name=service_name,
            username=service_username,
            password=encrypted_password,
            notes=notes
        )
        self.session.add(new_entry)
        self.session.commit()
        
        self.load_passwords()
        messagebox.showinfo("Éxito", "Contraseña agregada exitosamente")
    
    def edit_password(self):
        selected_index = self.passwords_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Por favor, selecciona una entrada para editar")
            return
        selected_text = self.passwords_listbox.get(selected_index)
        service_name, service_username = selected_text.split(' - ')
        entry = self.session.query(PasswordEntry).filter_by(user_id=self.current_user.id, service_name=service_name, username=service_username).first()
        if not entry:
            messagebox.showerror("Error", "Entrada de contraseña no encontrada")
            return
        
        new_service_name = simpledialog.askstring("Editar Contraseña", "Nombre del Servicio:", initialvalue=entry.service_name)
        if not new_service_name:
            return
        new_service_username = simpledialog.askstring("Editar Contraseña", "Nombre de Usuario:", initialvalue=entry.username)
        if not new_service_username:
            return
        new_service_password = simpledialog.askstring("Editar Contraseña", "Contraseña:", show='*', initialvalue=decrypt_password(entry.password))
        if not new_service_password:
            new_service_password = decrypt_password(entry.password)
        notes = simpledialog.askstring("Editar Contraseña", "Notas (opcional):", initialvalue=entry.notes)
        
        entry.service_name = new_service_name
        entry.username = new_service_username
        entry.password = encrypt_password(new_service_password)
        entry.notes = notes
        self.session.commit()
        
        self.load_passwords()
        messagebox.showinfo("Éxito", "Contraseña actualizada exitosamente")
    
    def delete_password(self):
        selected_index = self.passwords_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Por favor, selecciona una entrada para eliminar")
            return
        selected_text = self.passwords_listbox.get(selected_index)
        service_name, service_username = selected_text.split(' - ')
        entry = self.session.query(PasswordEntry).filter_by(user_id=self.current_user.id, service_name=service_name, username=service_username).first()
        if not entry:
            messagebox.showerror("Error", "Entrada de contraseña no encontrada")
            return
        
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar la contraseña para {service_name}?")
        if confirm:
            self.session.delete(entry)
            self.session.commit()
            self.load_passwords()
            messagebox.showinfo("Éxito", "Contraseña eliminada exitosamente")
        else:
            messagebox.showinfo("Cancelado", "Operación cancelada")
    
    def generate_password(self):
        length = simpledialog.askinteger("Generar Contraseña", "Longitud de la Contraseña:", minvalue=8, maxvalue=64)
        if not length:
            return
        use_special = messagebox.askyesno("Generar Contraseña", "¿Incluir caracteres especiales?")
        password = generate_password(length=length, use_special=use_special)
        messagebox.showinfo("Contraseña Generada", f"Contraseña: {password}")
    
    def logout(self):
        self.current_user = None
        self.main_frame.destroy()
        self.create_login_frame()

def launch_gui():
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()
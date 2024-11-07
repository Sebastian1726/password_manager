import argparse
from .gui import launch_gui
from .cli import launch_cli

def main():
    parser = argparse.ArgumentParser(description="Gestor de Contraseñas")
    parser.add_argument('--cli', action='store_true', help='Usar interfaz de línea de comandos')
    args = parser.parse_args()
    
    if args.cli:
        launch_cli()
    else:
        launch_gui()

if __name__ == "__main__":
    main()
import subprocess
import sys

# --- Paso 1: Verificar si Docker está instalado en el sistema ---
def check_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False

# --- Paso 2: Si no está, mostrar mensaje con link de descarga ---
def show_docker_install_message():
    print("\n[ERROR] Docker no está instalado en tu sistema.")
    print("➡ Instalación en Linux (Ubuntu/Debian): https://docs.docker.com/engine/install/ubuntu/")
    print("➡ Instalación en Windows: https://docs.docker.com/desktop/install/windows/")
    print("➡ Instalación en macOS: https://docs.docker.com/desktop/install/mac/")
    sys.exit(1)

# --- Paso 3: Importar librería docker-py sólo si está disponible ---
try:
    import docker
except ImportError:
    print("\n[ERROR] Falta la librería de Python `docker`.")
    print("Instalala con: pip install docker\n")
    sys.exit(1)

# --- Paso 4: Crear el contenedor demo con 3 BDs ---
def create_demo_container():
    client = docker.from_env()

    print("\n📦 Creando contenedor 'demo' con 3 bases de datos...")

    client.containers.run(
        "ubuntu:20.04",
        name="demo",
        command="sleep infinity",  # contenedor base que siempre corre
        detach=True,
        tty=True
    )

    print("✅ Contenedor base 'demo' creado.")

    # Ahora podemos instalar dentro del contenedor Mongo, Neo4j y Postgres
    print("⚙ Instalando dependencias dentro del contenedor...")
    client.containers.get("demo").exec_run("apt-get update && apt-get install -y postgresql mongodb neo4j", user="root")

    print("✅ Bases de datos instaladas dentro del contenedor 'demo'.")

# --- MAIN ---
if __name__ == "__main__":
    if not check_docker_installed():
        show_docker_install_message()
    else:
        create_demo_container()

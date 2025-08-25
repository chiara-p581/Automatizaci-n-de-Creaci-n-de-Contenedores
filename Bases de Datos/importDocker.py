import subprocess
import sys
import docker
from docker.errors import NotFound, APIError

# --- Paso 1: Verificar si Docker está instalado ---
def check_docker_installed():
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False

# --- Paso 2: Mostrar mensaje si falta Docker ---
def show_docker_install_message():
    print("\n[ERROR] Docker no está instalado en tu sistema.")
    print("➡ Linux: https://docs.docker.com/engine/install/ubuntu/")
    print("➡ Windows: https://docs.docker.com/desktop/install/windows/")
    print("➡ macOS: https://docs.docker.com/desktop/install/mac/")
    sys.exit(1)

# --- Paso 3: Crear network (si no existe) ---
def get_or_create_network(client, net_name="multi_db_net"):
    try:
        net = client.networks.get(net_name)
        print(f"[OK] Network '{net_name}' ya existe")
    except NotFound:
        net = client.networks.create(net_name, driver="bridge")
        print(f"[OK] Network '{net_name}' creada")
    return net

# --- Paso 4: Función para levantar contenedores de forma segura ---
def run_container(client, name, image, **kwargs):
    try:
        c = client.containers.get(name)
        c.remove(force=True)
        print(f"[INFO] Contenedor '{name}' eliminado previamente")
    except NotFound:
        pass

    try:
        cont = client.containers.run(image, name=name, detach=True, **kwargs)
        print(f"[OK] Contenedor '{name}' levantado")
        return cont
    except APIError as e:
        print(f"[ERROR] No se pudo levantar '{name}': {e}")

# --- Paso 5: Crear stack completo ---
def create_db_stack():
    client = docker.from_env()
    net = get_or_create_network(client, "multi_db_net")

    # PostgreSQL
    run_container(
        client,
        "pg_db",
        "postgres:15",
        environment={
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "adminpass",
            "POSTGRES_DB": "mydb"
        },
        network=net.name,
        ports={"5432/tcp": 5432}
    )

    # MongoDB
    run_container(
        client,
        "mongo_db",
        "mongo:7",
        network=net.name,
        ports={"27017/tcp": 27017}
    )

    # Neo4j
    run_container(
        client,
        "neo4j_db",
        "neo4j:5",
        environment={"NEO4J_AUTH": "neo4j/adminpass"},
        network=net.name,
        ports={"7474/tcp": 7474, "7687/tcp": 7687}
    )

    print("\n✅ Stack completo levantado en la red 'multi_db_net'")
    print("💡 Contenedores disponibles:")
    print("- PostgreSQL: pg_db (5432)")
    print("- MongoDB: mongo_db (27017)")
    print("- Neo4j: neo4j_db (7474/7687)")
    print("\nAccedé con las herramientas oficiales de cada DB")

# --- MAIN ---
if __name__ == "__main__":
    if not check_docker_installed():
        show_docker_install_message()
    else:
        create_db_stack()

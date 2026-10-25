import subprocess
import os

def main():
    port = os.environ.get("PORT", "10000")
    # Запускаем встроенный прокси-сервер на нужном порту
    subprocess.run(["python", "-m", "proxy", "--hostname", "0.0.0.0", "--port", port, "--num-workers", "4"])

if __name__ == "__main__":
    main()

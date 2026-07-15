"""
Servidor de rele para Tic Tac Toe 3D - Multijugador.
------------------------------------------------------
No conoce las reglas del juego: solo acepta EXACTAMENTE 2 jugadores,
le dice a cada uno si es el Jugador 0 o el Jugador 1, y reenvia cada
mensaje que le manda un cliente al otro cliente.

Uso:
    python server.py            (usa el puerto 5555 por defecto)
    python server.py 6000       (usa el puerto 6000)

Es 100% gratis: solo usa la libreria estandar de Python (no requiere
instalar nada). Puedes correrlo:
  - En tu propio PC + un tunel ngrok (ver README_JUGAR.md), o
  - En una VM gratuita en la nube (Oracle Cloud Free Tier, etc.)
"""
import socket
import threading
import sys

HOST = "0.0.0.0"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5555

clientes = []
lock = threading.Lock()


def manejar(conn, jugador):
    conn.sendall(("PLAYER," + str(jugador) + "\n").encode())
    try:
        print("Jugador", jugador, "conectado desde", conn.getpeername())
    except OSError:
        pass

    buffer = ""
    while True:
        try:
            data = conn.recv(1024)
        except OSError:
            break
        if not data:
            break
        buffer += data.decode()
        while "\n" in buffer:
            linea, buffer = buffer.split("\n", 1)
            if not linea:
                continue
            with lock:
                otro = clientes[1 - jugador] if len(clientes) == 2 else None
            if otro:
                try:
                    otro.sendall((linea + "\n").encode())
                except OSError:
                    pass
    print("Jugador", jugador, "desconectado")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(4)
    print("Servidor escuchando en " + HOST + ":" + str(PORT) + " ...")
    print("Esperando a que se conecten 2 jugadores...")

    while len(clientes) < 2:
        conn, addr = server.accept()
        with lock:
            clientes.append(conn)
            jugador = len(clientes) - 1
        threading.Thread(target=manejar, args=(conn, jugador), daemon=True).start()

    print("Los 2 jugadores estan conectados. La partida puede comenzar.")
    threading.Event().wait()  # mantiene vivo el proceso principal


if __name__ == "__main__":
    main()

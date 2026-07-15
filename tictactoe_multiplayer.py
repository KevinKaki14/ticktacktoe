"""
Tic Tac Toe 3D - Version Multijugador (dos PCs, cualquier distancia)
----------------------------------------------------------------------
Basado en el juego original de tablero 4x4x4 en Tkinter. Se le agrego
una capa de red (sockets + threading) para que cada jugador juegue
desde su propio computador, conectandose a un servidor de rele
(server.py, incluido junto a este archivo).

COMO JUGAR (100% gratis, ver tambien README_JUGAR.md):
  1. El jugador "anfitrion" corre:  python server.py
  2. El anfitrion expone su servidor a internet con ngrok (gratis):
        ngrok tcp 5555
     ngrok entrega una direccion tipo: 0.tcp.ngrok.io:12345
  3. Ambos jugadores corren:  python tictactoe_multiplayer.py
     - El anfitrion, cuando se le pida host/puerto, escribe: localhost / 5555
     - El otro jugador escribe el host/puerto que dio ngrok.
  4. El servidor asigna Jugador 1 (X) y Jugador 2 (O). Jugador 1 empieza.
"""

from tkinter import *
from tkinter import messagebox, simpledialog
import socket
import threading
import queue

# ---------------------------------------------------------------------
# Estado del juego (igual que el original)
# ---------------------------------------------------------------------
jugadas = [[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
           [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]]
botones = []
X = Y = Z = jugador = g = 0

# ---------------------------------------------------------------------
# Estado de red
# ---------------------------------------------------------------------
sock = None
mi_jugador = None          # 0 o 1, lo asigna el servidor al conectar
cola_red = queue.Queue()   # mensajes recibidos por la red, se procesan
                            # en el hilo principal (Tkinter no es thread-safe)


def enviar(msg):
    """Envia un mensaje de texto al servidor (que lo reenvia al rival)."""
    if sock is None:
        return
    try:
        sock.sendall((msg + "\n").encode())
    except OSError:
        pass


def hilo_receptor():
    """Corre en un hilo aparte: solo lee del socket y mete lo recibido
    en una cola. NO toca la interfaz directamente (no es seguro)."""
    buffer = ""
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:
            cola_red.put("DISCONNECT")
            break
        buffer += data.decode()
        while "\n" in buffer:
            linea, buffer = buffer.split("\n", 1)
            if linea:
                cola_red.put(linea)


def procesar_cola():
    """Se ejecuta cada 100ms en el hilo principal (via tablero.after).
    Aqui SI es seguro tocar la interfaz."""
    try:
        while True:
            msg = cola_red.get_nowait()
            if msg == "DISCONNECT":
                messagebox.showinfo("Conexion", "El rival se desconecto.")
            elif msg.startswith("PLAYER,"):
                global mi_jugador
                mi_jugador = int(msg.split(",")[1])
                texto_estado.config(
                    text="Conectado. Eres el Jugador " + str(mi_jugador + 1)
                )
            elif msg.startswith("MOVE,"):
                i = int(msg.split(",")[1])
                aplicar_jugada(i)
            elif msg == "RESET":
                inicio()
    except queue.Empty:
        pass
    tablero.after(100, procesar_cola)


def conectar(host, puerto):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, puerto))
    threading.Thread(target=hilo_receptor, daemon=True).start()


# ---------------------------------------------------------------------
# Interfaz / logica del juego
# ---------------------------------------------------------------------
def crearBoton(valor, i):
    return Button(tablero, text=valor, width=5, height=1, font=("Helvetica", 15),
                  command=lambda i=i: botonClick(i))


def seguir_o_finalizar():
    resp = messagebox.askyesno("FINALIZAR", "¿Quieres continuar?")
    if resp:
        if g:
            inicio()
            enviar("RESET")   # avisa al rival para que tambien reinicie
    else:
        try:
            if sock is not None:
                sock.close()
        except OSError:
            pass
        tablero.destroy()
    return


def botonClick(i):
    """Handler de click LOCAL. Valida turno/conexion y, si es valido,
    aplica la jugada y la envia por la red."""
    if g:
        seguir_o_finalizar()
        return
    if mi_jugador is None:
        messagebox.showinfo("Espera", "Todavia no estas conectado al servidor.")
        return
    if jugador != mi_jugador:
        messagebox.showinfo("Espera", "No es tu turno todavia.")
        return

    z = int(i / 16)
    y = int(i % 16)
    yy = int(y / 4)
    xx = int(y % 4)
    if jugadas[z][yy][xx]:
        texto = Label(tablero, text='Jugada Inválida ', font='arial, 20', fg='green')
        texto.place(x=20, y=5)
        return

    aplicar_jugada(i)
    enviar("MOVE," + str(i))


def aplicar_jugada(i):
    """Aplica una jugada al tablero (venga de un click local ya validado,
    o de una jugada recibida del rival por la red). Es la misma logica
    del juego original, solo que separada del control de turno."""
    global X, Y, Z, jugador

    Z = int(i / 16)
    y = int(i % 16)
    Y = int(y / 4)
    X = int(y % 4)
    Label(tablero, text='X=' + str(X), font='arial, 20', fg='green').place(x=20, y=50)
    Label(tablero, text='Y=' + str(Y), font='arial, 20', fg='green').place(x=20, y=100)
    Label(tablero, text='Z=' + str(Z), font='arial, 20', fg='green').place(x=20, y=150)

    if jugadas[Z][Y][X]:
        return  # proteccion extra por si llega una jugada repetida

    Label(tablero, text='                          ', font='arial, 20', fg='grey').place(x=20, y=5)
    if jugador == 0:
        texto = "X"
        jugadas[Z][Y][X] = -1
        botones[i].config(text="X", font='arial 15', fg='blue')
    else:
        texto = "O"
        jugadas[Z][Y][X] = 1
        botones[i].config(text="O", font='arial 15', fg='red')

    if horizontal():
        ganador()
        for x in range(4):
            botones[Z*16+Y*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if vertical():
        ganador()
        for y in range(4):
            botones[Z*16+y*4+X].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if profundidad():
        ganador()
        for z in range(4):
            botones[z*16+Y*4+X].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if X == Y and diagonal_frontal1():
        ganador()
        for x in range(4):
            y = x
            botones[Z*16+y*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if X+Y == 3 and diagonal_frontal2():
        ganador()
        for x in range(4):
            y = x
            botones[Z*16+(3-y)*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if X == Z and diagonal_horizontal1():
        ganador()
        for x in range(4):
            z = x
            botones[z*16+Y*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if X+Z == 3 and diagonal_horizontal2():
        ganador()
        for x in range(4):
            z = x
            botones[(3-z)*16+Y*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if Y == Z and diagonal_vertical1():
        ganador()
        for y in range(4):
            z = y
            botones[z*16+y*4+X].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if Y+Z == 3 and diagonal_vertical2():
        ganador()
        for y in range(4):
            z = y
            botones[(3-z)*16+y*4+X].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if X == Y and Y+Z == 3 and diagonal_cruzada1():
        ganador()
        for x in range(4):
            z = y = x
            botones[z*16+(3-y)*4+(3-x)].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if Z == X and Y+Z == 3 and diagonal_cruzada2():
        ganador()
        for x in range(4):
            z = y = x
            botones[z*16+(3-y)*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if Y == Z and X+Y == 3 and diagonal_cruzada3():
        ganador()
        for x in range(4):
            z = y = x
            botones[z*16+y*4+(3-x)].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return
    if Z == Y and Y == X and diagonal_cruzada4():
        ganador()
        for x in range(4):
            z = y = x
            botones[z*16+y*4+x].config(text=texto, font='arial 15', fg='yellow', bg='red')
        return

    if not g:
        jugador = not jugador
        estado = "Tu turno" if jugador == mi_jugador else "Turno del rival"
        texto_turno = Label(tablero, text='Jugador ' + str(int(jugador) + 1) + ' (' + estado + ')',
                             font='arial, 20', fg='green')
        texto_turno.place(x=430, y=620)


def ganador():
    global g
    texto = Label(tablero, text='Jugador ' + str(int(jugador) + 1) + ' GANO', font='arial, 20', fg='blue')
    texto.place(x=20, y=5)
    g = 1


def horizontal():
    s = 0
    for x in range(4):
        s += jugadas[Z][Y][x]
    return not (-4 < s < 4)


def vertical():
    s = 0
    for y in range(4):
        s += jugadas[Z][y][X]
    return not (-4 < s < 4)


def profundidad():
    s = 0
    for z in range(4):
        s += jugadas[z][Y][X]
    return not (-4 < s < 4)


def diagonal_frontal1():
    s = 0
    for x in range(4):
        y = x
        s += jugadas[Z][y][x]
    return not (-4 < s < 4)


def diagonal_frontal2():
    s = 0
    for y in range(4):
        s += jugadas[Z][y][3-y]
    return not (-4 < s < 4)


def diagonal_horizontal1():
    s = 0
    for z in range(4):
        s += jugadas[z][Y][z]
    return not (-4 < s < 4)


def diagonal_horizontal2():
    s = 0
    for z in range(4):
        s += jugadas[3-z][Y][z]
    return not (-4 < s < 4)


def diagonal_vertical1():
    s = 0
    for z in range(4):
        s += jugadas[z][z][X]
    return not (-4 < s < 4)


def diagonal_vertical2():
    s = 0
    for z in range(4):
        s += jugadas[3-z][z][X]
    return not (-4 < s < 4)


def diagonal_cruzada1():
    s = 0
    for x in range(4):
        s += jugadas[3-x][x][x]
    return not (-4 < s < 4)


def diagonal_cruzada2():
    s = 0
    for x in range(4):
        s += jugadas[x][3-x][x]
    return not (-4 < s < 4)


def diagonal_cruzada3():
    s = 0
    for y in range(4):
        s += jugadas[3-y][3-y][y]
    return not (-4 < s < 4)


def diagonal_cruzada4():
    s = 0
    for z in range(4):
        s += jugadas[z][z][z]
    return not (-4 < s < 4)


def inicio():
    global jugadas, X, Y, Z, jugador, g, botones
    for z in range(4):
        for y in range(4):
            for x in range(4):
                jugadas[z][y][x] = 0
                botones[z*16+y*4+x].config(text='', font='arial 15', fg='blue', bg='white')
    X = Y = Z = jugador = g = 0
    estado = "Tu turno" if (mi_jugador == 0) else "Turno del rival"
    texto = Label(tablero, text='Jugador 1 (' + estado + ')', font='arial, 20', fg='green')
    texto.place(x=430, y=620)


# ---------------------------------------------------------------------
# Arranque
# ---------------------------------------------------------------------
tablero = Tk()
tablero.title('Tic Tac Toe 3D - Multijugador')
try:
    tablero.iconbitmap('cubo.ico')
except Exception:
    pass
tablero.geometry("1040x720+100+5")
tablero.resizable(0, 0)

for b in range(64):
    botones.append(crearBoton(' ', b))

contador = 0
for z in range(3, -1, -1):
    for y in range(4):
        for x in range(4):
            botones[contador].grid(row=y+z*4, column=x+(3-z)*4)
            contador += 1

texto_estado = Label(tablero, text='Conectando...', font='arial, 16', fg='purple')
texto_estado.place(x=500, y=580)

inicio()

botonexit = Button(tablero, text='Exit', width=5, height=1, font=("Helvetica", 15), command=seguir_o_finalizar)
botonexit.grid(row=0, column=10)

# Pide los datos de conexion ANTES de arrancar el loop principal.
host_ip = simpledialog.askstring("Conexion", "IP o direccion del servidor:",
                                  initialvalue="localhost", parent=tablero)
puerto = simpledialog.askinteger("Conexion", "Puerto del servidor:",
                                  initialvalue=5555, parent=tablero)

if host_ip and puerto:
    try:
        conectar(host_ip, puerto)
    except OSError as e:
        messagebox.showerror("Error de conexion", "No se pudo conectar al servidor:\n" + str(e))
else:
    messagebox.showwarning("Sin conexion", "No ingresaste servidor/puerto. Jugaras sin red.")

tablero.after(100, procesar_cola)
tablero.mainloop()

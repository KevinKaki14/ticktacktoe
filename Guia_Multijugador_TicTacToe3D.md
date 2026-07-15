# Cómo convertir tu Tic Tac Toe 3D en un juego multijugador por internet

Tu juego actual (`4 Tic TacToe 3D - V2 - PARTE V FINAL-Jugadas.py`) es un tablero de 4x4x4 hecho en Tkinter donde los dos jugadores se turnan en la **misma ventana, en el mismo PC**. Para que cada jugador juegue desde su propio computador, sin importar la distancia, necesitas una **arquitectura cliente-servidor**: cada PC ejecuta un "cliente" (tu interfaz Tkinter) y ambos se conectan a un "servidor" que transmite las jugadas de uno al otro.

Esto se hace en Python con el módulo `socket` (comunicación TCP) y `threading` (para recibir datos sin congelar la interfaz). Esa parte es igual en las tres opciones. Lo que cambia entre opciones es **dónde vive el servidor** y cómo los dos PCs lo encuentran a través de internet.

---

## Las 3 opciones

### Opción A — Servidor propio en la nube (VPS) — Recomendada

Subes un pequeño script `server.py` a una máquina en internet que esté encendida todo el tiempo (ej. Oracle Cloud Free Tier, un droplet de DigitalOcean, Railway, Fly.io). Esa máquina tiene una IP pública fija. Ambos jugadores, sin importar en qué país o red estén, simplemente conectan su cliente a esa IP.

**Por qué la recomiendo:**
- Es la única opción que garantiza que funcione siempre, sin depender de la red doméstica de ninguno de los dos jugadores.
- No requiere que ninguno de los jugadores toque la configuración de su router.
- El servidor sigue disponible aunque ambos jugadores apaguen su PC — pueden jugar otro día sin volver a configurar nada.
- Es la arquitectura real que se usa en juegos multijugador de verdad, así que es lo más sólido para presentar como proyecto final.
- Existen niveles gratuitos suficientes para esto (una VM Oracle Cloud "Always Free", o un worker de Railway/Fly.io).

**Contras:** hay que crear una cuenta y hacer un despliegue inicial (subir el script, abrir el puerto). Es el único paso "extra" comparado con las otras opciones, pero se hace una sola vez.

### Opción B — Túnel con ngrok

Uno de los jugadores corre el servidor en su propio PC (localhost) y usa ngrok (ngrok.com) para exponer ese puerto a internet temporalmente. El otro jugador se conecta a la URL que genera ngrok.

**Ventajas:** cero configuración de red, se levanta en segundos, bueno para probar rápido o para una entrega/demo puntual.

**Contras:** con la cuenta gratuita, la URL de ngrok cambia cada vez que reinicias el túnel, así que hay que volver a compartirla cada sesión de juego. Además, el PC del jugador que hostea tiene que estar prendido y con ngrok corriendo mientras juegan — si lo cierra, el otro se desconecta.

Buena opción como **plan B** o para pruebas rápidas antes de montar el VPS.

### Opción C — Port forwarding manual

El jugador que hostea configura su router para redirigir un puerto (ej. 5555) hacia su PC, y comparte su IP pública con el otro jugador.

**Ventajas:** no depende de ningún servicio externo, no tiene costo.

**Contras:** requiere tener acceso de administrador al router (imposible en muchas redes universitarias, corporativas o de algunos ISPs), expone la IP y el puerto del PC del jugador directamente a internet (riesgo de seguridad), y **no funciona en absoluto** si el proveedor de internet usa CGNAT (cada vez más común en conexiones residenciales) — en ese caso ni siquiera abriendo el puerto en el router se logra la conexión.

Es la opción menos confiable de las tres para un requisito de "sin importar la distancia".

---

## Comparación rápida

| | Confiabilidad "cualquier distancia" | Dificultad inicial | Depende del PC de un jugador |
|---|---|---|---|
| A. VPS propio | Alta | Media (una vez) | No |
| B. ngrok | Media | Baja | Sí |
| C. Port forwarding | Baja (falla con CGNAT) | Media-Alta | Sí |

**Opción final recomendada: A — servidor propio en la nube.**

---

## Paso a paso — Opción A (VPS + sockets)

### 1. Elegir y preparar la máquina en la nube

Necesitas una VM que permita mantener un proceso corriendo indefinidamente y abrir un puerto TCP (no todos los "hosting gratuitos" lo permiten, ej. algunos PaaS solo aceptan HTTP). Opciones que sí sirven:

- **Oracle Cloud "Always Free"**: una VM Linux gratis para siempre, permite abrir cualquier puerto.
- **Railway / Fly.io**: tienen planes con "workers" de proceso persistente (no solo web).
- Un VPS económico (DigitalOcean, Hetzner, etc.) si tu institución/profesor lo permite.

Pasos generales una vez tienes la VM:
1. Conéctate por SSH.
2. Instala Python si no está: `sudo apt install python3`.
3. Abre el puerto que vayas a usar (ej. 5555) en el firewall de la nube (panel del proveedor) **y** en el firewall del sistema operativo (`ufw allow 5555`).

### 2. Escribir el servidor de relé (`server.py`)

El servidor no necesita duplicar toda la lógica del juego — su trabajo es: aceptar exactamente 2 conexiones, decirle a cada una si es el "Jugador 0" o "Jugador 1", y reenviar cada jugada que llega de un cliente al otro.

Idea general del código:

```python
import socket, threading

HOST, PORT = "0.0.0.0", 5555
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

clientes = []

def manejar(conn, jugador):
    conn.send(f"PLAYER,{jugador}\n".encode())
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # reenviar la jugada al otro cliente
            otro = clientes[1 - jugador]
            otro.send(data)
        except ConnectionResetError:
            break

while len(clientes) < 2:
    conn, _ = server.accept()
    clientes.append(conn)
    threading.Thread(target=manejar, args=(conn, len(clientes)-1), daemon=True).start()
```

Corre esto en la VM con `python3 server.py`, e idealmente usando `tmux`, `screen` o un servicio `systemd` para que siga corriendo aunque cierres la sesión SSH.

### 3. Definir el protocolo de mensajes

Antes de tocar el cliente, define un formato simple de texto para lo que viaja por el socket, por ejemplo:

- `PLAYER,<0|1>` → el servidor le dice al cliente qué jugador es al conectarse.
- `MOVE,<indice>` → una jugada (el `i` que ya usa tu función `botonClick(i)`).
- `RESET` → reiniciar el tablero.

Termina cada mensaje con `\n` para saber dónde corta uno y empieza el siguiente al leer el socket.

### 4. Modificar tu archivo Tkinter (el cliente)

Cambios sobre tu código actual:

1. **Al arrancar:** conectar al socket con la IP pública de tu VPS, y esperar el mensaje `PLAYER,<n>` para guardar `mi_jugador = n`.
2. **En `botonClick(i)`:** antes de aplicar la jugada, comprobar que `jugador == mi_jugador` (o sea, que es tu turno). Si es válido, aplicas la jugada como ya lo haces, y además envías `f"MOVE,{i}\n"` por el socket.
3. **Hilo receptor:** crear un `threading.Thread` que quede en bucle haciendo `sock.recv()`. Cuando llega `MOVE,<i>` del rival, **no** actualices la interfaz directamente desde ese hilo (Tkinter no es "thread-safe"). En vez de eso, guarda el índice recibido en una `queue.Queue`, y usa `tablero.after(100, procesar_cola)` para que, desde el hilo principal, se llame a la misma lógica de `botonClick(i)` con la jugada del rival.
4. El resto de tu lógica (`horizontal()`, `vertical()`, `ganador()`, etc.) no cambia — sigue funcionando igual, solo que ahora se dispara tanto por clicks locales como por jugadas recibidas por red.

### 5. Probar en local primero

Antes de tocar la red real: corre `server.py` y **dos instancias** del cliente en tu mismo PC (conectando ambas a `localhost`). Esto te permite depurar la lógica de turnos y sincronización sin depender de internet.

### 6. Probar entre dos PCs distintos

1. Primero en la misma red Wi-Fi, usando la IP local de tu VPS o de tu PC.
2. Luego con el cliente conectándose a la IP pública/dominio real de la VM, desde una red totalmente distinta (ej. datos móviles del celular como hotspot) para confirmar que efectivamente funciona sin importar la distancia.

### 7. Mejoras opcionales

- Manejo de desconexiones (`try/except` alrededor del socket, avisar si el rival se desconectó).
- Reconexión automática.
- Si más adelante quieres soportar varias partidas simultáneas en el mismo servidor, agregar el concepto de "salas" (cada par de jugadores identificado por un código).

---

**Resumen:** arquitectura cliente-servidor con `socket` + `threading` en Python (igual en las 3 opciones), servidor desplegado en una VM en la nube con IP pública fija (Opción A) para que la conexión funcione siempre, sin importar dónde estén los jugadores ni la configuración de sus routers.

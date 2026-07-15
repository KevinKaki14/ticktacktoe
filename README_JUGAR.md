# Cómo jugar en línea, gratis (sin comprar VPS)

Archivos:
- `server.py` — el intermediario que conecta a los dos jugadores.
- `tictactoe_multiplayer.py` — el juego (cada jugador corre su propia copia).

Requieren solo Python 3 (sin librerías extra: `tkinter`, `socket`, `threading` y `queue` ya vienen incluidas).

## Paso a paso (host = quien organiza la partida)

1. **El anfitrión** abre una terminal en la carpeta del proyecto y corre:
   ```
   python server.py
   ```
   Debe quedar mostrando "Esperando a que se conecten 2 jugadores...". Déjala abierta.

2. **Instalar ngrok** (gratis, no pide tarjeta): descárgalo de https://ngrok.com/download, crea una cuenta gratuita y sigue las instrucciones de la web para configurar tu authtoken (`ngrok config add-authtoken <tu_token>`, el token te lo da tu panel de ngrok).

3. **El anfitrión** abre OTRA terminal y corre:
   ```
   ngrok tcp 5555
   ```
   ngrok mostrará una línea como:
   ```
   Forwarding   tcp://0.tcp.ngrok.io:12345 -> localhost:5555
   ```
   Esa dirección (`0.tcp.ngrok.io` y el puerto `12345` en este ejemplo) es lo que hay que compartirle al otro jugador. Cambia cada vez que reinicias ngrok, así que compártela de nuevo cada sesión de juego.

4. **Ambos jugadores** corren, cada uno en su propio PC:
   ```
   python tictactoe_multiplayer.py
   ```
   Va a pedir "IP o dirección del servidor" y "Puerto":
   - El **anfitrión** escribe: `localhost` y `5555`.
   - El **otro jugador** escribe el host y puerto que dio ngrok (ej. `0.tcp.ngrok.io` y `12345`).

5. El servidor asigna Jugador 1 y Jugador 2 automáticamente (se ve arriba a la derecha de la ventana). Jugador 1 empieza. Solo puedes hacer clic cuando es tu turno; si no lo es, el juego te avisa.

6. Al terminar una partida, el botón **Exit** pregunta si quieren continuar: si ambos aceptan, el tablero se reinicia sincronizado para los dos.

## Notas

- Todo esto es 100% gratuito: `server.py` corre en tu propio PC (no necesitas alquilar nada), y el plan gratuito de ngrok es suficiente para esto.
- Si más adelante quieres que el servidor esté disponible sin depender de que el PC del anfitrión esté prendido, puedes mover `server.py` a una VM gratuita (ej. Oracle Cloud Always Free) — el archivo no cambia, solo dónde lo ejecutas.
- Si `ngrok tcp` no está disponible en tu cuenta gratuita por alguna restricción regional, la alternativa sin costo es jugar dentro de la misma red Wi-Fi usando la IP local del anfitrión (se obtiene con `ipconfig` en Windows o `ifconfig`/`ip addr` en Mac/Linux) y el puerto 5555, sin necesidad de ngrok.

# Tic Tac Toe 3D — versión web, gratis, sin PC encendida y sin instalar nada

Este es un solo archivo (`index.html`) que corre en cualquier navegador. Los dos jugadores
solo necesitan abrir un link — nada de Python, nada instalado. La sincronización de las
jugadas la hace **Firebase Realtime Database** (gratis, de Google), y el archivo se aloja
en **GitHub Pages** (gratis, siempre encendido, no depende de tu PC).

Se hace una sola vez (30-40 min). Después, jugar es solo compartir el link.

---

## Parte 1 — Crear tu base de datos gratis en Firebase

1. Ve a https://console.firebase.google.com con tu cuenta de Google (no pide tarjeta).
2. **Agregar proyecto** → ponle un nombre (ej. `tictactoe3d`) → puedes **desactivar** Google
   Analytics (no hace falta) → **Crear proyecto**.
3. En el menú de la izquierda: **Compilación → Realtime Database → Crear base de datos**.
   - Elige cualquier ubicación.
   - Selecciona **"Comenzar en modo de prueba"**.
4. Entra a la pestaña **Reglas** de Realtime Database y reemplaza el contenido por esto,
   luego dale a **Publicar**:
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```
   Esto evita que las reglas de "modo de prueba" expiren solas a los 30 días. (Nota: esto
   deja la base de datos abierta a cualquiera con el link — está bien para un proyecto de
   clase; no lo uses así para una app real con datos sensibles).
5. Click en el ícono de engranaje (arriba a la izquierda) → **Configuración del proyecto**.
   Baja hasta **"Tus apps"** → click en el ícono **`</>`** (Web) → ponle un apodo a la app →
   **Registrar app** (no hace falta activar Hosting aquí).
6. Te va a mostrar un bloque de código con `const firebaseConfig = { ... }`. Copia esos
   valores.

## Parte 2 — Conectar el archivo del juego a tu base de datos

1. Abre `index.html` con un editor de texto (Bloc de notas sirve).
2. Busca este bloque cerca del final del archivo:
   ```js
   const firebaseConfig = {
     apiKey: "PEGA_AQUI_TU_apiKey",
     authDomain: "PEGA_AQUI_TU_authDomain",
     databaseURL: "PEGA_AQUI_TU_databaseURL",
     projectId: "PEGA_AQUI_TU_projectId",
     storageBucket: "PEGA_AQUI_TU_storageBucket",
     messagingSenderId: "PEGA_AQUI_TU_messagingSenderId",
     appId: "PEGA_AQUI_TU_appId"
   };
   ```
3. Reemplaza cada valor por el que copiaste de Firebase en el paso anterior. Guarda el archivo.

## Parte 3 — Publicarlo gratis (sin que tu PC tenga que estar encendida)

Usamos GitHub Pages — gratuito, siempre disponible, no requiere instalar nada en tu PC:

1. Crea una cuenta gratis en https://github.com (si no tienes una).
2. Click en **New repository** → nómbralo (ej. `tictactoe3d-online`) → que sea **Público** →
   **Create repository**.
3. Dentro del repo: **Add file → Upload files** → arrastra tu `index.html` ya editado →
   **Commit changes**.
4. Ve a **Settings → Pages** (menú de la izquierda). En **"Source"** elige la rama
   `main` y la carpeta `/root` → **Save**.
5. Espera 1-2 minutos. GitHub te va a dar una URL así:
   `https://tu-usuario.github.io/tictactoe3d-online/index.html`
   Esa es la que compartes con el otro jugador. Queda funcionando 24/7 sin depender de tu PC.

## Parte 4 — Jugar

1. Ambos jugadores abren esa URL en cualquier navegador (PC, celular, tablet — no importa).
2. Uno hace click en **"Crear partida"**: le aparece un código de 5 letras (ej. `K7QXR`).
   Se lo pasa al otro por WhatsApp, chat, etc. Ese jugador queda como **X** y empieza.
3. El otro escribe ese código en **"Unirme a una partida"** y hace click en **Unirse**.
   Queda como **O**.
4. El tablero se sincroniza solo (Firebase avisa a los dos navegadores al instante). Solo
   puedes hacer click en tu turno; el otro jugador ve tu jugada aparecer en tiempo real.
5. **Reiniciar partida** reinicia el tablero para ambos. **Salir** sale de la sala.

## Notas

- El plan gratuito de Firebase (Spark) alcanza de sobra para esto — no tiene fecha de
  vencimiento ni pide tarjeta.
- Puedes crear varias partidas distintas al mismo tiempo (cada una con su propio código),
  todas usan la misma base de datos gratis.
- Limitación conocida: si alguien recarga la página a mitad de partida, pierde su lugar en
  la sala (tendría que crear/unirse de nuevo). Se puede mejorar más adelante guardando el
  `miJugador` en el navegador (localStorage) si lo necesitas para tu entrega final.

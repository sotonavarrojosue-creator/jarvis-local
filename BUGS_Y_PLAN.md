# JARVIS — Reporte de Bugs y Plan de Reparación

> **Fecha:** 2026-06-29  
> **Autor:** Análisis comparativo con [GauravSingh9356/J.A.R.V.I.S](https://github.com/GauravSingh9356/J.A.R.V.I.S) y [danilofalcao/jarvis](https://github.com/danilofalcao/jarvis)  
> **Estado:** Voice pipeline NO FUNCIONA — WebUI no detecta micrófono, CLI tiene race conditions

---

## Resumen Ejecutivo

JARVIS tiene 13 habilidades funcionales, un brain con OpenRouter, logging a Obsidian, y un WebUI con animación de esfera. Pero el **pipeline de voz está roto** en ambos modos (CLI y WebUI). La comparación con dos proyectos de referencia reveló 10 bugs, de los cuales 4 son críticos y bloquean el funcionamiento de voz.

---

## Bugs Críticos (bloquean voz)

### BUG-1: Sin calibración de ruido ambiental
- **Archivo:** `input/voice_input.py:36-50` (`record_to_wav()`)
- **Problema:** `sd.rec()` graba sin calibrar el nivel de ruido del ambiente. Faster-whisper recibe audio con ruido de fondo sin referencia, transcribiendo basura o nada.
- **Referencia:** GauravSingh9356 usa `r.adjust_for_ambient_noise(source, duration=1.5)` antes de cada escucha.
- **Fix:** Agregar 1.5s de captura de silencio antes de cada `sd.rec()` para establecer baseline de energía. Implementar VAD (Voice Activity Detection) con `webrtcvad` o detección de energía simple.

### BUG-2: Detección de palmas no es confiable
- **Archivo:** `input/voice_input.py:70-103` (`detect_claps()`)
- **Problema:** Usa detección estadística de picos en audio raw. Cualquier ruido (tos, puerta, teclado) puede activarlo. Un clap real a veces no se detecta. No hay alternativa de wake word por voz.
- **Fix:** Reemplazar con `webrtcvad` para detección de voz + detección de energía umbral. O usar `pvporcupine` para wake word "Jarvis" (requiere key gratuita). Alternativa simple: umbral de energía > N dB durante > 0.5s = alguien hablando.

### BUG-3: Micrófono contention entre threads
- **Archivo:** `main.py:69` + `input/voice_input.py:146`
- **Problema:** El wake thread hace `record_to_wav(duration=4)` en loop, y el main thread hace `listen_once(duration=5)`. Ambos usan `sd.rec()` que en muchas configs ALSA solo permite un stream por dispositivo. Resultado: crashes silenciosos de sounddevice o audio corrupto.
- **Fix:** Agregar un `threading.Lock` en el acceso al micrófono. Solo un thread puede grabar a la vez. El wake thread debe pausarse mientras se graba un comando.

### BUG-4: WebUI — ScriptProcessor deprecado + sin feedback
- **Archivo:** `webui/templates/index.html` (JS: `createScriptProcessor`)
- **Problema:** `ScriptProcessorNode` está deprecado y causa problemas en Chrome moderno. Además, no hay feedback visual de que el micrófono esté activo, ni de lo que se transcribe, ni de errores.
- **Fix:** Usar `MediaRecorder` para capturar audio del navegador y enviarlo via HTTP POST como PCM raw. El servidor convierte a WAV y transcribe con faster-whisper. Mostrar: indicador de mic activo, transcripción en tiempo real, errores visibles.

---

## Bugs Altos (afectan estabilidad)

### BUG-5: `speak()` bloquea el hilo principal
- **Archivo:** `main.py:68`, `output/voice_output.py:49`
- **Problema:** `voice_output.speak("Te escucho")` es síncrono — bloquea 2-5 segundos mientras descarga MP3 de edge-tts, reproduce, y limpia. En `main.py` bloquea el loop principal. En `server.py` corre en thread (correcto), pero no siempre.
- **Fix:** `speak()` SIEMPRE debe ejecutarse en un thread separado. Ni siquiera el caller debería preocuparse — hacer que `speak()` lance su propio thread internamente.

### BUG-6: `asyncio.run()` crashea en contexto con event loop existente
- **Archivo:** `output/voice_output.py:48-55`
- **Problema:** `asyncio.run()` lanza `RuntimeError` si ya hay un event loop corriendo. El fallback con `asyncio.new_event_loop()` es frágil, especialmente desde daemon threads.
- **Fix:** Usar `asyncio.new_event_loop()` + `loop.run_until_complete()` SIEMPRE, nunca `asyncio.run()`. O mejor: eliminar async y usar `subprocess` para llamar `edge-tts` directamente.

### BUG-7: Modelo Whisper duplicado en memoria
- **Archivo:** `server.py:25-33` vs `input/voice_input.py:26-33`
- **Problema:** El server y voice_input cargan instancias separadas de `WhisperModel("tiny")`. Dos copias en RAM, potencialmente inconsistentes.
- **Fix:** Crear `core/whisper_singleton.py` con una función `get_whisper_model()` que retorne la misma instancia siempre. Ambos módulos importan de ahí.

---

## Bugs Medianos

### BUG-8: `tempfile.mktemp()` — race condition
- **Archivo:** `input/voice_input.py:39`, `server.py:41`
- **Problema:** `mktemp()` crea un nombre pero no el archivo. Otro proceso puede crear un archivo con el mismo nombre antes de que se use.
- **Fix:** Usar `tempfile.NamedTemporaryFile(delete=False, suffix=".wav")`.

### BUG-9: Audio player detectado cada llamada
- **Archivo:** `output/voice_output.py:37-38`
- **Problema:** `subprocess.run(["which", player])` corre 5 veces por cada `speak()`. Debería detectarse una vez en `__init__`.
- **Fix:** Cachear el player disponible en `self._player` durante `__init__`.

### BUG-10: Modo voz cae a modo texto
- **Archivo:** `main.py:64-73`
- **Problema:** `voice_input.listen()` usa `get_nowait()` que retorna `""` si no hay resultado. El loop principal cae a `get_user_input()` (texto), entonces en modo voz, si voice no está listo, pide texto — confuso.
- **Fix:** En modo `--voice`, usar `queue.get(timeout=0.5)` y hacer `continue` si no hay resultado, NUNCA caer a texto.

---

## Plan de Reparación (orden de ejecución)

### Fase 1: Infraestructura de voz (CRÍTICO — sin esto nada funciona)

| # | Tarea | Archivos | Verificación |
|---|-------|----------|-------------|
| 1 | Crear `core/whisper_singleton.py` con modelo compartido | `core/whisper_singleton.py`, `input/voice_input.py`, `webui/server.py` | Ambos módulos usan misma instancia |
| 2 | Agregar calibración de ruido + VAD de energía | `input/voice_input.py` | Whisper transcribe correctamente en ambiente ruidoso |
| 3 | Agregar mutex de micrófono | `input/voice_input.py` | No crashes por concurrent sd.rec() |
| 4 | Reemplazar ScriptProcessor por MediaRecorder + HTTP POST | `webui/templates/index.html` | Mic se activa con click, audio llega al server |

### Fase 2: Estabilidad de voz

| # | Tarea | Archivos | Verificación |
|---|-------|----------|-------------|
| 5 | `speak()` siempre en thread interno | `output/voice_output.py`, `main.py` | speak() nunca bloquea caller |
| 6 | Eliminar `asyncio.run()` → `new_event_loop()` o subprocess | `output/voice_output.py` | No RuntimeError en ningún contexto |
| 7 | Cachear player de audio en `__init__` | `output/voice_output.py` | which() solo corre una vez |
| 8 | `mktemp()` → `NamedTemporaryFile(delete=False)` | `input/voice_input.py`, `webui/server.py` | Sin race conditions |

### Fase 3: Mejoras

| # | Tarea | Archivos | Verificación |
|---|-------|----------|-------------|
| 9 | pyttsx3 como TTS fallback local | `output/voice_output.py` | Funciona sin internet |
| 10 | Modo voz: no caer a texto | `main.py` | --voice nunca pide input de texto |
| 11 | Streaming de respuesta a WebUI (SSE) | `webui/server.py`, `webui/templates/index.html` | Texto aparece progresivamente |

---

## Arquitectura Objetivo (Voice Pipeline)

```
┌─────────────────────────────────────────────────────────┐
│  NAVEGADOR (WebUI)                                      │
│                                                          │
│  Click → getUserMedia → MediaRecorder                   │
│       → chunks de audio PCM (Int16, 16kHz)              │
│       → HTTP POST /api/transcribe cada 3s               │
│                                                          │
│  Recibe: {text, wake, response} via JSON                │
│  Muestra: transcripción, estado, respuesta              │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────┐
│  SERVIDOR (Flask)                                        │
│                                                          │
│  /api/transcribe                                         │
│    → whisper_singleton.transcribe(pcm_bytes, sr)        │
│    → if wake_word(text): return {wake: true}            │
│    → if awake: brain.think(text) → voice_output.speak() │
│    → return {text, wake, response}                      │
│                                                          │
│  /status → {speaking, thinking, voice_enabled}          │
│  /voice/toggle → habilita/deshabilita voz               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CLI (--voice)                                           │
│                                                          │
│  Main loop:                                              │
│    1. VAD energy detect → alguien hablando?              │
│    2. record_wav(duration=5) CON mutex                   │
│    3. whisper.transcribe(wav)                            │
│    4. if wake_word → escuchar comando                   │
│    5. brain.think(cmd) → voice_output.speak(resp)       │
│    6. NUNCA caer a texto en modo voz                     │
└─────────────────────────────────────────────────────────┘
```

---

## Dependencias Actuales

| Paquete | Versión | Propósito | Nota |
|---------|---------|-----------|------|
| flask | 3.1.3 | WebUI server | |
| faster-whisper | 1.2.1 | STT local | tiny/int8 ~75MB |
| sounddevice | — | Mic capture CLI | Usa libportaudio2 via ctypes |
| numpy | — | Audio processing | |
| edge-tts | — | TTS | Requiere internet |
| openai | — | OpenRouter client | |
| rich | — | CLI output | |
| simpleeval | >=1.0.5 | Calculator skill | CVE-2026-32640 fix |

## Dependencias por Agregar

| Paquete | Propósito | Tamaño |
|---------|-----------|--------|
| webrtcvad | VAD para detección de voz | ~1MB |
| pyttsx3 | TTS fallback local (sin internet) | ~5MB |

---

## Wake Words Soportados

`jarvis`, `jarviz`, `jarbis`, `jarbi`, `charvis`, `yabis`, `yavis`, `yarviz`, `jarvin`, `jabis`, `javis`, `oye`, `hey`

---

## Variables de Entorno (.env)

| Variable | Propósito | Requerida |
|----------|-----------|-----------|
| OPENROUTER_API_KEY | LLM API | Sí |
| JARVIS_MODEL | Override de modelo | No |
| OPENROUTER_BASE_URL | API endpoint | Default en config |

---

## Notas para el siguiente IA

1. El servidor web esta en **Flask puro** (sin SocketIO). Se quitó SocketIO porque complicaba sin agregar valor.
2. El audio del navegador seenvia como **PCM Int16 raw** via HTTP POST, no como WebM/Opus (porque no hay ffmpeg en el sistema para decodificar).
3. **No hay sudo** en este sistema. No se pueden instalar paquetes del sistema (`apt install`). Solo `pip install` dentro del `.venv`.
4. El AudioContext del navegador usa sample rate de **48000** por default. El server lee `X-Sample-Rate` del header para escribir el WAV correctamente.
5. faster-whisper internamente resamplea a 16kHz, así que cualquier sample rate funciona.
6. El `voice_output.speak()` corre edge-tts que **requiere internet**. Si no hay internet, falla silenciosamente. pyttsx3 sería el fallback.
7. El modelo Whisper `tiny` es rápido pero impreciso. Para mejor transcripción usar `base` o `small` (más RAM/CPU).
8. Los logs de Obsidian van a `data/obsidian/logs/` — NO borrar esa carpeta.

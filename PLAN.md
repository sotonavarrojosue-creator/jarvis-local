---
title: "Plan de Mejoras — JARVIS"
date: 2026-06-25
tags: [plan, j-1]
proyecto: JARVIS
tipo: ideas
---

# Plan de Mejoras — JARVIS-LOCAL

Priorizado por impacto × esfuerzo. **J-1** = más prioritario.

---

## J-1 — Voz: entrada y salida 🎤🔊

### STT (Speech-to-Text) — reemplazar `voice_input.py`
- Usar `whisper.cpp` o `faster-whisper` (modelo pequeño, ~1 GB RAM)
- Alternativa: API de Groq Whisper (gratis, 20 req/min) vía `groq` SDK
- Grabación con `sounddevice` + `numpy`
- Activar con tecla (ej. mantener Enter para hablar)

### TTS (Text-to-Speech) — reemplazar `voice_output.py`
- Usar `edge-tts` (Microsoft Edge TTS, gratis, offline-capable, voces naturales)
- Alternativa: `pyttsx3` (offline, voces robóticas)
- Control de voz (velocidad, tono)

### Wake word — reemplazar `wake_word.py`
- Usar `porcupine` (Picovoice, gratis con límite de palabras)
- Alternativa: implementar detección local con `speech_recognition` + umbral de energía

**Impacto:** Alto — interacción natural manos libres
**Esfuerzo:** Medio (STT/ TTS cada uno ~2-3 horas, wake word ~1-2 horas)

---

## J-2 — Streaming de respuestas en tiempo real ⚡

- `brain.py`: habilitar `stream=True` en la llamada a OpenRouter
- Mostrar tokens conforme llegan con Rich `Live` en vez de esperar la respuesta completa
- Indicador visual de "escribiendo..."

**Impacto:** Alto — sensación de velocidad
**Esfuerzo:** Bajo (~1 hora)

---

## J-3 — Memoria persistente con título de sesión 💾

- `memory.py`: al iniciar sesión, preguntar "¿título de esta sesión?" o generarlo automático
- Guardar cada sesión como `data/memory/session_YYYYMMDD_HHMMSS_nombre.json`
- Comando "lista sesiones" para ver historial
- Comando "carga sesión [nombre]" para retomar conversación anterior

**Impacto:** Medio — utilidad real para seguimiento
**Esfuerzo:** Bajo (~1-2 horas)

---

## J-4 — Plugins / skills externos 🧩

- Sistema de `skills/` cargables dinámicamente desde `skills/externas/`
- Cada skill: archivo `.py` con función `handle(text) -> str`
- `skill_manager.py` escanea `skills/externas/` al iniciar
- Documentación para que el usuario pueda crear sus propias skills sin tocar el core

**Impacto:** Alto — extensibilidad infinita
**Esfuerzo:** Medio (~3-4 horas)

---

## J-5 — WebUI opcional 🌐

- Servir interfaz web con Gradio o Flask + htmx (liviano, sin JS pesado)
- Chat en navegador, misma lógica que la terminal
- Opción de correr en LAN para acceder desde el celular

**Impacto:** Medio — comodidad de uso en otros dispositivos
**Esfuerzo:** Medio-Alto (~5-8 horas)

---

## J-6 — Más skills útiles 🛠️

### Traductor
- Usar `deep-translator` (gratis, múltiples fuentes: Google, Libre, etc.)
- "traduce hola al inglés" → "hello"

### Noticias
- RSS feeds de cabeceras principales
- "últimas noticias" o "noticias de tecnología"

### Recordatorios / alarmas
- Temporizadores en segundo plano con `threading`
- "recuérdame en 10 minutos X"

### IP / Geolocalización
- "cuál es mi IP", "dónde está este servidor"
- APIs gratuitas: ip-api.com, ipify

**Impacto:** Medio-Alto — más útil en el día a día
**Esfuerzo:** Medio (~2 horas cada una)

---

## J-7 — Configuración persistente ⚙️

- `config.json` en `data/config/` para guardar preferencias
- Comando "config" para ver/editar:
  - Modelo de IA (cambiar de deepseek a otro)
  - Idioma predeterminado
  - Voz de TTS
  - Tema de Rich (colores)
- Guardar también preferencias por sesión

**Impacto:** Medio — flexibilidad para el usuario
**Esfuerzo:** Bajo (~1 hora)

---

## J-8 — Tests automáticos 🧪

- Tests unitarios con `pytest`
- `tests/test_skills.py` — probar cada skill con entradas de ejemplo
- `tests/test_brain.py` — mock de OpenRouter
- `tests/test_memory.py` — probar guardado/carga/limpieza
- CI con GitHub Actions (opcional)

**Impacto:** Medio — confianza en el código
**Esfuerzo:** Medio (~3-4 horas)

---

## J-9 — Docker / distribución 🐳

- `Dockerfile` para ejecutar sin instalar Python localmente
- `docker-compose.yml` con volúmenes para datos persistentes
- Versión portable para compartir

**Impacto:** Bajo-Medio — facilita instalación en otros equipos
**Esfuerzo:** Bajo (~1 hora)

---

## Resumen de prioridades

| # | Mejora | Impacto | Esfuerzo |
|---|--------|---------|----------|
| J-1 | Voz (STT + TTS + wake word) | 🔥 Alto | ⚡ Medio |
| J-2 | Streaming de respuestas | 🔥 Alto | ✅ Bajo |
| J-3 | Memoria por sesión | 👍 Medio | ✅ Bajo |
| J-4 | Plugins externos | 🔥 Alto | ⚡ Medio |
| J-5 | WebUI | 👍 Medio | 🐘 Medio-Alto |
| J-6 | Más skills | 🔥 Alto | ⚡ Medio |
| J-7 | Config persistente | 👍 Medio | ✅ Bajo |
| J-8 | Tests | 👍 Medio | ⚡ Medio |
| J-9 | Docker | 🔹 Bajo-Medio | ✅ Bajo |

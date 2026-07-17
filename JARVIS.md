---
title: "JARVIS-LOCAL"
date: 2026-06-25
tags: [proyecto, python, ia]
status: activo
---

# JARVIS-LOCAL

Asistente de IA tipo Jarvis que corre en terminal usando OpenRouter (modelos gratuitos).

Nodo principal del proyecto. Todo el código y documentación cuelga de acá.

## Archivos del proyecto

### Entry point
- [[Proyectos/JARVIS/main.py]] — Punto de entrada, bucle principal con Rich UI

### Core (lógica central)
- [[Proyectos/JARVIS/core/brain.py]] — Conexión a OpenRouter, sistema de prompts, memoria
- [[Proyectos/JARVIS/core/config.py]] — Config desde .env (API key, modelo, rutas)
- [[Proyectos/JARVIS/core/memory.py]] — Historial de conversación JSON (últimos 20 mensajes)

### Input (entrada)
- [[Proyectos/JARVIS/input/text_input.py]] — Captura de texto desde terminal
- [[Proyectos/JARVIS/input/voice_input.py]] — Placeholder (voz, próximamente)
- [[Proyectos/JARVIS/input/wake_word.py]] — Placeholder (wake word, próximamente)

### Output (salida)
- [[Proyectos/JARVIS/output/display.py]] — Rich UI: banners, paneles, colores
- [[Proyectos/JARVIS/output/text_output.py]] — Salida de texto simple
- [[Proyectos/JARVIS/output/voice_output.py]] — Placeholder (TTS, próximamente)

### Skills (habilidades)
- [[Proyectos/JARVIS/skills/skill_manager.py]] — Detección de intenciones y enrutamiento
- [[Proyectos/JARVIS/skills/datetime_skill.py]] — Fecha, hora, días entre fechas
- [[Proyectos/JARVIS/skills/calculator.py]] — Evaluación matemática segura (simpleeval)
- [[Proyectos/JARVIS/skills/notes.py]] — CRUD de notas en markdown
- [[Proyectos/JARVIS/skills/web_search.py]] — Búsqueda DuckDuckGo
- [[Proyectos/JARVIS/skills/weather.py]] — Clima Open-Meteo (sin API key)
- [[Proyectos/JARVIS/skills/system_control.py]] — Abrir apps y ejecutar comandos

### Configuración
- [[Proyectos/JARVIS/.env.example]] — Template de variables de entorno
- [[Proyectos/JARVIS/requirements.txt]] — Dependencias Python
### Documentación y plan
- [[Proyectos/JARVIS/PLAN]] — Plan de mejoras priorizadas (J-1 a J-9)
- [[Proyectos/JARVIS/README]] — Documentación en español

## Stack técnico

- Python 3.10+
- OpenRouter API (deepseek/deepseek-chat-v3-0324:free)
- duckduckgo_search (búsqueda web)
- Open-Meteo (clima, gratis, sin API key)
- Rich (terminal UI)
- simpleeval (matemáticas seguras)
- python-dotenv (config)

## Conexiones

- Proyecto padre: [[Proyectos/VARIOS]]
- Relacionados: —

## Progreso

- [x] Conversación con IA (OpenRouter)
- [x] Fecha y hora
- [x] Calculadora
- [x] Notas (guardar/leer/listar/eliminar)
- [x] Búsqueda web
- [x] Clima
- [x] Control del sistema
- [ ] Entrada por voz
- [ ] Salida por voz
- [ ] Wake word

# JARVIS — Bug: No detecta "JARVIS" como wake word

> **Fecha:** 2026-06-29
> **Archivos analizados:** `input/voice_input.py`, `core/whisper_singleton.py`, `input/wake_word.py`, `main.py`

---

## Causa raíz principal

**`core/whisper_singleton.py` línea 10 fuerza `language="es"`:**

```python
# ❌ PROBLEMA — Whisper en modo español no reconoce "JARVIS"
segments, _ = model.transcribe(tmp, language="es", beam_size=1)
```

"JARVIS" es una palabra inglesa/inventada. Con `language="es"`, Whisper intenta forzar la transcripción al español y produce resultados como `"harpis"`, `"jabis"`, `"yar vis"` o silencio. La comparación contra `WAKE_WORDS` falla.

---

## Fix principal

**Archivo:** `core/whisper_singleton.py`

```python
# ✅ FIX — detección automática de idioma + mayor precisión
segments, _ = model.transcribe(tmp, language=None, beam_size=5)
```

| Parámetro | Antes | Después | Por qué |
|---|---|---|---|
| `language` | `"es"` | `None` | Deja que Whisper detecte el idioma automáticamente |
| `beam_size` | `1` | `5` | Más preciso; 1 es muy agresivo y pierde palabras cortas |

---

## Bugs secundarios que también afectan la detección

### BUG-1 — Sin calibración de ruido (crítico)

**Archivo:** `input/voice_input.py` → `record_to_wav()`

Graba sin establecer un baseline de ruido ambiental. Whisper recibe audio sucio y falla o transcribe basura.

```python
# ✅ FIX — calibrar antes de grabar
noise_floor = calibrate_noise(duration=1.5)
# (la función ya existe en voice_input.py, solo falta usarla en record_to_wav)
```

---

### BUG-3 — Race condition en el micrófono (crítico)

**Archivos:** `main.py` + `input/voice_input.py`

El wake thread y el main thread llaman `sd.rec()` simultáneamente. En ALSA/Linux solo un stream puede grabar a la vez → crash silencioso o audio corrupto.

El fix ya está parcialmente implementado (`MIC_LOCK` existe en `voice_input.py`), pero verificar que **todo acceso** a `sd.rec()` pase por ese lock.

```python
# Verificar que record_to_wav() y listen_for_voice() usen MIC_LOCK
with MIC_LOCK:
    recording = sd.rec(...)
    sd.wait()
```

---

### BUG-10 — Loop principal no espera respuesta de voz

**Archivo:** `main.py`

`voice_input.listen(timeout=0.5)` usa `queue.get(timeout=0.5)` — correcto. Pero si la queue está vacía devuelve `""` y el loop hace `continue` sin procesar nada. En configuraciones lentas (Whisper tarda), el resultado llega tarde y se pierde.

```python
# ✅ FIX — en modo --voice, nunca caer a texto, solo hacer continue
if args.voice:
    user_input = voice_input.listen(timeout=0.5)
    if not user_input or user_input == "__wake__":
        continue  # seguir esperando, nunca pedir texto
```

---

## Variantes de wake word faltantes

**Archivo:** `input/voice_input.py`

Whisper en español transcribe "JARVIS" de formas distintas a las que ya están en la lista. Agregar:

```python
WAKE_WORDS = [
    "jarvis", "jarviz", "jarbis", "jarbi", "charvis",
    "yabis", "yavis", "yarviz", "jarvin", "jabis", "javis",
    "oye", "hey",
    # ✅ Agregar estas:
    "harvis", "harpis", "jarwis", "yar", "jarv",
]
```

---

## Debug temporal (para verificar qué transcribe Whisper)

Agregar temporalmente en `input/voice_input.py` dentro de `_wake_loop`:

```python
text = transcribe_wav(wav_path)
print(f"[DEBUG wake] transcribió: '{text}'")  # ← agregar esta línea
if not text:
    continue
if is_wake_word(text):
    ...
```

Así ves exactamente qué está oyendo Whisper cuando decís "JARVIS".

---

## Orden de fixes recomendado

| Prioridad | Archivo | Cambio |
|---|---|---|
| 🔴 1 | `core/whisper_singleton.py` | `language=None, beam_size=5` |
| 🔴 2 | `input/voice_input.py` | Agregar variantes al `WAKE_WORDS` |
| 🟡 3 | `input/voice_input.py` | Verificar que `MIC_LOCK` cubra todos los `sd.rec()` |
| 🟡 4 | `main.py` | Fix del loop en modo `--voice` |
| 🟢 5 | `input/voice_input.py` | Print de debug temporal |

from deep_translator import GoogleTranslator

def handle_translator(text: str) -> str:
    try:
        t = text.lower()
        target = "en"
        query = text
        lang_map = {"ingles": "en", "inglés": "en", "english": "en", "portugues": "pt", "frances": "fr", "italiano": "it", "aleman": "de", "chino": "zh", "japones": "ja", "coreano": "ko", "arabe": "ar", "ruso": "ru", "holandes": "nl"}
        for word in t.replace(",","").split():
            if word in lang_map:
                target = lang_map[word]
        if "traduce " in t:
            query = text.split("traduce ", 1)[1]
        elif "translate " in t:
            query = text.split("translate ", 1)[1]
        for w in ["to", "al", "into"]:
            if f" {w} " in query.lower():
                idx = query.lower().index(f" {w} ")
                query = query[:idx].strip()
                break
        translated = GoogleTranslator(source="auto", target=target).translate(query.strip())
        return f"Translation ({target}): {translated}"
    except Exception as e:
        return f"Translation error: {e}"

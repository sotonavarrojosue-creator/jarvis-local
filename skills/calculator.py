from simpleeval import simple_eval, NameNotDefined
from rich.console import Console

console = Console()


def evaluate_math(expression: str) -> str:
    """Evaluar expresiones matemáticas de forma segura usando simpleeval"""
    try:
        # Limpiar la expresión
        expr = expression.strip()
        # Reemplazar comunes en español/inglés
        expr = expr.replace("^", "**")
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        expr = expr.replace(",", ".")

        resultado = simple_eval(expr)
        return f"🧮 {expression} = {resultado}"

    except NameNotDefined:
        return "No pude resolver esa expresión. Contiene variables no definidas."
    except SyntaxError:
        return "La expresión matemática tiene un error de sintaxis."
    except ZeroDivisionError:
        return "No se puede dividir entre cero, señor."
    except Exception as e:
        return f"No pude calcular eso: {e}"


def handle_calculator(text: str) -> str:
    """Manejar consultas de cálculo matemático"""
    # Extraer la expresión matemática del mensaje
    text_lower = text.lower()

    # Patrones comunes para detectar solicitudes de cálculo
    patrones = [
        "calcula", "calcula ", "calcular ", "cuánto es ", "cuanto es ",
        "resuelve ", "evalúa ", "evalua ", "compute ", "calculate ",
        "math ", "mát ",
    ]

    expr = text
    for patron in patrones:
        if text_lower.startswith(patron):
            expr = text[len(patron):]
            break

    # Si la expresión empieza con "de " o similar, limpiarla
    expr = expr.strip()
    if expr.startswith("de "):
        expr = expr[3:]

    return evaluate_math(expr)

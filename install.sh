#!/usr/bin/env bash
# JARVIS — Instalador para Ubuntu/Debian.
# Uso:  bash install.sh
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "══════════════════════════════════════"
echo "  Instalando J.A.R.V.I.S."
echo "══════════════════════════════════════"

# 1. Dependencias del sistema
echo "[1/4] Dependencias del sistema..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip \
    portaudio19-dev libasound2-dev pulseaudio-utils mpg123 \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1 2>/dev/null || \
sudo apt-get install -y -qq python3 python3-venv python3-pip \
    portaudio19-dev libasound2-dev pulseaudio-utils mpg123 \
    python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0

# 2. Entorno virtual + paquetes Python
echo "[2/4] Paquetes de Python (puede tardar unos minutos)..."
python3 -m venv .venv --system-site-packages
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

# 3. Lanzador
echo "[3/4] Creando lanzador..."
cat > jarvis-app.sh <<EOF
#!/usr/bin/env bash
cd "$DIR"
exec "$DIR/.venv/bin/python" app.py
EOF
chmod +x jarvis-app.sh

# 4. Entrada en el menú de aplicaciones
echo "[4/4] Registrando en el menú de aplicaciones..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/jarvis.desktop <<EOF
[Desktop Entry]
Type=Application
Name=JARVIS
Comment=Asistente personal de IA
Exec=$DIR/jarvis-app.sh
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;
StartupNotify=true
EOF
update-desktop-database ~/.local/share/applications 2>/dev/null || true

echo ""
echo "✓ Listo. Busca «JARVIS» en tu menú de aplicaciones,"
echo "  o ejecuta:  ./jarvis-app.sh"
echo ""
echo "  La primera vez, abre Ajustes (⚙) y pega tu API key de OpenRouter."

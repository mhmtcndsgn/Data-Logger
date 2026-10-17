"""Derlenen Windows klasöründeki her dosyanın SHA-256 parmak izini yazar.

    python packaging/make_manifest.py dist/Data_Logger

Çıktı: dist/Data_Logger/_internal/manifest.sha256
Uygulama bu listeyle kendi klasörünü doğrular (Yardım > Hakkında > Dosyaları doğrula)
ve Windows'un indirme etiketini sadece listedeki, değişmemiş dosyalardan kaldırır.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from stm32logger.system import manifest_path, write_manifest  # noqa: E402

root = sys.argv[1] if len(sys.argv) > 1 else os.path.join("dist", "Data_Logger")
out = manifest_path(root)
n = write_manifest(root, out)
print(f"{n} dosya -> {out}")

#!/usr/bin/env bash
# Установка окружения для пайплайна (без root).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"

# 1) Python-окружение
python3 -m venv "$HERE/venv"
"$HERE/venv/bin/pip" install -q -r "$HERE/requirements.txt"
echo "[ok] venv + зависимости"

# 2) LibreDWG (dwg2dxf) — только если ещё не установлен
if ! command -v dwg2dxf >/dev/null && [ ! -x "$HOME/.local/bin/dwg2dxf" ]; then
  echo "[..] собираю LibreDWG в ~/.local (нужны gcc, autotools, swig)"
  tmp="$(mktemp -d)"
  git clone --depth 1 https://github.com/LibreDWG/libredwg.git "$tmp/libredwg"
  cd "$tmp/libredwg"
  ./autogen.sh
  ./configure --prefix="$HOME/.local" --disable-bindings --disable-python
  make -j"$(nproc)"
  make install
  echo "[ok] dwg2dxf -> ~/.local/bin"
else
  echo "[ok] dwg2dxf уже есть"
fi

echo
echo "Готово. Пример запуска:"
echo "  $HERE/venv/bin/python $HERE/generate_genplan.py путь/к/топосъёмке.dwg --out результат --boundary-color 1 --target-ha 18"

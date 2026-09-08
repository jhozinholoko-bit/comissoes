# -*- coding: utf-8 -*-
"""Gera tests/runner.html injetando o JS real de index.html no harness.

Uso:
    python tests/build.py       # a partir da raiz do repo
    # depois abra tests/runner.html no navegador

O harness nao reimplementa nada: ele executa as funcoes reais do app
(buildTimeline, deriveClient, changeValue, getValueOverride...).
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
HARNESS = os.path.join(ROOT, 'tests', 'comissoes.test.html')
OUT = os.path.join(ROOT, 'tests', 'runner.html')

html = io.open(SRC, encoding='utf-8').read()
m = re.search(r'<script>\s*var DATA = JSON\.parse.*?</script>', html, re.S)
if not m:
    sys.exit('nao encontrei o bloco <script> principal em index.html')
js = m.group(0)[len('<script>'):-len('</script>')]

# Sem DOM real: remove o bootstrap e o pull-to-refresh (liga em elementos ausentes).
js = js.replace('loadState(function() { render(); });', '// [teste] bootstrap removido')
js = re.sub(r'// ── Pull-to-refresh ──\s*\(function\(\) \{.*?\n\}\)\(\);',
            '// [teste] pull-to-refresh removido', js, flags=re.S)
js = js.replace('function render() {',
                'function render() {\n  if (window.__NO_RENDER__) { buildTimeline(); return; }')

harness = io.open(HARNESS, encoding='utf-8').read()
marker = '// The app source is injected here at runtime by the runner (see run_tests.py).'
if marker not in harness:
    sys.exit('marcador nao encontrado no harness')

io.open(OUT, 'w', encoding='utf-8').write(
    harness.replace(marker, 'window.__NO_RENDER__ = true;\n' + js))
print('gerado:', OUT)
print('abra no navegador para ver o resultado dos testes')

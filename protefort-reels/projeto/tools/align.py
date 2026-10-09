"""Turn ElevenLabs Scribe word timestamps into animation cues.
usage: python3 align.py <words.json> <cues.js out> [lead]
words.json: list of {"text": str, "start": float, "end": float} (Scribe `words`)."""
import sys, json, re, unicodedata

words = json.load(open(sys.argv[1]))
if isinstance(words, dict): words = words.get('words', words)
words = [w for w in words if w.get('type', 'word') == 'word' and w['text'].strip()]
lead = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0   # seconds of silence added before the VO in the mix

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn'))

# cue -> accepted spellings, in script order
SEQ = [('seu', ['seu']), ('pesado', ['pesado']), ('entao', ['entao']), ('calcado', ['calcado']), ('forte', ['forte']),
       ('lama', ['lama']), ('impacto', ['impacto']), ('horas', ['horas']), ('protefort1', ['a', 'protefort']),
       ('aguenta', ['aguenta']), ('tudo', ['tudo']), ('comvoce', ['com']), ('direto', ['direto']), ('mococa', ['mococa']),
       ('anos', ['25', 'vinte', 'vinteecinco']), ('protegendo', ['protegendo']), ('brasil', ['brasil']),
       ('botinas', ['botinas']), ('coturnos', ['coturnos']), ('tenis', ['tenis']), ('sapatos', ['sapatos']),
       ('seguranca', ['seguranca']), ('todos', ['todos']), ('ca', ['ca', 'ce', 'cea', 'c']), ('bidensidade', ['bidensidade', 'bi']),
       ('conforto', ['conforto']), ('firmeza', ['firmeza']), ('primeiro', ['do', 'primeiro']), ('passo', ['passo']),
       ('obra', ['obra']), ('industria', ['industria']), ('hospital', ['hospital']), ('campo', ['campo']),
       ('protecao', ['protecao']), ('forte2', ['forte']), ('protefort', ['protefort', 'proteforte']),
       ('calcados', ['calcados']), ('verdade', ['verdade'])]

toks = [norm(w['text']) for w in words]
cues, i = {}, 0
for name, alts in SEQ:
    j = next((k for k in range(i, len(toks)) if toks[k] in alts or any(toks[k].startswith(a) for a in alts if len(a) > 3)), None)
    if j is None:
        print('WARN not found:', name); continue
    cues[name] = round(words[j]['start'] + lead, 3); i = j + 1
# fill gaps by interpolation
names = [n for n, _ in SEQ]
for k, n in enumerate(names):
    if n not in cues:
        prev = next((cues[names[a]] for a in range(k - 1, -1, -1) if names[a] in cues), 0.2)
        nxt = next((cues[names[a]] for a in range(k + 1, len(names)) if names[a] in cues), prev + 1)
        cues[n] = round((prev + nxt) / 2, 3)
last_end = words[-1]['end'] + lead
cues['cta'] = round(last_end + 0.45, 3)
cues['end'] = round(last_end + 3.4, 3)
open(sys.argv[2], 'w').write('window.CUES = ' + json.dumps(cues, indent=1) + ';\n')
print(json.dumps(cues))

"""Gera assets/logo.js com os paths do logo Inter (símbolo + letras) e a geometria dos raios."""
import json

d = json.load(open("assets/logo_paths.json"))
names = ["e", "i", "n", "t", "r", "sym", "e_hole"]
p = dict(zip(names, d["word"]["paths"]))
logo = {
    "viewBox": [70, 240, 1060, 285],
    "symbol": p["sym"],
    "letters": {"i": p["i"], "n": p["n"], "t": p["t"], "e": p["e"] + p["e_hole"], "r": p["r"]},
    "letterCenters": {"i": [389, 405], "n": [538, 403], "t": [697, 380], "e": [878, 404], "r": [1066, 403]},
    "symbolBox": [79.76, 297.43, 299.0, 510.5],
    # pivô dos raios (canto inferior, centro da barra vertical) medido na imagem do símbolo
    "pivot": [278.7, 510.5],
    # ângulos (graus, anti-horário a partir de +x) de cada peça e limites das cunhas de recorte
    "pieces": [
        {"angle": 90.0, "from": -40, "to": 101.5},
        {"angle": 111.0, "from": 101.5, "to": 120.0},
        {"angle": 128.5, "from": 120.0, "to": 137.5},
        {"angle": 144.5, "from": 137.5, "to": 151.5},
        {"angle": 157.5, "from": 151.5, "to": 163.0},
        {"angle": 168.5, "from": 163.0, "to": 174.0},
        {"angle": 179.0, "from": 174.0, "to": 200.0},
    ],
}
open("assets/logo.js", "w").write("window.LOGO = " + json.dumps(logo) + ";\n")
print("ok", sum(len(v) for v in logo["letters"].values()) + len(logo["symbol"]), "chars")

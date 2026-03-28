"""
=============================================================
 SISTEMA INTELIGENTE DE RUTAS - MEGABÚS PEREIRA
 Inteligencia Artificial Avanzada
 Basado en: Benítez R. (2014) - Inteligencia artificial avanzada
   Cap. 2: Lógica y representación del conocimiento
   Cap. 3: Sistemas basados en reglas (reglas IF-THEN)
   Cap. 9: Técnicas basadas en búsquedas heurísticas (A*)
=============================================================
"""

import heapq
import math
from typing import Optional

# 1. BASE DE CONOCIMIENTO (Cap. 2)

ESTACIONES = {
    "Terminal de Transportes":  (4.7865, -75.6960),
    "Cuba":                     (4.7918, -75.7060),
    "Los Alpes":                (4.7955, -75.7090),
    "El Plumón":                (4.7980, -75.7100),
    "El Remanso":               (4.8005, -75.7080),
    "Villa del Prado":          (4.8030, -75.7060),
    "Circunvalar":              (4.8070, -75.7020),
    "Av. Las Américas":         (4.8090, -75.7050),
    "San Mateo":                (4.8110, -75.7070),
    "Única":                    (4.8050, -75.6960),
    "Centro (Cl. 19)":          (4.8120, -75.6990),
    "Plaza de Bolívar":         (4.8130, -75.6980),
    "Lago Uribe Uribe":         (4.8145, -75.6975),
    "El Cable":                 (4.8150, -75.6950),
    "Av. 30 de Agosto":         (4.8100, -75.6940),
    "Ciudad Jardín":            (4.8080, -75.6920),
    "Álamos":                   (4.8060, -75.6900),
    "Brodway":                  (4.8040, -75.6885),
    "Simón Bolívar":            (4.8180, -75.6870),
    "La Popa":                  (4.8200, -75.6850),
    "Dosquebradas Centro":      (4.8340, -75.6730),
    "Los Molinos":              (4.8380, -75.6690),
    "Tráfico":                  (4.8420, -75.6650),
    "Terminal Dosquebradas":    (4.8460, -75.6600),
}

CONEXIONES_RAW = [
    ("Terminal de Transportes", "Cuba",                  6),
    ("Cuba",                    "Los Alpes",             4),
    ("Los Alpes",               "El Plumón",             3),
    ("El Plumón",               "El Remanso",            3),
    ("El Remanso",              "Villa del Prado",       3),
    ("Villa del Prado",         "Circunvalar",           5),
    ("Circunvalar",             "Av. Las Américas",      4),
    ("Av. Las Américas",        "San Mateo",             3),
    ("San Mateo",               "Centro (Cl. 19)",       5),
    ("Centro (Cl. 19)",         "Plaza de Bolívar",      2),
    ("Plaza de Bolívar",        "Lago Uribe Uribe",      3),
    ("Lago Uribe Uribe",        "El Cable",              4),
    ("El Cable",                "Av. 30 de Agosto",      3),
    ("Av. 30 de Agosto",        "Ciudad Jardín",         4),
    ("Ciudad Jardín",           "Álamos",                3),
    ("Álamos",                    
                                "Simón Bolívar",         4),
    ("Simón Bolívar",           "La Popa",               3),
    ("La Popa",                 "Dosquebradas Centro",   8),
    ("Dosquebradas Centro",     "Los Molinos",           4),
    ("Los Molinos",             "Tráfico",               4),
    ("Tráfico",                 "Terminal Dosquebradas", 4),
    ("Centro (Cl. 19)",         "Lago Uribe Uribe",      3),
    ("Lago Uribe Uribe",        "Plaza de Bolívar",      3),
    ("Centro (Cl. 19)",         "Única",                 3),
    ("Única",                   "Circunvalar",           4),
    ("Única",                   "Brodway",               5),
    ("Av. 30 de Agosto",        "Simón Bolívar",         6),
    ("El Cable",                "Plaza de Bolívar",      3),
]

GRAFO = {}
for _a, _b, _t in CONEXIONES_RAW:
    GRAFO.setdefault(_a, []).append((_b, _t))
    GRAFO.setdefault(_b, []).append((_a, _t))

INTERCAMBIADORES_CENTRALES = {"Centro (Cl. 19)", "Lago Uribe Uribe", "Plaza de Bolívar"}

# 2. REGLAS LÓGICAS (Cap. 3)

REGLAS = [
    {"id":"R1","nombre":"Conexión rápida",
     "descripcion":"SI tiempo_tramo <= 3 min ENTONCES priorizar (factor 0.80)",
     "condicion": lambda o, d, c, ctx: c <= 3, "factor": 0.80},
    {"id":"R2","nombre":"Tramo largo",
     "descripcion":"SI tiempo_tramo >= 8 min ENTONCES penalizar (factor 1.25)",
     "condicion": lambda o, d, c, ctx: c >= 8, "factor": 1.25},
    {"id":"R3","nombre":"Estación bloqueada",
     "descripcion":"SI destino IN lista_evitar ENTONCES bloquear (infinito)",
     "condicion": lambda o, d, c, ctx: d in ctx.get("evitar", set()), "factor": float("inf")},
    {"id":"R4","nombre":"Estación preferida",
     "descripcion":"SI destino IN lista_preferidas ENTONCES reducir fuerte (factor 0.65)",
     "condicion": lambda o, d, c, ctx: d in ctx.get("preferidas", set()), "factor": 0.65},
    {"id":"R5","nombre":"Hora pico",
     "descripcion":"SI hora_pico = True ENTONCES congestión (factor 1.40)",
     "condicion": lambda o, d, c, ctx: ctx.get("hora_pico", False), "factor": 1.40},
    {"id":"R6","nombre":"Intercambiador central",
     "descripcion":"SI destino ES intercambiador central → nodo estratégico (factor 0.90)",
     "condicion": lambda o, d, c, ctx: d in INTERCAMBIADORES_CENTRALES, "factor": 0.90},
]

class MotorInferencia:
    """Encadenamiento hacia adelante sobre las reglas lógicas."""
    def aplicar_reglas(self, origen, destino, costo_base, contexto):
        costo = costo_base
        disparadas = []
        for regla in REGLAS:
            if regla["condicion"](origen, destino, costo_base, contexto):
                if regla["factor"] == float("inf"):
                    return float("inf"), disparadas + [regla["id"]]
                costo *= regla["factor"]
                disparadas.append(regla["id"])
        return round(costo, 3), disparadas

# 3. HEURÍSTICA HAVERSINE (Cap. 9)

def heuristica_haversine(a, b):
    """Distancia geográfica real convertida a minutos (admisible para A*)."""
    lat1, lon1 = ESTACIONES[a]
    lat2, lon2 = ESTACIONES[b]
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    x = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(x), math.sqrt(1-x)) * 2.73

# 4. ALGORITMO A* (Cap. 9)

class SistemaMegabus:
    """Sistema inteligente de rutas Megabús Pereira.
    Combina A* con motor de inferencia basado en reglas lógicas.
    f(n) = g(n) + h(n)  donde:
      g(n) = costo acumulado ajustado por reglas lógicas
      h(n) = heurística Haversine al destino (admisible)
    """
    def __init__(self):
        self.motor = MotorInferencia()

    def encontrar_ruta(self, origen, destino, contexto=None):
        if contexto is None:
            contexto = {}
        for est in (origen, destino):
            if est not in ESTACIONES:
                return {"exito": False,
                        "error": f"Estación '{est}' no existe en la base de conocimiento."}
        if origen == destino:
            return {"exito":True,"ruta":[origen],"costo_total":0,"costo_base":0,
                    "paradas":0,"log_detallado":[]}

        cola = []
        heapq.heappush(cola, (0.0, 0.0, origen, [origen], []))
        visitados = {}

        while cola:
            f, g, nodo, camino, log = heapq.heappop(cola)
            if nodo == destino:
                return {"exito":True, "ruta":camino,
                        "costo_total": round(g,2),
                        "costo_base": sum(e["costo_base"] for e in log),
                        "paradas": len(camino)-1,
                        "log_detallado": log}
            if visitados.get(nodo, float("inf")) <= g:
                continue
            visitados[nodo] = g
            for vecino, costo_base in GRAFO.get(nodo, []):
                if visitados.get(vecino, float("inf")) <= g:
                    continue
                c_adj, reglas = self.motor.aplicar_reglas(nodo, vecino, costo_base, contexto)
                if c_adj == float("inf"):
                    continue
                g_n = g + c_adj
                h_n = heuristica_haversine(vecino, destino)
                entrada = {"tramo":f"{nodo} → {vecino}", "costo_base":costo_base,
                           "costo_ajustado":c_adj, "reglas":reglas, "h":round(h_n,2)}
                heapq.heappush(cola, (g_n+h_n, g_n, vecino,
                                      camino+[vecino], log+[entrada]))

        return {"exito":False, "error":"No existe ruta entre las estaciones indicadas."}

    def listar_estaciones(self):
        return sorted(ESTACIONES.keys())

# 5. INTERFAZ DE CONSOLA

def sep(c="═", n=65): print(c*n)

def imprimir_resultado(res):
    sep()
    if not res.get("exito"):
        print(f"  ✗  {res.get('error')}")
        sep(); return
    ruta, total, base, paradas, log = (res["ruta"], res["costo_total"],
        res["costo_base"], res["paradas"], res["log_detallado"])
    print(f"  ✔  RUTA ENCONTRADA — {paradas} parada(s)\n")
    for i, est in enumerate(ruta):
        icono = "🚌 INICIO " if i==0 else ("🏁 DESTINO" if i==len(ruta)-1 else f"   [{i:>2}]   ")
        t = f"  ({log[i-1]['costo_ajustado']} min)" if i>0 else ""
        print(f"  {icono}  {est}{t}")
    print(f"\n  ⏱  Tiempo estimado : {total} min  (base: {base} min)")
    print(f"  📍 Paradas          : {paradas}")
    conteo = {}
    for e in log:
        for r in e["reglas"]: conteo[r] = conteo.get(r,0)+1
    if conteo:
        print(f"\n  📋 Reglas disparadas:")
        for r_id, n in sorted(conteo.items()):
            regla = next(r for r in REGLAS if r["id"]==r_id)
            print(f"     {r_id} ({n}×) {regla['nombre']} → factor {regla['factor']}")
    print(f"\n  📝 Log por tramo:")
    for e in log:
        regs = ", ".join(e["reglas"]) if e["reglas"] else "ninguna"
        print(f"     {e['tramo']:<44} base={e['costo_base']}' → aj={e['costo_ajustado']}'  [{regs}]")
    sep()

def menu_interactivo():
    sistema = SistemaMegabus()
    ests = sistema.listar_estaciones()
    sep(); print("  🚌  MEGABÚS PEREIRA — SISTEMA INTELIGENTE DE RUTAS")
    print("       A* + Reglas Lógicas + Heurística Haversine"); sep()
    print("\n  Estaciones disponibles:")
    for i, e in enumerate(ests, 1): print(f"    {i:>2}. {e}")

    def leer(prompt):
        while True:
            v = input(f"\n  {prompt}: ").strip()
            if v in ESTACIONES: return v
            try:
                idx = int(v)-1
                if 0 <= idx < len(ests): return ests[idx]
            except ValueError: pass
            print("  ⚠  No válida. Usa nombre exacto o número.")

    print("\n" + "─"*65)
    origen  = leer("ORIGEN  (nombre o número)")
    destino = leer("DESTINO (nombre o número)")
    hora_pico = input("\n  ¿Hora pico? (s/n) [n]: ").strip().lower() == "s"
    ev_raw = input("  Estaciones a EVITAR (coma o Enter): ").strip()
    evitar = set(e.strip() for e in ev_raw.split(",") if e.strip() in ESTACIONES)
    pref_raw = input("  Estaciones PREFERIDAS (coma o Enter): ").strip()
    preferidas = set(e.strip() for e in pref_raw.split(",") if e.strip() in ESTACIONES)
    ctx = {"hora_pico": hora_pico, "evitar": evitar, "preferidas": preferidas}
    print(f"\n  🔍 Calculando: '{origen}' → '{destino}'\n")
    imprimir_resultado(sistema.encontrar_ruta(origen, destino, ctx))

# 6. PRUEBAS AUTOMÁTICAS

def ejecutar_pruebas():
    s = SistemaMegabus()
    casos = [
        {"titulo":"PRUEBA 1 — Ruta básica: Terminal de Transportes → Terminal Dosquebradas",
         "origen":"Terminal de Transportes","destino":"Terminal Dosquebradas","ctx":{}},
        {"titulo":"PRUEBA 2 — Hora pico: Cuba → Dosquebradas Centro",
         "origen":"Cuba","destino":"Dosquebradas Centro","ctx":{"hora_pico":True}},
        {"titulo":"PRUEBA 3 — Bloquear Centro (Cl. 19)",
         "origen":"Terminal de Transportes","destino":"Terminal Dosquebradas",
         "ctx":{"evitar":{"Centro (Cl. 19)"}}},
        {"titulo":"PRUEBA 4 — Preferir Lago Uribe Uribe",
         "origen":"Villa del Prado","destino":"La Popa",
         "ctx":{"preferidas":{"Lago Uribe Uribe"}}},
        {"titulo":"PRUEBA 5 — Ruta corta: El Plumón → El Remanso",
         "origen":"El Plumón","destino":"El Remanso","ctx":{}},
        {"titulo":"PRUEBA 6 — Estación inválida (manejo de error)",
         "origen":"Estacion Inexistente","destino":"Cuba","ctx":{}},
    ]
    sep(); print("  🧪  PRUEBAS AUTOMÁTICAS — MEGABÚS PEREIRA"); sep()
    for c in casos:
        print(f"\n  ▶  {c['titulo']}")
        imprimir_resultado(s.encontrar_ruta(c["origen"], c["destino"], c["ctx"]))



#  ENTRADA

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        {"--pruebas": ejecutar_pruebas,
         "--reglas":  lambda: MotorInferencia().mostrar_reglas()
        }.get(sys.argv[1], lambda: print("Uso: python megabus_pereira.py [--pruebas|--reglas]"))()
    else:
        menu_interactivo()


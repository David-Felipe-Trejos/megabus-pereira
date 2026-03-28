
SISTEMA INTELIGENTE DE RUTAS
Megabús Pereira
Algoritmo A*  ·  Reglas Lógicas IF-THEN  ·  Heurística Haversine

Asignatura
Inteligencia Artificial Avanzada	Sistema
Megabús — Pereira, Colombia	Referencia
Benítez R. (2014) — Cap. 2, 3, 9

 
1. Descripción del sistema

Sistema experto desarrollado en Python que calcula la mejor ruta en la red de transporte masivo Megabús de Pereira (Risaralda, Colombia). Integra tres técnicas de Inteligencia Artificial Avanzada:

Componente	Técnica utilizada	Capítulo Benítez
Base de conocimiento	Hechos y relaciones lógicas	Cap. 2
Motor de inferencia	Reglas IF-THEN (forward chaining)	Cap. 3
Algoritmo de búsqueda	A* con heurística Haversine	Cap. 9

2. Red de estaciones — 24 estaciones reales


Troncal Cuba	Terminal de Transportes → Cuba → Los Alpes → El Plumón → El Remanso → Villa del Prado
Troncal Centro	Circunvalar → Av. Las Américas → San Mateo → Centro (Cl. 19) → Plaza de Bolívar → Lago Uribe Uribe → El Cable → Av. 30 de Agosto → Ciudad Jardín → Álamos
Troncal Dosquebradas	Simón Bolívar → La Popa → Dosquebradas Centro → Los Molinos → Tráfico → Terminal Dosquebradas
Estaciones de conexión	Única  |  San Mateo  |  El Cable  |  Plaza de Bolívar

3. Reglas lógicas IF-THEN

El motor de inferencia evalúa 6 reglas en encadenamiento hacia adelante para cada arco del grafo:
ID	Condición (SI...)	Acción (ENTONCES...)
R1	tiempo_tramo <= 3 min	Reducir costo 20%  (conexión rápida)
R2	tiempo_tramo >= 8 min	Aumentar costo 25%  (tramo largo)
R3	estación IN lista_evitar	Bloquear conexión completamente
R4	estación IN lista_preferidas	Reducir costo 35%
R5	hora_pico = True	Aumentar costo 40%  (congestión)
R6	estación = intercambiador	Reducir costo 10%  (nodo estratégico)

4. Fundamento teórico — Algoritmo A*

El algoritmo A* combina el costo acumulado real con una heurística admisible:
f(n)  =  g(n)  +  h(n)

g(n) = costo acumulado ajustado por reglas lógicas
h(n) = distancia Haversine al destino convertida a minutos
       (nunca sobreestima → heurística ADMISIBLE → A* ÓPTIMO)

Heurística Haversine
Calcula la distancia geográfica real entre dos estaciones usando sus coordenadas GPS. Velocidad media del Megabús: 22 km/h → 1 km ≈ 2.73 minutos.

5. Instalación y ejecución

Requisitos
•	Python 3.8 o superior
•	Sin dependencias externas (solo módulos estándar: heapq, math)

Comandos
# Modo interactivo (menú en consola)
python megabus_pereira.py

# Ejecutar las 6 pruebas automáticas
python megabus_pereira.py --pruebas

# Ver las reglas de la base de conocimiento
python megabus_pereira.py --reglas

# Guardar resultados en archivo
python megabus_pereira.py --pruebas > resultados.txt

6. Ejemplo de salida

═══════════════════════════════════════════════════════
  ✔  RUTA ENCONTRADA — 14 parada(s)

  🚌 INICIO    Terminal de Transportes
     [ 1]      Cuba                         (6 min)
     [ 2]      Los Alpes                    (4 min)
     [ 3]      El Plumón                    (2.4 min)  [R1]
     [ 4]      El Remanso                   (2.4 min)  [R1]
     [ 5]      Villa del Prado              (2.4 min)  [R1]
     ...        ...
  🏁 DESTINO   Terminal Dosquebradas

  ⏱  Tiempo estimado : 59.6 min  (base: 60 min)
  📍 Paradas          : 14
  📋 Reglas: R1 (4×) conexión rápida · R2 (1×) tramo largo
═══════════════════════════════════════════════════════

7. Repositorio y entregables


Código fuente	megabus_pereira.py — lógica completa del sistema
Repositorio Git	[Agregar link de GitHub aquí]
Video explicativo	[Agregar link del video aquí — máx. 5 min]
PDF de pruebas	pruebas.pdf — capturas de pantalla de los 6 casos

Inteligencia Artificial Avanzada  ·  Megabús Pereira  ·  Benítez R. (2014) Caps. 2, 3 y 9


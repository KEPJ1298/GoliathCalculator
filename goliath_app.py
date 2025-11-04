import streamlit as st
import pandas as pd
import itertools
from math import prod
import os

st.set_page_config(page_title="Calculadora Goliath avanzada", layout="centered")

st.title("🏈 Calculadora Goliath Avanzada")
st.markdown("""
Esta herramienta te muestra:
- 💰 **Ganancia actual**
- 🟢 **Si los pendientes ganan**
- 🔴 **Si los pendientes pierden**
- 🔢 **Total de combinaciones**
- 💵 **Apuesta por combinación**
""")

# (Opcional) Muestra la ruta del archivo por si tienes dudas de dónde está corriendo
# st.info(f"Ruta de este archivo: `{os.path.abspath(__file__)}`")

# === 1. Entrada manual ===
st.subheader("➕ Añade tus selecciones")

num = st.number_input("¿Cuántas selecciones quieres añadir?", 1, 20, 8)
data = []
for i in range(int(num)):
    cols = st.columns(3)
    sel = cols[0].text_input(f"Selección #{i+1}", key=f"sel_{i}")
    odd = cols[1].text_input("Cuota americana (+110 o -143)", key=f"odd_{i}")
    res = cols[2].selectbox("Resultado", ["Pendiente", "Ganó", "Perdió"], key=f"res_{i}")
    data.append({"selection": sel, "american_odds": odd, "result": res})

df = pd.DataFrame(data)
st.write("### Tus selecciones")
st.dataframe(df)

# === 2. Monto principal de la apuesta ===
st.subheader("💵 Monto principal de la apuesta")
main_stake = st.number_input("Ingresa el monto total a apostar ($)", min_value=0.01, value=10.0, step=0.01, format="%.2f")

# === 3. Funciones auxiliares ===
def american_to_decimal(odd):
    try:
        odd = float(odd)
        return 1 + (odd / 100) if odd > 0 else 1 + (100 / abs(odd))
    except:
        return 1.0

def format_money(x):
    return "${:,.2f}".format(x)

def calculate_scenarios(df, main_stake=1):
    total_combos = 0
    actual_win = 0
    all_pending_win = 0
    all_pending_lose = 0

    # Identifica los índices de los pendientes
    pending_indices = [i for i, r in enumerate(df["result"]) if r == "Pendiente"]

    # Calcula todas las combinaciones posibles (de 2 a N)
    combos = []
    for r in range(2, len(df) + 1):
        combos += list(itertools.combinations(df.itertuples(), r))
    total_combos = len(combos)

    stake_per_bet = main_stake / total_combos if total_combos > 0 else 0

    for combo in combos:
        odds = [american_to_decimal(c.american_odds) for c in combo]
        res = [c.result for c in combo]

        # Ganancia actual: solo las combinaciones donde no hay "Perdió"
        if "Perdió" in res:
            continue
        # Si hay pendientes, solo cuenta las ganadas hasta ahora
        if "Pendiente" in res:
            current_win = prod([american_to_decimal(c.american_odds) if c.result == "Ganó" else 1 for c in combo])
            actual_win += current_win * stake_per_bet
        else:
            actual_win += prod(odds) * stake_per_bet

        # Si los pendientes GANAN: trata todos los "Pendiente" como "Ganó"
        odds_win = [
            american_to_decimal(c.american_odds)
            for c in combo
        ]
        all_pending_win += prod(odds_win) * stake_per_bet

        # Si los pendientes PIERDEN: si algún pendiente está en la combinación, la apuesta se pierde
        if any(c.result == "Pendiente" for c in combo):
            # Si hay al menos un pendiente en la combinación, se pierde
            continue
        else:
            all_pending_lose += prod(odds) * stake_per_bet

    return {
        "Ganancia actual": format_money(actual_win),
        "Si pendientes GANAN": format_money(all_pending_win),
        "Si pendientes PIERDEN": format_money(all_pending_lose),
        "Total de combinaciones": total_combos,
        "Apuesta por combinación": format_money(stake_per_bet),
    }

# === 4. Cálculo ===
if st.button("Calcular escenarios"):
    if df.empty:
        st.warning("Por favor añade al menos una selección.")
    else:
        summary = calculate_scenarios(df, main_stake)
        st.success("Resultados calculados exitosamente ✅")
        st.write("### 💹 Resumen de escenarios")
        st.table(pd.DataFrame(summary, index=["Monto estimado"]).T)
else:
    st.info("Completa tus selecciones, ingresa el monto y presiona **Calcular escenarios** para ver los resultados.")
st.caption("Versión 1.0 — Calculadora hecha por KEPJ1298 🧠")
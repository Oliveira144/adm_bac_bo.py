import streamlit as st
from datetime import datetime
import time
from collections import defaultdict, Counter

# Estilo visual
st.set_page_config(page_title="BAC BO LIVE ANALYZER", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #0F0F0F;
        color: #F8F8F2;
    }
    .stButton>button {
        background-color: #222;
        color: #F8F8F2;
        border: 2px solid #444;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-size: 1.2em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #444;
        border-color: #888;
        cursor: pointer;
    }
    .big-text {
        font-size: 1.4em;
        font-weight: bold;
        color: #00BFFF;
    }
    .box {
        border: 1px solid #333;
        background-color: #1C1C1C;
        padding: 1em;
        border-radius: 10px;
        margin-bottom: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa session_state
if "results" not in st.session_state:
    st.session_state["results"] = []
if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = None
if "stats" not in st.session_state:
    st.session_state["stats"] = {}

# Estatísticas
def calculate_stats():
    results = st.session_state["results"]
    total = len(results)
    player_count = sum(1 for r in results if r["result"] == "Player")
    banker_count = sum(1 for r in results if r["result"] == "Banker")
    tie_count = sum(1 for r in results if r["result"] == "Tie")

    streak = 1
    max_player = max_banker = 0
    if total > 0:
        t = results[0]["result"]
        for i in range(1, total):
            if results[i]["result"] == results[i-1]["result"] and results[i]["result"] != "Tie":
                streak += 1
            else:
                if results[i-1]["result"] == "Player":
                    max_player = max(max_player, streak)
                elif results[i-1]["result"] == "Banker":
                    max_banker = max(max_banker, streak)
                streak = 1
    current_streak = streak if results[0]["result"] != "Tie" else 0
    st.session_state["stats"] = {
        "total": total,
        "player": player_count,
        "banker": banker_count,
        "tie": tie_count,
        "streaks": {"player": max_player, "banker": max_banker, "current": current_streak}
    }

# Sequência atual
# Sequência atual
def get_streak_info():
    recent = [r for r in st.session_state["results"] if r["result"] != "Tie"][:10]
    if not recent:
        return None
    streak = 1
    current = recent[0]["result"]
    for i in range(1, len(recent)):
        if recent[i]["result"] == current:
            streak += 1
        else:
            break
    return {"type": current, "count": streak} if streak > 1 else None

# Adiciona resultado
def add_result(result):
    novo = {
        "id": int(time.time() * 1000),
        "result": result,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state["results"] = [novo] + st.session_state["results"]
    calculate_stats()
    generate_recommendation()

# Reset histórico
def reset_data():
    st.session_state["results"] = []
    st.session_state["recommendation"] = None

# Função dinâmica atualizada 🧠🔥
def scan_for_dynamic_patterns():
    raw = [r["result"] for r in st.session_state["results"]]
    results = [r for r in raw if r != "Tie"]

    min_block = 3
    max_block = 8
    from collections import defaultdict, Counter
    pattern_counter = defaultdict(list)

    for block_size in range(min_block, max_block + 1):
        for i in range(len(results) - block_size - 1):
            bloco = tuple(results[i:i + block_size])
            proximo = results[i + block_size]
            pattern_counter[bloco].append(proximo)

    ocorrencias = []
    for padrao, respostas in pattern_counter.items():
        depois = Counter(respostas).most_common(1)[0]
        proporcao = depois[1] / len(respostas)
        ocorrencias.append({
            "pattern": padrao,
            "next": depois[0],
            "count": len(respostas),
            "confidence": int(proporcao * 100)
        })

    if ocorrencias:
        ocorrencias = sorted(ocorrencias, key=lambda x: (x["confidence"], x["count"]), reverse=True)
        escolhido = ocorrencias[0]
        if escolhido["count"] >= 1 and escolhido["confidence"] >= 40:
            return {
                "bet": escolhido["next"],
                "confidence": min(escolhido["confidence"], 100),
                "strategy": f"Padrão dinâmico {len(escolhido['pattern'])}x observado",
                "reasoning": f"O padrão {escolhido['pattern']} ocorreu {escolhido['count']} vez(es) e geralmente é seguido por {escolhido['next']}"
            }
    return None


    generate_recommendation()

# Reset histórico
def reset_data():
    st.session_state["results"] = []
    st.session_state["recommendation"] = None

# NOVO MÓDULO: Varredura dinâmica de padrões
def scan_for_dynamic_patterns():
    results = [r["result"] for r in st.session_state["results"]]
    min_block = 3
    max_block = 8
    pattern_counter = defaultdict(list)

    for block_size in range(min_block, max_block + 1):
        for i in range(len(results) - block_size - 1):
            bloco = tuple(results[i:i + block_size])
            proximo = results[i + block_size]
            pattern_counter[bloco].append(proximo)

    ocorrencias = []
    for padrao, respostas in pattern_counter.items():
        if len(respostas) >= 2:
            depois = Counter(respostas).most_common(1)[0]
            ocorrencias.append({
                "pattern": padrao,
                "next": depois[0],
                "count": len(respostas),
                "confidence": int((depois[1] / len(respostas)) * 100)
            })

    if ocorrencias:
        ocorrencias = sorted(ocorrencias, key=lambda x: (x["confidence"], x["count"]), reverse=True)
        escolhido = ocorrencias[0]
        return {
            "bet": escolhido["next"],
            "confidence": min(escolhido["confidence"], 100),
            "strategy": f"Padrão recorrente {len(escolhido['pattern'])}x detectado",
            "reasoning": f"O padrão {escolhido['pattern']} ocorreu {escolhido['count']} vezes e geralmente é seguido por {escolhido['next']}"
        }
    return None

# Gera recomendação com todos os padrões
def generate_recommendation():
    results = st.session_state["results"]
    if len(results) < 5:
        st.session_state["recommendation"] = {
            "bet": "Aguarde",
            "confidence": 0,
            "strategy": "Coletando dados...",
            "reasoning": f"Menos de 5 resultados registrados ({len(results)})"
        }
        return

    freq = {"Player": 0, "Banker": 0, "Tie": 0}
    for r in results:
        freq[r["result"]] += 1

    ordered = results[::-1]
    last_non_tie = [r for r in ordered if r["result"] != "Tie"]
    strategies = []

    # Zig Zag
    if len(last_non_tie) >= 6:
        if all(last_non_tie[i]["result"] != last_non_tie[i-1]["result"] for i in range(1, 6)):
            next_bet = "Banker" if last_non_tie[0]["result"] == "Player" else "Player"
            strategies.append({"bet": next_bet, "weight": 3, "reason": "Padrão Zig Zag"})

    # 2x2
    if len(last_non_tie) >= 6:
        seq = [r["result"] for r in last_non_tie[:6]]
        if seq[0] == seq[1] and seq[2] == seq[3] and seq[4] == seq[5] and seq[0] != seq[2] and seq[2] == seq[4]:
            next_bet = "Player" if seq[5] == "Banker" else "Banker"
            strategies.append({"bet": next_bet, "weight": 4, "reason": "Padrão 2x2 detectado"})

    # 2-1-2
    if len(last_non_tie) >= 5:
        seq = [r["result"] for r in last_non_tie[:5]]
        if seq[0] == seq[1] and seq[3] == seq[4] and seq[0] == seq[3] and seq[2] != seq[0]:
            strategies.append({"bet": seq[2], "weight": 3, "reason": "Padrão 2-1-2 detectado"})

    # Streak
    streak = 1
    atual = results[0]["result"]
    for i in range(1, len(results)):
        if results[i]["result"] == atual and atual != "Tie":
            streak += 1
        else:
            break
    if streak >= 4:
        strategies.append({"bet": atual, "weight": 4, "reason": f"{streak} {atual} consecutivos"})

    # Frequência
    if freq["Player"] > freq["Banker"] + 5:
        strategies.append({"bet": "Banker", "weight": 2, "reason": "Player domina o histórico"})
    # Frequência
    if freq["Player"] > freq["Banker"] + 5:
        strategies.append({"bet": "Banker", "weight": 2, "reason": "Player domina o histórico"})
    elif freq["Banker"] > freq["Player"] + 5:
        strategies.append({"bet": "Player", "weight": 2, "reason": "Banker domina o histórico"})

    # Padrões com empate
    empates = [i for i, r in enumerate(results) if r["result"] == "Tie"]
    if len(empates) >= 2:
        intervalos = [empates[i] - empates[i - 1] for i in range(1, len(empates))]
        if all(x == intervalos[0] for x in intervalos):
            strategies.append({
                "bet": "Tie", "weight": 2,
                "reason": f"Empates com intervalo fixo de {intervalos[0]} rodadas"
            })
    if len(results) >= 3:
        ultimos = [r["result"] for r in results[:3]]
        if ultimos[0] == "Tie" and ultimos[1] != "Tie" and ultimos[2] == "Tie":
            strategies.append({
                "bet": "Tie", "weight": 3,
                "reason": "Padrão Tie alternado detectado (ex: Tie, X, Tie)"
            })
    if freq["Tie"] / len(results) > 0.15:
        strategies.append({
            "bet": "Tie", "weight": 2,
            "reason": "Alta frequência de empates no histórico"
        })

    # Melhor estratégia
    if strategies:
        best = sorted(strategies, key=lambda x: x["weight"], reverse=True)[0]
        st.session_state["recommendation"] = {
            "bet": best["bet"],
            "confidence": min(best["weight"] * 25, 100),
            "strategy": "Padrão detectado",
            "reasoning": best["reason"]
        }
        return

    # 🔍 Se nenhuma estratégia tradicional, aplicar padrão dinâmico
    dyn = scan_for_dynamic_patterns()
    if dyn:
        st.session_state["recommendation"] = dyn
    else:
        st.session_state["recommendation"] = {
            "bet": "Aguardar",
            "confidence": 0,
            "strategy": "Sem padrão forte",
            "reasoning": "Análise inconclusiva no momento"
        }
# Título
st.title("🎲 BAC BO LIVE ANALYZER")
st.markdown("<p class='big-text'>Leitura de padrões e inteligência adaptativa em tempo real 💡</p>", unsafe_allow_html=True)

# Botões de entrada
st.subheader("🎯 Registrar Resultado")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🟦 PLAYER"):
        add_result("Player")
with col2:
    if st.button("🟥 BANKER"):
        add_result("Banker")
with col3:
    if st.button("🟨 EMPATE"):
        add_result("Tie")

# Bloco de Recomendação
st.subheader("📈 Recomendação Estratégica")
rec = st.session_state["recommendation"]
if rec:
    st.markdown(f"""
        <div class='box'>
            <p class='big-text'>🎯 Próxima Aposta: {rec['bet']}</p>
            <p>Confiança: {rec['confidence']}%</p>
            <p><strong>Estratégia:</strong> {rec['strategy']}</p>
            <p><em>{rec['reasoning']}</em></p>
        </div>
    """, unsafe_allow_html=True)

# Estatísticas
st.subheader("📊 Estatísticas da Mesa")
stats = st.session_state["stats"]
streak_info = get_streak_info()
if stats:
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.markdown(f"**Total de jogos:** {stats['total']}")
    st.markdown(f"**Player:** {stats['player']} ({(stats['player'] / stats['total'] * 100):.1f}%)")
    st.markdown(f"**Banker:** {stats['banker']} ({(stats['banker'] / stats['total'] * 100):.1f}%)")
    st.markdown(f"**Empate:** {stats['tie']} ({(stats['tie'] / stats['total'] * 100):.1f}%)")
    if streak_info:
        st.markdown(f"**Sequência Atual:** {streak_info['count']} {streak_info['type']}")
    st.markdown("</div>", unsafe_allow_html=True)

# Histórico visual
st.subheader("📜 Histórico de Resultados")
if st.session_state["results"]:
    icons = {"Player": "🟦", "Banker": "🟥", "Tie": "🟨"}
    sequencia = ' '.join([icons[r["result"]] for r in st.session_state["results"]])
    st.markdown(f"<div class='box'><strong>{sequencia}</strong></div>", unsafe_allow_html=True)

# Diagnóstico detalhado
if rec:
    st.subheader("🧠 Diagnóstico Estratégico")
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    st.markdown(f"**Última jogada:** {st.session_state['results'][0]['result'] if st.session_state['results'] else 'N/A'}")
    st.markdown(f"**Recomendação com base em:** {rec['reasoning']}")
    st.markdown(f"**Confiança estimada:** {rec['confidence']}%")
    st.markdown("</div>", unsafe_allow_html=True)

# Reset
st.subheader("🔄 Reiniciar Histórico")
if st.button("Limpar tudo"):
    reset_data()
    st.success("Histórico apagado com sucesso!")

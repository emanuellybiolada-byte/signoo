from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def criar_banco():
    db_path = os.path.join(BASE_DIR, "signos.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tabela dos signos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            glifo TEXT NOT NULL,
            periodo TEXT NOT NULL,
            elemento TEXT NOT NULL,
            modalidade TEXT NOT NULL,
            planeta TEXT NOT NULL,
            descricao TEXT NOT NULL,
            caracteristicas TEXT NOT NULL,
            pontos_fortes TEXT NOT NULL,
            pontos_fracos TEXT NOT NULL,
            mes_inicio INTEGER NOT NULL,
            dia_inicio INTEGER NOT NULL,
            mes_fim INTEGER NOT NULL,
            dia_fim INTEGER NOT NULL
        )
    """)

    # Nova tabela de consultas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consulta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_nascimento TEXT NOT NULL,
            signo TEXT,
            data_ocorrencia DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    signos = [
        ("aries", "Áries", "♈", "21 de março a 19 de abril", "Fogo", "Cardinal", "Marte",
         "Áries é o primeiro signo do zodíaco e representa o início, a coragem e a iniciativa. Pessoas de Áries são energéticas, diretas e gostam de liderar.",
         "Corajoso,Impulsivo,Líder,Dinâmico,Independente,Entusiasta",
         "Determinação, honestidade e capacidade de motivar os outros.",
         "Pode ser impaciente, temperamental e pouco diplomático.",
         3, 21, 4, 19),

        ("touro", "Touro", "♉", "20 de abril a 20 de maio", "Terra", "Fixo", "Vênus",
         "Touro valoriza a estabilidade, o conforto e os prazeres sensoriais. São pessoas práticas, leais e persistentes.",
         "Paciente,Sensual,Confiável,Teimoso,Prático,Leal",
         "Constância, bom gosto e capacidade de criar segurança.",
         "Resistência excessiva a mudanças e tendência à possessividade.",
         4, 20, 5, 20),

        ("gemeos", "Gêmeos", "♊", "21 de maio a 20 de junho", "Ar", "Mutável", "Mercúrio",
         "Gêmeos é o signo da comunicação e da curiosidade. Pessoas de Gêmeos são versáteis, inteligentes e sociáveis.",
         "Comunicativo,Curioso,Versátil,Inteligente,Sociável,Ágil",
         "Adaptabilidade, raciocínio rápido e facilidade de expressão.",
         "Pode ser disperso, superficial ou indeciso.",
         5, 21, 6, 20),

        ("cancer", "Câncer", "♋", "21 de junho a 22 de julho", "Água", "Cardinal", "Lua",
         "Câncer é profundamente ligado às emoções, à família e ao sentimento de pertencimento.",
         "Emotivo,Protetor,Intuitivo,Sensível,Acolhedor,Leal",
         "Empatia, memória afetiva e capacidade de cuidar dos outros.",
         "Pode ser temperamental, defensivo ou excessivamente apegado.",
         6, 21, 7, 22),

        ("leao", "Leão", "♌", "23 de julho a 22 de agosto", "Fogo", "Fixo", "Sol",
         "Leão irradia confiança, criatividade e generosidade. Pessoas de Leão gostam de brilhar e inspirar.",
         "Confiante,Criativo,Generoso,Carismático,Orgulhoso,Leal",
         "Liderança natural, calor humano e capacidade de motivar.",
         "Pode ser vaidoso, dramático ou excessivamente centrado em si.",
         7, 23, 8, 22),

        ("virgem", "Virgem", "♍", "23 de agosto a 22 de setembro", "Terra", "Mutável", "Mercúrio",
         "Virgem busca a excelência através da análise, organização e serviço.",
         "Analítico,Organizado,Perfeccionista,Prestativo,Discreto,Prático",
         "Atenção aos detalhes, eficiência e senso de utilidade.",
         "Pode ser crítico demais, ansioso ou excessivamente exigente.",
         8, 23, 9, 22),

        ("libra", "Libra", "♎", "23 de setembro a 22 de outubro", "Ar", "Cardinal", "Vênus",
         "Libra busca equilíbrio, harmonia e justiça nas relações.",
         "Diplomático,Justo,Elegante,Sociável,Indeciso,Charmoso",
         "Habilidade de mediar conflitos e criar harmonia.",
         "Pode evitar confrontos e ter dificuldade em decidir.",
         9, 23, 10, 22),

        ("escorpiao", "Escorpião", "♏", "23 de outubro a 21 de novembro", "Água", "Fixo", "Plutão / Marte",
         "Escorpião é intenso, profundo e transformador. Possuem grande força emocional e lealdade.",
         "Intenso,Misterioso,Leal,Apaixonado,Determinado,Perceptivo",
         "Resiliência, profundidade emocional e foco.",
         "Pode ser ciumento, vingativo ou excessivamente controlador.",
         10, 23, 11, 21),

        ("sagitario", "Sagitário", "♐", "22 de novembro a 21 de dezembro", "Fogo", "Mutável", "Júpiter",
         "Sagitário é o signo da expansão, da aventura e da busca por significado.",
         "Aventureiro,Otimista,Filosófico,Honesto,Independente,Entusiasta",
         "Visão ampla, sinceridade e sede de aprender.",
         "Pode ser imprudente, excessivamente direto ou inquieto.",
         11, 22, 12, 21),

        ("capricornio", "Capricórnio", "♑", "22 de dezembro a 19 de janeiro", "Terra", "Cardinal", "Saturno",
         "Capricórnio representa ambição, responsabilidade e construção a longo prazo.",
         "Ambicioso,Disciplinado,Responsável,Paciente,Prático,Reservado",
         "Persistência, maturidade e capacidade de alcançar metas.",
         "Pode ser rígido, pessimista ou excessivamente focado no trabalho.",
         12, 22, 1, 19),

        ("aquario", "Aquário", "♒", "20 de janeiro a 18 de fevereiro", "Ar", "Fixo", "Urano / Saturno",
         "Aquário é inovador, humanitário e independente. Valorizam a liberdade e a originalidade.",
         "Inovador,Independente,Humanitário,Original,Intelectual,Livre",
         "Visão de futuro, imparcialidade e criatividade social.",
         "Pode parecer distante, teimoso ou rebelde sem causa.",
         1, 20, 2, 18),

        ("peixes", "Peixes", "♓", "19 de fevereiro a 20 de março", "Água", "Mutável", "Netuno / Júpiter",
         "Peixes é o signo da empatia, da imaginação e da conexão espiritual.",
         "Empático,Criativo,Intuitivo,Compassivo,Sonhador,Sensível",
         "Compaixão, imaginação e sensibilidade artística.",
         "Pode ser escapista, indeciso ou excessivamente idealista.",
         2, 19, 3, 20),
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO signos 
        (chave, nome, glifo, periodo, elemento, modalidade, planeta, descricao, 
         caracteristicas, pontos_fortes, pontos_fracos, mes_inicio, dia_inicio, mes_fim, dia_fim)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, signos)

    conn.commit()
    conn.close()


def obter_signo(mes, dia):
    db_path = os.path.join(BASE_DIR, "signos.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nome, glifo, periodo, elemento, modalidade, planeta, descricao, 
               caracteristicas, pontos_fortes, pontos_fracos,
               mes_inicio, dia_inicio, mes_fim, dia_fim
        FROM signos
    """)
    
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        mes_inicio = row[10]
        dia_inicio = row[11]
        mes_fim = row[12]
        dia_fim = row[13]

        if mes_inicio < mes_fim:
            if (mes == mes_inicio and dia >= dia_inicio) or \
               (mes == mes_fim and dia <= dia_fim) or \
               (mes > mes_inicio and mes < mes_fim):
                return row[:10]
        else:
            if (mes == mes_inicio and dia >= dia_inicio) or \
               (mes == mes_fim and dia <= dia_fim) or \
               (mes > mes_inicio or mes < mes_fim):
                return row[:10]

    return None


def registrar_consulta(data_nascimento, signo):
    """Salva a consulta na tabela consulta"""
    db_path = os.path.join(BASE_DIR, "signos.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO consulta (data_nascimento, signo, data_ocorrencia)
        VALUES (?, ?, ?)
    """, (data_nascimento, signo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Descubra seu Signo</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #1a0a14;
      --card: #2a1220;
      --accent: #f472b6;
      --text: #fce7f3;
      --muted: #f9a8d4;
      --border: rgba(244, 114, 182, 0.3);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Outfit', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 2rem 1rem;
      background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(244, 114, 182, 0.25), transparent),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(236, 72, 153, 0.2), transparent);
    }
    .container { width: 100%; max-width: 500px; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 2rem 1.75rem;
      box-shadow: 0 25px 50px -12px rgba(236, 72, 153, 0.25);
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, #f9a8d4, #ec4899, #f472b6);
    }
    .header { text-align: center; margin-bottom: 1.75rem; }
    .stars { font-size: 1.8rem; letter-spacing: 0.4rem; margin-bottom: 0.6rem; color: #f9a8d4; }
    h1 {
      font-size: 1.7rem;
      font-weight: 700;
      background: linear-gradient(135deg, #fbcfe8, #f472b6, #ec4899);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.4rem;
    }
    .subtitle { color: var(--muted); font-size: 0.92rem; font-weight: 300; }
    label { display: block; font-size: 0.875rem; font-weight: 500; color: var(--muted); margin-bottom: 0.45rem; }
    input[type="date"] {
      width: 100%;
      padding: 0.85rem 1rem;
      background: #1f0d18;
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-family: inherit;
      font-size: 1rem;
      outline: none;
      margin-bottom: 1.1rem;
    }
    button {
      width: 100%;
      padding: 0.95rem;
      background: linear-gradient(135deg, #f472b6, #ec4899);
      border: none;
      border-radius: 12px;
      color: white;
      font-family: inherit;
      font-size: 1.05rem;
      font-weight: 600;
      cursor: pointer;
      transition: 0.2s;
    }
    button:hover { transform: translateY(-2px); }
    #resultado {
      margin-top: 1.75rem;
      padding-top: 1.75rem;
      border-top: 1px solid var(--border);
      display: none;
    }
    #resultado.ativo { display: block; }
    .resultado-header { text-align: center; margin-bottom: 1.25rem; }
    .glyph { font-size: 3.8rem; margin-bottom: 0.3rem; }
    .resultado-header h2 {
      font-size: 1.9rem;
      font-weight: 700;
      background: linear-gradient(135deg, #fbcfe8, #f472b6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .periodo { color: var(--muted); font-size: 0.92rem; }
    .data-nasc { text-align: center; color: var(--muted); font-size: 0.85rem; margin-bottom: 1.25rem; }
    .badges { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-bottom: 1.35rem; }
    .badge {
      background: rgba(244, 114, 182, 0.15);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.35rem 0.85rem;
      font-size: 0.78rem;
      color: #f9a8d4;
    }
    .section { margin-bottom: 1.25rem; }
    .section h3 {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--accent);
      margin-bottom: 0.4rem;
    }
    .section p { line-height: 1.65; font-size: 0.93rem; font-weight: 300; }
    .traits { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.3rem; }
    .trait {
      background: #1f0d18;
      border-radius: 8px;
      padding: 0.3rem 0.65rem;
      font-size: 0.78rem;
      color: var(--muted);
    }
    .fracos {
      background: rgba(244, 114, 182, 0.08);
      border-left: 3px solid #f472b6;
      padding: 0.75rem 1rem;
      border-radius: 0 10px 10px 0;
    }
    .erro { text-align: center; color: #fda4af; padding: 1rem 0; }
    .footer { text-align: center; margin-top: 1.25rem; font-size: 0.78rem; color: var(--muted); }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="header">
        <div class="stars">✦ ✧ ✦</div>
        <h1>Descubra seu Signo</h1>
        <p class="subtitle">Coloque sua data de nascimento e descubra as principais características do seu signo zodiacal.</p>
      </div>

      <div>
        <label for="nascimento">Data de nascimento</label>
        <input type="date" id="nascimento" required>
        <button type="button" id="btnRevelar">Revelar meu signo</button>
      </div>

      <div id="resultado"></div>
      <p class="footer">Astrologia ocidental • Signo solar • Python + SQLite</p>
    </div>
  </div>

  <script>
    document.getElementById("btnRevelar").addEventListener("click", async function () {
      const input = document.getElementById("nascimento");
      const data = input.value;
      const caixa = document.getElementById("resultado");

      if (!data) {
        caixa.innerHTML = '<p class="erro">Por favor, selecione sua data de nascimento.</p>';
        caixa.classList.add("ativo");
        return;
      }

      const formData = new FormData();
      formData.append("nascimento", data);

      try {
        const response = await fetch("/revelar", {
          method: "POST",
          body: formData
        });
        const s = await response.json();

        if (s.erro) {
          caixa.innerHTML = `<p class="erro">${s.erro}</p>`;
          caixa.classList.add("ativo");
          return;
        }

        let tags = "";
        s.caracteristicas.forEach(c => {
          tags += `<span class="trait">${c}</span>`;
        });

        caixa.innerHTML = `
          <div class="resultado-header">
            <div class="glyph">${s.glifo}</div>
            <h2>${s.nome}</h2>
            <p class="periodo">${s.periodo}</p>
          </div>
          <p class="data-nasc">Data informada: <strong>${s.data_formatada}</strong></p>
          <div class="badges">
            <span class="badge">Elemento: ${s.elemento}</span>
            <span class="badge">Modalidade: ${s.modalidade}</span>
            <span class="badge">Planeta: ${s.planeta}</span>
          </div>
          <div class="section">
            <h3>Sobre o signo</h3>
            <p>${s.descricao}</p>
          </div>
          <div class="section">
            <h3>Principais características</h3>
            <div class="traits">${tags}</div>
          </div>
          <div class="section">
            <h3>Pontos fortes</h3>
            <p>${s.pontos_fortes}</p>
          </div>
          <div class="section">
            <h3>Pontos fracos</h3>
            <div class="fracos"><p>${s.pontos_fracos}</p></div>
          </div>
        `;
        caixa.classList.add("ativo");
      } catch (err) {
        caixa.innerHTML = '<p class="erro">Erro ao conectar com o servidor.</p>';
        caixa.classList.add("ativo");
      }
    });
  </script>
</body>
</html>
'''


@app.route("/")
def index():
    return HTML


@app.route("/revelar", methods=["POST"])
def revelar():
    data = request.form.get("nascimento")
    if not data:
        return jsonify({"erro": "Por favor, selecione sua data de nascimento."})

    try:
        dt = datetime.strptime(data, "%Y-%m-%d")
        mes = dt.month
        dia = dt.day
        data_formatada = dt.strftime("%d/%m/%Y")

        row = obter_signo(mes, dia)
        if not row:
            return jsonify({"erro": "Não foi possível determinar o signo."})

        # Registra a consulta no banco
        registrar_consulta(data, row[0])   # data_nascimento e nome do signo

        return jsonify({
            "nome": row[0],
            "glifo": row[1],
            "periodo": row[2],
            "elemento": row[3],
            "modalidade": row[4],
            "planeta": row[5],
            "descricao": row[6],
            "caracteristicas": row[7].split(","),
            "pontos_fortes": row[8],
            "pontos_fracos": row[9],
            "data_formatada": data_formatada
        })
    except Exception as e:
        return jsonify({"erro": str(e)})


if __name__ == "__main__":
    criar_banco()
    print("\n>>> Abra no navegador: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
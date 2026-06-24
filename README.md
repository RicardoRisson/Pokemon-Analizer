# 🎮 Pokémon Team Analyzer

Uma interface gráfica moderna e intuitiva desenvolvida em Python para analisar estrategicamente confrontos (*matchups*) no ecossistema Pokémon. O programa utiliza matrizes de efetividade oficial para calcular vantagens ofensivas e defensivas, gerando instantaneamente a ordem ideal de envio dos seus Pokémon contra o time adversário.

---

## 🚀 Funcionalidades

* **Seleção Visual Dinâmica:** Botões coloridos baseados nas paletas hexadecimais oficiais de cada um dos 18 tipos Pokémon.
* **Sistema de Wizard (Passo a Passo):** Monte o time inimigo facilmente clicando nos tipos e avançando para o próximo slot.
* **Cálculo Automatizado de Matchups:** Avalia imunidades (+8 pts), resistências (+5 pts), super efetividade (+4 pts) e penaliza fraquezas (-3 pts).
* **Fator "Certeza" (Confirmado):** Multiplica o peso da pontuação caso você tenha certeza do set do oponente.
* **Fácil Correção:** Botão de "Desfazer Último" para corrigir cliques errados sem reiniciar o fluxo.
* **Relatório Limpo:** Exibe de forma direta a melhor escolha absoluta para abrir a partida, a ordem dos reservas e quem você deve evitar a todo custo.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3** (Lógica principal de dados e ordenação)
* **CustomTkinter** (Interface gráfica customizada com suporte nativo a Dark Mode)

---

## 📦 Instalação e Como Rodar

### Pré-requisitos
Certifique-se de ter o **Python** instalado em seu sistema operacional Windows. 

1. **Instale a biblioteca de interface gráfica:**
   Abra o terminal (Prompt de Comando ou PowerShell) e execute:
   ```bash
   pip install customtkinter
   ```
2. **Clone o repositório ou baixe o código:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
   ```
3. **Execute o programa:**
   ```bash
   python pokemon_analyzer.py
   ```

## 🎮 Como Usar
Na tela principal, selecione até 2 tipos para o Pokémon atual do adversário (os botões ativos ganharão um destaque visual).

Marque a caixa "Confirmado" se tiver certeza absoluta daquele membro do time inimigo.

Clique em "Próximo Pokémon ->" para registrar o monstrinho na lista e limpar o painel.

Repita o processo para os outros Pokémons do oponente. Se errar, basta clicar em "Desfazer Último".

Quando o time deles estiver montado, clique no botão verde "CALCULAR MELHOR ESCOLHA" e veja o ranking ideal do seu time na tela de resultados!

## 📝 Como Customizar o Seu Time
Atualmente, o seu time está fixado diretamente no código para facilitar o carregamento. Para alterar os seus 6 Pokémons, abra o arquivo pokemon_analyzer.py e edite a lista self.my_team dentro do método init:
   ```bash
    self.my_team = [
    Pokemon("NomeDoSeuPokemon", ID_DO_TIPO_1, ID_DO_TIPO_2_OU_NONE),
    # Exemplo: Pokemon("Charizard", 1, 9) -> Fire (1) / Flying (9)
]
   ```

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo __LICENSE__ para mais detalhes.
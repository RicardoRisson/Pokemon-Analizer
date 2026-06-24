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
   pip install customtkinter pillow
   ```
2. **Clone o repositório ou baixe o código:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
   ```
3. **Execute o programa:**
   ```bash
   python pokemon_analyzer.py
   ```

## 🎮 Como Usar (Fluxo do Systema)

1. **Passo 1 (Team Setup):** Na primeira inicialização, utilize a barra de pesquisa para filtrar e selecionar exatamente 5 Pokémon para o seu time. Clique em **Avançar para Moves**.
2. **Passo 2 (Moves Setup):** Clique nas abas superiores para alternar entre os seus Pokémon. Use os menus seletores para preencher o nome e as propriedades dos até 4 golpes que ele carrega. Clique em **Time Pronto**.
3. **Passo 3 (Matchup Arena):** No painel central, selecione até 2 tipos elementares para o Pokémon do adversário. Marque "Confirmado" se necessário, e clique em **Próximo Pokémon ->** para montar a equipe deles.
4. **Passo 4 (Resultado):** Clique no botão verde **CALCULAR MELHOR ESCOLHA** para abrir o relatório completo com a melhor opção de abertura, reservas e alertas.

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo __LICENSE__ para mais detalhes.
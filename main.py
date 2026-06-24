import customtkinter as ctk

# ==========================================
# PALETA DE CORES OFICIAIS DOS TIPOS POKÉMON
# ==========================================
TYPE_DATA = {
    "Normal":   {"id": 0,  "color": "#A8A77A"},
    "Fire":     {"id": 1,  "color": "#EE8130"},
    "Water":    {"id": 2,  "color": "#6390F0"},
    "Electric": {"id": 3,  "color": "#F7D02C"},
    "Grass":    {"id": 4,  "color": "#7AC74C"},
    "Ice":      {"id": 5,  "color": "#96D9D6"},
    "Fighting": {"id": 6,  "color": "#C22E28"},
    "Poison":   {"id": 7,  "color": "#A33EA1"},
    "Ground":   {"id": 8,  "color": "#E2BF65"},
    "Flying":   {"id": 9,  "color": "#A98FF3"},
    "Psychic":  {"id": 10, "color": "#F95587"},
    "Bug":      {"id": 11, "color": "#A6B91A"},
    "Rock":     {"id": 12, "color": "#B6A136"},
    "Ghost":    {"id": 13, "color": "#735797"},
    "Dragon":   {"id": 14, "color": "#6F35FC"},
    "Dark":     {"id": 15, "color": "#705746"},
    "Steel":    {"id": 16, "color": "#B7B7CE"},
    "Fairy":    {"id": 17, "color": "#D685AD"}
}

TYPE_NAMES = list(TYPE_DATA.keys())

# Matriz de Efetividade (Atacante linha -> Defensor coluna)
EFFECTIVENESS = [
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,  5,  0, 10, 10,  5, 10], # NORMAL
    [10,  5,  5, 10, 20, 20, 10, 10, 10, 10, 10, 20,  5, 10,  5, 10, 20, 10], # FIRE
    [10, 20,  5, 10,  5, 10, 10, 10, 20, 10, 10, 10, 20, 10,  5, 10, 10, 10], # WATER
    [10, 10, 20,  5,  5, 10, 10, 10,  0, 20, 10, 10, 10, 10,  5, 10, 10, 10], # ELECTRIC
    [10,  5, 20,  5,  5, 10, 10,  5, 20,  5, 10,  5, 20, 10,  5, 10,  5, 10], # GRASS
    [10,  5,  5, 10, 20,  5, 10, 10, 20, 20, 10, 10, 10, 10, 20, 10,  5, 10], # ICE
    [20, 10, 10, 10, 10, 20, 10,  5, 10,  5,  5,  5, 20,  0, 10, 20, 20,  5], # FIGHTING
    [10, 10, 10, 10, 20, 10, 10,  5,  5, 10, 10, 10,  5,  5, 10, 10,  0, 20], # POISON
    [10, 20, 10, 20,  5, 10, 10, 20, 10,  0, 10,  5, 20, 10, 10, 10, 20, 10], # GROUND
    [10, 10, 10,  5, 20, 10, 20, 10, 10, 10, 10, 20,  5, 10, 10, 10,  5, 10], # FLYING
    [10, 10, 10, 10, 10, 10, 20, 20, 10, 10,  5, 10, 10, 10, 10,  0,  5, 10], # PSYCHIC
    [10,  5, 10, 10, 20, 10,  5,  5, 10,  5, 20, 10, 10,  5, 10, 20,  5,  5], # BUG
    [10, 20, 10, 10, 10, 20,  5, 10,  5, 20, 10, 20, 10, 10, 10, 10,  5, 10], # ROCK
    [ 0, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 10,  5, 10, 10], # GHOST
    [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 20, 10,  5,  0], # DRAGON
    [10, 10, 10, 10, 10, 10,  5, 10, 10, 10, 20, 10, 10, 20, 10,  5, 10,  5], # DARK
    [10,  5,  5,  5, 10, 20, 10, 10, 10, 10, 10, 10, 20, 10, 10, 10,  5, 20], # STEEL
    [10,  5, 10, 10, 10, 10, 20,  5, 10, 10, 10, 10, 10, 10, 20, 20,  5, 10]  # FAIRY
]

# ==========================================
# CLASSES DE ESTRUTURA
# ==========================================

class Pokemon:
    def __init__(self, name, type1, type2=None):
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.score = 0

    def get_type_str(self):
        t1_name = TYPE_NAMES[self.type1] if self.type1 is not None else "None"
        t2_name = f"/{TYPE_NAMES[self.type2]}" if self.type2 is not None else ""
        return f"{t1_name}{t2_name}"

class EnemyPokemon:
    def __init__(self, type1, type2, is_confirmed):
        self.type1 = type1
        self.type2 = type2
        self.is_confirmed = is_confirmed
        
        t1_name = TYPE_NAMES[type1]
        t2_name = f"/{TYPE_NAMES[type2]}" if type2 is not None else ""
        self.display_name = f"{t1_name}{t2_name}"

def get_damage_modifier(attacker, def1, def2):
    if attacker is None:
        return 10
    mod = EFFECTIVENESS[attacker][def1]
    if def2 is not None:
        mod2 = EFFECTIVENESS[attacker][def2]
        mod = (mod * mod2) // 10
    return mod

def evaluate_team(my_team, enemy_team):
    for p in my_team:
        p.score = 0
        
        for enemy in enemy_team:
            if enemy.type1 is None:
                continue

            match_score = 0

            # Ofensiva
            dmg_t1 = get_damage_modifier(p.type1, enemy.type1, enemy.type2)
            dmg_t2 = get_damage_modifier(p.type2, enemy.type1, enemy.type2) if p.type2 is not None else 0
            max_dmg_out = max(dmg_t1, dmg_t2)

            if max_dmg_out > 10:
                match_score += 4
            elif max_dmg_out == 10:
                match_score += 2

            # Defesa
            dmg_in_t1 = get_damage_modifier(enemy.type1, p.type1, p.type2)
            dmg_in_t2 = get_damage_modifier(enemy.type2, p.type1, p.type2) if enemy.type2 is not None else 0
            max_dmg_in = max(dmg_in_t1, dmg_in_t2)

            if (enemy.type1 is not None and dmg_in_t1 == 0) or (enemy.type2 is not None and dmg_in_t2 == 0):
                match_score += 8
            elif max_dmg_in >= 20:
                match_score -= 3
            elif 0 < max_dmg_in < 10:
                match_score += 5

            if enemy.is_confirmed:
                match_score *= 3

            p.score += match_score

# ==========================================
# INTERFACE GRÁFICA (GUI)
# ==========================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pokémon Team Analyzer")
        self.geometry("850x650")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Seu Time Atual
        self.my_team = [
            Pokemon("Snorlax", 0),                 # Normal
            Pokemon("Dragonite", 14, 9),           # Dragon / Flying
            Pokemon("Greninja", 15, 2),            # Dark / Water
            Pokemon("Hawlucha", 6, 9),             # Fighting / Flying
            Pokemon("Typhlosion Corrupt", 1, 15),  # Fire / Dark
            Pokemon("Sceptile", 4)                 # Grass
        ]
        
        self.enemy_team = []
        self.current_selected_types = []

        # ======================================
        # TELA 1: SELEÇÃO DE TIPOS
        # ======================================
        self.frame_selection = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_selection.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_title = ctk.CTkLabel(self.frame_selection, text="Montar Time Inimigo", font=("Arial", 26, "bold"))
        self.lbl_title.pack(pady=(0, 5))

        self.lbl_subtitle = ctk.CTkLabel(self.frame_selection, text="Selecione até 2 tipos para o Pokémon inimigo:", font=("Arial", 14), text_color="gray")
        self.lbl_subtitle.pack(pady=(0, 20))

        # Grade de Botões Coloridos
        self.grid_frame = ctk.CTkFrame(self.frame_selection, fg_color="transparent")
        self.grid_frame.pack()

        self.type_buttons = []
        row_idx, col_idx = 0, 0
        for t_name, info in TYPE_DATA.items():
            # Cria o botão com a cor oficial do tipo
            btn = ctk.CTkButton(self.grid_frame, text=t_name.upper(), width=120, height=45,
                                fg_color=info["color"], hover_color=info["color"], font=("Arial", 12, "bold"),
                                text_color="#FFFFFF" if t_name not in ["Electric", "Ice"] else "#111111",
                                command=lambda t_id=info["id"]: self.toggle_type(t_id))
            btn.grid(row=row_idx, column=col_idx, padx=6, pady=6)
            self.type_buttons.append((btn, info["color"]))
            
            col_idx += 1
            if col_idx > 5:
                col_idx = 0
                row_idx += 1

        # Checkbox e Ações
        self.actions_frame = ctk.CTkFrame(self.frame_selection, fg_color="transparent")
        self.actions_frame.pack(pady=20)

        self.var_confirmed = ctk.BooleanVar(value=True)
        self.chk_confirmed = ctk.CTkCheckBox(self.actions_frame, text="Confirmado", font=("Arial", 14), variable=self.var_confirmed)
        self.chk_confirmed.grid(row=0, column=0, padx=10)

        self.btn_next = ctk.CTkButton(self.actions_frame, text="Próximo Pokémon ->", font=("Arial", 13, "bold"), fg_color="#1f538d", command=self.add_enemy)
        self.btn_next.grid(row=0, column=1, padx=10)

        self.btn_undo = ctk.CTkButton(self.actions_frame, text="Desfazer Último", font=("Arial", 13), fg_color="#555555", hover_color="#777777", command=self.undo_enemy)
        self.btn_undo.grid(row=0, column=2, padx=10)

        # Status Inimigos Adicionados
        self.lbl_added = ctk.CTkLabel(self.frame_selection, text="Inimigos Adicionados: Nenhum", font=("Arial", 14, "italic"), text_color="#A8A77A")
        self.lbl_added.pack(pady=(10, 20))

        self.btn_analyze = ctk.CTkButton(self.frame_selection, text="✔ CALCULAR MELHOR ESCOLHA", height=50, 
                                         fg_color="#28a745", hover_color="#218838", font=("Arial", 16, "bold"),
                                         command=self.show_results)
        self.btn_analyze.pack()

        # ======================================
        # TELA 2: RESULTADOS (LOG LIMPO)
        # ======================================
        self.frame_results = ctk.CTkFrame(self, fg_color="transparent")
        
        self.lbl_res_title = ctk.CTkLabel(self.frame_results, text="ORDEM SUGERIDA DE ENVIO", font=("Arial", 26, "bold"), text_color="#28a745")
        self.lbl_res_title.pack(pady=10)

        self.lbl_res_subtitle = ctk.CTkLabel(self.frame_results, text="Do melhor (topo) para o pior (base) contra o time informado:", font=("Arial", 14, "italic"), text_color="gray")
        self.lbl_res_subtitle.pack(pady=(0, 10))

        self.textbox_results = ctk.CTkTextbox(self.frame_results, width=700, height=400, font=("Consolas", 16))
        self.textbox_results.pack(pady=10)

        self.btn_back = ctk.CTkButton(self.frame_results, text="<- Voltar e Refazer Nova Análise", font=("Arial", 14), command=self.back_to_selection)
        self.btn_back.pack(pady=10)


    # --- LÓGICA DE INTERAÇÃO ---

    def toggle_type(self, type_id):
        if type_id in self.current_selected_types:
            self.current_selected_types.remove(type_id)
        elif len(self.current_selected_types) < 2:
            self.current_selected_types.append(type_id)
        else:
            self.current_selected_types[1] = type_id

        self.update_button_visuals()

    def update_button_visuals(self):
        for i, (btn, orig_color) in enumerate(self.type_buttons):
            if i in self.current_selected_types:
                # Se selecionado, ganha borda grossa e destaca o texto
                btn.configure(border_width=4, border_color="#FFFFFF")
            else:
                # Volta ao normal
                btn.configure(border_width=0)

    def add_enemy(self):
        if not self.current_selected_types:
            return 
        
        t1 = self.current_selected_types[0]
        t2 = self.current_selected_types[1] if len(self.current_selected_types) > 1 else None
        
        new_enemy = EnemyPokemon(t1, t2, self.var_confirmed.get())
        self.enemy_team.append(new_enemy)

        self.update_enemy_list_text()

        # Reseta botões
        self.current_selected_types = []
        self.update_button_visuals()

    def undo_enemy(self):
        if self.enemy_team:
            self.enemy_team.pop()
            self.update_enemy_list_text()

    def update_enemy_list_text(self):
        if not self.enemy_team:
            self.lbl_added.configure(text="Inimigos Adicionados: Nenhum")
        else:
            names = [f"[{e.display_name}]" for e in self.enemy_team]
            self.lbl_added.configure(text=f"Time Inimigo ({len(self.enemy_team)}): " + ", ".join(names))

    def show_results(self):
        if not self.enemy_team:
            self.lbl_added.configure(text="Adicione pelo menos um Pokémon inimigo antes de calcular!", text_color="#C22E28")
            return

        # Roda o cálculo
        evaluate_team(self.my_team, self.enemy_team)
        
        # Ordena: maior pontuação vai para o topo da lista
        self.my_team.sort(key=lambda p: p.score, reverse=True)

        # Monta a exibição limpa (Apenas Nome, Posição e Tipos)
        output = "\n"
        output += " 🥇 DEVE IR PRIMEIRO (Melhor Escolha):\n"
        output += f" ➔ 1º LUGAR: {self.my_team[0].name.upper()} ({self.my_team[0].get_type_str()})\n"
        output += " —" * 28 + "\n\n"
        
        output += " 📋 ORDEM DE RESERVAS SUGERIDA:\n"
        for i in range(1, len(self.my_team)):
            p = self.my_team[i]
            output += f"   {i+1}º Lugar: {p.name:<22} | Tipo: {p.get_type_str()}\n"
            
        output += "\n " + "—" * 28 + "\n"
        output += " ⚠️ EVITE (Último lugar no ranking):\n"
        p_worst = self.my_team[-1]
        output += f" ➔ {len(self.my_team)}º LUGAR: {p_worst.name.upper()} ({p_worst.get_type_str()})\n"

        self.textbox_results.delete("1.0", "end")
        self.textbox_results.insert("1.0", output)

        # Alterna para a tela de log limpo
        self.frame_selection.pack_forget()
        self.frame_results.pack(fill="both", expand=True, padx=20, pady=20)

    def back_to_selection(self):
        self.enemy_team = []
        self.lbl_added.configure(text="Inimigos Adicionados: Nenhum", text_color="#A8A77A")
        self.frame_results.pack_forget()
        self.frame_selection.pack(fill="both", expand=True, padx=20, pady=20)


if __name__ == "__main__":
    app = App()
    app.mainloop()
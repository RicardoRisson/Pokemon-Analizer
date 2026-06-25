import customtkinter as ctk
import os
import pickle
from PIL import Image

# Importando os módulos do projeto
from efetivos import TYPE_DATA, TYPE_NAMES, EFFECTIVENESS
from disponiveis import POKEMON_DATABASE
from moves import Move

# ==========================================
# CLASSES DE ESTRUTURA E CÁLCULO
# ==========================================

class Pokemon:
    def __init__(self, name, type1, type2=None, prefer="Especial"):
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.prefer = prefer
        self.moves = [None, None, None, None]
        self.score = 0

    def get_type_str(self):
        t1_name = TYPE_NAMES[self.type1] if self.type1 is not None else "None"
        t2_name = f"/{TYPE_NAMES[self.type2]}" if self.type2 is not None else ""
        return f"{t1_name}{t2_name}"

class EnemyPokemon:
    def __init__(self, name, type1, type2, is_confirmed):
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.is_confirmed = is_confirmed
        
        t1_name = TYPE_NAMES[type1]
        t2_name = f"/{TYPE_NAMES[type2]}" if type2 is not None else ""
        self.display_name = f"{name} [{t1_name}{t2_name}]"

def get_damage_modifier(attacker_type, def1, def2):
    if attacker_type is None:
        return 10
    mod = EFFECTIVENESS[attacker_type][def1]
    if def2 is not None:
        mod2 = EFFECTIVENESS[attacker_type][def2]
        mod = (mod * mod2) // 10
    return mod

def evaluate_team(my_team, enemy_team):
    for p in my_team:
        p.score = 0
        for enemy in enemy_team:
            if enemy.type1 is None:
                continue

            match_score = 0
            max_move_dmg = 0
            utility_score = 0

            for move in p.moves:
                if move is None or not move.name:
                    continue
                
                if move.move_kind == "Buff/Debuff":
                    utility_score += 2
                    continue
                
                dmg = get_damage_modifier(move.move_type, enemy.type1, enemy.type2)
                
                if move.move_type == p.type1 or move.move_type == p.type2:
                    dmg = (dmg * 15) // 10

                if move.category == p.prefer:
                    dmg += 2

                if dmg > max_move_dmg:
                    max_move_dmg = dmg

            if max_move_dmg > 15:     match_score += 7
            elif max_move_dmg > 10:   match_score += 4
            elif max_move_dmg == 10:  match_score += 2
            elif max_move_dmg > 0:    match_score -= 1
            
            match_score += utility_score

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
# FUNÇÃO PARA CARREGAR ARTES (SPRITES)
# ==========================================

def carrega_artes(pokemon_name, tamanho=(40, 40)):
    nome_limpo = pokemon_name.replace("/", "_").replace("?", "").replace(":", "").strip()
    caminho_imagem = os.path.join("artes", f"{nome_limpo}.png")
    
    if os.path.exists(caminho_imagem):
        img_pil = Image.open(caminho_imagem)
    else:
        caminho_default = os.path.join("artes", "default.png")
        if os.path.exists(caminho_default):
            img_pil = Image.open(caminho_default)
        else:
            img_pil = Image.new("RGBA", tamanho, (0, 0, 0, 0))
            
    return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=tamanho)


# ==========================================
# INTERFACE GRÁFICA (GUI)
# ==========================================

BIN_FILE = "my_pokemon_team.bin"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pokémon Team Analyzer")
        self.geometry("1160x860")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.my_team = []
        self.enemy_team = []
        self.selected_team_indices = [] 
        
        self.selected_enemy_index = None 
        self.active_pokemon_index = 0 

        if hasattr(TYPE_NAMES, "keys"):
            self.available_types_list = [TYPE_NAMES[key] for key in sorted(TYPE_NAMES.keys())]
        else:
            self.available_types_list = sorted([str(t) for t in TYPE_NAMES])

        self.frame_team_setup = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_moves_setup = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_selection = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_results = ctk.CTkFrame(self, fg_color="transparent")

        self.load_team_from_bin()

    def load_team_from_bin(self):
        if os.path.exists(BIN_FILE):
            try:
                with open(BIN_FILE, "rb") as f:
                    saved_data = pickle.load(f)
                    self.my_team = []
                    for p in saved_data:
                        # Corrigido para evitar quebras se o dicionário antigo vier inválido
                        if isinstance(p, dict) and 'name' in p and 't1' in p:
                            pk = Pokemon(p['name'], p['t1'], p['t2'], p.get('prefer', 'Especial'))
                            for idx, m_data in enumerate(p.get('moves', [])):
                                if m_data:
                                    pk.moves[idx] = Move(m_data['name'], m_data['type_str'], m_data['cat'], m_data['kind'])
                            self.my_team.append(pk)
                
                if len(self.my_team) < 6:
                    self.build_team_setup_screen()
                else:
                    self.build_main_selection_screen()
            except Exception:
                self.build_team_setup_screen() 
        else:
            self.build_team_setup_screen()

    def save_team_to_bin(self):
        data_to_save = []
        for p in self.my_team:
            moves_data = []
            for m in p.moves:
                if m: moves_data.append({'name': m.name, 'type_str': m.move_type_str, 'cat': m.category, 'kind': m.move_kind})
                else: moves_data.append(None)
            data_to_save.append({'name': p.name, 't1': p.type1, 't2': p.type2, 'prefer': p.prefer, 'moves': moves_data})
        with open(BIN_FILE, "wb") as f:
            pickle.dump(data_to_save, f)

    # --- TELA 1: SELEÇÃO DE INTEGRANTES ---
    def build_team_setup_screen(self):
        self.frame_selection.pack_forget()
        self.frame_results.pack_forget()
        self.frame_moves_setup.pack_forget()
        self.frame_team_setup.destroy()
        
        self.frame_team_setup = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_team_setup.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.frame_team_setup, text="Passo 1: Escolha Seus 6 Pokémon", font=("Arial", 22, "bold"), text_color="#F7D02C").pack(pady=5)

        top_bar = ctk.CTkFrame(self.frame_team_setup, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(top_bar, text="❌ Desmarcar Todos", font=("Arial", 12, "bold"), fg_color="#A52A2A", hover_color="#8B0000", command=self.clear_all_selections).pack(side="left")
        self.lbl_setup_counter = ctk.CTkLabel(top_bar, text="Selecionados: 0 de 6", font=("Arial", 14, "italic"))
        self.lbl_setup_counter.pack(side="right")

        filter_box = ctk.CTkFrame(self.frame_team_setup, fg_color="transparent")
        filter_box.pack(pady=10)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_pokemon)
        ctk.CTkEntry(filter_box, placeholder_text="Filtrar por nome...", textvariable=self.search_var, width=280, height=35).grid(row=0, column=0, padx=5)

        # CORREÇÃO: Removido 'textvariable' e adicionado comando direto
        self.cmb_team_type = ctk.CTkComboBox(filter_box, values=["Todos os Tipos"] + self.available_types_list, 
                                             width=160, height=35, state="readonly", command=self.filter_pokemon)
        self.cmb_team_type.set("Todos os Tipos")
        self.cmb_team_type.grid(row=0, column=1, padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self.frame_team_setup, height=360)
        self.scroll_frame.pack(pady=10, fill="both", expand=True)

        self.db_buttons = {}
        for idx, p_info in enumerate(POKEMON_DATABASE):
            t1_n = TYPE_NAMES[p_info["t1"]]
            t2_n = f"/{TYPE_NAMES[p_info['t2']]}" if p_info["t2"] is not None else ""
            
            foto_pk = carrega_artes(p_info['name'], tamanho=(32, 32))

            btn = ctk.CTkButton(self.scroll_frame, text=f" {p_info['name']} [{t1_n}{t2_n}]", font=("Arial", 12),
                                image=foto_pk, compound="left", anchor="w",
                                fg_color="#2b2b2b", border_color=TYPE_DATA[t1_n]["color"], border_width=1, height=40, command=lambda i=idx: self.toggle_team_member(i))
            btn.pack(fill="x", padx=10, pady=4)
            self.db_buttons[idx] = btn

        self.selected_team_indices = [idx for current_p in self.my_team for idx, db_p in enumerate(POKEMON_DATABASE) if db_p["name"] == current_p.name]
        self.update_setup_visuals()

        ctk.CTkButton(self.frame_team_setup, text="AVANÇAR PARA MOVES ➔", height=50, fg_color="#28a745", hover_color="#218838", font=("Arial", 15, "bold"), command=self.go_to_moves_setup).pack(pady=15)

    def filter_pokemon(self, *args):
        query = self.search_var.get().lower().strip()
        selected_type = self.cmb_team_type.get() # Obtém o valor selecionado diretamente do componente

        for idx, p_info in enumerate(POKEMON_DATABASE):
            btn = self.db_buttons.get(idx)
            if btn:
                t1_name = TYPE_NAMES[p_info["t1"]]
                t2_name = TYPE_NAMES[p_info["t2"]] if p_info["t2"] is not None else ""
                
                match_name = query in p_info["name"].lower()
                match_type = (selected_type == "Todos os Tipos" or selected_type == t1_name or selected_type == t2_name)

                if match_name and match_type: 
                    btn.pack(fill="x", padx=10, pady=4)
                else: 
                    btn.pack_forget()

    def toggle_team_member(self, idx):
        if idx in self.selected_team_indices: 
            self.selected_team_indices.remove(idx)
        elif len(self.selected_team_indices) < 6: 
            self.selected_team_indices.append(idx)
        else: 
            self.selected_team_indices[-1] = idx
        self.update_setup_visuals()

    def clear_all_selections(self):
        self.selected_team_indices.clear()
        self.update_setup_visuals()

    def update_setup_visuals(self):
        self.lbl_setup_counter.configure(text=f"Selecionados: {len(self.selected_team_indices)} de 6")
        for idx, btn in self.db_buttons.items():
            btn.configure(fg_color="#1f538d" if idx in self.selected_team_indices else "#2b2b2b")

    def go_to_moves_setup(self):
        if len(self.selected_team_indices) != 6:
            self.lbl_setup_counter.configure(text="Erro: Escolha exatamente 6 Pokémon!", text_color="#C22E28")
            return
        new_team = []
        for idx in self.selected_team_indices:
            db_p = POKEMON_DATABASE[idx]
            existing = next((p for p in self.my_team if p.name == db_p["name"]), None)
            new_team.append(existing if existing else Pokemon(db_p["name"], db_p["t1"], db_p["t2"], db_p.get("prefer", "Especial")))
        self.my_team = new_team
        self.active_pokemon_index = 0
        self.build_moves_setup_screen()

    # --- TELA 2: INTERFACE DE ABAS ---
    def build_moves_setup_screen(self):
        self.frame_team_setup.pack_forget()
        self.frame_selection.pack_forget()
        self.frame_moves_setup.destroy()

        self.frame_moves_setup = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_moves_setup.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.frame_moves_setup, text="Passo 2: Clique no Pokémon e use os menus para configurar os Moves", font=("Arial", 18, "bold"), text_color="#F7D02C").pack(pady=(0, 15))

        self.pokemon_tabs_frame = ctk.CTkFrame(self.frame_moves_setup, fg_color="transparent")
        self.pokemon_tabs_frame.pack(fill="x", pady=5)
        
        self.tab_buttons = []
        for i, p in enumerate(self.my_team):
            filled_moves = sum(1 for m in p.moves if m and m.name)
            foto_aba = carrega_artes(p.name, tamanho=(28, 28))

            btn = ctk.CTkButton(self.pokemon_tabs_frame, text=f" {p.name}\n({filled_moves}/4 Moves)", font=("Arial", 11, "bold"), height=55,
                                image=foto_aba, compound="top",
                                fg_color="#1e1e1e", border_width=2, border_color="#444444", command=lambda idx=i: self.switch_active_pokemon(idx))
            btn.grid(row=0, column=i, padx=4, sticky="ew")
            self.pokemon_tabs_frame.grid_columnconfigure(i, weight=1)
            self.tab_buttons.append(btn)

        self.inputs_container = ctk.CTkFrame(self.frame_moves_setup, fg_color="#1a1a1a", border_width=1, border_color="#333333")
        self.inputs_container.pack(fill="both", expand=True, pady=15, ipady=10)

        self.render_active_pokemon_inputs()

        ctk.CTkButton(self.frame_moves_setup, text="✔ TIME PRONTO! IR PARA ANÁLISE DE COMBATE", height=55,
                      fg_color="#28a745", hover_color="#218838", font=("Arial", 16, "bold"), command=self.finalize_moves_and_next).pack(pady=10)

    def switch_active_pokemon(self, idx):
        self.save_current_fields_to_memory()
        self.active_pokemon_index = idx
        self.render_active_pokemon_inputs()

    def render_active_pokemon_inputs(self):
        for widget in self.inputs_container.winfo_children():
            widget.destroy()

        p = self.my_team[self.active_pokemon_index]

        for i, btn in enumerate(self.tab_buttons):
            filled = sum(1 for m in self.my_team[i].moves if m and m.name)
            btn.configure(text=f" {self.my_team[i].name}\n({filled}/4 Moves)", 
                          fg_color="#1f538d" if i == self.active_pokemon_index else "#1e1e1e", 
                          border_color="#6390F0" if i == self.active_pokemon_index else "#444444")

        header_frame = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
        header_frame.pack(anchor="w", padx=20, pady=10)
        
        foto_grande = carrega_artes(p.name, tamanho=(45, 45))
        lbl_img = ctk.CTkLabel(header_frame, text="", image=foto_grande)
        lbl_img.pack(side="left", padx=(0, 10))

        lbl_info = ctk.CTkLabel(header_frame, text=f"Configurando: {p.name.upper()} | Tipo: {p.get_type_str()} | Foco Nativo: {p.prefer}", font=("Arial", 15, "bold"), text_color="#6390F0")
        lbl_info.pack(side="left")

        grid_frame = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10)

        self.current_entry_slots = []

        for slot in range(4):
            slot_box = ctk.CTkFrame(grid_frame, fg_color="#2b2b2b", border_width=1, border_color="#444444")
            slot_box.grid(row=0, column=slot, padx=6, pady=5, sticky="nsew")
            grid_frame.grid_columnconfigure(slot, weight=1)

            ctk.CTkLabel(slot_box, text=f"Slot de Move {slot+1}", font=("Arial", 11, "bold"), text_color="gray").pack(pady=4)

            m = p.moves[slot]
            m_name = m.name if m else ""
            m_type = m.move_type_str if m else "Normal"
            m_cat = m.category if m else "Físico"
            m_kind = m.move_kind if m else "Ataque Direto"

            ent_name = ctk.CTkEntry(slot_box, placeholder_text="Nome do Golpe", width=205)
            ent_name.insert(0, m_name)
            ent_name.pack(padx=10, pady=5)

            ctk.CTkLabel(slot_box, text="Tipo do Golpe:", font=("Arial", 10), text_color="#aaaaaa").pack()
            cmb_type = ctk.CTkComboBox(slot_box, values=self.available_types_list, width=205, state="readonly")
            cmb_type.set(m_type)
            cmb_type.pack(padx=10, pady=5)

            ctk.CTkLabel(slot_box, text="Categoria de Dano:", font=("Arial", 10), text_color="#aaaaaa").pack()
            cmb_cat = ctk.CTkComboBox(slot_box, values=["Físico", "Especial"], width=205, state="readonly")
            cmb_cat.set(m_cat)
            cmb_cat.pack(padx=10, pady=5)

            ctk.CTkLabel(slot_box, text="Propriedade do Golpe:", font=("Arial", 10), text_color="#aaaaaa").pack()
            cmb_kind = ctk.CTkComboBox(slot_box, values=["Ataque Direto", "Buff/Debuff"], width=205, state="readonly")
            cmb_kind.set(m_kind)
            cmb_kind.pack(padx=10, pady=(5, 15))

            self.current_entry_slots.append({"name": ent_name, "type": cmb_type, "cat": cmb_cat, "kind": cmb_kind})

    def save_current_fields_to_memory(self):
        if not hasattr(self, 'current_entry_slots') or len(self.current_entry_slots) < 4:
            return

        p = self.my_team[self.active_pokemon_index]
        for slot in range(4):
            fields = self.current_entry_slots[slot]
            name = fields["name"].get().strip()
            t_str = fields["type"].get()
            cat = fields["cat"].get()
            kind = fields["kind"].get()

            if name:
                p.moves[slot] = Move(name, t_str, cat, kind)
            else:
                p.moves[slot] = None

    def finalize_moves_and_next(self):
        self.save_current_fields_to_memory()
        self.save_team_to_bin()
        self.build_main_selection_screen()

    # --- TELA 3: MONTAGEM DO TIME INIMIGO ---
    def build_main_selection_screen(self):
        self.frame_team_setup.pack_forget()
        self.frame_moves_setup.pack_forget()
        self.frame_results.pack_forget()
        self.frame_selection.destroy()

        self.frame_selection = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_selection.pack(fill="both", expand=True, padx=20, pady=20)

        team_manager_frame = ctk.CTkFrame(self.frame_selection, fg_color="#1e1e1e", border_width=1, border_color="#333333")
        team_manager_frame.pack(fill="x", pady=(0, 20))

        center_bar = ctk.CTkFrame(team_manager_frame, fg_color="transparent")
        center_bar.pack(anchor="center", pady=12)

        badges_frame = ctk.CTkFrame(center_bar, fg_color="transparent")
        badges_frame.pack(pady=(0, 12))
        
        ctk.CTkLabel(badges_frame, text="SEU TIME:", font=("Arial", 11, "bold"), text_color="gray").pack(side="left", padx=10)
        for p in self.my_team:
            filled = sum(1 for m in p.moves if m)
            mini_foto = carrega_artes(p.name, tamanho=(22, 22))
            
            lbl_p = ctk.CTkLabel(badges_frame, text=f" {p.name} ({filled} mv) ", font=("Arial", 11, "bold"), 
                                 image=mini_foto, compound="left", fg_color="#2d2d2d", corner_radius=5)
            lbl_p.pack(side="left", padx=4)

        buttons_frame = ctk.CTkFrame(center_bar, fg_color="transparent")
        buttons_frame.pack()

        ctk.CTkButton(buttons_frame, text="⚔️ Alterar os Moves", font=("Arial", 12, "bold"), width=160, height=28, fg_color="#34495e", hover_color="#2c3e50",
                      command=self.build_moves_setup_screen).pack(side="left", padx=8)
        
        ctk.CTkButton(buttons_frame, text="🔄 Alterar o Time", font=("Arial", 12, "bold"), width=160, height=28, fg_color="#7f8c8d", hover_color="#95a5a6",
                      command=self.build_team_setup_screen).pack(side="left", padx=8)

        ctk.CTkLabel(self.frame_selection, text="Montar Time Inimigo", font=("Arial", 22, "bold")).pack()
        ctk.CTkLabel(self.frame_selection, text="Filtre por nome ou selecione o tipo do alvo:", font=("Arial", 13), text_color="gray").pack(pady=2)

        enemy_filter_box = ctk.CTkFrame(self.frame_selection, fg_color="transparent")
        enemy_filter_box.pack(pady=8)

        self.enemy_search_var = ctk.StringVar()
        self.enemy_search_var.trace_add("write", self.filter_enemy_pokemon)
        ctk.CTkEntry(enemy_filter_box, placeholder_text="Filtrar por nome do alvo...", textvariable=self.enemy_search_var, width=260, height=32).grid(row=0, column=0, padx=4)

        # CORREÇÃO: Removido 'textvariable' e adicionado comando direto
        self.cmb_enemy_type = ctk.CTkComboBox(enemy_filter_box, values=["Todos os Tipos"] + self.available_types_list, 
                                              width=140, height=32, state="readonly", command=self.filter_enemy_pokemon)
        self.cmb_enemy_type.set("Todos os Tipos")
        self.cmb_enemy_type.grid(row=0, column=1, padx=4)

        self.enemy_scroll_frame = ctk.CTkScrollableFrame(self.frame_selection, height=200)
        self.enemy_scroll_frame.pack(fill="x", padx=40, pady=5)

        self.enemy_db_buttons = {}
        for idx, p_info in enumerate(POKEMON_DATABASE):
            t1_n = TYPE_NAMES[p_info["t1"]]
            t2_n = f"/{TYPE_NAMES[p_info['t2']]}" if p_info["t2"] is not None else ""
            foto_enemy = carrega_artes(p_info['name'], tamanho=(28, 28))

            btn = ctk.CTkButton(self.enemy_scroll_frame, text=f" {p_info['name']} [{t1_n}{t2_n}]", font=("Arial", 12),
                                image=foto_enemy, compound="left", anchor="w",
                                fg_color="#2b2b2b", border_color=TYPE_DATA[t1_n]["color"], border_width=1, height=35, 
                                command=lambda i=idx: self.select_enemy_from_list(i))
            btn.pack(fill="x", padx=10, pady=3)
            self.enemy_db_buttons[idx] = btn

        actions = ctk.CTkFrame(self.frame_selection, fg_color="transparent")
        actions.pack(pady=12)

        self.var_confirmed = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(actions, text="Confirmado", font=("Arial", 13), variable=self.var_confirmed).grid(row=0, column=0, padx=15)
        
        self.btn_add_enemy = ctk.CTkButton(actions, text="Adicionar Alvo Selecionado", font=("Arial", 13, "bold"), fg_color="#1f538d", command=self.add_enemy_confirmed)
        self.btn_add_enemy.grid(row=0, column=1, padx=15)
        
        ctk.CTkButton(actions, text="Desfazer", font=("Arial", 13), fg_color="#555555", command=self.undo_enemy).grid(row=0, column=2, padx=15)

        self.lbl_added = ctk.CTkLabel(self.frame_selection, text="Inimigos Adicionados: Nenhum", font=("Arial", 14, "italic"), text_color="#A8A77A")
        self.lbl_added.pack(pady=8)

        ctk.CTkButton(self.frame_selection, text="✔ CALCULAR MELHOR ESCOLHA", height=50, fg_color="#28a745", hover_color="#218838", font=("Arial", 16, "bold"), command=self.show_results).pack()

        self.selected_enemy_index = None
        self.update_enemy_list_text()

    def filter_enemy_pokemon(self, *args):
        query = self.enemy_search_var.get().lower().strip()
        selected_type = self.cmb_enemy_type.get() # Obtém o valor selecionado diretamente do componente

        for idx, p_info in enumerate(POKEMON_DATABASE):
            btn = self.enemy_db_buttons.get(idx)
            if btn:
                t1_name = TYPE_NAMES[p_info["t1"]]
                t2_name = TYPE_NAMES[p_info["t2"]] if p_info["t2"] is not None else ""

                match_name = query in p_info["name"].lower()
                match_type = (selected_type == "Todos os Tipos" or selected_type == t1_name or selected_type == t2_name)

                if match_name and match_type: 
                    btn.pack(fill="x", padx=10, pady=3)
                else: 
                    btn.pack_forget()

    def select_enemy_from_list(self, idx):
        self.selected_enemy_index = idx
        for i, btn in self.enemy_db_buttons.items():
            btn.configure(fg_color="#1f538d" if i == idx else "#2b2b2b")

    def add_enemy_confirmed(self):
        if self.selected_enemy_index is None:
            self.lbl_added.configure(text="Erro: Selecione um Pokémon da lista primeiro!", text_color="#C22E28")
            return
        
        db_p = POKEMON_DATABASE[self.selected_enemy_index]
        self.enemy_team.append(EnemyPokemon(db_p["name"], db_p["t1"], db_p["t2"], self.var_confirmed.get()))
        
        self.update_enemy_list_text()
        self.selected_enemy_index = None
        self.enemy_search_var.set("") 
        self.cmb_enemy_type.set("Todos os Tipos")
        
        for btn in self.enemy_db_buttons.values():
            btn.configure(fg_color="#2b2b2b")

    def undo_enemy(self):
        if self.enemy_team: 
            self.enemy_team.pop()
            self.update_enemy_list_text()

    def update_enemy_list_text(self):
        if not self.enemy_team: 
            self.lbl_added.configure(text="Inimigos Adicionados: Nenhum", text_color="#A8A77A")
        else: 
            nomes = [f"[{e.display_name}]" for e in self.enemy_team]
            self.lbl_added.configure(text=f"Time Inimigo ({len(self.enemy_team)}): " + ", ".join(nomes), text_color="#A8A77A")

    # --- TELA 4: RESULTADOS ---
    def show_results(self):
        if not self.enemy_team:
            self.lbl_added.configure(text="Adicione ao menos um Pokémon inimigo!", text_color="#C22E28")
            return

        evaluate_team(self.my_team, self.enemy_team)
        self.my_team.sort(key=lambda p: p.score, reverse=True)

        self.frame_selection.pack_forget()
        self.frame_results.destroy()

        self.frame_results = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_results.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.frame_results, text="ORDEM DE ENVIO IDEAL", font=("Arial", 20, "bold"), text_color="#28a745").pack(pady=5)

        textbox = ctk.CTkTextbox(self.frame_results, width=900, height=450, font=("Consolas", 14))
        textbox.pack(pady=10)

        best = self.my_team[0]
        output = f"\n 🥇 MELHOR OPÇÃO CONTRA O INIMIGO:\n"
        output += f" ➔ 1º LUGAR: {best.name.upper()} ({best.get_type_str()}) | Eficácia: {best.score} pts\n"
        output += "    Moves Considerados:\n"
        for m in best.moves:
            if m: output += f"     · {m.name:<18} | Tipo: {m.move_type_str:<10} | Cat: {m.category:<9} | {m.move_kind}\n"
        output += " —" * 40 + "\n\n"
        
        output += " 📋 FILA DE RESERVA DETALHADA:\n"
        for i in range(1, len(self.my_team)):
            p = self.my_team[i]
            m_count = sum(1 for m in p.moves if m)
            output += f"   {i+1}º Lugar: {p.name:<20} | Pontos: {p.score:<3} | Tipo: {p.get_type_str():<14} | {m_count} moves configurados\n"
            
        output += "\n " + "—" * 40 + "\n"
        output += f" ⚠️ EVITE ENVIAR:\n ➔ {len(self.my_team)}º LUGAR: {self.my_team[-1].name.upper()} ({self.my_team[-1].get_type_str()}) | Pontuação: {self.my_team[-1].score} pts\n"

        textbox.insert("1.0", output)
        ctk.CTkButton(self.frame_results, text="<- Voltar para Nova Análise", font=("Arial", 14), command=self.back_to_selection).pack(pady=10)

    def back_to_selection(self):
        self.enemy_team = []
        self.build_main_selection_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()
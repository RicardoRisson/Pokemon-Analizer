# moves.py
from efetivos import TYPE_NAMES

class Move:
    def __init__(self, name, move_type_str, category, move_kind):
        self.name = name.strip()
        self.move_type_str = move_type_str.strip() # ex: "Fire", "Normal"
        self.category = category.strip()           # "Físico" ou "Especial"
        self.move_kind = move_kind.strip()         # "Ataque Direto" ou "Buff/Debuff"
        
        self.move_type = self._resolve_type_id(self.move_type_str)

    def _resolve_type_id(self, type_str):
        # Verifica se TYPE_NAMES é um dicionário ou uma lista para evitar o AttributeError
        if hasattr(TYPE_NAMES, "items"):
            for t_id, name in TYPE_NAMES.items():
                if name.lower() == type_str.lower():
                    return t_id
        else:
            # Se for uma lista, o ID do tipo é o próprio índice dele na lista
            for t_id, name in enumerate(TYPE_NAMES):
                if name.lower() == type_str.lower():
                    return t_id
        return 0 # Caso não encontre, define como 0 (Normal)
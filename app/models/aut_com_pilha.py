from pydantic import BaseModel
from typing import List, Dict, Tuple

class AutomatoComPilha(BaseModel):
    estados: List[str]
    alfabeto_entrada: List[str]
    alfabeto_pilha: List[str]
    estado_inicial: str
    simbolo_inicial_pilha: str
    estados_finais: List[str]
    transicoes: Dict[str, Dict[str, Dict[str, Tuple[str, List[str]]]]]

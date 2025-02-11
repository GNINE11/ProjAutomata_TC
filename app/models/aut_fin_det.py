from pydantic import BaseModel
from typing import List, Dict

class AutomatoFinitoDeterministico(BaseModel):
    estados: List[str]
    alfabeto_entrada: List[str]
    estado_inicial: str
    estados_finais: List[str]
    transicoes: Dict[str, Dict[str, str]]

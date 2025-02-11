from pydantic import BaseModel
from typing import List, Dict, Tuple

class MaquinaTuring(BaseModel):
    estados: List[str]
    alfabeto_entrada: List[str]
    alfabeto_fita: List[str]
    estado_inicial: str
    estados_finais: List[str]
    branco: str
    transicoes: Dict[str, Dict[str, Tuple[str, str, str]]]

from fastapi import APIRouter, HTTPException
from ..models.aut_fin_det import AutomatoFinitoDeterministico
import uuid
from automata.fa.dfa import DFA
from fastapi.responses import FileResponse
import graphviz
from typing import Dict

router = APIRouter()

aut_fin_det_db: Dict[str, DFA] = {}

@router.post(
    "/criar",
    summary="Criar um novo autômato finito determinístico",
    response_description="Retorna o ID do autômato criado"
)
async def criar_aut_fin_det(request: AutomatoFinitoDeterministico):
    """
    Cria um novo autômato finito determinístico (AFD) com base nos dados fornecidos.

    Args:\n
        request (AutomatoFinitoDeterministico): Objeto contendo os dados do autômato:
            - estados (List[str]): Lista de estados do autômato.
            - alfabeto_entrada (List[str]): Lista de símbolos do alfabeto de entrada.
            - estado_inicial (str): Estado inicial do autômato.
            - estados_finais (List[str]): Lista de estados finais.
            - transicoes (Dict[str, Dict[str, str]]): Dicionário de transições.

    Exemplo de entrada: aceita todas as cadeias que contêm pelo menos um "a" seguido por pelo menos um "b", como: "ab", "aab", etc.

    ```json
    {
        "estados": ["q0", "q1", "q2"],
        "alfabeto_entrada": ["a", "b"],
        "estado_inicial": "q0",
        "estados_finais": ["q2"],
        "transicoes": {
            "q0": {"a": "q1", "b": "q0"},
            "q1": {"a": "q1", "b": "q2"},
            "q2": {"a": "q2", "b": "q2"}
        }
    }
    ```

    Returns:\n
        Dict[str, str]: Dicionário contendo o ID do autômato criado:
            - id (str): ID único do autômato.

    Raises:\n
        HTTPException: Erro 400 se os parâmetros do autômato forem inválidos.
    """
    aut_fin_det_id = str(uuid.uuid4())
    try:
        dfa = DFA(
            states=set(request.estados),
            input_symbols=set(request.alfabeto_entrada),
            initial_state=request.estado_inicial,
            final_states=set(request.estados_finais),
            transitions=request.transicoes
        )
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    
    aut_fin_det_db[aut_fin_det_id] = dfa
    return {"id": aut_fin_det_id}



@router.post(
    "/{aut_fin_det_id}/testar",
    summary="Testar uma entrada no autômato",
    response_description="Retorna se a entrada é aceita pelo autômato"
)
async def testar_aut_fin_det(aut_fin_det_id: str, entrada: str):
    """
    Testa se uma string de entrada é aceita pelo autômato finito determinístico (AFD).

    Args:\n
        aut_fin_det_id (str): ID do autômato a ser utilizado.
        entrada (str): String de entrada a ser testada.

    Exemplo de entrada:\n
        "aab"

    Returns:\n
        Dict[str, bool]: Dicionário indicando se a entrada foi aceita:
            - aceita (bool): True se a entrada foi aceita, False caso contrário.

    Raises:\n
        HTTPException: Erro 404 se o autômato não for encontrado.
        HTTPException: Erro 400 se a entrada for inválida.
    """
    if aut_fin_det_id not in aut_fin_det_db:
        raise HTTPException(status_code=404, detail="Autômato não encontrado")
    
    dfa = aut_fin_det_db[aut_fin_det_id]
    try:
        aceita = dfa.accepts_input(entrada)
        return {"aceita": aceita}
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get(
    "/{aut_fin_det_id}/visualizar",
    response_class=FileResponse,
    summary="Gerar visualização do autômato",
    response_description="Retorna uma imagem PNG do autômato"
)
async def visualizar_aut_fin_det(aut_fin_det_id: str):
    """
    Gera uma visualização gráfica do autômato finito determinístico (AFD) em formato PNG.

    Args:\n
        aut_fin_det_id (str): ID do autômato a ser visualizado.

    Returns:\n
        FileResponse: Arquivo PNG contendo a visualização do autômato.

    Raises:\n
        HTTPException: Erro 404 se o autômato não for encontrado.
        RuntimeError: Erro se o Graphviz não estiver instalado ou configurado corretamente.
    """
    if aut_fin_det_id not in aut_fin_det_db:
        raise HTTPException(status_code=404, detail="Autômato não encontrado")
    
    dfa = aut_fin_det_db[aut_fin_det_id]
    
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', nodesep="0.5", ranksep="1", size="10", ratio="compress", dpi = "300")

    dot.node('', '', shape='none')
    dot.edge('', dfa.initial_state)

    for estado in dfa.states:
        if estado in dfa.final_states:
            dot.node(estado, shape="doublecircle")
        else:
            dot.node(estado, shape="circle")
    
    for origem, transicoes in dfa.transitions.items():
        for simbolo, destino in transicoes.items():
            dot.edge(origem, destino, label=simbolo)

    # Espaço à direita invisível para centralizar a imagem
    dot.node("dummy", "", shape="none", width="0", height="0")
    dot.edge(list(dfa.states)[-1], "dummy", style="invis")  

    dot.render(f"aut_fin_det_{aut_fin_det_id}", format="png", cleanup=True)
    
    return FileResponse(f"aut_fin_det_{aut_fin_det_id}.png")

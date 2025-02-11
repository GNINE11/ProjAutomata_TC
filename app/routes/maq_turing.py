from fastapi import APIRouter, HTTPException
import uuid
from automata.tm.dtm import DTM
from fastapi.responses import FileResponse
import graphviz
from ..models.maq_turing import MaquinaTuring
from typing import Dict

router = APIRouter()
maquinas_turing_db: Dict[str, DTM] = {}

@router.post(
    "/criar", 
    summary="Criar uma Máquina de Turing", 
    response_description="Retorna o ID da Máquina de Turing criada"
)
async def criar_maquina_turing(request: MaquinaTuring):
    """
    Cria uma nova Máquina de Turing com base nos dados fornecidos.

    Args:\n
        request (MaquinaTuring): Objeto contendo os dados da MT:
            - estados (List[str]): Lista de estados da MT.
            - alfabeto_entrada (List[str]): Lista de símbolos do alfabeto de entrada.
            - alfabeto_fita(List[str]): Lista de símbolos do alfabeto da fita.
            - estado_inicial (str): Estado inicial da MT.
            - estados_finais (List[str]): Lista de estados finais.
            - branco (str): Símbolo que representa o branco
            - transicoes (transicoes: Dict[str, Dict[str, Tuple[str, str, str]]]): Dicionário de transições.

    Exemplo de entrada: aceita números par de a, como: "abaaba", "aaaabbb", etc.

    ```json
    {
        "estados": ["q0", "q1", "q_accept"],
        "alfabeto_entrada": ["a", "b"],
        "alfabeto_fita": ["a", "b", "_"],
        "estado_inicial": "q0",
        "estados_finais": ["q_accept"],
        "branco": "_",
        "transicoes": {
            "q0": {
                "a": ["q1", "a", "R"],
                "b": ["q0", "b", "R"],
                "_": ["q_accept", "_", "R"]
            },
            "q1": {
                "a": ["q0", "a", "R"],
                "b": ["q1", "b", "R"]
            }
        }
    }
    ```

    Returns:\n
        Dict[str, str]: Dicionário contendo o ID da MT criada:
            - id (str): ID único da MT.

    Raises:\n
        HTTPException: Erro 400 se os parâmetros do autômato forem inválidos.
    """
    maquina_turing_id = str(uuid.uuid4())
    try:
        dtm = DTM(
            states=set(request.estados),
            input_symbols=set(request.alfabeto_entrada),
            tape_symbols=set(request.alfabeto_fita),
            transitions=request.transicoes,
            initial_state=request.estado_inicial,
            blank_symbol=request.branco,
            final_states=set(request.estados_finais)
        )
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    
    maquinas_turing_db[maquina_turing_id] = dtm
    return {"id": maquina_turing_id}


@router.post(
    "/{maquina_turing_id}/testar", 
    summary="Testar uma entrada na Máquina de Turing", 
    response_description="Retorna se a entrada é aceita pela Máquina de Turing"
)
async def testar_maquina_turing(maquina_turing_id: str, entrada: str):
    """
    Testa se uma string de entrada é aceita pela Máquina de Turing.

    Args:\n
        maquina_turing_id (str): ID da MT a ser utilizada.
        entrada (str): String de entrada a ser testada.

    Exemplo de entrada:\n
        "aaaabbb"
  

    Returns:\n
        Dict[str, bool]: Dicionário indicando se a entrada foi aceita:
            - aceita (bool): True se a entrada foi aceita, False caso contrário.

    Raises:\n
        HTTPException: Erro 404 se a Máquina de Turing não for encontrada.
        HTTPException: Erro 400 se a entrada for inválida.
    """
    if maquina_turing_id not in maquinas_turing_db:
        raise HTTPException(status_code=404, detail="Máquina de Turing não encontrada")
    
    dtm = maquinas_turing_db[maquina_turing_id]
    try:
        aceita = dtm.accepts_input(entrada)
        return {"aceita": aceita}
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get(
    "/{maquina_turing_id}/visualizar", 
    response_class=FileResponse, 
    summary="Gerar visualização da Máquina de Turing", 
    response_description="Retorna uma imagem PNG da Máquina de Turing"
)
async def visualizar_maquina_turing(maquina_turing_id: str):
    """
    Gera uma visualização gráfica da Máquina de Turing em formato PNG.

    Args:\n
        maquina_turing_id (str): ID do MT a ser visualizada.

    Returns:\n
        FileResponse: Arquivo PNG contendo a visualização da MT.

    Raises:\n
        HTTPException: Erro 404 se a Máquina de Turing não for encontrada.
        RuntimeError: Erro se o Graphviz não estiver instalado ou configurado corretamente.
    """
    
    if maquina_turing_id not in maquinas_turing_db:
        raise HTTPException(status_code=404, detail="Máquina de Turing não encontrada")
    
    dtm = maquinas_turing_db[maquina_turing_id]
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', nodesep="0.5", ranksep="1", size="10", ratio="compress", dpi = "300")

    dot.node('', '', shape='none')
    dot.edge('', dtm.initial_state)
    
    for estado in dtm.states:
        if estado in dtm.final_states:
            dot.node(estado, shape="doublecircle")
        else:
            dot.node(estado)
    
    for origem, transicoes in dtm.transitions.items():
        for simbolo, (destino, escrita, direcao) in transicoes.items():
            label = f"{simbolo} → {escrita}, {direcao}"
            dot.edge(origem, destino, label=label)
            
    # Espaço à direita invisível para centralizar a imagem
    dot.node("dummy", "", shape="none", width="0", height="0")
    dot.edge(list(dtm.states)[-1], "dummy", style="invis")  

    dot.render(f"maquina_turing_{maquina_turing_id}", format="png", cleanup=True)
    return FileResponse(f"maquina_turing_{maquina_turing_id}.png")

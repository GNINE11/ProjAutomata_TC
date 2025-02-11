from fastapi import APIRouter, HTTPException
import uuid
from automata.pda.dpda import DPDA
from fastapi.responses import FileResponse
import graphviz
from ..models.aut_com_pilha import AutomatoComPilha
from typing import Dict

router = APIRouter()
aut_pilha_db: Dict[str, DPDA] = {}

@router.post(
    "/criar", 
    summary="Criar um novo autômato com pilha",
    response_description="Retorna o ID do autômato criado"
)
async def criar_aut_pilha(request: AutomatoComPilha):
    """
    Cria um novo autômato com pilha com base nos dados fornecidos.

    Args:\n
        request (AutomatoComPilha): Objeto contendo os dados do autômato:
            - estados (List[str]): Lista de estados do autômato.
            - alfabeto_entrada (List[str]): Lista de símbolos do alfabeto de entrada.
            - alfabeto_pilha(List[str]): Lista de símbolos do alfabeto da pilha.
            - simbolo_inicial_pilha (str): Símbolo inicial da pilha.
            - estado_inicial (str): Estado inicial do autômato.
            - estados_finais (List[str]): Lista de estados finais.
            - transicoes (Dict[str, Dict[str, Dict[str, Tuple[str, List[str]]]]]): Dicionário de transições.

    Exemplo de entrada: aceita (a^n b^n), como: "ab", "aaabbb", etc.

    ```json
    {
        "estados": ["q0", "q1", "q2"],
        "alfabeto_entrada": ["a", "b"],
        "alfabeto_pilha": ["A", "Z"],
        "estado_inicial": "q0",
        "simbolo_inicial_pilha": "Z",
        "estados_finais": ["q2"],
        "transicoes": {
            "q0": {
                "a": {
                    "Z": ["q0", ["A", "Z"]],
                    "A": ["q0", ["A", "A"]]
                },
                "b": {
                    "A": ["q1", []]
                }
            },
            "q1": {
                "b": {
                    "A": ["q1", []]
                },
                "": {
                    "Z": ["q2", ["Z"]]
                }
            }
        }
    }
    ```

    Returns:\n
        Dict[str, str]: Dicionário contendo o ID do autômato criado:
            - id (str): ID único do autômato.

    Raises:\n
        HTTPException: Erro 400 se os parâmetros do autômato forem inválidos.
    """

    aut_pilha_id = str(uuid.uuid4())
    try:
        formatted_transitions = {
            state: {
                input_sym: {
                    stack_sym: (dest_state, tuple(stack_symbols))
                    for stack_sym, (dest_state, stack_symbols) in stack_trans.items()
                }
                for input_sym, stack_trans in input_trans.items()
            }
            for state, input_trans in request.transicoes.items()
        }
        
        pda = DPDA(
            states=set(request.estados),
            input_symbols=set(request.alfabeto_entrada),
            stack_symbols=set(request.alfabeto_pilha),
            initial_state=request.estado_inicial,
            initial_stack_symbol=request.simbolo_inicial_pilha,
            final_states=set(request.estados_finais),
            transitions=formatted_transitions
        )
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    
    aut_pilha_db[aut_pilha_id] = pda
    return {"id": aut_pilha_id}


@router.post(
    "/{aut_pilha_id}/testar",
     summary="Testar uma entrada no autômato", 
     response_description="Retorna se a entrada é aceita pelo autômato"
)

async def testar_aut_pilha(aut_pilha_id: str, entrada: str):
    """
    Testa se uma string de entrada é aceita pelo autômato com pilha.

    Args:\n
        aut_pilha_id (str): ID do autômato a ser utilizado.
        entrada (str): String de entrada a ser testada.

    Exemplo de entrada:\n
        "aaabbb"

    Returns:\n
        Dict[str, bool]: Dicionário indicando se a entrada foi aceita:
            - aceita (bool): True se a entrada foi aceita, False caso contrário.

    Raises:\n
        HTTPException: Erro 404 se o autômato não for encontrado.
        HTTPException: Erro 400 se a entrada for inválida.
    """
    
    if aut_pilha_id not in aut_pilha_db:
        raise HTTPException(status_code=404, detail="Autômato não encontrado")
    
    pda = aut_pilha_db[aut_pilha_id]
    try:
        aceita = pda.accepts_input(entrada)
        return {"aceita": aceita}
    except Exception as erro:
        raise HTTPException(status_code=400, detail=str(erro))


@router.get(
    "/{aut_pilha_id}/visualizar", 
    response_class=FileResponse,
    summary="Gerar visualização do autômato",
    response_description="Retorna uma imagem PNG do autômato"
)
async def visualizar_aut_pilha(aut_pilha_id: str):
    """
    Gera uma visualização gráfica do autômato com pilha em formato PNG.

    Args:\n
        aut_pilha_id (str): ID do autômato a ser visualizado.

    Returns:\n
        FileResponse: Arquivo PNG contendo a visualização do autômato.

    Raises:\n
        HTTPException: Erro 404 se o autômato não for encontrado.
        RuntimeError: Erro se o Graphviz não estiver instalado ou configurado corretamente.
    """
    if aut_pilha_id not in aut_pilha_db:
        raise HTTPException(status_code=404, detail="Autômato não encontrado")
    
    pda = aut_pilha_db[aut_pilha_id]
    dot = graphviz.Digraph()
    dot.attr(rankdir='LR', nodesep="0.5", ranksep="1", size="10", ratio="compress", dpi = "300")
    
    dot.node('', '', shape='none')
    dot.edge('', pda.initial_state)

    
    for estado in pda.states:
        if estado in pda.final_states:
            dot.node(estado, shape="doublecircle")
        else:
            dot.node(estado)
    
    for from_state, input_dict in pda.transitions.items():
        for input_symbol, stack_dict in input_dict.items():
            for stack_top, (to_state, stack_push) in stack_dict.items():
                label = f"{input_symbol},{stack_top}/{','.join(stack_push) if stack_push else 'ε'}"
                dot.edge(from_state, to_state, label=label)
    
    # Espaço à direita invisível para centralizar a imagem
    dot.node("dummy", "", shape="none", width="0", height="0")
    dot.edge(list(pda.states)[-1], "dummy", style="invis")  
    
    dot.render(f"aut_pilha_{aut_pilha_id}", format="png", cleanup=True)
    return FileResponse(f"aut_pilha_{aut_pilha_id}.png")    
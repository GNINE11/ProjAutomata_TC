# AutomataAPI - Simulador de Autômatos e Máquina de Turing

Este projeto implementa uma API RESTful para simular diferentes tipos de autômatos e máquina de Turing, incluindo:
- Autômato Finito Determinístico (AFD)
- Autômato com Pilha (AP)
- Máquina de Turing (MT)

## Configuração do Ambiente

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Graphviz (para visualização dos autômatos)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/GNINE11/ProjAutomata_TC.git
cd ProjAutomata_TC
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Instale o Graphviz:
- **Ubuntu/Debian**: `sudo apt-get install graphviz`
- **MacOS**: `brew install graphviz`
- **Windows**: Baixe e instale do [site oficial](https://graphviz.org/download/)

### Executando o Projeto

1. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```
2. Caso o comando acima retorne um erro informando que uvicorn não foi encontrado, utilize:
```bash
python -m uvicorn app.main:app --reload
```
3. Acesse:
- Interface Web: `http://localhost:8000`
- Documentação da API: `http://localhost:8000/docs`

## Uso da API

### Autômato Finito Determinístico (AFD)

#### Criar AFD
Exemplo de entrada: AFD que aceita todas as cadeias que contêm pelo menos um "a" seguido por pelo menos um "b", como: "ab", "aab", etc.
```bash
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

#### Testar entrada
Exemplo de entrada:
```bash
aab
```



### Autômato com Pilha (AP)

#### Criar AP
Exemplo de entrada: AP que aceita (a^n b^n), como: "ab", "aaabbb", etc.
```bash
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

#### Testar entrada
Exemplo de entrada:
```bash
aabb
```



### Máquina de Turing (MT)

#### Criar MT
Exemplo de entrada: MT que aceita números par de a, como: "abaaba", "aaaabbb", etc.
```bash
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

#### Testar entrada
Exemplo de entrada:
```bash
ababaa
```


## Limitações e Pressupostos

### Limitações
1. **Autômatos Finitos**:
   - Suporta apenas autômatos determinísticos
   - Não implementa minimização de estados
   - Não suporta ε-transições

2. **Autômatos com Pilha**:
   - Suporta apenas autômatos determinísticos
   - Aceita por estado final (não por pilha vazia)
   - Não suporta múltiplos símbolos de entrada por transição

3. **Máquina de Turing**:
   - Suporta apenas máquinas determinísticas
   - Fita infinita apenas à direita
   - Não implementa máquinas multi-fita

### Pressupostos
1. Os identificadores de estados devem ser strings únicas
2. Símbolos do alfabeto devem ser caracteres únicos
3. Todas as transições devem ser definidas explicitamente
4. O estado inicial deve estar incluído no conjunto de estados
5. Os estados finais devem estar incluídos no conjunto de estados
6. O símbolo branco ('_') é reservado para a Máquina de Turing

### Observações de Implementação
- Os autômatos são mantidos em memória usando um dicionário
- Os IDs são gerados usando UUID4
- A visualização é gerada usando Graphviz
- A API não possui persistência de dados
- Os autômatos são perdidos ao reiniciar o servidor

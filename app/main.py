from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes import aut_fin_det, aut_com_pilha, maq_turing

app = FastAPI(title="AutomataAPI_TC_GabrielJardim", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Redirecionamento automático para a interface
@app.get("/", include_in_schema=False)
async def redirect_to_index():
    return RedirectResponse(url="/static/index.html")

# Rotas da API
app.include_router(aut_fin_det.router, prefix="/afd", tags=["Autômato Finito Determinístico"])
app.include_router(aut_com_pilha.router, prefix="/ap", tags=["Autômato Com Pilha"])
app.include_router(maq_turing.router, prefix="/mt", tags=["Máquina de Turing"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

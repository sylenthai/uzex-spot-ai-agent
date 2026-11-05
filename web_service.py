"""
UZEX Birja Bitimlari AI Agent — FastAPI Web Service
Provides REST API endpoints and an interactive Web UI for spot exchange queries.
Includes interactive Swagger docs at /docs and OpenAPI schema.
"""

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine import database
from engine.router import route_query

app = FastAPI(
    title="UZEX Spot Bitimlari AI Agent API",
    description="500 000 ta birja bitimlari asosida o'zbek va rus tillarida xizmat ko'rsatuvchi zero-hallucination AI-agent REST API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., examples=["504707-sonli bitim haqida ma'lumot ber"])
    language: Optional[str] = Field(None, examples=["uz"], description="'uz' or 'ru'")

class QueryResponse(BaseModel):
    intent: str
    language: str
    found: bool
    response_text: str
    entity_type: Optional[str] = None
    entity_value: Optional[str] = None
    raw_data: Optional[Any] = None

@app.post("/api/query", response_model=QueryResponse, summary="Universal Natural Language & Structured Query Endpoint")
def process_query(req: QueryRequest):
    """
    Processes natural language questions or structured entity queries in Uzbek or Russian.
    Enforces strict Zero-Hallucination: returns 'found=False' with polite refusal if data is absent.
    """
    res = route_query(req.query, forced_lang=req.language)
    return QueryResponse(
        intent=res["intent"],
        language=res["language"],
        found=res["found"],
        response_text=res["response_text"],
        entity_type=res.get("entity_type"),
        entity_value=res.get("entity_value"),
        raw_data=res.get("raw_data")
    )

@app.get("/api/deal/{deal_id}", summary="Get Deal Details by Deal Number")
def get_deal(deal_id: int):
    d = database.get_deal_by_id(deal_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Deal #{deal_id} not found in UZEX registry.")
    return d

@app.get("/api/contract/{contract_id}", summary="Get Contract Details by Contract Number")
def get_contract(contract_id: int):
    c = database.get_contract_by_id(contract_id)
    if not c:
        raise HTTPException(status_code=404, detail=f"Contract #{contract_id} not found.")
    return c

@app.get("/api/company/{inn}", summary="Get Participant Company Profile by INN/STIR")
def get_company(inn: str):
    p = database.get_participant_by_inn(inn)
    if not p:
        raise HTTPException(status_code=404, detail=f"Company with INN {inn} not found.")
    return p

@app.get("/api/broker/{code}", summary="Get Broker Details by Broker Code")
def get_broker(code: str):
    b = database.get_broker_by_code(code)
    if not b:
        raise HTTPException(status_code=404, detail=f"Broker {code} not found.")
    return b

@app.get("/api/stats/overview", summary="High-level Exchange Statistics")
def get_overview(year: Optional[int] = Query(None, description="Year between 2022 and 2026")):
    return database.get_general_stats(year=year)

@app.get("/api/stats/top-sellers", summary="Top Sellers Leaderboard")
def get_top_sellers_api(limit: int = 5, year: Optional[int] = Query(None)):
    return database.get_top_sellers(limit=limit, year=year)

@app.get("/api/stats/top-buyers", summary="Top Buyers Leaderboard")
def get_top_buyers_api(limit: int = 5, year: Optional[int] = Query(None)):
    return database.get_top_buyers(limit=limit, year=year)

@app.get("/api/stats/region", summary="Regional Exchange Statistics")
def get_region_api(region: str = Query(..., examples=["Toshkent"]), year: Optional[int] = Query(None)):
    res = database.get_region_stats(region, year=year)
    if not res:
        raise HTTPException(status_code=404, detail=f"No data for region '{region}'.")
    return res

@app.get("/api/price-trend", summary="Commodity Price Trend Dynamics")
def get_price_trend(product: str = Query(..., examples=["цемент"]), year: Optional[int] = Query(None)):
    stats = database.get_product_price_stats(product, year=year)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No trade records found for commodity '{product}'.")
    return stats

@app.get("/api/usd-rate", summary="USD Daily Exchange Rate")
def get_usd(date: Optional[str] = Query(None, description="DD.MM.YYYY format")):
    if date:
        rate = database.get_usd_rate(date)
    else:
        rate = database.get_latest_usd_rate()
    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate for specified date not found.")
    return rate

@app.get("/", response_class=HTMLResponse, summary="Interactive Web Chat & Dashboard Interface")
def web_dashboard():
    """Serves a modern, responsive web dashboard for testing queries."""
    html_content = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>UZEX Spot Bitimlari AI Agent</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
            .header-box { background: linear-gradient(135deg, #1e293b, #0f172a); border-bottom: 1px solid #334155; padding: 2rem 0; }
            .card { background: #1e293b; border: 1px solid #334155; color: #f8fafc; border-radius: 12px; }
            .btn-primary { background: #3b82f6; border: none; font-weight: 600; }
            .btn-primary:hover { background: #2563eb; }
            .chat-container { height: 420px; overflow-y: auto; padding: 1rem; background: #0b1120; border-radius: 8px; border: 1px solid #334155; }
            .msg-user { background: #1e3a8a; padding: 10px 14px; border-radius: 14px; margin-bottom: 10px; max-width: 80%; margin-left: auto; }
            .msg-bot { background: #1e293b; border: 1px solid #475569; padding: 12px 16px; border-radius: 14px; margin-bottom: 12px; max-width: 85%; }
            .badge-custom { background: #334155; color: #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; margin: 4px; cursor: pointer; display: inline-block; }
            .badge-custom:hover { background: #3b82f6; color: #fff; }
        </style>
    </head>
    <body>
        <div class="header-box text-center">
            <div class="container">
                <h1 class="fw-bold mb-2">🏛 UZEX Spot Bitimlari AI Agenti</h1>
                <p class="text-secondary mb-0">500 000 ta birja bitimi (2022-2026) bo'yicha qat'iy ma'lumotga asoslangan tahliliy tizim (RU + UZ)</p>
                <div class="mt-2">
                    <span class="badge bg-success">500 000 Deals</span>
                    <span class="badge bg-info text-dark">6 616 Contracts</span>
                    <span class="badge bg-primary">14 392 Companies</span>
                    <span class="badge bg-warning text-dark">Zero-Hallucination Guardrail</span>
                </div>
            </div>
        </div>

        <div class="container my-4">
            <div class="row">
                <div class="col-lg-8 mx-auto">
                    <div class="card p-3 shadow-lg">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0">💬 Interaktiv So'rov Oynasi</h5>
                            <a href="/docs" target="_blank" class="btn btn-sm btn-outline-info">REST API Swagger</a>
                        </div>
                        
                        <div id="chatBox" class="chat-container mb-3">
                            <div class="msg-bot">
                                <b>Assalomu alaykum!</b> Birja bitimlari, shartnomalar, tovar narxlari yoki ishtirokchilar bo'yicha savolingizni yozing.
                            </div>
                        </div>

                        <div class="mb-3">
                            <small class="text-secondary d-block mb-1">Tezkor namunaviy so'rovlar:</small>
                            <span class="badge-custom" onclick="sendQuick('Bitim 504707')">🔍 Bitim 504707</span>
                            <span class="badge-custom" onclick="sendQuick('Shartnoma 100001')">📄 Shartnoma 100001</span>
                            <span class="badge-custom" onclick="sendQuick('915688255')">🏢 STIR 915688255</span>
                            <span class="badge-custom" onclick="sendQuick('sement narxi qancha')">📊 Sement narxi</span>
                            <span class="badge-custom" onclick="sendQuick('топ продавцов за 2024 год')">🏆 Топ продавцов 2024</span>
                            <span class="badge-custom" onclick="sendQuick('Apple Inc qancha paxta sotdi?')">❌ Apple Inc (Zero-Hallucination)</span>
                        </div>

                        <div class="input-group">
                            <input type="text" id="userInput" class="form-control bg-dark text-white border-secondary" placeholder="Savol yoki bitim raqamini kiriting...">
                            <button class="btn btn-primary px-4" onclick="handleSend()">Yuborish</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function appendMsg(text, isUser = false) {
                const box = document.getElementById('chatBox');
                const div = document.createElement('div');
                div.className = isUser ? 'msg-user' : 'msg-bot';
                div.innerHTML = text.replace(/\\n/g, '<br>');
                box.appendChild(div);
                box.scrollTop = box.scrollHeight;
            }

            async function handleSend() {
                const input = document.getElementById('userInput');
                const text = input.value.trim();
                if (!text) return;

                appendMsg(text, true);
                input.value = '';

                try {
                    const res = await fetch('/api/query', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query: text })
                    });
                    const data = await res.json();
                    appendMsg(data.response_text);
                } catch (e) {
                    appendMsg('Xatolik yuz berdi: ' + e);
                }
            }

            function sendQuick(q) {
                document.getElementById('userInput').value = q;
                handleSend();
            }

            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') handleSend();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_service:app", host="127.0.0.1", port=8000, reload=True)

import pandas as pd
import requests
from io import StringIO
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ضع روابطك الحقيقية هنا ---
SHEET_URLS = {
    "Football": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=621025358&single=true&output=csv",
    "Dodgeball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=863642824&single=true&output=csv",
    "Volleyball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=1033302345&single=true&output=csv",
    "Ultimate Ball": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=2017169226&single=true&output=csv"
}

MATCHES_URLS = {
    "Day1": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=1977977902&single=true&output=csv",
    "Day2": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqzlySvoK19S0Maw_xLSlUMmGcOPx6eNqiwKJKCtrHwkDxKuO95ZJKbvyNcXns8TxRe1oYnhZRtlNs/pub?gid=1547895490&single=true&output=csv",
}

all_sports_data = {k: [] for k in SHEET_URLS.keys()}
all_matches_data = {k: [] for k in MATCHES_URLS.keys()}

async def sync_all_data_loop():
    while True:
        print("🔄 جاري مزامنة كل البيانات من Google Sheets...")
        loop = asyncio.get_event_loop()
        
        # مزامنة جداول الترتيب
        for sport, url in SHEET_URLS.items():
            try:
                response = await loop.run_in_executor(None, requests.get, url)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    df = pd.read_csv(StringIO(response.text))
                    df.columns = df.columns.str.strip()
                    df.rename(columns=lambda x: x.replace('\n', '').strip(), inplace=True)
                    if 'المجموعة' in df.columns and 'نقاط' in df.columns:
                        df['نقاط'] = pd.to_numeric(df['نقاط'], errors='coerce').fillna(0)
                        df = df.sort_values(by=['المجموعة', 'نقاط'], ascending=[True, False])
                        all_sports_data[sport] = df.to_dict(orient='records')
            except Exception as e: print(f"❌ خطأ {sport}: {e}")

        # مزامنة المباريات
        for day, url in MATCHES_URLS.items():
            try:
                response = await loop.run_in_executor(None, requests.get, url)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    df = pd.read_csv(StringIO(response.text))
                    df.columns = df.columns.str.strip()
                    all_matches_data[day] = df.to_dict(orient='records')
            except Exception as e: print(f"❌ خطأ {day}: {e}")
        
        print("✅ تم تحديث كل البيانات")
        await asyncio.sleep(120)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_all_data_loop())

@app.get("/")
async def serve_home(): return FileResponse("index.html")

@app.get("/standings/{sport_name}")
def get_standings(sport_name: str):
    data = all_sports_data.get(sport_name, [])
    groups = {}
    for entry in data:
        grp = str(entry.get('المجموعة', 'A'))
        if grp not in groups: groups[grp] = []
        groups[grp].append(entry)
    return groups

@app.get("/matches/{day_name}")
def get_matches(day_name: str):
    return all_matches_data.get(day_name, [])

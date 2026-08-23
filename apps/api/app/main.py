from fastapi import FastAPI

app = FastAPI(
    title="LedgerGuard API",
    description="AI Finance Controller API for Razorpay AI Buildathon",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "LedgerGuard API"}

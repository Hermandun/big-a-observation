from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, stock_analysis
from services.news_monitor import NewsMonitor
from services.auth_service import AuthService

app = FastAPI(title="A股观察室")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # 允许 Live Server 的默认地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(stock_analysis.router, prefix="/api/analysis", tags=["股票分析"])

@app.on_event("startup")
async def startup_event():
    # 确保默认用户存在
    auth_service = AuthService()
    auth_service.ensure_default_user()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
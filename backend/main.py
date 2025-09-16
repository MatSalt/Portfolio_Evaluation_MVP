from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
from api.analyze import router as analyze_router

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Portfolio Evaluation MVP API",
    description="AI 포트폴리오 분석 API - Gemini 2.5 Flash 기반 마크다운 리포트 생성",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
# 원래 설정 (프로덕션용)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         os.getenv("FRONTEND_URL", "http://localhost:3000"),
#         "http://localhost:3000",
#         "https://portfolio-evaluation-mvp.vercel.app"  # 배포용
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     allow_headers=["*"],
#     expose_headers=["*"]
# )

# 임시 설정 (모든 도메인 허용 - 배포 테스트용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=False,  # credentials는 false로 설정
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 글로벌 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "내부 서버 오류가 발생했습니다.", "detail": str(exc)}
    )

# 라우터 등록
app.include_router(analyze_router, prefix="/api", tags=["분석"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Portfolio Evaluation MVP API", 
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs",
        "output_format": "markdown_text"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # Gemini API 키 확인
        api_key = os.getenv("GEMINI_API_KEY")
        api_key_status = "configured" if api_key else "missing"
        
        return {
            "status": "healthy", 
            "version": "0.1.0",
            "gemini_api_key": api_key_status,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "output_format": "markdown_text"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info"
    )

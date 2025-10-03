"""
포트폴리오 분석 API 엔드포인트

이 모듈은 포트폴리오 이미지 분석을 위한 FastAPI 엔드포인트들을 제공합니다.
마크다운 텍스트 출력 방식에 최적화된 API를 구현합니다.
"""

import time
import uuid
import logging
from typing import Optional, List, Union
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from models.portfolio import (
    AnalysisResponse, AnalysisRequest, 
    ErrorResponse, StructuredAnalysisResponse
)
from services.gemini_service import get_gemini_service, GeminiService
from utils.image_utils import validate_image, is_supported_image_type, get_image_info

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter()

@router.post(
    "/analyze",
    response_model=Union[AnalysisResponse, StructuredAnalysisResponse],
    responses={
        200: {"description": "분석 성공"},
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 오류"},
        503: {"model": ErrorResponse, "description": "서비스 사용 불가"},
    },
    summary="포트폴리오 이미지 분석",
    description="업로드된 포트폴리오 스크린샷을 분석하여 마크다운 또는 4개 탭 구조의 JSON을 반환합니다. 기본값은 마크다운입니다."
)
async def analyze_portfolio(
    files: List[UploadFile] = File(
        default=[],
        description="포트폴리오 스크린샷 파일들 (1-5개), 필드명: files"
    ),
    file: Optional[UploadFile] = File(
        default=None,
        description="단일 파일 업로드 하위호환 필드명: file"
    ),
    format: str = Query(
        default="markdown",
        description="출력 형식: 'json' (구조화된 출력) 또는 'markdown' (기존 방식)",
        regex="^(json|markdown)$"
    ),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """
    포트폴리오 이미지 분석 엔드포인트 (단일/다중 통합)
    
    Args:
        files: 업로드된 이미지 파일들 (1-5개)
        format: 출력 형식 ('json' | 'markdown')
        background_tasks: 백그라운드 작업
        gemini_service: Gemini 서비스 인스턴스
    
    Returns:
        AnalysisResponse | StructuredAnalysisResponse
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # 하위호환: 단일 파일 필드 지원(file -> files 승격)
        incoming_files: List[UploadFile] = []
        if files:
            incoming_files = list(files)
        elif file is not None:
            incoming_files = [file]

        logger.info(
            f"포트폴리오 분석 요청 시작 (ID: {request_id}, 파일 수: {len(incoming_files)}, format: {format})"
        )
        
        # 1. 파일 개수 검증
        if not incoming_files or len(incoming_files) == 0:
            raise HTTPException(
                status_code=422,
                detail="최소 1개의 파일이 필요합니다."
            )
        
        if len(incoming_files) > 5:
            raise HTTPException(
                status_code=400,
                detail="최대 5개의 파일만 업로드 가능합니다."
            )
        
        # 2. 파일 유효성 검사 및 데이터 읽기
        image_data_list = []
        for i, file in enumerate(incoming_files):
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}의 파일명이 없습니다."
                )
            
            # Content-Type 검증
            if not is_supported_image_type(file.content_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: 지원하지 않는 파일 형식입니다. (지원: JPEG, PNG)"
                )
            
            # 파일 데이터 읽기
            try:
                image_data = await file.read()
            except Exception as e:
                logger.error(f"파일 {i+1} 읽기 실패 (ID: {request_id}): {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}을 읽을 수 없습니다."
                )
            
            # 이미지 검증
            try:
                await validate_image(image_data, file.filename)
                logger.info(f"이미지 {i+1} 검증 성공 (ID: {request_id})")
            except ValueError as e:
                logger.warning(f"이미지 {i+1} 검증 실패 (ID: {request_id}): {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"파일 {i+1}: {str(e)}"
                )
            
            image_data_list.append(image_data)
        
        # 3. Gemini API를 통한 분석 (format에 따라 구조화/마크다운 통합 처리)
        try:
            logger.info(f"Gemini 분석 시작 (ID: {request_id}, 이미지 수: {len(image_data_list)}, format: {format})")
            result = await gemini_service.analyze_portfolio_structured(
                image_data_list=image_data_list,
                format_type=format
            )
            logger.info(f"Gemini 분석 완료 (ID: {request_id})")
            
        except TimeoutError as e:
            logger.error(f"Gemini API 타임아웃 (ID: {request_id}): {str(e)}")
            if len(image_data_list) > 1:
                raise HTTPException(
                    status_code=503,
                    detail="다중 이미지 분석 시간이 초과되었습니다. 이미지 수를 줄이거나 잠시 후 다시 시도해 주세요."
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="분석 요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요."
                )
        except ValueError as e:
            logger.error(f"Gemini 분석 값 오류 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Gemini 분석 실패 (ID: {request_id}): {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="AI 분석 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해 주세요."
            )
        
        # 4. 응답 생성 및 백그라운드 로깅
        processing_time = time.time() - start_time
        
        # result는 AnalysisResponse 또는 StructuredAnalysisResponse
        if isinstance(result, AnalysisResponse):
            response = result
            content_length = len(result.content)
        else:
            response = result
            content_length = 0
        
        # 백그라운드 로깅
        total_file_size = sum(len(data) for data in image_data_list)
        background_tasks.add_task(
            log_analysis_success,
            request_id=request_id,
            filename=f"{len(incoming_files)}개 파일",
            file_size=total_file_size,
            processing_time=processing_time,
            content_length=content_length
        )
        
        logger.info(f"포트폴리오 분석 완료 (ID: {request_id}, {processing_time:.2f}초, format: {format})")
        return response
        
    except HTTPException:
        # HTTPException은 그대로 전달
        raise
    except Exception as e:
        # 예상치 못한 오류
        logger.error(f"예상치 못한 오류 (ID: {request_id}): {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )

@router.get(
    "/analyze/sample",
    response_model=AnalysisResponse,
    summary="샘플 분석 결과",
    description="테스트용 샘플 포트폴리오 마크다운 분석 결과를 반환합니다."
)
async def get_sample_analysis(
    gemini_service: GeminiService = Depends(get_gemini_service)
):
    """샘플 분석 결과 반환 (테스트/데모용) - 마크다운 텍스트"""
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"샘플 마크다운 분석 요청 (ID: {request_id})")
        
        markdown_content = await gemini_service.get_sample_analysis()
        
        response = AnalysisResponse(
            content=markdown_content,
            processing_time=0.1,  # 즉시 반환
            request_id=request_id,
            images_processed=1  # 샘플은 단일 이미지로 처리
        )
        
        logger.info(f"샘플 마크다운 분석 반환 완료 (ID: {request_id})")
        return response
        
    except Exception as e:
        logger.error(f"샘플 분석 실패 (ID: {request_id}): {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="샘플 데이터 생성 실패"
        )

# 백그라운드 작업 함수들
async def log_analysis_success(
    request_id: str,
    filename: str,
    file_size: int,
    processing_time: float,
    content_length: int
):
    """분석 성공 로깅 (백그라운드)"""
    logger.info(
        f"분석 완료 통계 - "
        f"ID: {request_id}, "
        f"파일: {filename}, "
        f"크기: {file_size:,}bytes, "
        f"처리시간: {processing_time:.2f}초, "
        f"마크다운 길이: {content_length:,}자"
    )

# 에러 핸들러는 main.py의 글로벌 핸들러에서 처리됩니다.

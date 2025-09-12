"""
이미지 처리 유틸리티

이 모듈은 이미지 파일의 검증, 최적화, 정보 추출을 담당합니다.
"""

import os
from typing import Tuple, Optional
from io import BytesIO
from PIL import Image, ImageOps
import logging

logger = logging.getLogger(__name__)

# 설정값
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_MIME_TYPES = os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/jpg").split(",")
MAX_IMAGE_DIMENSION = 2048  # 최대 이미지 크기
JPEG_QUALITY = 85  # JPEG 압축 품질

async def validate_image(image_data: bytes, filename: Optional[str] = None) -> None:
    """
    이미지 파일 검증
    
    Args:
        image_data: 이미지 바이트 데이터
        filename: 파일명 (선택적)
        
    Raises:
        ValueError: 검증 실패
    """
    try:
        # 파일 크기 검증
        if len(image_data) > MAX_FILE_SIZE:
            raise ValueError(f"파일 크기가 {MAX_FILE_SIZE / 1024 / 1024:.1f}MB를 초과합니다.")
        
        if len(image_data) == 0:
            raise ValueError("빈 파일입니다.")
        
        # PIL로 이미지 검증
        try:
            with Image.open(BytesIO(image_data)) as img:
                # 이미지 포맷 검증
                if img.format not in ['JPEG', 'PNG', 'JPG']:
                    raise ValueError(f"지원하지 않는 이미지 형식입니다. (지원: JPEG, PNG)")
                
                # 이미지 크기 검증
                width, height = img.size
                if width < 100 or height < 100:
                    raise ValueError("이미지 크기가 너무 작습니다. (최소 100x100)")
                
                if width > 10000 or height > 10000:
                    raise ValueError("이미지 크기가 너무 큽니다. (최대 10000x10000)")
                
                # 이미지 모드 검증 (RGB, RGBA만 허용)
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    logger.warning(f"이미지 모드 변환 필요: {img.mode} -> RGB")
                
                logger.info(f"이미지 검증 성공: {width}x{height}, {img.format}, {img.mode}")
                
        except Exception as e:
            raise ValueError(f"유효하지 않은 이미지 파일입니다: {str(e)}")
            
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"이미지 검증 중 오류: {str(e)}")
        raise ValueError(f"이미지 검증 실패: {str(e)}")

async def optimize_image(image_data: bytes) -> bytes:
    """
    이미지 최적화 (크기 조정 및 압축)
    
    Args:
        image_data: 원본 이미지 바이트 데이터
        
    Returns:
        bytes: 최적화된 이미지 바이트 데이터
        
    Raises:
        ValueError: 이미지 처리 실패
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            original_size = len(image_data)
            original_dimensions = img.size
            
            # EXIF 정보 기반 회전 수정
            img = ImageOps.exif_transpose(img)
            
            # RGBA를 RGB로 변환 (JPEG 호환성)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # 알파 채널을 마스크로 사용
                img = background
            elif img.mode not in ['RGB', 'L']:
                img = img.convert('RGB')
            
            # 이미지 크기 조정
            if max(img.size) > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
                logger.info(f"이미지 크기 조정: {original_dimensions} -> {img.size}")
            
            # 최적화된 이미지 저장
            output_buffer = BytesIO()
            
            if img.format == 'PNG' or any(band.mode == 'RGBA' for band in [img]):
                # PNG는 무손실 압축
                img.save(output_buffer, format='PNG', optimize=True)
                format_used = 'PNG'
            else:
                # JPEG 압축
                img.save(output_buffer, format='JPEG', quality=JPEG_QUALITY, optimize=True)
                format_used = 'JPEG'
            
            optimized_data = output_buffer.getvalue()
            optimized_size = len(optimized_data)
            
            compression_ratio = (1 - optimized_size / original_size) * 100
            logger.info(f"이미지 최적화 완료: {format_used}, "
                       f"{original_size:,} -> {optimized_size:,} bytes "
                       f"({compression_ratio:.1f}% 압축)")
            
            return optimized_data
            
    except Exception as e:
        logger.error(f"이미지 최적화 실패: {str(e)}")
        raise ValueError(f"이미지 처리 실패: {str(e)}")

async def get_image_info(image_data: bytes) -> dict:
    """
    이미지 정보 추출
    
    Args:
        image_data: 이미지 바이트 데이터
        
    Returns:
        dict: 이미지 정보
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            return {
                "format": img.format,
                "mode": img.mode,
                "size": img.size,
                "width": img.size[0],
                "height": img.size[1],
                "file_size": len(image_data),
                "has_transparency": img.mode in ['RGBA', 'LA'] or 'transparency' in img.info
            }
    except Exception as e:
        logger.error(f"이미지 정보 추출 실패: {str(e)}")
        return {}

# 지원되는 MIME 타입 확인
def is_supported_image_type(content_type: str) -> bool:
    """지원되는 이미지 타입인지 확인"""
    return content_type.lower() in [mime.strip().lower() for mime in ALLOWED_MIME_TYPES]

# 파일 확장자로 MIME 타입 추측
def guess_content_type(filename: str) -> Optional[str]:
    """파일 확장자로 MIME 타입 추측"""
    if not filename:
        return None
    
    extension = filename.lower().split('.')[-1]
    mime_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    return mime_map.get(extension)

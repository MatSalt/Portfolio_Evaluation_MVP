"""
이미지 유틸리티 테스트

이 모듈은 이미지 처리 유틸리티 함수들의 단위 테스트를 제공합니다.
"""

import pytest
import asyncio
from unittest.mock import patch, Mock
from PIL import Image
from io import BytesIO
from utils.image_utils import (
    validate_image, optimize_image, get_image_info,
    is_supported_image_type, guess_content_type
)

class TestImageUtils:
    """이미지 유틸리티 테스트 클래스"""
    
    @pytest.fixture
    def sample_image_data(self):
        """테스트용 이미지 데이터"""
        # 500x500 RGB 이미지 생성
        img = Image.new('RGB', (500, 500), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    @pytest.fixture
    def large_image_data(self):
        """큰 이미지 데이터 (11MB)"""
        return b'x' * (11 * 1024 * 1024)
    
    @pytest.fixture
    def small_image_data(self):
        """작은 이미지 데이터 (50x50)"""
        img = Image.new('RGB', (50, 50), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()
    
    @pytest.mark.asyncio
    async def test_validate_image_success(self, sample_image_data):
        """정상 이미지 검증 성공 테스트"""
        # 예외가 발생하지 않아야 함
        await validate_image(sample_image_data, 'test.jpg')
        assert True  # 예외 없이 통과
    
    @pytest.mark.asyncio
    async def test_validate_image_empty_file(self):
        """빈 파일 검증 실패 테스트"""
        with pytest.raises(ValueError, match="빈 파일입니다"):
            await validate_image(b'', 'empty.jpg')
    
    @pytest.mark.asyncio
    async def test_validate_image_too_large(self, large_image_data):
        """큰 파일 검증 실패 테스트"""
        with pytest.raises(ValueError, match="파일 크기가.*초과합니다"):
            await validate_image(large_image_data, 'large.jpg')
    
    @pytest.mark.asyncio
    async def test_validate_image_too_small(self, small_image_data):
        """작은 이미지 검증 실패 테스트"""
        with pytest.raises(ValueError, match="이미지 크기가 너무 작습니다"):
            await validate_image(small_image_data, 'small.jpg')
    
    @pytest.mark.asyncio
    async def test_validate_image_invalid_data(self):
        """잘못된 이미지 데이터 검증 실패 테스트"""
        with pytest.raises(ValueError, match="유효하지 않은 이미지 파일입니다"):
            await validate_image(b'not_an_image', 'fake.jpg')
    
    @pytest.mark.asyncio
    async def test_optimize_image_success(self, sample_image_data):
        """이미지 최적화 성공 테스트"""
        optimized = await optimize_image(sample_image_data)
        
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0
        # 최적화된 이미지가 원본보다 작거나 같아야 함
        assert len(optimized) <= len(sample_image_data)
    
    @pytest.mark.asyncio
    async def test_optimize_image_png_conversion(self):
        """PNG 이미지 최적화 테스트"""
        # RGBA PNG 이미지 생성
        img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 128))
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        png_data = buffer.getvalue()
        
        optimized = await optimize_image(png_data)
        
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0
    
    @pytest.mark.asyncio
    async def test_optimize_image_invalid_data(self):
        """잘못된 이미지 데이터 최적화 실패 테스트"""
        with pytest.raises(ValueError, match="이미지 처리 실패"):
            await optimize_image(b'invalid_image_data')
    
    @pytest.mark.asyncio
    async def test_get_image_info_success(self, sample_image_data):
        """이미지 정보 추출 성공 테스트"""
        info = await get_image_info(sample_image_data)
        
        assert isinstance(info, dict)
        assert "format" in info
        assert "mode" in info
        assert "size" in info
        assert "width" in info
        assert "height" in info
        assert "file_size" in info
        assert "has_transparency" in info
        
        assert info["format"] == "JPEG"
        assert info["mode"] == "RGB"
        assert info["size"] == (500, 500)
        assert info["width"] == 500
        assert info["height"] == 500
        assert info["file_size"] == len(sample_image_data)
        assert info["has_transparency"] == False
    
    @pytest.mark.asyncio
    async def test_get_image_info_invalid_data(self):
        """잘못된 이미지 데이터 정보 추출 테스트"""
        info = await get_image_info(b'invalid_data')
        
        # 잘못된 데이터의 경우 빈 딕셔너리 반환
        assert isinstance(info, dict)
        assert len(info) == 0
    
    def test_is_supported_image_type_valid(self):
        """지원되는 이미지 타입 검증 테스트"""
        assert is_supported_image_type("image/jpeg") == True
        assert is_supported_image_type("image/png") == True
        assert is_supported_image_type("IMAGE/JPEG") == True  # 대소문자 무시
    
    def test_is_supported_image_type_invalid(self):
        """지원되지 않는 이미지 타입 검증 테스트"""
        assert is_supported_image_type("text/plain") == False
        assert is_supported_image_type("application/pdf") == False
        assert is_supported_image_type("") == False
    
    def test_guess_content_type_valid(self):
        """유효한 파일 확장자 타입 추측 테스트"""
        assert guess_content_type("test.jpg") == "image/jpeg"
        assert guess_content_type("image.jpeg") == "image/jpeg"
        assert guess_content_type("photo.png") == "image/png"
        assert guess_content_type("TEST.JPG") == "image/jpeg"  # 대소문자 무시
    
    def test_guess_content_type_invalid(self):
        """유효하지 않은 파일 확장자 타입 추측 테스트"""
        assert guess_content_type("document.txt") == None
        assert guess_content_type("file.pdf") == None
        assert guess_content_type("") == None
        assert guess_content_type("no_extension") == None

@pytest.mark.asyncio
async def test_image_utils_integration():
    """이미지 유틸리티 통합 테스트"""
    # 실제 이미지 생성
    img = Image.new('RGB', (300, 300), color='green')
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    image_data = buffer.getvalue()
    
    # 1. 이미지 검증
    await validate_image(image_data, 'integration_test.jpg')
    
    # 2. 이미지 최적화
    optimized = await optimize_image(image_data)
    
    # 3. 이미지 정보 추출
    info = await get_image_info(optimized)
    
    # 검증
    assert len(optimized) > 0
    assert info["format"] == "JPEG"
    assert info["width"] == 300
    assert info["height"] == 300
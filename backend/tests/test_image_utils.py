import pytest
from unittest.mock import patch, mock_open
from PIL import Image
from io import BytesIO
import os
from utils.image_utils import (
    validate_image, 
    optimize_image, 
    get_image_info,
    is_supported_image_type,
    guess_content_type
)

class TestImageUtils:
    """이미지 유틸리티 테스트 클래스"""
    
    @pytest.fixture
    def sample_jpeg_data(self):
        """테스트용 JPEG 이미지 데이터"""
        # 작은 JPEG 이미지 생성
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        return buffer.getvalue()
    
    @pytest.fixture
    def sample_png_data(self):
        """테스트용 PNG 이미지 데이터"""
        # 작은 PNG 이미지 생성
        img = Image.new('RGB', (100, 100), color='blue')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    @pytest.fixture
    def large_image_data(self):
        """테스트용 큰 이미지 데이터"""
        # 큰 이미지 생성 (10MB 초과)
        return b"x" * (11 * 1024 * 1024)  # 11MB
    
    async def test_validate_image_success_jpeg(self, sample_jpeg_data):
        """JPEG 이미지 검증 성공 테스트"""
        # 정상적인 JPEG 이미지는 예외가 발생하지 않아야 함
        await validate_image(sample_jpeg_data, "test.jpg")
    
    async def test_validate_image_success_png(self, sample_png_data):
        """PNG 이미지 검증 성공 테스트"""
        # 정상적인 PNG 이미지는 예외가 발생하지 않아야 함
        await validate_image(sample_png_data, "test.png")
    
    async def test_validate_image_file_too_large(self, large_image_data):
        """파일 크기 초과 테스트"""
        with pytest.raises(ValueError, match="파일 크기가"):
            await validate_image(large_image_data, "large.jpg")
    
    async def test_validate_image_empty_file(self):
        """빈 파일 테스트"""
        with pytest.raises(ValueError, match="빈 파일입니다"):
            await validate_image(b"", "empty.jpg")
    
    async def test_validate_image_invalid_format(self):
        """잘못된 이미지 형식 테스트"""
        with pytest.raises(ValueError, match="유효하지 않은 이미지 파일"):
            await validate_image(b"not_an_image", "test.txt")
    
    async def test_validate_image_too_small(self):
        """이미지 크기가 너무 작은 경우 테스트"""
        # 50x50 이미지 생성 (최소 100x100 미만)
        img = Image.new('RGB', (50, 50), color='green')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        small_image = buffer.getvalue()
        
        with pytest.raises(ValueError, match="이미지 크기가 너무 작습니다"):
            await validate_image(small_image, "small.jpg")
    
    async def test_optimize_image_jpeg(self, sample_jpeg_data):
        """JPEG 이미지 최적화 테스트"""
        optimized = await optimize_image(sample_jpeg_data)
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0
    
    async def test_optimize_image_png(self, sample_png_data):
        """PNG 이미지 최적화 테스트"""
        optimized = await optimize_image(sample_png_data)
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0
    
    async def test_optimize_image_invalid(self):
        """잘못된 이미지 최적화 테스트"""
        with pytest.raises(ValueError, match="이미지 처리 실패"):
            await optimize_image(b"invalid_image_data")
    
    async def test_get_image_info_jpeg(self, sample_jpeg_data):
        """JPEG 이미지 정보 추출 테스트"""
        info = await get_image_info(sample_jpeg_data)
        assert info["format"] == "JPEG"
        assert info["size"] == (100, 100)
        assert info["width"] == 100
        assert info["height"] == 100
        assert info["file_size"] == len(sample_jpeg_data)
    
    async def test_get_image_info_png(self, sample_png_data):
        """PNG 이미지 정보 추출 테스트"""
        info = await get_image_info(sample_png_data)
        assert info["format"] == "PNG"
        assert info["size"] == (100, 100)
        assert info["width"] == 100
        assert info["height"] == 100
        assert info["file_size"] == len(sample_png_data)
    
    async def test_get_image_info_invalid(self):
        """잘못된 이미지 정보 추출 테스트"""
        info = await get_image_info(b"invalid_data")
        assert info == {}
    
    def test_is_supported_image_type(self):
        """지원되는 이미지 타입 확인 테스트"""
        assert is_supported_image_type("image/jpeg") == True
        assert is_supported_image_type("image/png") == True
        assert is_supported_image_type("image/jpg") == True
        assert is_supported_image_type("image/gif") == False
        assert is_supported_image_type("text/plain") == False
    
    def test_guess_content_type(self):
        """파일 확장자로 MIME 타입 추측 테스트"""
        assert guess_content_type("test.jpg") == "image/jpeg"
        assert guess_content_type("test.jpeg") == "image/jpeg"
        assert guess_content_type("test.png") == "image/png"
        assert guess_content_type("test.txt") == None
        assert guess_content_type("") == None
        assert guess_content_type(None) == None

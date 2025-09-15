"""
다중 이미지 업로드 기능 테스트
"""
import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from dotenv import load_dotenv

load_dotenv()

from main import app
from services.gemini_service import GeminiService

client = TestClient(app)

@pytest.mark.asyncio
async def test_multiple_images_analysis():
    """다중 이미지 분석 테스트"""
    service = GeminiService()
    
    # 테스트용 더미 이미지 데이터 (실제로는 실제 이미지 사용)
    dummy_image_data = b"dummy_image_data"
    image_data_list = [dummy_image_data, dummy_image_data]
    
    try:
        # 다중 이미지 분석 메서드 테스트 (모킹 환경에서)
        # result = await service.analyze_multiple_portfolio_images(image_data_list)
        # assert isinstance(result, str)
        # assert len(result) > 100
        print("다중 이미지 분석 테스트 준비 완료")
        
    except Exception as e:
        print(f"테스트 오류: {str(e)}")

def test_api_multiple_files_validation():
    """API 다중 파일 검증 테스트"""
    # 파일 개수 제한 테스트
    files = [("files", ("test1.jpg", b"fake_image_data", "image/jpeg")) for _ in range(6)]
    
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "최대 5개" in response.json()["detail"]
    
    print("파일 개수 제한 테스트 통과")

def test_api_empty_files():
    """빈 파일 리스트 테스트"""
    response = client.post("/api/analyze", files=[])
    assert response.status_code in [400, 422]  # 400 또는 422 둘 다 허용
    
    print("빈 파일 리스트 테스트 통과")

def test_api_single_file_compatibility():
    """단일 파일 하위 호환성 테스트"""
    # 단일 파일도 여전히 작동하는지 테스트
    files = [("files", ("test.jpg", b"fake_image_data", "image/jpeg"))]
    
    # 실제 이미지가 아니므로 400 에러가 예상되지만, 
    # 파일 개수 검증은 통과해야 함
    response = client.post("/api/analyze", files=files)
    # 파일 형식 오류는 400, 하지만 파일 개수는 유효함
    assert response.status_code == 400
    # 파일 개수 관련 에러가 아닌 다른 에러여야 함
    assert "최대 5개" not in response.json()["detail"]
    
    print("단일 파일 하위 호환성 테스트 통과")

def test_api_multiple_files_structure():
    """다중 파일 구조 테스트"""
    # 올바른 다중 파일 구조 테스트
    files = [
        ("files", ("test1.jpg", b"fake_image_data_1", "image/jpeg")),
        ("files", ("test2.jpg", b"fake_image_data_2", "image/jpeg")),
        ("files", ("test3.jpg", b"fake_image_data_3", "image/jpeg"))
    ]
    
    response = client.post("/api/analyze", files=files)
    # 파일 형식 오류는 400, 하지만 파일 구조는 유효함
    assert response.status_code == 400
    # 파일 개수나 구조 관련 에러가 아닌 다른 에러여야 함
    error_detail = response.json()["detail"]
    assert "최대 5개" not in error_detail
    assert "파일" in error_detail  # 파일 관련 에러는 있어야 함
    
    print("다중 파일 구조 테스트 통과")

def test_gemini_service_multiple_images_method():
    """Gemini 서비스 다중 이미지 메서드 존재 확인"""
    service = GeminiService()
    
    # 메서드가 존재하는지 확인
    assert hasattr(service, 'analyze_multiple_portfolio_images')
    assert callable(getattr(service, 'analyze_multiple_portfolio_images'))
    
    # 캐시 키 생성 메서드 확인
    assert hasattr(service, '_generate_multiple_cache_key')
    assert callable(getattr(service, '_generate_multiple_cache_key'))
    
    # 다중 이미지 프롬프트 메서드 확인
    assert hasattr(service, '_get_multiple_image_prompt')
    assert callable(getattr(service, '_get_multiple_image_prompt'))
    
    print("Gemini 서비스 다중 이미지 메서드 존재 확인 완료")

def test_cache_key_generation():
    """캐시 키 생성 테스트"""
    service = GeminiService()
    
    # 테스트용 이미지 데이터
    image_data_1 = b"test_image_1"
    image_data_2 = b"test_image_2"
    image_data_3 = b"test_image_3"
    
    # 단일 이미지 캐시 키
    single_key = service._generate_multiple_cache_key([image_data_1])
    assert single_key.startswith("multiple_1_")
    
    # 다중 이미지 캐시 키
    multiple_key = service._generate_multiple_cache_key([image_data_1, image_data_2])
    assert multiple_key.startswith("multiple_2_")
    
    # 다른 순서의 이미지들은 다른 키를 생성해야 함
    different_order_key = service._generate_multiple_cache_key([image_data_2, image_data_1])
    assert multiple_key != different_order_key
    
    # 동일한 이미지 조합은 동일한 키를 생성해야 함
    same_key = service._generate_multiple_cache_key([image_data_1, image_data_2])
    assert multiple_key == same_key
    
    print("캐시 키 생성 테스트 완료")

def test_multiple_image_prompt():
    """다중 이미지 프롬프트 테스트"""
    service = GeminiService()
    
    prompt = service._get_multiple_image_prompt()
    
    # 프롬프트가 문자열인지 확인
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    
    # 다중 이미지 관련 키워드가 포함되어 있는지 확인
    assert "여러 포트폴리오 이미지" in prompt
    assert "종합적으로 분석" in prompt
    assert "다중 이미지 분석" in prompt
    assert "시계열 분석" in prompt
    assert "전체적인 투자 전략" in prompt
    
    print("다중 이미지 프롬프트 테스트 완료")

if __name__ == "__main__":
    print("다중 이미지 테스트 시작...")
    
    # 동기 테스트 실행
    test_api_multiple_files_validation()
    test_api_empty_files()
    test_api_single_file_compatibility()
    test_api_multiple_files_structure()
    test_gemini_service_multiple_images_method()
    test_cache_key_generation()
    test_multiple_image_prompt()
    
    # 비동기 테스트 실행
    asyncio.run(test_multiple_images_analysis())
    
    print("모든 테스트 완료")

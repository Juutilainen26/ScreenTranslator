"""
번역 엔진(config.TRANSLATE_BACKEND) 연결 테스트용 진단 스크립트.
실행: python test_translate.py
"""
import config
from translate import translate_text


def main():
    print(f"백엔드: {config.TRANSLATE_BACKEND}")
    print("테스트 번역 요청 중...")
    try:
        result = translate_text("こんにちは、元気ですか?", source="ja", target="ko")
        print(f"번역 결과: {result}")
        print("\n✅ 정상 동작합니다.")
    except Exception as e:
        print(f"\n❌ 오류: {e}")


if __name__ == "__main__":
    main()

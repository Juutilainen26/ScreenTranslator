@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   ScreenTranslator 빌드를 시작합니다.
echo ============================================
echo.

if not exist venv\Scripts\activate.bat (
    echo [0/3] 가상환경이 없어서 새로 만듭니다...
    python -m venv venv
    echo.
)

echo [1/3] 가상환경을 활성화합니다...
call venv\Scripts\activate.bat

echo [2/3] 필요한 패키지를 설치합니다...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [3/3] 폴더 형태로 빌드합니다 (onedir)...
echo.

pyinstaller --onedir --windowed --name ScreenTranslator --collect-all keyboard app.py

echo.
if exist dist\ScreenTranslator\ScreenTranslator.exe (
    echo 빌드 완료! dist\ScreenTranslator 폴더 안의 ScreenTranslator.exe 를 실행하세요.
    echo ^(폴더째로 옮겨야 정상 동작합니다 — exe 파일만 따로 옮기면 안 돼요^)
) else (
    echo 빌드에 실패한 것 같아요. 위쪽 에러 메시지를 캡쳐해서 알려주시면 같이 고쳐볼게요.
)
pause

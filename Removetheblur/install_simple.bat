@echo off
echo Installing Python packages...
echo.

python -m pip install --upgrade pip
python -m pip install openai pillow python-dotenv numpy flask

echo.
echo Installation complete!
pause





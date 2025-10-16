@echo off
chcp 65001 >nul
cd /d "%~dp0"
git init
git remote add origin https://github.com/DaniilZebzeev/hse-ml-contrast-checker.git
git add .
git commit -m "feat: добавлен веб-интерфейс, batch analyzer и продвинутый scraper"
echo Git setup complete!
pause


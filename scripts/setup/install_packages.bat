@echo off
REM 安裝必要的Python包 - 使用清華鏡像

echo 🔧 安裝TradingAgents必要的Python包
echo =====================================

echo.
echo 🔄 升級pip (重要！避免安裝錯誤)...
python -m pip install --upgrade pip

echo.
echo 📦 使用清華大學鏡像安裝包...
echo 鏡像地址: https://pypi.tuna.tsinghua.edu.cn/simple/

echo.
echo 📥 安裝pymongo...
python -m pip install pymongo -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 📥 安裝redis...
python -m pip install redis -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 📥 安裝其他常用包...
python -m pip install pandas requests -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 📊 檢查已安裝的包...
python -m pip list | findstr -i "pymongo redis pandas"

echo.
echo ✅ 包安裝完成!
echo.
echo 💡 提示:
echo 1. 如果安裝失败，可以嘗試其他鏡像:
echo    - 豆瓣: -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com
echo    - 中科大: -i https://pypi.mirrors.ustc.edu.cn/simple/ --trusted-host pypi.mirrors.ustc.edu.cn
echo.
echo 2. 下一步運行:
echo    python scripts\setup\initialize_system.py
echo.

pause

#!/usr/bin/env python3
"""
Docker環境PDF導出適配器
處理Docker容器中的PDF生成特殊需求
"""

import os
import subprocess
import tempfile
from typing import Optional

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

def is_docker_environment() -> bool:
    """檢測是否在Docker環境中運行"""
    try:
        # 檢查/.dockerenv文件
        if os.path.exists('/.dockerenv'):
            return True
        
        # 檢查cgroup信息
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            if 'docker' in content or 'containerd' in content:
                return True
    except:
        pass
    
    # 檢查環境變量
    return os.environ.get('DOCKER_CONTAINER', '').lower() == 'true'

def setup_xvfb_display():
    """設置虛擬顯示器 (Docker環境需要)"""
    if not is_docker_environment():
        return True

    try:
        # 檢查Xvfb是否已經在運行
        try:
            result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True, timeout=2)
            if result.returncode == 0:
                logger.info(f"✅ Xvfb已在運行")
                os.environ['DISPLAY'] = ':99'
                return True
        except:
            pass

        # 啟動Xvfb虛擬顯示器 (後台運行)
        subprocess.Popen([
            'Xvfb', ':99', '-screen', '0', '1024x768x24', '-ac', '+extension', 'GLX'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 等待一下让Xvfb啟動
        import time
        time.sleep(2)

        # 設置DISPLAY環境變量
        os.environ['DISPLAY'] = ':99'
        logger.info(f"✅ Docker虛擬顯示器設置成功")
        return True
    except Exception as e:
        logger.error(f"⚠️ 虛擬顯示器設置失败: {e}")
        # 即使Xvfb失败，也嘗試繼续，某些情况下wkhtmltopdf可以無头運行
        return False

def get_docker_wkhtmltopdf_args():
    """獲取Docker環境下wkhtmltopdf的特殊參數"""
    if not is_docker_environment():
        return []

    # 這些是wkhtmltopdf的參數，不是pandoc的參數
    return [
        '--disable-smart-shrinking',
        '--print-media-type',
        '--no-background',
        '--disable-javascript',
        '--quiet'
    ]

def test_docker_pdf_generation() -> bool:
    """測試Docker環境下的PDF生成"""
    if not is_docker_environment():
        return True
    
    try:
        import pypandoc

        
        # 設置虛擬顯示器
        setup_xvfb_display()
        
        # 測試內容
        test_html = """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Docker PDF Test</title>
        </head>
        <body>
            <h1>Docker PDF 測試</h1>
            <p>這是在Docker環境中生成的PDF測試文档。</p>
            <p>中文字符測試：你好世界！</p>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_file = tmp.name
        
        # Docker環境下使用簡化的參數
        extra_args = [
            '--pdf-engine=wkhtmltopdf',
            '--pdf-engine-opt=--disable-smart-shrinking',
            '--pdf-engine-opt=--quiet'
        ]

        pypandoc.convert_text(
            test_html,
            'pdf',
            format='html',
            outputfile=output_file,
            extra_args=extra_args
        )
        
        # 檢查文件是否生成
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            os.unlink(output_file)  # 清理測試文件
            logger.info(f"✅ Docker PDF生成測試成功")
            return True
        else:
            logger.error(f"❌ Docker PDF生成測試失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ Docker PDF測試失败: {e}")
        return False

def get_docker_pdf_extra_args():
    """獲取Docker環境下PDF生成的額外參數"""
    base_args = [
        '--toc',
        '--number-sections',
        '-V', 'geometry:margin=2cm',
        '-V', 'documentclass=article'
    ]

    if is_docker_environment():
        # Docker環境下的特殊配置 - 使用正確的pandoc參數格式
        docker_args = []
        wkhtmltopdf_args = get_docker_wkhtmltopdf_args()

        # 将wkhtmltopdf參數正確傳遞給pandoc
        for arg in wkhtmltopdf_args:
            docker_args.extend(['--pdf-engine-opt=' + arg])

        return base_args + docker_args

    return base_args

def check_docker_pdf_dependencies():
    """檢查Docker環境下PDF生成的依賴"""
    if not is_docker_environment():
        return True, "非Docker環境"
    
    missing_deps = []
    
    # 檢查wkhtmltopdf
    try:
        result = subprocess.run(['wkhtmltopdf', '--version'], 
                              capture_output=True, timeout=10)
        if result.returncode != 0:
            missing_deps.append('wkhtmltopdf')
    except:
        missing_deps.append('wkhtmltopdf')
    
    # 檢查Xvfb
    try:
        result = subprocess.run(['Xvfb', '-help'], 
                              capture_output=True, timeout=10)
        if result.returncode not in [0, 1]:  # Xvfb -help 返回1是正常的
            missing_deps.append('xvfb')
    except:
        missing_deps.append('xvfb')
    
    # 檢查字體
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/liberation/'
    ]
    
    font_found = any(os.path.exists(path) for path in font_paths)
    if not font_found:
        missing_deps.append('chinese-fonts')
    
    if missing_deps:
        return False, f"缺少依賴: {', '.join(missing_deps)}"
    
    return True, "所有依賴已安裝"

def get_docker_status_info():
    """獲取Docker環境狀態信息"""
    info = {
        'is_docker': is_docker_environment(),
        'dependencies_ok': False,
        'dependency_message': '',
        'pdf_test_ok': False
    }
    
    if info['is_docker']:
        info['dependencies_ok'], info['dependency_message'] = check_docker_pdf_dependencies()
        if info['dependencies_ok']:
            info['pdf_test_ok'] = test_docker_pdf_generation()
    else:
        info['dependencies_ok'] = True
        info['dependency_message'] = '非Docker環境，使用標準配置'
        info['pdf_test_ok'] = True
    
    return info

if __name__ == "__main__":
    logger.info(f"🐳 Docker PDF適配器測試")
    logger.info(f"=")
    
    status = get_docker_status_info()
    
    logger.info(f"Docker環境: {'是' if status['is_docker'] else '否'}")
    logger.error(f"依賴檢查: {'✅' if status['dependencies_ok'] else '❌'} {status['dependency_message']}")
    logger.error(f"PDF測試: {'✅' if status['pdf_test_ok'] else '❌'}")
    
    if status['is_docker'] and status['dependencies_ok'] and status['pdf_test_ok']:
        logger.info(f"\n🎉 Docker PDF功能完全正常！")
    elif status['is_docker'] and not status['dependencies_ok']:
        logger.warning(f"\n⚠️ Docker環境缺少PDF依賴，請重新構建鏡像")
    elif status['is_docker'] and not status['pdf_test_ok']:
        logger.error(f"\n⚠️ Docker PDF測試失败，可能需要調整配置")
    else:
        logger.info(f"\n✅ 非Docker環境，使用標準PDF配置")

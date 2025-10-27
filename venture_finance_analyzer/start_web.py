"""
快速启动Web界面
"""
import os
import sys

def main():
    print("\n" + "="*60)
    print("💰 Venture Finance Analyzer - Web Interface")
    print("="*60)
    print("\n正在启动Web服务器...")
    print("\n访问地址: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 导入并运行Flask应用
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()


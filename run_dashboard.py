#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit 交易数据分析仪表盘启动脚本
提供更好的进程管理和信号处理
"""

import os
import subprocess
import signal
import sys
import time
import webbrowser

def main():
    print("启动 Streamlit 交易数据分析仪表盘...")
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    # 启动 Streamlit 进程
    streamlit_cmd = ["streamlit", "run", "ui/trading_dashboard.py"]
    process = subprocess.Popen(
        streamlit_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )
    
    # 处理终止信号
    def signal_handler(sig, frame):
        print("\n正在关闭 Streamlit 应用...")
        process.terminate()
        
        # 给进程一些时间来正常关闭
        try:
            process.wait(timeout=5)
            print("Streamlit 应用已关闭")
        except subprocess.TimeoutExpired:
            print("Streamlit 应用未能正常关闭，强制终止...")
            process.kill()
        
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 终止信号
    
    # 监控输出以获取URL
    url_found = False
    print("等待 Streamlit 启动...")
    
    try:
        # 读取输出直到找到URL或超时
        start_time = time.time()
        while not url_found and (time.time() - start_time) < 30:  # 30秒超时
            if process.poll() is not None:
                # 进程已结束
                print("Streamlit 进程意外终止")
                break
                
            output = process.stdout.readline().strip()
            if output:
                print(output)
                
                # 检查输出中是否包含URL
                if "External URL:" in output:
                    url = output.split("External URL:")[1].strip()
                    print(f"\n交易数据分析仪表盘已启动！")
                    print(f"访问地址: {url}")
                    
                    # 自动打开浏览器
                    try:
                        webbrowser.open(url)
                        print("已在浏览器中打开仪表盘")
                    except:
                        print("无法自动打开浏览器，请手动访问上述地址")
                    
                    url_found = True
                elif "Network URL:" in output and not url_found:
                    url = output.split("Network URL:")[1].strip()
                    print(f"\n交易数据分析仪表盘已启动！")
                    print(f"访问地址: {url}")
                    
                    # 自动打开浏览器
                    try:
                        webbrowser.open(url)
                        print("已在浏览器中打开仪表盘")
                    except:
                        print("无法自动打开浏览器，请手动访问上述地址")
                    
                    url_found = True
        
        if not url_found:
            print("Streamlit 可能已启动，但未能检测到URL")
            print("请尝试访问: http://localhost:8501")
        
        print("\n按 Ctrl+C 可以关闭应用")
        
        # 等待进程结束
        while True:
            if process.poll() is not None:
                print("Streamlit 进程已结束")
                break
            
            # 继续输出日志
            output = process.stdout.readline().strip()
            if output:
                print(output)
            
            # 减少CPU使用率
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        # 捕获 Ctrl+C
        signal_handler(signal.SIGINT, None)
    
    except Exception as e:
        print(f"发生错误: {e}")
        signal_handler(signal.SIGTERM, None)

if __name__ == "__main__":
    main()
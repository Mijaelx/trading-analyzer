@echo off
chcp 65001 >nul
echo 🚀 交易数据分析系统 - Cloudflare 部署脚本
echo ================================================
echo.

:: 检查Node.js是否安装
echo 📋 检查部署要求...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装
    echo 请访问 https://nodejs.org/ 下载并安装 Node.js LTS 版本
    echo 安装完成后重新运行此脚本
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

:: 检查npm是否可用
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm 不可用
    pause
    exit /b 1
)
echo ✅ npm 已安装

:: 安装Wrangler CLI
echo.
echo 📦 安装 Wrangler CLI...
wrangler --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Wrangler CLI...
    npm install -g wrangler
    if %errorlevel% neq 0 (
        echo ❌ Wrangler CLI 安装失败
        pause
        exit /b 1
    )
    echo ✅ Wrangler CLI 安装完成
) else (
    echo ✅ Wrangler CLI 已安装
)

:: 检查是否已登录
echo.
echo 🔐 检查 Cloudflare 登录状态...
wrangler whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 需要登录 Cloudflare 账号...
    echo 浏览器将打开，请完成登录授权
    pause
    wrangler login
    if %errorlevel% neq 0 (
        echo ❌ Cloudflare 登录失败
        pause
        exit /b 1
    )
) else (
    echo ✅ 已登录 Cloudflare
)

:: 创建KV命名空间
echo.
echo 🗄️ 创建 KV 存储命名空间...
echo 正在创建生产环境 KV 命名空间...
wrangler kv:namespace create "TRADING_DATA" > kv_prod.txt 2>&1
if %errorlevel% neq 0 (
    echo ❌ 生产环境 KV 创建失败
    type kv_prod.txt
    pause
    exit /b 1
)

echo 正在创建预览环境 KV 命名空间...
wrangler kv:namespace create "TRADING_DATA" --preview > kv_preview.txt 2>&1
if %errorlevel% neq 0 (
    echo ❌ 预览环境 KV 创建失败
    type kv_preview.txt
    pause
    exit /b 1
)

echo ✅ KV 命名空间创建完成
echo.
echo 📝 请手动更新 wrangler.toml 文件中的 KV 命名空间 ID：
echo.
echo 生产环境 KV 信息：
type kv_prod.txt | findstr "id ="
echo.
echo 预览环境 KV 信息：
type kv_preview.txt | findstr "id ="
echo.
echo 请将这些 ID 复制到 wrangler.toml 文件中对应的位置
echo 完成后按任意键继续部署...
pause

:: 部署到Cloudflare Workers
echo.
echo 🚀 部署到 Cloudflare Workers...
wrangler deploy
if %errorlevel% neq 0 (
    echo ❌ 部署失败
    pause
    exit /b 1
)

echo.
echo 🎉 部署完成！
echo.
echo 📱 你的应用已部署到 Cloudflare Workers
echo 🔗 访问地址将在上面的输出中显示
echo.
echo 📋 后续步骤：
echo 1. 访问部署地址测试功能
echo 2. 如需自定义域名，请在 Cloudflare Dashboard 中配置
echo 3. 查看实时日志：wrangler tail
echo.
echo 🎊 享受你的云端交易分析系统吧！

:: 清理临时文件
del kv_prod.txt kv_preview.txt 2>nul

pause
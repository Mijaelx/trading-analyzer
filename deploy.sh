#!/bin/bash

# 交易数据分析系统部署脚本

echo "🚀 开始部署交易数据分析系统..."

# 检查是否安装了必要工具
check_requirements() {
    echo "📋 检查部署要求..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm 未安装，请先安装 npm"
        exit 1
    fi
    
    echo "✅ 基础要求检查通过"
}

# 安装Wrangler CLI
install_wrangler() {
    echo "📦 安装 Wrangler CLI..."
    
    if ! command -v wrangler &> /dev/null; then
        npm install -g wrangler
        echo "✅ Wrangler CLI 安装完成"
    else
        echo "✅ Wrangler CLI 已安装"
    fi
}

# 登录Cloudflare
login_cloudflare() {
    echo "🔐 登录 Cloudflare..."
    
    if ! wrangler whoami &> /dev/null; then
        echo "请在浏览器中完成 Cloudflare 登录..."
        wrangler login
    else
        echo "✅ 已登录 Cloudflare"
    fi
}

# 创建KV命名空间
create_kv_namespace() {
    echo "🗄️ 创建 KV 命名空间..."
    
    # 创建生产环境KV
    echo "创建生产环境 KV 命名空间..."
    PROD_KV_ID=$(wrangler kv:namespace create "TRADING_DATA" --env production | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    
    # 创建预览环境KV
    echo "创建预览环境 KV 命名空间..."
    PREVIEW_KV_ID=$(wrangler kv:namespace create "TRADING_DATA" --preview --env production | grep -o 'id = "[^"]*"' | cut -d'"' -f2)
    
    # 更新wrangler.toml配置
    if [ ! -z "$PROD_KV_ID" ] && [ ! -z "$PREVIEW_KV_ID" ]; then
        sed -i "s/your-kv-namespace-id/$PROD_KV_ID/g" wrangler.toml
        sed -i "s/your-preview-kv-namespace-id/$PREVIEW_KV_ID/g" wrangler.toml
        echo "✅ KV 命名空间创建完成"
        echo "   生产环境 ID: $PROD_KV_ID"
        echo "   预览环境 ID: $PREVIEW_KV_ID"
    else
        echo "❌ KV 命名空间创建失败"
        exit 1
    fi
}

# 部署到Cloudflare Workers
deploy_workers() {
    echo "🚀 部署到 Cloudflare Workers..."
    
    # 部署到生产环境
    if wrangler deploy --env production; then
        echo "✅ 部署成功！"
        
        # 获取部署URL
        WORKER_URL=$(wrangler subdomain get 2>/dev/null | grep -o 'https://[^[:space:]]*' || echo "https://trading-analyzer.your-subdomain.workers.dev")
        
        echo ""
        echo "🎉 部署完成！"
        echo "📱 访问地址: $WORKER_URL"
        echo ""
        echo "📋 后续步骤:"
        echo "1. 访问上述地址测试功能"
        echo "2. 如需自定义域名，请在 Cloudflare Dashboard 中配置"
        echo "3. 查看日志: wrangler tail --env production"
        echo ""
    else
        echo "❌ 部署失败"
        exit 1
    fi
}

# 主函数
main() {
    echo "交易数据分析系统 - Cloudflare Workers 部署脚本"
    echo "=================================================="
    echo ""
    
    check_requirements
    install_wrangler
    login_cloudflare
    create_kv_namespace
    deploy_workers
    
    echo "🎊 所有步骤完成！享受你的云端交易分析系统吧！"
}

# 运行主函数
main "$@"
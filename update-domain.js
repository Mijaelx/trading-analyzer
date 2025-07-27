#!/usr/bin/env node
/**
 * 域名更新脚本
 * 用于快速更新代码中的API域名
 */

const fs = require('fs');
const path = require('path');

// 获取命令行参数
const args = process.argv.slice(2);
if (args.length === 0) {
    console.log('使用方法: node update-domain.js <your-domain.com>');
    console.log('例如: node update-domain.js api.example.com');
    process.exit(1);
}

const newDomain = args[0];
const apiUrl = `https://${newDomain}`;

console.log(`🔄 更新API域名为: ${apiUrl}`);

// 更新 public/app.js
const appJsPath = path.join(__dirname, 'public', 'app.js');
if (fs.existsSync(appJsPath)) {
    let content = fs.readFileSync(appJsPath, 'utf8');
    
    // 替换API_BASE_URL
    content = content.replace(
        /const API_BASE_URL = ['"][^'"]*['"];/,
        `const API_BASE_URL = '${apiUrl}';`
    );
    
    fs.writeFileSync(appJsPath, content);
    console.log('✅ 已更新 public/app.js');
} else {
    console.log('❌ 未找到 public/app.js');
}

// 更新 _redirects 文件
const redirectsPath = path.join(__dirname, '_redirects');
if (fs.existsSync(redirectsPath)) {
    const redirectContent = `/api/* ${apiUrl}/api/:splat 200`;
    fs.writeFileSync(redirectsPath, redirectContent);
    console.log('✅ 已更新 _redirects');
}

// 更新 Functions 中的 Workers URL
const functionsDir = path.join(__dirname, 'functions', 'api');
if (fs.existsSync(functionsDir)) {
    const files = fs.readdirSync(functionsDir);
    
    files.forEach(file => {
        if (file.endsWith('.js')) {
            const filePath = path.join(functionsDir, file);
            let content = fs.readFileSync(filePath, 'utf8');
            
            // 替换 Workers URL
            content = content.replace(
                /https:\/\/trading-analyzer\.qfz4kq6xmr\.workers\.dev/g,
                apiUrl
            );
            
            fs.writeFileSync(filePath, content);
            console.log(`✅ 已更新 functions/api/${file}`);
        }
    });
}

console.log('');
console.log('🎉 域名更新完成！');
console.log('');
console.log('📋 下一步：');
console.log('1. 在Cloudflare中配置自定义域名');
console.log('2. 运行: wrangler pages deploy public');
console.log('3. 测试新域名是否正常工作');
console.log('');
console.log(`🌐 新的API地址: ${apiUrl}`);
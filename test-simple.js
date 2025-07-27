// 简单测试脚本
export default {
  async fetch(request, env, ctx) {
    return new Response('Hello World! 交易分析系统正在运行！', {
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
};
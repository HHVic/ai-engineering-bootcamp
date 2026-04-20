#!/bin/bash
# 启动脚本

set -e

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 未找到 .env 文件"
    echo "请先运行：cp .env.example .env"
    echo "然后编辑 .env 文件，填入 API 密钥"
    exit 1
fi

# 安装依赖
if [ ! -d .venv ]; then
    echo "📦 创建虚拟环境并安装依赖..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q -e .
else
    source .venv/bin/activate
fi

# 运行应用
echo ""
python run.py

#!/bin/bash
# 港股新股发行信息获取系统启动脚本

cd "$(dirname "$0")/.."

echo "=========================================="
echo "港股新股发行信息获取系统"
echo "=========================================="

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行: uv venv"
    exit 1
fi

# 检查 deploy/hk_main.py 是否存在
if [ ! -f "deploy/hk_main.py" ]; then
    echo "错误: deploy/hk_main.py 不存在"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 进入 deploy 目录
cd deploy

# 激活虚拟环境并运行应用
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash)
    echo "启动港股新股系统..."
    ../.venv/Scripts/python.exe hk_main.py "$@"
else
    # Linux/Mac
    echo "启动港股新股系统..."
    source ../.venv/bin/activate
    python hk_main.py "$@"
fi

#!/bin/bash

pkill -f "main.py"
sleep 1
echo "AcSYS LLMs REST API Starting..."
echo "====================="
echo ""

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed."
    echo "Please install Ollama from: https://ollama.ai"
    exit 1
fi

if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Ollama is not running."
    echo "Please start Ollama first."
    echo ""
    exit 1
fi

echo "Ollama is running"
echo ""

echo "Activating virtual environment..."
source .venv/bin/activate

nohup python main.py &
echo "Server started in the background."

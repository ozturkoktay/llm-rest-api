#!/bin/bash

echo "LLM API Quick Start"
echo "====================="
echo ""

if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed."
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    echo "After installation, run:"
    echo "  ollama pull llama2"
    echo ""
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

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -q -e .

echo ""
echo "Setup complete!"
echo ""
echo "   Starting LLM API server..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

python main.py

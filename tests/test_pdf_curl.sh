#!/bin/bash

# Simple script to test PDF question answering feature
# Usage: ./test_pdf_curl.sh <path-to-pdf> "<your-question>"

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pdf-file> \"<question>\""
    echo "Example: $0 document.pdf \"What is this document about?\""
    exit 1
fi

PDF_FILE="$1"
QUESTION="$2"
API_URL="http://0.0.0.0:8001/llm-api/v1/document/question"

if [ ! -f "$PDF_FILE" ]; then
    echo "Error: File '$PDF_FILE' not found!"
    exit 1
fi

echo "📄 PDF: $PDF_FILE"
echo "❓ Question: $QUESTION"
echo ""
echo "Sending request to API..."
echo ""

curl -X POST "$API_URL" \
  -F "file=@$PDF_FILE" \
  -F "question=$QUESTION" \
  -F "temperature=0.3" \
  -F "max_tokens=1024" \
  -F "context_mode=full" \
  | jq '.'

echo ""
echo "✅ Done!"

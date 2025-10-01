"""Test client for PDF document question answering feature.

This script demonstrates how to upload a PDF and ask questions about it.
"""

from fastapi import status
import httpx

# API Configuration
API_BASE_URL = "http://localhost:8000"


async def ask_pdf_question(
  pdf_path: str,
  question: str,
  model: str | None = None,
  max_tokens: int = 1024,
  temperature: float = 0.7,
  context_mode: str = "full",
):
  """Ask a question about a PDF document.

  Args:
      pdf_path: Path to the PDF file
      question: The question to ask about the document
      model: Optional model name to use
      max_tokens: Maximum tokens to generate
      temperature: Sampling temperature
      context_mode: Context mode ('full' or 'summary')

  Returns:
      Dictionary with the response
  """
  url = f"{API_BASE_URL}/document/question"

  # Prepare the multipart form data
  with open(pdf_path, "rb") as f:
    files = {"file": (pdf_path.split("/")[-1], f, "application/pdf")}

    data = {
      "question": question,
      "max_tokens": max_tokens,
      "temperature": temperature,
      "context_mode": context_mode,
    }

    if model:
      data["model"] = model

    async with httpx.AsyncClient(timeout=120.0) as client:
      response = await client.post(url, files=files, data=data)

  if response.status_code == status.HTTP_200_OK:
    return response.json()
  print(f"Error: {response.status_code}")
  print(response.text)
  return None


async def main():
  """Run example PDF question answering."""
  print("PDF Document Question Answering Test")
  print("=" * 50)

  # Example 1: Ask a question about a PDF
  pdf_path = "example.pdf"  # Replace with your PDF path
  question = "What is the main topic of this document?"

  print(f"\n📄 PDF: {pdf_path}")
  print(f"❓ Question: {question}")
  print("\nProcessing...")

  result = await ask_pdf_question(
    pdf_path=pdf_path, question=question, temperature=0.3, context_mode="full"
  )

  if result:
    print("\n✅ Answer received:")
    print("-" * 50)
    print(result["generated_text"])
    print("-" * 50)
    print(f"\nModel used: {result['model_used']}")
    print(f"Tokens generated: {result['tokens_generated']}")
    print(f"Generation time: {result['generation_time_ms']:.2f}ms")
  else:
    print("\n❌ Failed to get answer")

  # Example 2: Ask multiple questions about the same PDF
  print("\n" + "=" * 50)
  print("Multiple Questions Example")
  print("=" * 50)

  questions = [
    "Summarize the key points in 3 bullet points.",
    "What are the main conclusions?",
    "Are there any recommendations mentioned?",
  ]

  for i, q in enumerate(questions, 1):
    print(f"\nQuestion {i}: {q}")
    result = await ask_pdf_question(pdf_path=pdf_path, question=q, temperature=0.5)

    if result:
      print(f"Answer: {result['generated_text'][:200]}...")
    else:
      print("Failed to get answer")


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())

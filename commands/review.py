from pathlib import Path

from openai import OpenAI

from loaders.pdf_loader import load_pdf


client = OpenAI()


def run():
    print("\n=== JasonAI Board Paper Review ===\n")

    filename = input("Enter the PDF filename or full path: ").strip()

    if not filename:
        print("No filename entered.")
        return

    file_path = Path(filename).expanduser()

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    if file_path.suffix.lower() != ".pdf":
        print("This version currently supports PDF files only.")
        return

    try:
        document_text = load_pdf(file_path)
    except Exception as exc:
        print(f"Could not read the PDF: {exc}")
        return

    if not document_text.strip():
        print("No readable text was found in the PDF.")
        return

    print(f"\nLoaded: {file_path.name}")
    print(f"Characters extracted: {len(document_text):,}")
    print("Analysing the board paper...\n")

    prompt = f"""
You are an experienced board adviser reviewing a board paper.

Use only the evidence contained in the document below.
Do not invent facts, figures, risks, or recommendations.
Where evidence is missing, state that clearly.

Produce the review using these headings:

1. Decision Required
2. Executive Summary
3. Strategic Alignment
4. Financial Case
5. Principal Risks
6. Assumptions Requiring Challenge
7. Missing Evidence
8. Questions the Board Should Ask
9. Recommendation
10. Confidence and Limitations

DOCUMENT:
{document_text}
"""

    try:
        response = client.responses.create(
            model="gpt-5",
            input=prompt,
        )
    except Exception as exc:
        print(f"OpenAI request failed: {exc}")
        return

    print(response.output_text)
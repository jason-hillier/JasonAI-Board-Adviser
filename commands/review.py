from openai import OpenAI

client = OpenAI()


def run():
    print("\n=== JasonAI Board Paper Review ===\n")

    filename = input("Enter the document name to review: ")

    print(f"\nReviewing: {filename}")

    prompt = f"""
You are an experienced FTSE Board Advisor.

Review the document called '{filename}'.

Produce:

1. Executive Summary
2. Strategic Assessment
3. Financial Risks
4. Operational Risks
5. Governance Risks
6. Questions the Board Should Ask
7. Recommendation

Write professionally.
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    print("\n")
    print(response.output_text)
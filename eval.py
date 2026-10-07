"""
eval.py
-------
A small evaluation script to test the RAG system's retrieval + gating
behavior across three categories:
1. In-scope questions   — should be answered correctly
2. Near-topic questions — real ML terms, but not in this PDF; should be
                           gated OR correctly say "I don't know"
3. Off-topic questions  — completely unrelated; should always be gated
"""

from generator import generate_answer

# (question, category) — category is just for reporting/grouping
TEST_QUESTIONS = [
    # In-scope — should get a real, correct answer
    ("What is the difference between bagging and boosting?", "in-scope"),
    ("What is the bias-variance tradeoff?", "in-scope"),
    ("What is RAG (Retrieval-Augmented Generation)?", "in-scope"),
    ("What is regularization, and how do L1 and L2 differ?", "in-scope"),
    ("What is overfitting and how do you prevent it?", "in-scope"),

    # Near-topic — real ML terms NOT covered in this PDF
    ("What is a Support Vector Machine?", "near-topic"),
    ("What is a Gaussian Mixture Model?", "near-topic"),
    ("What is the Elbow Method for choosing K?", "near-topic"),

    # Off-topic — completely unrelated
    ("What is the capital of France?", "off-topic"),
    ("What's a good recipe for pasta?", "off-topic"),
]

MAX_DISTANCE = 0.8  # matches the threshold merged in PR #1


def run_eval():
    results = []

    for question, category in TEST_QUESTIONS:
        result = generate_answer(question, max_distance=MAX_DISTANCE)

        gated = result.get("gated", False)
        answer = result["answer"]

        results.append({
            "question": question,
            "category": category,
            "gated": gated,
            "answer": answer[:100],  # trimmed for display
        })

    return results


def print_report(results):
    print("\n" + "=" * 70)
    print("EVAL REPORT")
    print("=" * 70)

    for category in ["in-scope", "near-topic", "off-topic"]:
        print(f"\n--- {category.upper()} ---")
        for r in results:
            if r["category"] != category:
                continue
            status = "GATED" if r["gated"] else "ANSWERED"
            print(f"[{status}] {r['question']}")
            print(f"          -> {r['answer']}")

    # Simple summary
    in_scope_answered = sum(1 for r in results if r["category"] == "in-scope" and not r["gated"])
    off_topic_gated = sum(1 for r in results if r["category"] == "off-topic" and r["gated"])

    print("\n" + "=" * 70)
    print(f"In-scope correctly answered: {in_scope_answered}/5")
    print(f"Off-topic correctly gated:   {off_topic_gated}/2")
    print("=" * 70)


if __name__ == "__main__":
    results = run_eval()
    print_report(results)
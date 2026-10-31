import csv
from collections import defaultdict
from pathlib import Path

from detector import predict_category

DATASET_PATH = Path(__file__).parent / "sample_data.csv"


def evaluate():

    total = 0
    correct = 0

    category_results = defaultdict(
        lambda: {"correct": 0, "total": 0}
    )

    labels = set()
    confusion_matrix = defaultdict(int)

    with open(DATASET_PATH, "r", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:

            message = row["message"]
            expected = row["expected_category"]

            predicted = predict_category(message)

            total += 1
            labels.add(expected)
            labels.add(predicted)

            category_results[expected]["total"] += 1

            if expected == predicted:
                correct += 1
                category_results[expected]["correct"] += 1

            confusion_matrix[(expected, predicted)] += 1

            print(f"\nMessage: {message}")
            print(f"Expected: {expected}")
            print(f"Predicted: {predicted}")
            print(
                "Result:",
                "PASS" if expected == predicted else "FAIL"
            )

    accuracy = (correct / total * 100) if total else 0

    print("\n========== EVALUATION REPORT ==========")
    print(f"Total messages: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Incorrect predictions: {total - correct}")
    print(f"Classification accuracy: {accuracy:.2f}%")

    print("\n========== CATEGORY PERFORMANCE ==========")

    for category, result in sorted(category_results.items()):

        count = result["total"]
        category_accuracy = (
            result["correct"] / count * 100
            if count else 0
        )

        print(f"\nCategory: {category}")
        print(f"Correct: {result['correct']}/{count}")
        print(f"Accuracy: {category_accuracy:.2f}%")

    print("\n========== CONFUSION MATRIX ==========")

    labels = sorted(labels)

    print("Expected \\ Predicted")

    print("Expected".ljust(35), end="")

    for label in labels:
        print(label[:15].ljust(18), end="")

    print()

    for expected in labels:

        print(expected[:34].ljust(35), end="")

        for predicted in labels:
            value = confusion_matrix[(expected, predicted)]
            print(str(value).ljust(18), end="")

        print()


if __name__ == "__main__":
    evaluate()

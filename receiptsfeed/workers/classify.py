from ..nlp.clickbait_model import score_clickbait

def main():
    demo_titles = [
        "10 reasons you won't believe #3",
        "Quarterly earnings call summary",
    ]
    for t in demo_titles:
        print(f"[classify] '{t}' -> clickbait_score={score_clickbait(t):.3f}")

if __name__ == "__main__":
    main()

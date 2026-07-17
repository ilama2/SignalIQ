from app.agents.news import NewsAgent


def main() -> None:
    agent = NewsAgent()

    report = agent.run("2222")

    print("\nCompany")
    print(report.company_name)

    print("\nArticle count")
    print(report.article_count)

    print("\nScore")
    print(report.score.score)

    print("\nRating")
    print(report.score.rating)

    print("\nAverage sentiment")
    print(report.score.average_sentiment)

    print("\nSummary")
    print(report.summary.summary)

    print("\nOpportunities")
    for opportunity in report.summary.opportunities:
        print(f"- {opportunity}")

    print("\nRisks")
    for risk in report.summary.risks:
        print(f"- {risk}")


if __name__ == "__main__":
    main()
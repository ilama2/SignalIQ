from app.clients.news_client import NewsClient


def main() -> None:
    client = NewsClient()

    results = client.search_news(
        query="Saudi Aramco",
    )

    print(type(results))
    print(results)


if __name__ == "__main__":
    main()
    
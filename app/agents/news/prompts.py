"""
SignalIQ - News Agent Prompts

Centralized prompts used by the News Agent.
"""

from __future__ import annotations


def news_summary_prompt(
    symbol: str,
    company_name: str,
    articles: str,
) -> str:
    """
    Prompt used by NewsSummarizer to generate an
    investment-focused summary.
    """

    return f"""
You are a senior equity research analyst specializing in the Saudi stock market.

Your task is to analyze recent news about:

Company:
{company_name}

Saudi Exchange Symbol:
{symbol}

The provided articles have already been filtered for relevance.
Some articles also include sentiment predictions from an AI model.
Treat those predictions only as supporting evidence—not as facts.

Your objectives:

1. Summarize the most important recent developments.
2. Identify company-specific events.
3. Ignore duplicated information.
4. Ignore general market news unless it directly affects the company.
5. Focus on information that could influence:
   - Revenue
   - Earnings
   - Margins
   - Cash flow
   - Debt
   - Dividends
   - Regulations
   - Expansion
   - Contracts
   - Acquisitions
   - Investor confidence
6. List investment opportunities.
7. List investment risks.
8. Estimate the likely stock impact.

Return ONLY valid JSON.

JSON schema:

{{
    "summary": "Short investment-focused summary.",

    "key_events": [
        "Event 1",
        "Event 2"
    ],

    "opportunities": [
        "Opportunity 1"
    ],

    "risks": [
        "Risk 1"
    ],

    "expected_impact": "Positive"
}}

Rules:

- No markdown.
- No explanations.
- No code fences.
- No comments.
- Do not invent facts.
- Use only information contained in the articles.

expected_impact MUST be one of:

Strong Positive
Positive
Neutral
Negative
Strong Negative
Unknown

Articles:

{articles}
""".strip()


def article_relevance_prompt(
    company_name: str,
    article_title: str,
    article_text: str,
) -> str:
    """
    Optional prompt for future relevance filtering.
    """

    return f"""
Determine whether this article is primarily about:

{company_name}

Title:
{article_title}

Article:
{article_text}

Return only JSON.

{{
    "relevant": true,
    "confidence": 0.93,
    "reason": "The article discusses the company's earnings."
}}
""".strip()


def article_impact_prompt(
    company_name: str,
    article_title: str,
    article_text: str,
) -> str:
    """
    Optional prompt for estimating business impact.
    """

    return f"""
You are an equity analyst.

Estimate how important this news is for:

{company_name}

Title:
{article_title}

Article:
{article_text}

Return JSON only.

{{
    "impact_score": 0.82,
    "impact": "High",
    "reason": "Large government contract."
}}

impact_score ranges from:

-1.0 = extremely negative

0.0 = neutral

1.0 = extremely positive
""".strip()
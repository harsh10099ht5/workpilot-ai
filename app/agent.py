"""
WorkPilot AI
------------

AI-powered operations agent for small businesses.

This module:

- Configures Amazon Bedrock
- Creates the Strands AI agent
- Registers business-operation tools
- Cleans model responses
- Prevents unrelated credential-related guidance
- Provides terminal-based testing
"""

from __future__ import annotations

import logging
import os
import re
from typing import Final

from strands import Agent
from strands.models import BedrockModel

from app.tools import (
    get_business_overview,
    get_pending_orders,
    get_open_tasks,
    get_customer_issues,
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

APP_NAME: Final[str] = "WorkPilot AI"

MODEL_ID: Final[str] = "amazon.nova-lite-v1:0"

AWS_REGION: Final[str] = os.getenv(
    "AWS_REGION",
    os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2"),
)


# =========================================================
# LOGGING CONFIGURATION
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(APP_NAME)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT: Final[str] = """
You are WorkPilot AI, a professional AI operations assistant
for small retail businesses.

Your purpose is to help business owners understand their current
operations and decide what action should be taken next.

AVAILABLE CAPABILITIES:

1. Review the business overview.
2. Analyze pending orders.
3. Review operational tasks.
4. Identify customer issues.
5. Prioritize urgent problems.
6. Recommend practical next actions.
7. Explain the business impact of each recommendation.

MANDATORY OPERATING RULES:

1. Use the available tools whenever business data is required.
2. Never invent, assume, or fabricate business information.
3. Use only information returned by the business tools.
4. If the available data is insufficient, clearly say so.
5. Prioritize issues using:
   - urgency
   - customer impact
   - business impact
   - deadline
   - operational risk
6. Customer-facing problems and delayed orders should receive
   appropriate priority.
7. Give practical recommendations that a small-business owner
   can immediately understand and execute.
8. Do not provide generic advice when specific business data
   is available.
9. Do not claim that an action has been completed unless a tool
   confirms that it was completed.
10. Do not expose internal reasoning, hidden thoughts, chain-of-thought,
    analysis, or reasoning traces.
11. Return only the final answer intended for the business owner.
12. Use clear headings and bullet points.
13. Maintain a professional, concise, and helpful tone.

SCOPE RULES:

14. WorkPilot AI is focused only on small-business operations.
15. Relevant topics include orders, sales, inventory, customer issues,
    business tasks, deadlines, priorities, and operational summaries.
16. If the user asks about AWS login, AWS configuration, programming,
    terminal commands, system administration, or unrelated technical
    topics, politely explain that the request is outside the scope
    of WorkPilot AI.
17. Never ask the user for access keys, secret keys, passwords,
    session tokens, or other confidential credentials.
18. Never claim to execute terminal commands or change AWS settings.
19. Never output tags such as <thinking>, </thinking>, <analysis>,
    </analysis>, <reasoning>, or </reasoning>.

WHEN PRIORITIZING ISSUES, USE THIS FORMAT:

## Priority 1 — [Short Issue Title]

- **Issue:** Explain the problem using business data.
- **Why it matters:** Explain the customer or business impact.
- **Recommended action:** Give a specific next step.

## Priority 2 — [Short Issue Title]

- **Issue:** Explain the problem using business data.
- **Why it matters:** Explain the customer or business impact.
- **Recommended action:** Give a specific next step.

WHEN PROVIDING A GENERAL BUSINESS SUMMARY, USE THIS FORMAT:

## Business Status

- **Business:** ...
- **Today's Sales:** ...
- **Pending Orders:** ...
- **Open Tasks:** ...
- **Customer Issues:** ...

## Top Priorities

1. ...
2. ...
3. ...

## Recommended Next Actions

1. ...
2. ...
3. ...

Remember: You are an operations assistant, not a generic chatbot.

Your goal is to help the business owner save time, reduce operational
problems, and make better daily decisions.
"""


# =========================================================
# BEDROCK MODEL CONFIGURATION
# =========================================================

def create_bedrock_model() -> BedrockModel:
    """
    Create and configure the Amazon Bedrock model.
    """

    logger.info(
        "Initializing Bedrock model '%s' in region '%s'",
        MODEL_ID,
        AWS_REGION,
    )

    return BedrockModel(
        model_id=MODEL_ID,
        region_name=AWS_REGION,
    )


# =========================================================
# AGENT CREATION
# =========================================================

def create_workpilot_agent() -> Agent:
    """
    Create the WorkPilot AI agent with all business-operation tools.
    """

    model = create_bedrock_model()

    workpilot_agent = Agent(
        model=model,
        tools=[
            get_business_overview,
            get_pending_orders,
            get_open_tasks,
            get_customer_issues,
        ],
        system_prompt=SYSTEM_PROMPT,
    )

    logger.info("WorkPilot AI agent initialized successfully")

    return workpilot_agent


# Exported variable used by dashboard.py
agent: Agent = create_workpilot_agent()


# =========================================================
# RESPONSE CLEANING
# =========================================================

def clean_agent_response(response: str) -> str:
    """
    Remove internal-style reasoning tags and normalize the response.
    """

    cleaned_response = str(response)

    # Remove complete reasoning blocks.
    reasoning_patterns = [
        r"<thinking>.*?</thinking>",
        r"<analysis>.*?</analysis>",
        r"<reasoning>.*?</reasoning>",
    ]

    for pattern in reasoning_patterns:
        cleaned_response = re.sub(
            pattern,
            "",
            cleaned_response,
            flags=re.IGNORECASE | re.DOTALL,
        )

    # Remove any remaining standalone tags.
    cleaned_response = re.sub(
        r"</?(thinking|analysis|reasoning)>",
        "",
        cleaned_response,
        flags=re.IGNORECASE,
    )

    # Remove excessive blank lines.
    cleaned_response = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned_response,
    )

    return cleaned_response.strip()


# =========================================================
# REQUEST SCOPE VALIDATION
# =========================================================

def is_outside_business_scope(user_request: str) -> bool:
    """
    Detect requests that are clearly unrelated to business operations.

    This function does not inspect or access credentials.
    """

    request = user_request.lower()

    unrelated_terms = (
        "aws login",
        "aws configure",
        "aws cli",
        "access key",
        "secret key",
        "secret access key",
        "session token",
        "iam user",
        "iam role",
        "powershell",
        "terminal command",
        "python code",
        "write code",
        "debug code",
        "install package",
        "pip install",
        "programming help",
        "system administration",
    )

    return any(term in request for term in unrelated_terms)


def get_scope_message() -> str:
    """
    Return a safe response for unrelated requests.
    """

    return (
        "I am WorkPilot AI, a small-business operations assistant. "
        "I can help with business summaries, sales, pending orders, "
        "customer issues, operational tasks, deadlines, and priorities. "
        "Please ask a question related to your business operations."
    )


# =========================================================
# AGENT EXECUTION HELPER
# =========================================================

def ask_workpilot(user_request: str) -> str:
    """
    Send a user request to WorkPilot AI and return a clean response.

    Args:
        user_request: Natural-language question from the user.

    Returns:
        A clean, user-facing response string.
    """

    cleaned_request = user_request.strip()

    if not cleaned_request:
        return "Please enter a question about your business operations."

    if is_outside_business_scope(cleaned_request):
        logger.warning("Out-of-scope request blocked")
        return get_scope_message()

    logger.info("Processing WorkPilot business request")

    try:
        response = agent(cleaned_request)

        cleaned_response = clean_agent_response(str(response))

        if not cleaned_response:
            return (
                "I could not generate a useful response. "
                "Please ask another business-related question."
            )

        return cleaned_response

    except Exception:
        logger.exception("WorkPilot AI failed to process the request")

        return (
            "WorkPilot AI could not complete this business request. "
            "Please verify the AWS session and Bedrock access, "
            "then try again."
        )


# =========================================================
# TERMINAL INTERFACE
# =========================================================

def print_header() -> None:
    """
    Display the terminal application header.
    """

    print("=" * 68)
    print(f"{APP_NAME} - Small Business Operations Agent")
    print("=" * 68)
    print(f"Model : {MODEL_ID}")
    print(f"Region: {AWS_REGION}")
    print("Type 'exit' or 'quit' to close the application.")
    print()


def run_terminal_chat() -> None:
    """
    Run the interactive terminal chat interface.
    """

    print_header()

    while True:
        try:
            user_request = input("You: ").strip()

        except KeyboardInterrupt:
            print("\n\nApplication closed.")
            break

        except EOFError:
            print("\n\nApplication closed.")
            break

        if user_request.lower() in {"exit", "quit"}:
            print("\nGoodbye!")
            break

        if not user_request:
            print("Please enter a valid business question.\n")
            continue

        print("\nWorkPilot AI:")
        print(ask_workpilot(user_request))
        print()


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":
    run_terminal_chat()
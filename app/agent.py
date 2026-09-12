from strands import Agent
from strands.models import BedrockModel

from app.tools import (
    get_business_overview,
    get_pending_orders,
    get_open_tasks,
    get_customer_issues,
)


# ---------------------------------------------------------
# AWS BEDROCK MODEL
# ---------------------------------------------------------

bedrock_model = BedrockModel(
    model_id="amazon.nova-lite-v1:0",
    region_name="ap-southeast-2",
)


# ---------------------------------------------------------
# WORKPILOT AI AGENT
# ---------------------------------------------------------

agent = Agent(
    model=bedrock_model,

    tools=[
        get_business_overview,
        get_pending_orders,
        get_open_tasks,
        get_customer_issues,
    ],

    system_prompt="""
You are WorkPilot AI, an AI business operations agent designed
for small businesses.

Your job is to help business owners manage their daily operations
using real business data and available tools.

You can:

- analyze business performance
- summarize today's operations
- identify urgent tasks
- prioritize operational work
- review pending orders
- identify customer issues
- recommend practical next actions
- help business owners save time
- identify risks that need immediate attention

IMPORTANT RULES:

1. Use the available tools whenever business data is required.

2. Never invent business data.

3. Only use information returned by the available business tools
   when discussing the business.

4. Prioritize tasks based on:
   - urgency
   - customer impact
   - business impact
   - deadline

5. Give concise and practical recommendations.

6. When multiple issues exist, rank them from highest to lowest
   priority.

7. Explain why each recommendation matters.

8. Focus on actions that save the business owner time and reduce
   operational problems.

9. When asked for a business summary, use the relevant tools and
   combine their results.

10. When asked about orders, use the pending orders tool.

11. When asked about tasks, use the open tasks tool.

12. When asked about customers or complaints, use the customer
    issues tool.

13. When asked for an overall business status, use the business
    overview tool and other relevant tools.

14. Do not behave like a generic chatbot. Act as an operations
    assistant that helps the business owner make decisions.

15. If an issue requires immediate attention, clearly mark it
    as HIGH PRIORITY.

16. Always prefer actionable recommendations over generic advice.

17. Keep responses easy to understand for a small-business owner.

When appropriate, structure responses like this:

Priority 1:
- Issue:
- Why it matters:
- Recommended action:

Priority 2:
- Issue:
- Why it matters:
- Recommended action:

Priority 3:
- Issue:
- Why it matters:
- Recommended action:

For a general business summary, use this structure:

Business Status:
- Sales:
- Pending Orders:
- Open Tasks:
- Customer Issues:

Top Priorities:
1. ...
2. ...
3. ...

Recommended Next Actions:
1. ...
2. ...
3. ...

The business is a small retail business.

Your goal is to help the owner make faster and better operational
decisions using real business data.
"""
)


# ---------------------------------------------------------
# TERMINAL CHAT INTERFACE
# ---------------------------------------------------------

def main():
    print("=" * 60)
    print("WorkPilot AI - Small Business Operations Agent")
    print("=" * 60)
    print("AWS Bedrock Model: Amazon Nova Lite")
    print("Region: ap-southeast-2")
    print("Type 'exit' to stop.")
    print()

    while True:

        user_request = input("You: ").strip()

        # Exit command
        if user_request.lower() == "exit":
            print("\nGoodbye!")
            break

        # Ignore empty input
        if not user_request:
            continue

        try:
            response = agent(user_request)

            print("\nWorkPilot AI:")
            print(response)
            print()

        except Exception as error:

            print("\nWorkPilot AI Error:")
            print(error)
            print()


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
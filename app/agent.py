from strands import Agent

from app.tools import (
    get_business_overview,
    get_pending_orders,
    get_open_tasks,
    get_customer_issues,
)


agent = Agent(
    tools=[
        get_business_overview,
        get_pending_orders,
        get_open_tasks,
        get_customer_issues,
    ],
    system_prompt="""
You are WorkPilot AI, an AI business operations agent designed for small businesses.

Your job is to help business owners manage their daily operations using the available business data and tools.

You can:
- analyze the current business situation
- summarize today's business performance
- identify and prioritize urgent tasks
- review pending customer orders
- identify customer issues that need attention
- provide practical operational recommendations
- help the owner decide what should be done first

IMPORTANT BEHAVIOR:
1. Use the available tools whenever the user's request requires actual business data.
2. Do not invent business data.
3. Prioritize recommendations based on urgency, customer impact, and business impact.
4. Give concise, practical, action-oriented answers.
5. When useful, organize the response as:
   - Priority
   - Reason
   - Recommended Action
6. If the user asks for a business summary, combine information from the relevant tools.
7. If there are multiple issues, clearly identify the most important ones first.
8. Act like an operations assistant, not just a chatbot.

The business is a small retail business, and your goal is to help the owner save time, respond to customers faster, and make better operational decisions.
"""
)


def main():
    print("=" * 60)
    print("WorkPilot AI - Small Business Operations Agent")
    print("=" * 60)
    print("Type 'exit' to stop.\n")

    while True:
        user_request = input("You: ").strip()

        if user_request.lower() == "exit":
            print("\nGoodbye!")
            break

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


if __name__ == "__main__":
    main()
import streamlit as st

from app.agent import agent
from app.tools import (
    get_business_overview,
    get_pending_orders,
    get_open_tasks,
    get_customer_issues,
)


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="WorkPilot AI",
    page_icon="",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("WorkPilot AI")
st.caption("AI-powered operations assistant for small businesses")

st.divider()


# ---------------------------------------------------------
# LOAD BUSINESS DATA
# ---------------------------------------------------------

overview = get_business_overview()
orders = get_pending_orders()
tasks = get_open_tasks()
issues = get_customer_issues()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Today's Sales",
        f"₹{overview['today_sales']:,}",
    )

with col2:
    st.metric(
        "Pending Orders",
        overview["pending_orders"],
    )

with col3:
    st.metric(
        "Open Tasks",
        overview["open_tasks"],
    )

with col4:
    st.metric(
        "Customer Issues",
        overview["customer_issues"],
    )


st.divider()


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------

left, right = st.columns(2)


# ---------------------------------------------------------
# PENDING ORDERS
# ---------------------------------------------------------

with left:
    st.subheader("Pending Orders")

    for order in orders:
        st.markdown(
            f"""
**{order['order_id']} — {order['customer']}**

Amount: ₹{order['amount']:,}

Status: {order['status']}
"""
        )
        st.divider()


# ---------------------------------------------------------
# PRIORITY TASKS
# ---------------------------------------------------------

with right:
    st.subheader("Operational Tasks")

    for task in tasks:
        priority = task["priority"]

        st.markdown(
            f"""
**{task['task']}**

Priority: **{priority}**

Deadline: {task['deadline']}
"""
        )
        st.divider()


# ---------------------------------------------------------
# CUSTOMER ISSUES
# ---------------------------------------------------------

st.subheader("Customer Issues")

for issue in issues:
    st.markdown(
        f"""
**{issue['customer']} — {issue['priority']} Priority**

{issue['issue']}
"""
    )


st.divider()


# ---------------------------------------------------------
# AI ASSISTANT
# ---------------------------------------------------------

st.subheader("Ask WorkPilot AI")

st.write(
    "Ask questions about your business, priorities, orders, "
    "tasks, or customer issues."
)


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_prompt = st.chat_input(
    "Example: What should I focus on first today?"
)


if user_prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("WorkPilot is analyzing your business..."):

            try:
                response = agent(user_prompt)

                response_text = str(response)

                st.markdown(response_text)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response_text,
                    }
                )

            except Exception as error:

                error_message = (
                    "WorkPilot could not complete the request.\n\n"
                    f"Error: `{error}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )
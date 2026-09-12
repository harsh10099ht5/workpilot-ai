import json
from pathlib import Path

from strands import tool


DATA_FILE = Path(__file__).parent / "data" / "business.json"


def load_business_data():
    """Load the small-business data used by WorkPilot."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@tool
def get_business_overview():
    """Return a summary of the business."""
    data = load_business_data()

    return {
        "business_name": data["business_name"],
        "today_sales": data["today_sales"],
        "pending_orders": len(data["pending_orders"]),
        "open_tasks": len(data["tasks"]),
        "customer_issues": len(data["customer_issues"]),
    }


@tool
def get_pending_orders():
    """Return orders that still need attention."""
    data = load_business_data()
    return data["pending_orders"]


@tool
def get_open_tasks():
    """Return current operational tasks."""
    data = load_business_data()
    return data["tasks"]


@tool
def get_customer_issues():
    """Return customer issues requiring attention."""
    data = load_business_data()
    return data["customer_issues"]
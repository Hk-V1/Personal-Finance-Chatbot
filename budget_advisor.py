import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import json

class BudgetAdvisor:
    def __init__(self):
        self.expenses = []
        self.budgets = {
            "food_dining": 500,
            "transportation": 300,
            "shopping": 400,
            "entertainment": 200,
            "utilities_bills": 250,
            "healthcare": 150,
            "education": 100,
            "travel": 300,
            "other": 200
        }
        self.total_budget = sum(self.budgets.values())
    
    def add_expense(self, amount: float, description: str, category: str):
        expense = {
            "id": len(self.expenses) + 1,
            "amount": amount,
            "description": description,
            "category": category,
            "date": datetime.now(),
            "month": datetime.now().strftime("%Y-%m")
        }
        self.expenses.append(expense)
        return expense
    
    def get_expenses_df(self) -> pd.DataFrame:
        if not self.expenses:
            return pd.DataFrame()
        return pd.DataFrame(self.expenses)
    
    def get_monthly_summary(self, month: str = None) -> Dict:
        if not self.expenses:
            return {"total": 0, "by_category": {}, "transaction_count": 0}
        
        df = self.get_expenses_df()
        
        if month:
            df = df[df['month'] == month]
        else:
            current_month = datetime.now().strftime("%Y-%m")
            df = df[df['month'] == current_month]
        
        summary = {
            "total": df['amount'].sum(),
            "by_category": df.groupby('category')['amount'].sum().to_dict(),
            "transaction_count": len(df),
            "average_transaction": df['amount'].mean() if len(df) > 0 else 0
        }
        
        return summary
    
    def get_budget_status(self) -> Dict:
        summary = self.get_monthly_summary()
        status = {}
        
        for category, budget_limit in self.budgets.items():
            spent = summary["by_category"].get(category, 0)
            remaining = budget_limit - spent
            percentage_used = (spent / budget_limit) * 100 if budget_limit > 0 else 0
            
            status[category] = {
                "budget": budget_limit,
                "spent": spent,
                "remaining": remaining,
                "percentage_used": percentage_used,
                "status": "over_budget" if spent > budget_limit else 
                         "warning" if percentage_used > 80 else "good"
            }
        
        total_spent = summary["total"]
        total_remaining = self.total_budget - total_spent
        
        status["overall"] = {
            "budget": self.total_budget,
            "spent": total_spent,
            "remaining": total_remaining,
            "percentage_used": (total_spent / self.total_budget) * 100,
            "status": "over_budget" if total_spent > self.total_budget else
                     "warning" if (total_spent / self.total_budget) > 0.8 else "good"
        }
        
        return status
    
    def get_spending_advice(self) -> List[str]:
        advice = []
        budget_status = self.get_budget_status()
        summary = self.get_monthly_summary()
        
        overall = budget_status["overall"]
        if overall["status"] == "over_budget":
            advice.append(f"You're over budget by ${overall['spent'] - overall['budget']:.2f}. Consider reducing spending in your highest categories.")
        elif overall["status"] == "warning":
            advice.append(f"You've used {overall['percentage_used']:.1f}% of your budget. Be mindful of remaining expenses this month.")
        else:
            advice.append(f"Good job! You're at {overall['percentage_used']:.1f}% of your budget with ${overall['remaining']:.2f} remaining.")
        
        over_budget_categories = []
        warning_categories = []
        
        for category, status in budget_status.items():
            if category == "overall":
                continue
                
            if status["status"] == "over_budget":
                over_budget_categories.append((category, status["spent"] - status["budget"]))
            elif status["status"] == "warning":
                warning_categories.append((category, status["percentage_used"]))
        
        if over_budget_categories:
            worst_category = max(over_budget_categories, key=lambda x: x[1])
            advice.append(f"Your '{worst_category[0]}' spending is ${worst_category[1]:.2f} over budget. This is your biggest overspend area.")
        
        if warning_categories:
            high_usage = max(warning_categories, key=lambda x: x[1])
            advice.append(f"Watch your '{high_usage[0]}' spending - you're at {high_usage[1]:.1f}% of budget.")
        
        if summary["transaction_count"] > 0:
            avg_transaction = summary["average_transaction"]
            if avg_transaction < 10:
                advice.append("Tip: You make many small purchases. Consider bulk buying for items like groceries to save money.")
            elif avg_transaction > 100:
                advice.append("Tip: You tend to make large purchases. Consider waiting 24 hours before big buys to avoid impulse spending.")
        
        if summary["by_category"]:
            top_category = max(summary["by_category"], key=summary["by_category"].get)
            top_amount = summary["by_category"][top_category]
            advice.append(f"Your highest spending category is '{top_category}' at ${top_amount:.2f}.")
        
        return advice if advice else ["Great job managing your finances! Keep tracking your expenses."]
    
    def set_budget(self, category: str, amount: float):
        if category in self.budgets:
            old_amount = self.budgets[category]
            self.budgets[category] = amount
            self.total_budget = sum(self.budgets.values())
            return f"Updated {category} budget from ${old_amount:.2f} to ${amount:.2f}"
        else:
            return f"Category '{category}' not found. Available categories: {list(self.budgets.keys())}"

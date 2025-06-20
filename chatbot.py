import json
from typing import Dict
from datetime import datetime
from intent_classifier import IntentClassifier
from budget_advisor import BudgetAdvisor

class FinanceChatbot:
    def __init__(self):
        self.classifier = IntentClassifier()
        self.advisor = BudgetAdvisor()
        self.conversation_history = []
    
    def process_message(self, user_input: str) -> str:
        intent, confidence, extracted_info = self.classifier.classify_intent(user_input)
        
        self.conversation_history.append({
            "user": user_input,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now()
        })
        
        response = self._generate_response(intent, extracted_info, user_input)
        
        self.conversation_history.append({
            "bot": response,
            "timestamp": datetime.now()
        })
        
        return response
    
    def _generate_response(self, intent: str, extracted_info: Dict, user_input: str) -> str:
        
        if intent == "greeting":
            return "Hello! I'm your personal finance assistant. I can help you track expenses, manage budgets, and provide financial advice. What would you like to do?"
        
        elif intent == "help":
            return """I can help you with:
            
 Track Expenses: Say "I spent $50 on groceries" or "Add $25 for coffee"
 View Budget: Ask "Show my budget" or "How much have I spent?"  
 Get Advice: Ask "Give me budget advice" or "How's my spending?"
 Set Budgets: Say "Set food budget to $400" or "Update my shopping budget"
 Analyze Trends: Ask "Show spending trends" or "What's my top category?"

Just tell me what you'd like to do!"""
        
        elif intent == "add_expense":
            if extracted_info.get("amount") and extracted_info.get("description"):
                expense = self.advisor.add_expense(
                    amount=extracted_info["amount"],
                    description=extracted_info["description"],
                    category=extracted_info.get("category", "other")
                )
                return f"Added expense: ${expense['amount']:.2f} for {expense['description']} (Category: {expense['category']})\n\nYour current month total is now ${self.advisor.get_monthly_summary()['total']:.2f}"
            else:
                return "I couldn't extract the expense details. Please try: 'I spent $50 on groceries' or 'Add $25 for coffee'"
        
        elif intent == "view_budget":
            summary = self.advisor.get_monthly_summary()
            budget_status = self.advisor.get_budget_status()
            
            response = f"Current Month Summary\n"
            response += f"Total Spent: ${summary['total']:.2f} / ${self.advisor.total_budget:.2f}\n"
            response += f"Transactions: {summary['transaction_count']}\n\n"
            
            response += "By Category:\n"
            for category, status in budget_status.items():
                if category == "overall":
                    continue
                emoji = "🚨" if status["status"] == "over_budget" else "⚠️" if status["status"] == "warning" else "✅"
                response += f"{emoji} {category}: ${status['spent']:.2f} / ${status['budget']:.2f} ({status['percentage_used']:.1f}%)\n"
            
            return response
        
        elif intent == "get_advice":
            advice_list = self.advisor.get_spending_advice()
            response = "Your Personalized Financial Advice: \n\n"
            response += "\n".join([f"• {advice}" for advice in advice_list])
            return response
        
        elif intent == "set_budget":
            if extracted_info.get("budget_amount"):
                self.advisor.total_budget = extracted_info["budget_amount"]
                return f"Updated your total monthly budget to ${extracted_info['budget_amount']:.2f}"
            else:
                return "Please specify a budget amount, like: 'Set my budget to $3000' or 'Update food budget to $500'"
        
        elif intent == "analyze_trends":
            summary = self.advisor.get_monthly_summary()
            if not summary["by_category"]:
                return "No expenses recorded yet. Start by adding some expenses!"
            
            top_category = max(summary["by_category"], key=summary["by_category"].get)
            top_amount = summary["by_category"][top_category]
            
            response = f" Spending Analysis \n\n"
            response += f" Top Category: {top_category} (${top_amount:.2f})\n"
            response += f" Average Transaction: ${summary['average_transaction']:.2f}\n"
            response += f" Total Transactions: {summary['transaction_count']}\n\n"
            
            response += "**Category Breakdown:**\n"
            for cat, amount in sorted(summary["by_category"].items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / summary["total"]) * 100
                response += f"• {cat}: ${amount:.2f} ({percentage:.1f}%)\n"
            
            return response
        
        else:
            return "I'm not sure how to help with that. Try asking about expenses, budgets, or say 'help' for more options."

def main():
    bot = FinanceChatbot()
    
    print("🤖 Personal Finance Chatbot")
    print("=" * 40)
    print("Type 'quit' to exit, 'help' for commands\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye! Keep tracking those expenses!")
            break
        
        if not user_input:
            continue
        
        response = bot.process_message(user_input)
        print(f"Bot: {response}\n")

if __name__ == "__main__":
    main()

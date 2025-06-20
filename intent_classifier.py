from transformers import pipeline
import re
import json
from typing import Dict, List, Tuple
import pandas as pd
from datasets import load_dataset

class IntentClassifier:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification", 
                                 model="facebook/bart-large-mnli")
        
        self.intents = [
            "add_expense",
            "view_budget", 
            "get_advice",
            "categorize_spending",
            "set_budget",
            "analyze_trends",
            "greeting",
            "help"
        ]
        
        self.financial_context = self._load_financial_context()
    
    def _load_financial_context(self) -> Dict:
        try:
            dataset = load_dataset("takala/financial_phrasebank", split="train")
            
            context = {
                "positive": [],
                "negative": [], 
                "neutral": []
            }
            
            for item in dataset:
                sentence = item['sentence']
                label = item['label']
                
                if label == 0:  
                    context["negative"].append(sentence)
                elif label == 1:  
                    context["neutral"].append(sentence) 
                elif label == 2:  
                    context["positive"].append(sentence)
                    
            return context
        except Exception as e:
            print(f"Warning: Could not load financial dataset: {e}")
            return {"positive": [], "negative": [], "neutral": []}
    
    def extract_expense_info(self, text: str) -> Dict:
        amount_patterns = [
            r'\$(\d+(?:\.\d{2})?)',  
            r'(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?|\$)',
            r'spent\s+(\d+(?:\.\d{2})?)', 
        ]
        
        amount = None
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = float(match.group(1))
                break
        
        description = re.sub(r'\$\d+(?:\.\d{2})?', '', text)
        description = re.sub(r'\d+(?:\.\d{2})?\s*(?:dollars?|bucks?)', '', description)
        description = re.sub(r'spent\s+\d+(?:\.\d{2})?', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\b(?:i|on|for|at|in)\b', '', description, flags=re.IGNORECASE)
        description = description.strip()
        
        return {
            "amount": amount,
            "description": description
        }
    
    def categorize_expense(self, description: str) -> str:
        categories = [
            "food_dining",
            "transportation", 
            "shopping",
            "entertainment",
            "utilities_bills",
            "healthcare",
            "education",
            "travel",
            "other"
        ]
        
        result = self.classifier(description, categories)
        return result['labels'][0]
    
    def classify_intent(self, text: str) -> Tuple[str, float, Dict]:
        result = self.classifier(text, self.intents)
        intent = result['labels'][0]
        confidence = result['scores'][0]
        
        extracted_info = {}
        
        if intent == "add_expense":
            extracted_info = self.extract_expense_info(text)
            if extracted_info["description"]:
                extracted_info["category"] = self.categorize_expense(extracted_info["description"])
        
        elif intent == "set_budget":
            amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', text)
            if amount_match:
                extracted_info["budget_amount"] = float(amount_match.group(1))
        
        return intent, confidence, extracted_info

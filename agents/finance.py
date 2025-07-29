"""
Finance Agent - NOVA's financial management and analysis specialist

Handles:
- Expense tracking and categorization
- Budget planning and monitoring
- Investment analysis and recommendations
- Bill payment reminders and automation
- Financial goal tracking
- Market analysis and insights
- Tax preparation assistance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass
from decimal import Decimal

# Import from parent core directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import BaseAgent, AgentType, Task, AgentCapability


@dataclass
class Transaction:
    """Represents a financial transaction"""
    id: str
    amount: Decimal
    category: str
    description: str
    date: datetime
    account: str
    transaction_type: str  # income, expense, transfer
    tags: List[str] = None
    recurring: bool = False


@dataclass
class Budget:
    """Represents a budget category"""
    category: str
    monthly_limit: Decimal
    current_spent: Decimal = Decimal('0')
    period_start: datetime = None
    period_end: datetime = None


class FinanceAgent(BaseAgent):
    """Agent specialized in financial management and analysis"""
    
    def __init__(self):
        super().__init__(AgentType.FINANCE)
        self.capabilities = [
            AgentCapability("expense_tracking", "Track and categorize expenses", 
                          ["transaction_data"], ["expense_report"], "basic", "fast"),
            AgentCapability("budget_management", "Create and monitor budgets", 
                          ["budget_preferences"], ["budget_plan"], "intermediate", "medium"),
            AgentCapability("investment_analysis", "Analyze investment opportunities", 
                          ["portfolio_data"], ["analysis_report"], "advanced", "medium"),
            AgentCapability("bill_reminders", "Track and remind about bills", 
                          ["bill_data"], ["reminder_schedule"], "basic", "fast"),
            AgentCapability("financial_planning", "Long-term financial planning", 
                          ["financial_goals"], ["planning_strategy"], "advanced", "slow"),
            AgentCapability("market_analysis", "Market trends and insights", 
                          ["market_query"], ["market_report"], "advanced", "medium"),
            AgentCapability("tax_assistance", "Tax preparation and optimization", 
                          ["financial_records"], ["tax_report"], "advanced", "slow")
        ]
        
        # In-memory storage (would integrate with NOVA's memory system)
        self.transactions: List[Transaction] = []
        self.budgets: List[Budget] = []
        self.accounts: Dict[str, Decimal] = {"checking": Decimal('5000'), "savings": Decimal('15000')}
        self.bills: List[Dict[str, Any]] = []
        self.investments: Dict[str, Any] = {}
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute financial management tasks"""
        try:
            self.current_task = task
            self.logger.info(f"💰 Executing finance task: {task.description}")
            
            action = task.parameters.get("action", "general")
            
            if action == "track_expense":
                return await self._track_expense(task.parameters)
            elif action == "create_budget":
                return await self._create_budget(task.parameters)
            elif action == "analyze_spending":
                return await self._analyze_spending(task.parameters)
            elif action == "investment_advice":
                return await self._investment_advice(task.parameters)
            elif action == "bill_reminder":
                return await self._bill_reminder(task.parameters)
            elif action == "financial_summary":
                return await self._financial_summary(task.parameters)
            elif action == "market_analysis":
                return await self._market_analysis(task.parameters)
            elif action == "tax_preparation":
                return await self._tax_preparation(task.parameters)
            else:
                return await self._general_finance(task.parameters)
            
        except Exception as e:
            self.logger.error(f"Finance task failed: {e}")
            return {"error": str(e), "status": "failed"}
        finally:
            self.current_task = None
    
    async def _track_expense(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track a new expense transaction"""
        amount = Decimal(str(params.get("amount", "0")))
        category = params.get("category", "miscellaneous")
        description = params.get("description", "Expense")
        account = params.get("account", "checking")
        
        transaction = Transaction(
            id=f"txn_{datetime.now().isoformat()}",
            amount=amount,
            category=category,
            description=description,
            date=datetime.now(),
            account=account,
            transaction_type="expense",
            tags=params.get("tags", [])
        )
        
        self.transactions.append(transaction)
        
        # Update account balance
        if account in self.accounts:
            self.accounts[account] -= amount
        
        # Check budget impact
        budget_impact = await self._check_budget_impact(category, amount)
        
        return {
            "transaction": {
                "id": transaction.id,
                "amount": str(transaction.amount),
                "category": transaction.category,
                "description": transaction.description,
                "date": transaction.date.isoformat()
            },
            "account_balance": str(self.accounts.get(account, Decimal('0'))),
            "budget_impact": budget_impact,
            "status": "completed",
            "message": f"Expense of ${amount} tracked successfully"
        }
    
    async def _create_budget(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a budget"""
        budget_data = params.get("budget", {})
        
        # Default budget categories
        default_categories = {
            "housing": Decimal('1500'),
            "food": Decimal('600'),
            "transportation": Decimal('400'),
            "utilities": Decimal('200'),
            "entertainment": Decimal('300'),
            "healthcare": Decimal('200'),
            "shopping": Decimal('250'),
            "miscellaneous": Decimal('150')
        }
        
        # Create budgets
        new_budgets = []
        for category, limit in budget_data.items() if budget_data else default_categories.items():
            budget = Budget(
                category=category,
                monthly_limit=Decimal(str(limit)),
                period_start=datetime.now().replace(day=1),
                period_end=(datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            )
            new_budgets.append(budget)
        
        self.budgets = new_budgets
        
        return {
            "budgets": [
                {
                    "category": b.category,
                    "limit": str(b.monthly_limit),
                    "spent": str(b.current_spent),
                    "remaining": str(b.monthly_limit - b.current_spent)
                }
                for b in self.budgets
            ],
            "total_budget": str(sum(b.monthly_limit for b in self.budgets)),
            "status": "completed",
            "message": "Budget created successfully"
        }
    
    async def _analyze_spending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spending patterns and trends"""
        timeframe = params.get("timeframe", "month")
        
        if timeframe == "month":
            start_date = datetime.now().replace(day=1)
        elif timeframe == "week":
            start_date = datetime.now() - timedelta(days=7)
        else:
            start_date = datetime.now() - timedelta(days=30)
        
        # Filter transactions
        relevant_txns = [
            t for t in self.transactions 
            if t.date >= start_date and t.transaction_type == "expense"
        ]
        
        # Analyze by category
        category_spending = {}
        for txn in relevant_txns:
            if txn.category not in category_spending:
                category_spending[txn.category] = Decimal('0')
            category_spending[txn.category] += txn.amount
        
        total_spent = sum(category_spending.values())
        
        # Generate insights
        insights = []
        if category_spending:
            top_category = max(category_spending.items(), key=lambda x: x[1])
            insights.append(f"Highest spending category: {top_category[0]} (${top_category[1]})")
            
            avg_daily = total_spent / (datetime.now() - start_date).days if (datetime.now() - start_date).days > 0 else Decimal('0')
            insights.append(f"Average daily spending: ${avg_daily:.2f}")
        
        return {
            "analysis": {
                "total_spent": str(total_spent),
                "timeframe": timeframe,
                "category_breakdown": {k: str(v) for k, v in category_spending.items()},
                "transaction_count": len(relevant_txns),
                "insights": insights
            },
            "recommendations": [
                "Consider setting up automatic savings transfers",
                "Review subscription services for potential savings",
                "Track cash transactions for complete picture"
            ],
            "status": "completed"
        }
    
    async def _investment_advice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide investment analysis and advice"""
        investment_type = params.get("type", "general")
        risk_tolerance = params.get("risk_tolerance", "moderate")
        amount = params.get("amount", "1000")
        
        # Mock investment recommendations
        recommendations = {
            "conservative": {
                "bonds": 60,
                "stocks": 30,
                "cash": 10,
                "expected_return": "4-6%"
            },
            "moderate": {
                "stocks": 60,
                "bonds": 30,
                "alternatives": 10,
                "expected_return": "6-8%"
            },
            "aggressive": {
                "stocks": 80,
                "alternatives": 15,
                "bonds": 5,
                "expected_return": "8-12%"
            }
        }
        
        allocation = recommendations.get(risk_tolerance, recommendations["moderate"])
        
        return {
            "investment_advice": {
                "risk_profile": risk_tolerance,
                "recommended_allocation": allocation,
                "investment_amount": amount,
                "diversification_tips": [
                    "Don't put all eggs in one basket",
                    "Consider low-cost index funds",
                    "Rebalance portfolio quarterly",
                    "Dollar-cost averaging for regular investments"
                ]
            },
            "market_outlook": {
                "trend": "cautiously optimistic",
                "key_factors": ["inflation trends", "interest rates", "geopolitical stability"]
            },
            "status": "completed"
        }
    
    async def _bill_reminder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Manage bill reminders and payment tracking"""
        action = params.get("bill_action", "list")
        
        if action == "add":
            bill = {
                "id": f"bill_{datetime.now().isoformat()}",
                "name": params.get("name", "New Bill"),
                "amount": params.get("amount", "0"),
                "due_date": params.get("due_date"),
                "frequency": params.get("frequency", "monthly"),
                "auto_pay": params.get("auto_pay", False)
            }
            self.bills.append(bill)
            return {
                "bill": bill,
                "status": "completed",
                "message": f"Bill '{bill['name']}' added successfully"
            }
        
        # List upcoming bills
        upcoming_bills = []
        for bill in self.bills:
            # Mock upcoming bill calculation
            upcoming_bills.append({
                "name": bill.get("name", "Unknown"),
                "amount": bill.get("amount", "0"),
                "due_date": bill.get("due_date", "Unknown"),
                "days_until_due": 5  # Mock value
            })
        
        return {
            "upcoming_bills": upcoming_bills,
            "total_amount": sum(float(bill.get("amount", "0")) for bill in upcoming_bills),
            "reminders_set": len(upcoming_bills),
            "status": "completed"
        }
    
    async def _financial_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive financial summary"""
        total_assets = sum(self.accounts.values())
        monthly_expenses = sum(t.amount for t in self.transactions if t.transaction_type == "expense")
        monthly_income = sum(t.amount for t in self.transactions if t.transaction_type == "income")
        
        summary = {
            "accounts": {name: str(balance) for name, balance in self.accounts.items()},
            "total_assets": str(total_assets),
            "monthly_income": str(monthly_income),
            "monthly_expenses": str(monthly_expenses),
            "net_cash_flow": str(monthly_income - monthly_expenses),
            "savings_rate": f"{((monthly_income - monthly_expenses) / monthly_income * 100):.1f}%" if monthly_income > 0 else "0%",
            "budget_utilization": [
                {
                    "category": b.category,
                    "used_percentage": f"{(b.current_spent / b.monthly_limit * 100):.1f}%"
                }
                for b in self.budgets
            ]
        }
        
        return {
            "financial_summary": summary,
            "recommendations": [
                "Aim for 20% savings rate",
                "Build emergency fund (3-6 months expenses)",
                "Review and optimize subscription services",
                "Consider increasing retirement contributions"
            ],
            "status": "completed"
        }
    
    async def _market_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide market analysis and trends"""
        symbol = params.get("symbol", "SPY")
        
        # Mock market data
        analysis = {
            "symbol": symbol,
            "current_price": "$420.50",
            "change": "+2.3%",
            "trend": "bullish",
            "support_level": "$415.00",
            "resistance_level": "$430.00",
            "analyst_rating": "BUY",
            "key_metrics": {
                "pe_ratio": "18.5",
                "dividend_yield": "1.8%",
                "52_week_high": "$450.00",
                "52_week_low": "$380.00"
            },
            "news_sentiment": "positive"
        }
        
        return {
            "market_analysis": analysis,
            "recommendations": [
                f"Consider dollar-cost averaging into {symbol}",
                "Monitor support/resistance levels",
                "Keep an eye on broader market trends"
            ],
            "status": "completed"
        }
    
    async def _tax_preparation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assist with tax preparation and optimization"""
        tax_year = params.get("year", datetime.now().year)
        
        # Calculate basic tax information from transactions
        income_txns = [t for t in self.transactions if t.transaction_type == "income"]
        deductible_expenses = [t for t in self.transactions if t.category in ["healthcare", "charitable", "business"]]
        
        total_income = sum(t.amount for t in income_txns)
        total_deductions = sum(t.amount for t in deductible_expenses)
        
        tax_summary = {
            "tax_year": tax_year,
            "total_income": str(total_income),
            "potential_deductions": str(total_deductions),
            "estimated_taxable_income": str(total_income - total_deductions),
            "tax_documents_needed": [
                "W-2 forms",
                "1099 forms",
                "Bank statements",
                "Investment statements",
                "Receipts for deductions"
            ],
            "key_deadlines": {
                "filing_deadline": f"April 15, {tax_year + 1}",
                "extension_deadline": f"October 15, {tax_year + 1}",
                "estimated_payments": "Quarterly"
            }
        }
        
        return {
            "tax_preparation": tax_summary,
            "optimization_tips": [
                "Maximize retirement contributions",
                "Consider HSA contributions if eligible",
                "Track charitable donations",
                "Keep detailed records of business expenses"
            ],
            "status": "completed"
        }
    
    async def _check_budget_impact(self, category: str, amount: Decimal) -> Dict[str, Any]:
        """Check if expense impacts budget"""
        for budget in self.budgets:
            if budget.category == category:
                budget.current_spent += amount
                remaining = budget.monthly_limit - budget.current_spent
                
                if remaining < Decimal('0'):
                    return {
                        "over_budget": True,
                        "category": category,
                        "overage": str(abs(remaining)),
                        "warning": f"Over budget in {category} by ${abs(remaining)}"
                    }
                elif remaining < budget.monthly_limit * Decimal('0.1'):  # Less than 10% remaining
                    return {
                        "warning": True,
                        "category": category,
                        "remaining": str(remaining),
                        "message": f"Only ${remaining} left in {category} budget"
                    }
        
        return {"status": "ok"}
    
    async def _general_finance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general financial queries"""
        content = params.get("content", "")
        
        return {
            "result": f"Financial query processed: {content}",
            "general_tips": [
                "Pay yourself first - automate savings",
                "Track expenses to understand spending patterns",
                "Build an emergency fund",
                "Invest for long-term goals",
                "Review and update budget regularly"
            ],
            "status": "completed"
        }

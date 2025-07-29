"""
Life Manager Agent - NOVA's personal productivity and organization specialist

Handles:
- Schedule management and calendar integration
- Task and project tracking
- Goal setting and progress monitoring
- Habit tracking and wellness reminders
- Note-taking and knowledge organization
- Personal productivity optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass

# Import from parent core directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import BaseAgent, AgentType, Task, AgentCapability


@dataclass
class ScheduleItem:
    """Represents a scheduled item"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str = ""
    priority: str = "medium"
    category: str = "general"
    reminders: List[int] = None  # Minutes before
    recurring: bool = False


@dataclass
class Goal:
    """Represents a personal or professional goal"""
    id: str
    title: str
    description: str
    category: str
    target_date: datetime
    progress: float = 0.0  # 0-100
    milestones: List[str] = None
    created_at: datetime = None


class LifeManagerAgent(BaseAgent):
    """Agent specialized in life management and productivity tasks"""
    
    def __init__(self):
        super().__init__(AgentType.LIFE_MANAGER)
        self.capabilities = [
            AgentCapability("schedule_management", "Manage calendar and appointments", 
                          ["schedule_request"], ["calendar_update"], "basic", "fast"),
            AgentCapability("task_tracking", "Track todos and project progress", 
                          ["task_list"], ["progress_update"], "basic", "fast"),
            AgentCapability("goal_setting", "Set and track personal/professional goals", 
                          ["goal_description"], ["goal_plan"], "intermediate", "medium"),
            AgentCapability("habit_tracking", "Monitor and encourage good habits", 
                          ["habit_data"], ["habit_analysis"], "intermediate", "medium"),
            AgentCapability("productivity_analysis", "Analyze and optimize productivity patterns", 
                          ["activity_data"], ["optimization_plan"], "advanced", "medium"),
            AgentCapability("wellness_reminders", "Health and wellness check-ins", 
                          ["wellness_preferences"], ["reminder_schedule"], "basic", "fast")
        ]
        
        # In-memory storage (would integrate with NOVA's memory system)
        self.schedule_items: List[ScheduleItem] = []
        self.goals: List[Goal] = []
        self.tasks: List[Dict[str, Any]] = []
        self.habits: Dict[str, Any] = {}
    
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute life management tasks"""
        try:
            self.current_task = task
            self.logger.info(f"📅 Executing life management task: {task.description}")
            
            action = task.parameters.get("action", "general")
            
            if action == "create_weekly_plan":
                return await self._create_weekly_plan(task.parameters)
            elif action == "schedule_meeting":
                return await self._schedule_meeting(task.parameters)
            elif action == "track_habit":
                return await self._track_habit(task.parameters)
            elif action == "set_goal":
                return await self._set_goal(task.parameters)
            elif action == "get_schedule":
                return await self._get_schedule(task.parameters)
            elif action == "productivity_analysis":
                return await self._analyze_productivity(task.parameters)
            elif action == "wellness_check":
                return await self._wellness_check(task.parameters)
            else:
                return await self._general_life_management(task.parameters)
            
        except Exception as e:
            self.logger.error(f"Life management task failed: {e}")
            return {"error": str(e), "status": "failed"}
        finally:
            self.current_task = None
    
    async def _create_weekly_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured weekly plan"""
        timeframe = params.get("timeframe", "week")
        preferences = params.get("user_preferences", {})
        
        # Generate weekly structure
        plan = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "structure": {
                "monday": {
                    "focus": "Planning & Strategy",
                    "blocks": [
                        {"time": "09:00-10:00", "activity": "Week planning review"},
                        {"time": "10:00-12:00", "activity": "Deep work block 1"},
                        {"time": "14:00-16:00", "activity": "Meetings & communication"},
                        {"time": "16:00-17:00", "activity": "Admin tasks"}
                    ]
                },
                "tuesday": {
                    "focus": "Execution & Progress",
                    "blocks": [
                        {"time": "09:00-11:00", "activity": "Deep work block 2"},
                        {"time": "11:00-12:00", "activity": "Project check-ins"},
                        {"time": "14:00-16:00", "activity": "Creative work"},
                        {"time": "16:00-17:00", "activity": "Learning time"}
                    ]
                },
                "wednesday": {
                    "focus": "Collaboration & Reviews",
                    "blocks": [
                        {"time": "09:00-10:00", "activity": "Team meetings"},
                        {"time": "10:00-12:00", "activity": "Collaborative projects"},
                        {"time": "14:00-15:00", "activity": "Progress reviews"},
                        {"time": "15:00-17:00", "activity": "Deep work block 3"}
                    ]
                },
                "thursday": {
                    "focus": "Innovation & Development",
                    "blocks": [
                        {"time": "09:00-11:00", "activity": "Skill development"},
                        {"time": "11:00-12:00", "activity": "Research time"},
                        {"time": "14:00-16:00", "activity": "Innovation projects"},
                        {"time": "16:00-17:00", "activity": "Network building"}
                    ]
                },
                "friday": {
                    "focus": "Completion & Reflection",
                    "blocks": [
                        {"time": "09:00-11:00", "activity": "Week wrap-up"},
                        {"time": "11:00-12:00", "activity": "Loose ends cleanup"},
                        {"time": "14:00-15:00", "activity": "Week reflection"},
                        {"time": "15:00-17:00", "activity": "Next week preparation"}
                    ]
                }
            },
            "goals": [
                "Complete 3 major project milestones",
                "Dedicate 5 hours to skill development",
                "Maintain work-life balance",
                "Network with 2 new professional contacts"
            ]
        }
        
        return {
            "plan": plan,
            "status": "completed",
            "message": "Weekly plan created successfully"
        }
    
    async def _schedule_meeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a meeting or appointment"""
        title = params.get("title", "Meeting")
        start_time = params.get("start_time")
        duration = params.get("duration", 60)  # minutes
        
        # Parse time if string
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time)
            except:
                start_time = datetime.now() + timedelta(hours=1)
        
        end_time = start_time + timedelta(minutes=duration)
        
        meeting = ScheduleItem(
            id=f"meeting_{datetime.now().isoformat()}",
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=params.get("description", ""),
            priority=params.get("priority", "medium"),
            category="meeting"
        )
        
        self.schedule_items.append(meeting)
        
        return {
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "start": meeting.start_time.isoformat(),
                "end": meeting.end_time.isoformat()
            },
            "status": "completed",
            "message": f"Meeting '{title}' scheduled successfully"
        }
    
    async def _track_habit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track habit completion and progress"""
        habit_name = params.get("habit", "")
        completed = params.get("completed", False)
        date = params.get("date", datetime.now().date().isoformat())
        
        if habit_name not in self.habits:
            self.habits[habit_name] = {
                "name": habit_name,
                "streak": 0,
                "total_days": 0,
                "completions": {}
            }
        
        habit = self.habits[habit_name]
        habit["completions"][date] = completed
        habit["total_days"] += 1
        
        if completed:
            habit["streak"] += 1
        else:
            habit["streak"] = 0
        
        return {
            "habit": habit_name,
            "streak": habit["streak"],
            "completion_rate": sum(habit["completions"].values()) / len(habit["completions"]) * 100,
            "status": "completed",
            "message": f"Habit '{habit_name}' updated"
        }
    
    async def _set_goal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a new personal or professional goal"""
        title = params.get("title", "New Goal")
        description = params.get("description", "")
        category = params.get("category", "personal")
        target_date = params.get("target_date")
        
        if isinstance(target_date, str):
            try:
                target_date = datetime.fromisoformat(target_date)
            except:
                target_date = datetime.now() + timedelta(days=30)
        
        goal = Goal(
            id=f"goal_{datetime.now().isoformat()}",
            title=title,
            description=description,
            category=category,
            target_date=target_date,
            created_at=datetime.now()
        )
        
        self.goals.append(goal)
        
        return {
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category,
                "target_date": goal.target_date.isoformat()
            },
            "status": "completed",
            "message": f"Goal '{title}' set successfully"
        }
    
    async def _get_schedule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get schedule for specified timeframe"""
        timeframe = params.get("timeframe", "today")
        
        if timeframe == "today":
            start_date = datetime.now().date()
            end_date = start_date
        elif timeframe == "week":
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=7)
        else:
            start_date = datetime.now().date()
            end_date = start_date
        
        relevant_items = [
            {
                "id": item.id,
                "title": item.title,
                "start": item.start_time.isoformat(),
                "end": item.end_time.isoformat(),
                "category": item.category
            }
            for item in self.schedule_items
            if start_date <= item.start_time.date() <= end_date
        ]
        
        return {
            "schedule": relevant_items,
            "timeframe": timeframe,
            "total_items": len(relevant_items),
            "status": "completed"
        }
    
    async def _analyze_productivity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze productivity patterns and suggest improvements"""
        timeframe = params.get("timeframe", "week")
        
        # Mock productivity analysis
        analysis = {
            "peak_hours": ["09:00-11:00", "14:00-16:00"],
            "productivity_score": 78,
            "focus_sessions": 12,
            "interruptions": 8,
            "recommendations": [
                "Block calendar during peak hours (9-11 AM)",
                "Use Pomodoro technique for better focus",
                "Reduce notification checking to hourly",
                "Schedule breaks every 90 minutes"
            ],
            "weekly_pattern": {
                "monday": 85,
                "tuesday": 92,
                "wednesday": 73,
                "thursday": 81,
                "friday": 69
            }
        }
        
        return {
            "analysis": analysis,
            "status": "completed",
            "message": "Productivity analysis completed"
        }
    
    async def _wellness_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform wellness check and provide recommendations"""
        check_type = params.get("type", "general")
        
        wellness_tips = {
            "general": [
                "Take a 5-minute break every hour",
                "Stay hydrated - aim for 8 glasses of water",
                "Do some desk stretches",
                "Practice deep breathing for stress relief"
            ],
            "stress": [
                "Try a 2-minute meditation",
                "Go for a short walk",
                "Practice progressive muscle relaxation",
                "Listen to calming music"
            ],
            "energy": [
                "Take a power nap (15-20 minutes)",
                "Have a healthy snack",
                "Do some light exercise",
                "Ensure good lighting in workspace"
            ]
        }
        
        tips = wellness_tips.get(check_type, wellness_tips["general"])
        
        return {
            "wellness_check": {
                "type": check_type,
                "recommendations": tips,
                "next_check": (datetime.now() + timedelta(hours=2)).isoformat()
            },
            "status": "completed",
            "message": "Wellness check completed"
        }
    
    async def _general_life_management(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general life management tasks"""
        content = params.get("content", "")
        
        return {
            "result": f"Life management task processed: {content}",
            "suggestions": [
                "Consider using time-blocking for better schedule management",
                "Set SMART goals for better achievement tracking",
                "Use the 2-minute rule for quick tasks"
            ],
            "status": "completed"
        }

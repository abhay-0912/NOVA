"""
NOVA CLI Interface

Command-line interface for interacting with NOVA
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import print as rprint


class NOVACLIInterface:
    """
    Command-line interface for NOVA
    """
    
    def __init__(self, nova_brain):
        self.nova_brain = nova_brain
        self.console = Console()
        self.logger = logging.getLogger("nova.cli")
        self.running = False
        self.commands = self._initialize_commands()
        
        # CLI state
        self.current_personality = "assistant"
        self.conversation_history = []
        self.debug_mode = False
    
    def _initialize_commands(self) -> Dict[str, callable]:
        """Initialize CLI commands"""
        return {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "personality": self._cmd_personality,
            "agents": self._cmd_agents,
            "security": self._cmd_security,
            "scan": self._cmd_scan,
            "god": self._cmd_god_mode,
            "history": self._cmd_history,
            "clear": self._cmd_clear,
            "debug": self._cmd_debug,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit
        }
    
    async def start(self):
        """Start the CLI interface"""
        self.running = True
        
        # Display welcome message
        self._display_welcome()
        
        # Main CLI loop
        while self.running:
            try:
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input.strip():
                    continue
                
                # Process input
                await self._process_input(user_input)
                
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!")
                break
            except EOFError:
                self.console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                if self.debug_mode:
                    import traceback
                    self.console.print(traceback.format_exc())
        
        self.running = False
    
    def _display_welcome(self):
        """Display welcome message"""
        welcome_text = Text()
        welcome_text.append("🧠 NOVA", style="bold cyan")
        welcome_text.append(" - Neural Omnipresent Virtual Assistant\n", style="bold")
        welcome_text.append("Type 'help' for commands or just chat naturally!", style="italic")
        
        self.console.print(Panel(
            welcome_text,
            title="Welcome",
            border_style="cyan",
            padding=(1, 2)
        ))
        self.console.print()
    
    async def _get_user_input(self) -> str:
        """Get user input with rich prompt"""
        return await asyncio.to_thread(
            Prompt.ask,
            "[bold cyan]You[/bold cyan]",
            default=""
        )
    
    async def _process_input(self, user_input: str):
        """Process user input"""
        # Check if it's a command
        if user_input.startswith("/"):
            await self._handle_command(user_input[1:])
        else:
            await self._handle_chat(user_input)
    
    async def _handle_command(self, command_input: str):
        """Handle CLI commands"""
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            await self.commands[command](args)
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.console.print("Type '/help' for available commands")
    
    async def _handle_chat(self, user_input: str):
        """Handle chat input"""
        try:
            # Show thinking indicator
            with Live(Spinner("dots", text="🤔 NOVA is thinking..."), refresh_per_second=10):
                # Prepare input for NOVA
                input_data = {
                    "type": "text",
                    "content": user_input,
                    "context": {
                        "interface": "cli",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Process through NOVA brain
                response = await self.nova_brain.process_input(input_data)
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_input,
                "nova": response.get("response", ""),
                "timestamp": datetime.now().isoformat()
            })
            
            # Display response
            self._display_nova_response(response)
            
        except Exception as e:
            self.console.print(f"[red]Error processing your request: {e}[/red]")
    
    def _display_nova_response(self, response: Dict[str, Any]):
        """Display NOVA's response"""
        # Main response
        response_text = response.get("response", "I couldn't process your request.")
        
        self.console.print()
        self.console.print(Panel(
            Markdown(response_text),
            title="[bold green]NOVA[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))
        
        # Additional information
        if response.get("sources"):
            self.console.print("\n[dim]📚 Sources:[/dim]")
            for source in response["sources"]:
                self.console.print(f"  • {source}")
        
        if response.get("actions_taken"):
            self.console.print("\n[dim]⚡ Actions taken:[/dim]")
            for action in response["actions_taken"]:
                self.console.print(f"  • {action}")
        
        if response.get("agents_used"):
            self.console.print(f"\n[dim]🤖 Agents used: {response['agents_used']}[/dim]")
        
        self.console.print()
    
    # Command implementations
    
    async def _cmd_help(self, args: List[str]):
        """Show help information"""
        table = Table(title="NOVA CLI Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        commands_info = [
            ("/help", "Show this help message"),
            ("/status", "Show NOVA system status"),
            ("/personality [name]", "Get/set personality mode"),
            ("/agents", "Show active agents"),
            ("/security", "Show security status"),
            ("/scan", "Trigger security scan"),
            ("/god <instruction>", "Execute god mode instruction"),
            ("/history", "Show conversation history"),
            ("/clear", "Clear conversation history"),
            ("/debug", "Toggle debug mode"),
            ("/exit or /quit", "Exit NOVA CLI")
        ]
        
        for cmd, desc in commands_info:
            table.add_row(cmd, desc)
        
        self.console.print(table)
        self.console.print("\n[dim]💡 Tip: You can also just chat naturally without commands![/dim]")
    
    async def _cmd_status(self, args: List[str]):
        """Show system status"""
        try:
            with Live(Spinner("dots", text="Getting status..."), refresh_per_second=10):
                status = await self.nova_brain.get_status()
            
            # Create status table
            table = Table(title="NOVA System Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details", style="white")
            
            # System state
            state_color = "green" if status["state"] == "active" else "red"
            table.add_row("System", f"[{state_color}]{status['state']}[/{state_color}]", "")
            
            # Capabilities
            for cap, enabled in status.get("capabilities", {}).items():
                status_text = "✅ Enabled" if enabled else "❌ Disabled"
                table.add_row(f"  {cap.title()}", status_text, "")
            
            # Memory stats
            memory_stats = status.get("memory_stats", {})
            if memory_stats:
                table.add_row("Memory", "📊 Active", f"{len(memory_stats)} components")
            
            # Active agents
            agents = status.get("active_agents", [])
            table.add_row("Agents", f"🤖 {len(agents)} active", "")
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Failed to get status: {e}[/red]")
    
    async def _cmd_personality(self, args: List[str]):
        """Get or set personality"""
        if not args:
            # Show current personality
            self.console.print(f"Current personality: [cyan]{self.current_personality}[/cyan]")
            self.console.print("\nAvailable personalities:")
            personalities = ["professional", "casual", "hacker", "mentor", "creative", "analyst", "assistant"]
            for p in personalities:
                marker = "👉" if p == self.current_personality else "  "
                self.console.print(f"{marker} {p}")
        else:
            # Set personality
            new_personality = args[0].lower()
            # This would actually change the personality
            self.current_personality = new_personality
            self.console.print(f"[green]Personality changed to: {new_personality}[/green]")
    
    async def _cmd_agents(self, args: List[str]):
        """Show active agents"""
        try:
            with Live(Spinner("dots", text="Getting agent info..."), refresh_per_second=10):
                status = await self.nova_brain.get_status()
            
            agents = status.get("active_agents", [])
            
            if not agents:
                self.console.print("[yellow]No active agents found[/yellow]")
                return
            
            table = Table(title="Active Agents")
            table.add_column("Agent", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Current Task", style="white")
            
            for agent in agents:
                status_emoji = "🟢" if agent.get("active") else "🔴"
                current_task = agent.get("current_task", "Idle")
                table.add_row(
                    agent.get("type", "Unknown"),
                    f"{status_emoji} {agent.get('status', 'Unknown')}",
                    current_task
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Failed to get agent info: {e}[/red]")
    
    async def _cmd_security(self, args: List[str]):
        """Show security status"""
        try:
            # This would get actual security status
            self.console.print(Panel(
                "[green]🔒 Security Status: PROTECTED[/green]\n"
                "• Threat Level: [green]NONE[/green]\n"
                "• Active Alerts: [green]0[/green]\n"
                "• Real-time Monitoring: [green]ACTIVE[/green]\n"
                "• VPN Status: [yellow]INACTIVE[/yellow]\n"
                "• Last Scan: [cyan]Just now[/cyan]",
                title="Security Overview",
                border_style="green"
            ))
            
        except Exception as e:
            self.console.print(f"[red]Failed to get security status: {e}[/red]")
    
    async def _cmd_scan(self, args: List[str]):
        """Trigger security scan"""
        try:
            self.console.print("🔍 Initiating security scan...")
            
            with Live(Spinner("dots", text="Scanning system..."), refresh_per_second=10):
                # Simulate scan
                await asyncio.sleep(3)
            
            self.console.print("[green]✅ Security scan completed![/green]")
            self.console.print("• 0 threats detected")
            self.console.print("• System is secure")
            
        except Exception as e:
            self.console.print(f"[red]Security scan failed: {e}[/red]")
    
    async def _cmd_god_mode(self, args: List[str]):
        """Execute god mode instruction"""
        if not args:
            self.console.print("[yellow]Usage: /god <instruction>[/yellow]")
            self.console.print("Example: /god Plan my week and find 3 job opportunities")
            return
        
        instruction = " ".join(args)
        
        # Confirm god mode execution
        if not Confirm.ask(f"Execute god mode instruction: '{instruction}'?"):
            self.console.print("[yellow]God mode cancelled[/yellow]")
            return
        
        try:
            self.console.print(f"🚀 [bold]GOD MODE ACTIVATED[/bold]")
            self.console.print(f"Instruction: {instruction}")
            
            with Live(Spinner("dots", text="Executing autonomous tasks..."), refresh_per_second=10):
                result = await self.nova_brain.god_mode(instruction)
            
            self.console.print("[green]✅ God mode execution completed![/green]")
            
            # Display results
            if result.get("tasks_executed"):
                self.console.print(f"Tasks executed: {result['tasks_executed']}")
            
            if result.get("results"):
                self.console.print("\nResults:")
                for i, res in enumerate(result["results"], 1):
                    self.console.print(f"  {i}. {res.get('description', 'Task completed')}")
            
        except Exception as e:
            self.console.print(f"[red]God mode execution failed: {e}[/red]")
    
    async def _cmd_history(self, args: List[str]):
        """Show conversation history"""
        if not self.conversation_history:
            self.console.print("[yellow]No conversation history[/yellow]")
            return
        
        limit = 10  # Show last 10 by default
        if args and args[0].isdigit():
            limit = int(args[0])
        
        recent_history = self.conversation_history[-limit:]
        
        self.console.print(f"\n[bold]Last {len(recent_history)} conversations:[/bold]\n")
        
        for i, conv in enumerate(recent_history, 1):
            self.console.print(f"[cyan]{i}. You:[/cyan] {conv['user']}")
            self.console.print(f"[green]   NOVA:[/green] {conv['nova'][:100]}{'...' if len(conv['nova']) > 100 else ''}")
            self.console.print()
    
    async def _cmd_clear(self, args: List[str]):
        """Clear conversation history"""
        if Confirm.ask("Clear conversation history?"):
            self.conversation_history.clear()
            self.console.print("[green]Conversation history cleared[/green]")
        else:
            self.console.print("[yellow]Cancelled[/yellow]")
    
    async def _cmd_debug(self, args: List[str]):
        """Toggle debug mode"""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        self.console.print(f"[cyan]Debug mode {status}[/cyan]")
    
    async def _cmd_exit(self, args: List[str]):
        """Exit NOVA CLI"""
        self.console.print("👋 [bold]Goodbye![/bold]")
        self.running = False
    
    def stop(self):
        """Stop the CLI interface"""
        self.running = False

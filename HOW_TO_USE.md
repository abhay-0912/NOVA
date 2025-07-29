# 🚀 How to Use NOVA - Your Personal AI Assistant

*A beginner-friendly guide to getting started with NOVA*

---

## 📋 Table of Contents
- [What is NOVA?](#what-is-nova)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Tips & Tricks](#tips--tricks)

---

## 🤔 What is NOVA?

NOVA is your **personal AI assistant** that can:
- 💬 **Chat with you** like a smart friend
- 🔍 **Research anything** for you on the internet
- 💻 **Help with coding** and technical tasks
- 🛡️ **Protect your computer** from threats
- 📊 **Analyze data** and create reports
- 🎨 **Create content** like designs and writing
- 📅 **Manage your schedule** and remind you of tasks
- 💰 **Track your finances** and expenses

Think of NOVA as having **8 different expert assistants** working together to help you!

---

## ⚡ Quick Start (5 Minutes)

### 🪟 **For Windows Users (PowerShell):**
```powershell
# Download NOVA (if you haven't already)
git clone https://github.com/abhay-0912/NOVA.git
cd NOVA

# Install everything automatically
.\scripts\install.bat

# Start NOVA
.\scripts\start.bat
```

### 🐧 **For Mac/Linux Users:**
```bash
# Download NOVA (if you haven't already)
git clone https://github.com/abhay-0912/NOVA.git
cd NOVA

# Install everything automatically
./scripts/install.sh

# Start NOVA
./scripts/start.sh
```

### Step 3: Verify Installation ✅
Test that NOVA is working correctly:
```bash
# Quick installation check
python check_installation.py

# Test basic functionality
python main.py --help

# Test God Mode (should see "✅ Result" at the end)
python main.py --god-mode "Hello NOVA! Test your functionality."
```

**Expected output:** You should see NOVA start up (possibly with some warnings - this is normal) and then execute your command successfully.

### Step 4: Say Hello! 👋
Once NOVA starts, you'll see a friendly interface. Try typing:
```
Hello NOVA! Can you introduce yourself?
```

**That's it!** NOVA is now running and ready to help you.

---

## 🎯 Basic Usage

### 💬 How to Talk to NOVA

NOVA understands natural language - just talk to it like you would a friend!

#### **Simple Commands:**
```
"What's the weather like today?"
"Help me write an email to my boss"
"Find me information about Python programming"
"Set a reminder for 3 PM to call mom"
```

#### **God Mode (Advanced Control):**
For more powerful commands, use God Mode:
```bash
# Method 1: God Mode flag
python main.py --god-mode "analyze my computer's security"
python main.py --god-mode "create a budget tracker"

# Method 2: God Mode (full hyper-intelligent capabilities)
python main.py --mode=god
```

### 🎭 Choose Your Assistant's Personality

NOVA has different personalities for different tasks:

- **🤖 Professional**: For work and business tasks
- **� Casual**: For relaxed, fun interactions
- **🔐 Hacker**: For cybersecurity and technical tasks
- **🎓 Mentor**: For learning and explanations
- **🎨 Creative**: For artistic and design work
- **🧠 Analyst**: For data and research
- **🤵 Assistant**: Default helpful assistant mode

**How to switch:**
```
"Switch to creative personality"
"I need help with hacker tasks"
"Can you be more analytical?"
"Change to professional mode"
```

Or use command line:
```bash
python main.py --personality=creative
python main.py --personality=hacker
python main.py --personality=analyst
```

### 📱 Different Ways to Use NOVA

#### 1. **Chat Mode** (Easiest)
```bash
python main.py
# Then just type your questions!
```

#### 2. **Web Interface** (Pretty)
```bash
python main.py --mode=web
# Open http://localhost:8000 in your browser
```

#### 3. **API Mode** (For Developers)
```bash
python main.py --mode=api
# Access via http://localhost:8000/docs
```

---

## 🌟 Advanced Features

### 🔍 Research Agent
Ask NOVA to research anything for you:
```
"Research the latest trends in artificial intelligence"
"Find me the best laptops under $1000"
"Summarize this research paper: [paste URL]"
```

### 💻 Developer Agent
Get coding help:
```
"Write a Python script to organize my photos"
"Debug this code: [paste your code]"
"Create a simple website for my small business"
```

### 🛡️ Security Agent
Protect your computer:
```
"Scan my computer for threats"
"Check if this website is safe: example.com"
"Monitor my network for suspicious activity"
```

### 📊 Data Analyst Agent
Analyze your data:
```
"Analyze my expenses from last month"
"Create a chart showing my productivity trends"
"Find patterns in this dataset: [upload file]"
```

### 🎨 Creative Agent
Get creative help:
```
"Design a logo for my coffee shop"
"Write a poem about friendship"
"Create a color scheme for my website"
```

### 📅 Life Manager Agent
Organize your life:
```
"Add a meeting tomorrow at 2 PM"
"What's on my schedule today?"
"Create a to-do list for my vacation planning"
```

### 💰 Finance Agent
Manage your money:
```
"Track my grocery expenses"
"Analyze my spending habits"
"Create a budget for next month"
```

### 🎓 AI Instructor Agent
Learn new things:
```
"Teach me the basics of photography"
"Quiz me on Spanish vocabulary"
"Explain quantum physics in simple terms"
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### ❌ "NOVA won't start"
**Solution:**
```bash
# Check if Python is installed
python --version

# Reinstall dependencies
./scripts/install.sh    # On Mac/Linux
./scripts/install.bat   # On Windows

# For Windows PowerShell:
.\scripts\install.bat
```

#### ❌ "Can't connect to the internet"
**Solution:**
```bash
# Check your internet connection
ping google.com

# Restart NOVA
./scripts/start.sh      # On Mac/Linux
./scripts/start.bat     # On Windows

# For Windows PowerShell:
.\scripts\start.bat
```

#### ❌ "NOVA is running slow"
**Solutions:**
- Close other heavy programs
- Restart NOVA: `Ctrl+C` then restart using your platform's script:
  - Mac/Linux: `./scripts/start.sh`
  - Windows: `.\scripts\start.bat`
- Use lighter models: `python main.py` (uses default settings)

#### ❌ "Can't understand my commands"
**Tips:**
- Be more specific: Instead of "help me", try "help me write an email"
- Use simple language
- Try rephrasing your request

#### ⚠️ Common Warnings (Normal - You Can Ignore These)
**These warnings are normal and NOVA will still work perfectly:**

- `ChromaDB not available, using fallback memory system` - Using simpler memory, still functional
- `Next-gen capabilities not available` - Advanced features not loaded, basic features work fine
- `Security alert: Port X is open` - Security monitoring is working as intended

**Solution:** These are informational warnings. NOVA functions normally with fallback systems.

#### ❌ "ModuleNotFoundError: No module named 'yaml'" **[FIXED]**
**Solution:**
```bash
# Install missing dependencies
pip install pyyaml numpy

# Or reinstall everything
.\scripts\install.bat    # Windows
./scripts/install.sh     # Mac/Linux
```

#### ❌ "ChromaDB configuration errors" **[FIXED]**
**Solution:** This has been automatically fixed in the latest version. NOVA now uses the updated ChromaDB API.

### 🆘 Getting Help

If you're stuck:

1. **Check the logs:**
   ```bash
   # Linux/Mac
   cat logs/nova.log
   
   # Windows PowerShell
   Get-Content logs/nova.log
   ```

2. **Ask NOVA itself:**
   ```
   "NOVA, I'm having trouble with [describe problem]"
   ```

3. **Community Support:**
   - GitHub Issues: [Report a bug](https://github.com/abhay-0912/NOVA/issues)
   - Documentation: Check `docs/` folder

---

## 💡 Tips & Tricks

### 🚀 Pro Tips

1. **Be Specific**: Instead of "help me work", try "help me write a presentation about climate change"

2. **Use Context**: NOVA remembers your conversation, so you can say "make it shorter" after asking for a summary

3. **Combine Agents**: "Research Python tutorials and then help me practice coding"

4. **Set Preferences**: "Remember that I prefer casual communication style"

5. **Use Templates**: "Create a weekly report template for my team"

### 🎯 Power User Commands

```bash
# God Mode (full hyper-intelligent capabilities)
python main.py --mode=god

# API server mode
python main.py --mode=api --host=0.0.0.0 --port=8000

# Web interface mode
python main.py --mode=web

# Daemon mode (background service)
python main.py --mode=daemon

# Debug mode with specific personality
python main.py --debug --personality=hacker

# Execute single God Mode command
python main.py --god-mode "system status check"
```

### 📚 Example Workflows

#### **Daily Productivity:**
```
1. "What's on my schedule today?"
2. "Check for any security threats"
3. "Summarize my unread emails"
4. "Create a priority task list"
```

#### **Research Project:**
```
1. "Research the topic: sustainable energy"
2. "Create an outline for a 10-page report"
3. "Find relevant statistics and data"
4. "Write the introduction section"
```

#### **Creative Work:**
```
1. "Brainstorm ideas for a mobile app"
2. "Design a user interface mockup"
3. "Write marketing copy for the app"
4. "Create a project timeline"
```

---

## 🎉 You're Ready!

Congratulations! You now know how to use NOVA effectively. Remember:

- 💬 **Just talk naturally** - NOVA understands everyday language
- 🎭 **Switch personalities** based on your needs
- 🔍 **Ask for help** when you're stuck
- 🚀 **Experiment** with different commands and features

**Need more help?** Just ask NOVA: *"How do I [what you want to do]?"*

---

## 📞 Quick Reference Card

| Want to... | Say this... |
|------------|-------------|
| **Research something** | "Research [topic] for me" |
| **Get coding help** | "Help me code [what you want]" |
| **Check security** | "Scan for threats" |
| **Organize tasks** | "Create a to-do list for [project]" |
| **Analyze data** | "Analyze this data: [description]" |
| **Create content** | "Create [what you want]" |
| **Learn something** | "Teach me about [topic]" |
| **Manage money** | "Track my [expense type]" |
| **Change personality** | "Switch to [personality] mode" |
| **Get help** | "Help me with [specific problem]" |

---

*Happy exploring with NOVA! 🚀*

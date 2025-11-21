---
title: "Bird-PAM Capstone: Cross-Environment Workflow Guide"
author: SUNY-Poly-Mark
date: 2025-01-19
---

# 🔄 Cross-Environment Workflow Guide
## Maintaining Consistency Between VS Code and GitHub Copilot Chat

**Version:** 1.0  
**Last Updated:** 2025-01-19  
**Project:** Bird-PAM Capstone

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [The Challenge](#the-challenge)
3. [Core Principles](#core-principles)
4. [Recommended Workflow](#recommended-workflow)
5. [Environment-Specific Tips](#environment-specific-tips)
6. [Quick Reference Guide](#quick-reference-guide)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

This guide provides a systematic approach to maintaining project consistency when working across multiple development environments:
- **VS Code** with GitHub Copilot extension (local development)
- **GitHub.com** with Copilot Chat (browser-based)

### Why This Matters
- Different Copilot instances don't share conversation history
- Context must be explicitly maintained across sessions
- Consistency prevents duplicate work and confusion

---

## 🤔 The Challenge

### What Happens Without a System:
❌ Copilot in VS Code doesn't know what you discussed in the browser  
❌ You repeat context explanations every session  
❌ Different environments make conflicting decisions  
❌ You forget what you were working on between sessions  
❌ Code changes aren't synchronized with conversation context  

### What We're Solving:
✅ Seamless context transfer between environments  
✅ Consistent development approach regardless of where you work  
✅ Clear progress tracking across sessions  
✅ Single source of truth for project state  

---

## 💡 Core Principles

### 1. **Issues Are Your North Star** ⭐
- All work is tied to a GitHub issue
- Issues #1-#7 contain detailed requirements
- Reference issues in commits, PRs, and conversations
- Both VS Code and browser Copilot can access issues

### 2. **Git Commits Are Your Timeline** 📚
- Commit frequently with descriptive messages
- Always reference issue numbers: `#1`, `#2`, etc.
- Commits create a traceable history both Copilots can read

### 3. **Documentation Is Your Memory** 🧠
- `docs/PROJECT_CONTEXT.md` - Current project state
- Issue comments - Session progress updates
- File headers - Context for individual modules

### 4. **Consistency Through Standardization** 🎯
- Use the same prompts across environments
- Follow the same commit message format
- Update documentation at the same checkpoints

---

## 🚀 Recommended Workflow

### Phase 1: Starting a Work Session

#### Step 1.1: Pull Latest Changes
```bash
cd ~/bird-pam-capstone
git pull origin main  # or develop
```

#### Step 1.2: Review Project Context
Read these three things:
1. **Issue you're working on** - https://github.com/SUNY-Poly-Mark/bird-pam-capstone/issues
2. **PROJECT_CONTEXT.md** - Check "Recent Activity" section
3. **Last commit** - `git log --oneline -3`

#### Step 1.3: Set Context with Copilot
Use this standard prompt:

**In VS Code:**
```
I'm working on the Bird-PAM capstone project (SUNY-Poly-Mark/bird-pam-capstone).
Currently implementing Issue #[NUMBER]: [TITLE].
Last session I [what you did]. Now I need to [what's next].
Review docs/PROJECT_CONTEXT.md for full context.
```

**In Browser:**
```
Continuing Bird-PAM capstone work on Issue #[NUMBER].
Show me recent commits related to this issue and help me continue.
Check docs/PROJECT_CONTEXT.md for project state.
```

---

### Phase 2: During Development

#### Step 2.1: Commit Frequently
```bash
# Make changes
git add src/data/audio_utils.py

# Commit with issue reference
git commit -m "Add windowing function for 5-second clips #1"

# Push to remote
git push origin main
```

**Commit Message Format:**
```
<verb> <what you did> #<issue-number>

Examples:
- "Implement audio windowing logic #1"
- "Add unit tests for windowing #1"
- "Fix padding bug in audio loader #1"
```

#### Step 2.2: Update Context Documents
Every 1-2 hours or at natural breakpoints:

1. **Update PROJECT_CONTEXT.md:**
   ```markdown
   ### 2025-01-19 Afternoon Session
   - ✅ Implemented windowing function in src/data/audio_utils.py
   - ✅ Added unit tests with pytest
   - 🔄 Working on: Handling edge cases for very short clips
   - 📝 Next: Test with real audio files from dataset
   ```

2. **Add Issue Comment:**
   Go to the issue on GitHub and add:
   ```markdown
   **Progress Update:**
   - Implemented core windowing function
   - Added tests for normal cases
   - Still need to handle clips shorter than 5 seconds
   
   **Next session:** Test with real data and handle edge cases
   ```

#### Step 2.3: Use Descriptive File Headers
Add context at the top of new files:

```python
"""
Audio Windowing Utilities - Issue #1
Project: Bird-PAM Capstone
Author: SUNY-Poly-Mark
Created: 2025-01-19

Purpose:
    Extract fixed-length windows from variable-length audio clips.
    Handles padding, truncation, and overlapping windows.

Key Functions:
    - load_audio_file(): Load audio with librosa
    - extract_windows(): Create fixed-length segments
    - pad_or_truncate(): Handle length mismatches

Configuration:
    See conf/config.yaml for window_seconds, sample_rate, hop_seconds

Related:
    - Issue #1: https://github.com/SUNY-Poly-Mark/bird-pam-capstone/issues/1
    - Config: conf/config.yaml
    - Tests: tests/test_audio_utils.py
"""
```

---

### Phase 3: Ending a Work Session

#### Step 3.1: Commit All Work
```bash
# Check for uncommitted changes
git status

# Add and commit everything
git add .
git commit -m "Complete windowing implementation with tests #1"
git push origin main
```

#### Step 3.2: Update Documentation

1. **Update PROJECT_CONTEXT.md:**
   - Move completed tasks from "In Progress" to "Completed"
   - Update "Recent Activity" with today's work
   - Note any blockers or questions in "Session Notes"

2. **Add Final Issue Comment:**
   ```markdown
   **End of session update:**
   
   Completed:
   - ✅ Windowing function fully implemented
   - ✅ Unit tests passing
   - ✅ Handles edge cases (short clips, padding)
   
   Status: Issue #1 is ~80% complete
   
   Next session TODO:
   - [ ] Test with real audio files from dataset
   - [ ] Profile performance for large batches
   - [ ] Update documentation in README
   ```

#### Step 3.3: Create Checkpoint Commit
```bash
# Tag your progress
git tag -a session-2025-01-19 -m "Completed windowing implementation"
git push origin session-2025-01-19
```

---

### Phase 4: Switching Environments

#### Scenario A: From VS Code → Browser

**Before leaving VS Code:**
1. Commit and push all changes
2. Add issue comment with progress
3. Update PROJECT_CONTEXT.md

**Starting in Browser:**
1. Pull latest changes (if working locally too)
2. Read your issue comment
3. Tell Copilot:
   ```
   I was working on Issue #1 in VS Code. Check my last commit
   and the issue comments. I implemented windowing and now need
   to add integration tests. Let's continue from there.
   ```

#### Scenario B: From Browser → VS Code

**Before leaving Browser:**
1. Ensure all changes are committed to GitHub
2. Add issue comment summarizing work
3. Note what to do next

**Starting in VS Code:**
1. `git pull origin main`
2. Read PROJECT_CONTEXT.md
3. Tell Copilot:
   ```
   I was working on Issue #1 in the browser. Pull up my last
   commit and help me continue with integration testing.
   ```

---

## 🛠️ Environment-Specific Tips

### VS Code with GitHub Copilot

#### Advantages:
- Full IDE features (debugging, testing, linting)
- Direct file system access
- Better for writing lots of code
- Copilot sees your entire workspace

#### Best Practices:
```
✅ Use for: Heavy coding, debugging, local testing
✅ Reference: "@workspace" for file context
✅ Leverage: Copilot Chat sidebar for inline help
✅ Command: "Explain this file" for quick context
```

#### Standard Prompts:
```
# Starting work
"Review Issue #[N] and show me relevant files in @workspace"

# Getting help
"How should I implement [feature] according to Issue #[N]?"

# Code review
"Review my changes in @workspace for Issue #[N]"
```

---

### GitHub Copilot Chat (Browser)

#### Advantages:
- Direct GitHub integration
- Can see PRs, issues, commits immediately
- No local setup needed
- Great for planning and design discussions

#### Best Practices:
```
✅ Use for: Planning, design discussions, reviewing PRs
✅ Reference: Specific URLs to issues, commits, files
✅ Leverage: Natural language for repository queries
✅ Command: "Show me changes in the last commit"
```

#### Standard Prompts:
```
# Starting work
"Show me Issue #[N] and recent commits related to it"

# Getting context
"What files were modified for Issue #[N]?"

# Planning
"Help me plan the implementation for Issue #[N]"
```

---

## 📋 Quick Reference Guide

### Daily Workflow Checklist

**🌅 Starting Your Day:**
- [ ] `git pull origin main`
- [ ] Read PROJECT_CONTEXT.md "Recent Activity"
- [ ] Check your current issue on GitHub
- [ ] Review last commit: `git log -1`
- [ ] Tell Copilot where you left off

**🔄 During Work:**
- [ ] Commit every meaningful change
- [ ] Use issue references in commits: `#1`
- [ ] Update PROJECT_CONTEXT.md every 1-2 hours
- [ ] Add file headers to new files

**🌙 End of Day:**
- [ ] Commit and push all changes
- [ ] Update PROJECT_CONTEXT.md
- [ ] Add progress comment on issue
- [ ] Note next steps for tomorrow

---

### Commit Message Templates

```bash
# Feature implementation
git commit -m "Implement [feature] for [purpose] #[issue]"

# Bug fix
git commit -m "Fix [bug] in [component] #[issue]"

# Tests
git commit -m "Add tests for [feature] #[issue]"

# Documentation
git commit -m "Update docs for [feature] #[issue]"

# Refactoring
git commit -m "Refactor [component] for better [quality] #[issue]"
```

---

### Standard Copilot Prompts

#### Context Setting:
```
"I'm working on Issue #[N] of SUNY-Poly-Mark/bird-pam-capstone.
Review docs/PROJECT_CONTEXT.md and help me continue."
```

#### Getting Help:
```
"Show me the current implementation of [feature] and suggest improvements."
```

#### Code Review:
```
"Review my changes for Issue #[N]. Do they match the acceptance criteria?"
```

#### Planning:
```
"Help me break down Issue #[N] into smaller tasks."
```

---

## 🐛 Troubleshooting

### Problem: Copilot doesn't understand project context

**Solution:**
1. Explicitly reference PROJECT_CONTEXT.md in your prompt
2. Provide the issue URL directly
3. Copy key details from the issue into your prompt

**Example:**
```
I'm working on Bird-PAM audio windowing (Issue #1):
https://github.com/SUNY-Poly-Mark/bird-pam-capstone/issues/1

The goal is to create 5-second windows with 2.5-second overlap.
Show me how to implement this in src/data/audio_utils.py
```

---

### Problem: Lost track of what you were doing

**Solution:**
1. Check PROJECT_CONTEXT.md "Recent Activity"
2. Read your last issue comment
3. Run `git log --oneline -5` to see recent commits
4. Check the issue task checklist

---

### Problem: Different Copilots give conflicting advice

**Solution:**
1. Always reference the same issue and config files
2. Show Copilot previous decisions from PROJECT_CONTEXT.md
3. Ask: "Is this consistent with the approach in [file/issue]?"

---

### Problem: Can't remember configuration details

**Solution:**
All config is in one place: `conf/config.yaml`

Standard prompt:
```
"Show me the audio processing config from conf/config.yaml
and explain how it affects my implementation."
```

---

## 🎯 Success Metrics

You're doing it right when:

✅ You can switch environments mid-task without losing context  
✅ Each Copilot session starts with clear direction  
✅ Your commits tell a clear story of progress  
✅ PROJECT_CONTEXT.md always reflects current reality  
✅ You never ask "What was I working on?"  
✅ Issue comments document your journey  

---

## 📚 Additional Resources

### Project Files:
- **PROJECT_CONTEXT.md** - Your project memory
- **Issues #1-#7** - Detailed task requirements
- **conf/config.yaml** - All configuration parameters
- **README.md** - Project overview

### Git Commands:
```bash
# See recent activity
git log --oneline --graph --decorate -10

# See changes since last session
git log --since="yesterday" --oneline

# See what files changed
git log --name-status --oneline -5

# Find commits for an issue
git log --grep="#1" --oneline
```

### GitHub CLI (Optional):
```bash
# Install: https://cli.github.com

# View issues
gh issue list

# View specific issue
gh issue view 1

# Add comment to issue
gh issue comment 1 --body "Progress update: ..."
```

---

## 🎓 Best Practices Summary

### The Golden Rules:

1. **Always reference issue numbers** in commits and conversations
2. **Update PROJECT_CONTEXT.md** at every session boundary
3. **Add progress comments** to issues when switching environments
4. **Commit frequently** with descriptive messages
5. **Use file headers** to provide context for Copilot
6. **Tell Copilot explicitly** what you did last time

### The Context Mantra:
> "Issues define what, commits show progress, documentation maintains memory"

---

## 📞 Need Help?

If you're stuck:
1. Read the relevant issue carefully
2. Check PROJECT_CONTEXT.md for decisions made
3. Review recent commits: `git log --oneline -5`
4. Look at file headers for context
5. Ask Copilot: "Help me understand the current state of Issue #[N]"

---

**Remember:** This workflow becomes natural after 2-3 sessions. The upfront structure saves hours of confusion later!

---

*Last updated: 2025-01-19*  
*Project: SUNY-Poly-Mark/bird-pam-capstone*  
*Author: SUNY-Poly-Mark*
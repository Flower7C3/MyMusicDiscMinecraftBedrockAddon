# Git Hooks Documentation

## Pre-commit Hooks

This project includes pre-commit hooks to ensure code quality before commits.

### Available Hooks

#### 1. `pre-commit` (Default)
- **Location:** `.git/hooks/pre-commit`
- **Purpose:** Checks syntax of staged Python files only
- **Behavior:** Only validates files that are staged for commit
- **Use case:** Faster validation when you only want to check changed files

#### 2. `pre-commit-all` (Alternative)
- **Location:** `.git/hooks/pre-commit-all`
- **Purpose:** Checks syntax of ALL Python files in the project
- **Behavior:** Validates every Python file, regardless of git status
- **Use case:** Comprehensive validation to ensure no syntax errors exist anywhere

### How to Use

#### Enable Default Hook (Staged Files Only)
```bash
# The default hook is already active
git add .
git commit -m "Your commit message"
# Hook will run automatically and check only staged Python files
```

#### Enable All Files Hook
```bash
# Rename the alternative hook to activate it
mv .git/hooks/pre-commit-all .git/hooks/pre-commit
# Or copy it
cp .git/hooks/pre-commit-all .git/hooks/pre-commit
```

#### Disable Hooks Temporarily
```bash
# Skip hooks for one commit
git commit --no-verify -m "Your commit message"
```

### Hook Behavior

#### Success Case
```
🔍 Checking Python syntax...
🔍 Checking syntax: ./music_disc_generator.py
✅ ./music_disc_generator.py - syntax OK
✅ All Python files have valid syntax - commit allowed
```

#### Error Case
```
🔍 Checking Python syntax...
🔍 Checking syntax: ./broken_file.py
❌ ./broken_file.py - syntax error found
  File "./broken_file.py", line 5
    print("unclosed quote
                    ^
SyntaxError: EOL while scanning string literal

❌ Commit blocked: 1 Python file(s) have syntax errors
Please fix the syntax errors before committing
```

### What the Hooks Check

- ✅ **Syntax errors** (SyntaxError, IndentationError)
- ✅ **F-string issues** (like backslashes in expressions)
- ✅ **Missing brackets/parentheses**
- ✅ **Invalid Python syntax**

### What the Hooks DON'T Check

- ❌ **Runtime errors** (only syntax)
- ❌ **Import errors** (only syntax)
- ❌ **Logic errors** (only syntax)
- ❌ **Style issues** (only syntax)

### Customization

You can modify the hooks to add additional checks:

1. **Add linting:**
   ```bash
   # Add to the hook
   if ! flake8 "$file"; then
       echo "❌ $file - linting errors"
       ERRORS_FOUND=$((ERRORS_FOUND + 1))
   fi
   ```

2. **Add type checking:**
   ```bash
   # Add to the hook
   if ! mypy "$file"; then
       echo "❌ $file - type errors"
       ERRORS_FOUND=$((ERRORS_FOUND + 1))
   fi
   ```

### Troubleshooting

#### Hook not running
```bash
# Check if hook is executable
ls -la .git/hooks/pre-commit

# Make executable if needed
chmod +x .git/hooks/pre-commit
```

#### Hook too slow
- Use the default `pre-commit` hook (staged files only)
- Exclude large directories in the find command
- Consider using `pre-commit-all` only for final commits

#### False positives
- The hooks use `python3 -m py_compile` which is very reliable
- If you get false positives, check for:
  - Hidden characters in the file
  - Encoding issues
  - Mixed tabs/spaces 
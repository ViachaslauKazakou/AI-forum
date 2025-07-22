# Pyenv Shell Integration Fix

This document provides instructions to fix the common pyenv error: `pyenv: shell integration not enabled. Run 'pyenv init' for instructions.`

## Problem Description

When pyenv is installed but not properly integrated with your shell, you'll see the warning message:
```
pyenv: shell integration not enabled. Run `pyenv init' for instructions.
```

This happens because pyenv needs to be initialized in your shell configuration files to work properly.

## Solution

### Step 1: Check Your Current Shell

First, identify which shell you're using:

```bash
echo $SHELL
```

### Step 2: Get Pyenv Initialization Instructions

Run the following command to see the specific instructions for your system:

```bash
pyenv init
```

### Step 3: Configure Your Shell

The configuration depends on your shell type:

#### For Zsh (macOS default)

Add the following lines to both `~/.zshrc` and `~/.zprofile`:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

**Quick setup commands:**

```bash
# Add to .zshrc (for interactive shells)
echo 'export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"' >> ~/.zshrc

# Add to .zprofile (for login shells)
echo 'export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"' >> ~/.zprofile
```

#### For Bash

Add the following lines to `~/.bashrc` and `~/.bash_profile`:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

**Quick setup commands:**

```bash
# Add to .bashrc (for interactive shells)
echo 'export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"' >> ~/.bashrc

# Add to .bash_profile (for login shells)
echo 'export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"' >> ~/.bash_profile
```

### Step 4: Reload Your Shell Configuration

After adding the configuration, reload your shell:

```bash
# For zsh
source ~/.zshrc

# For bash
source ~/.bashrc
```

Alternatively, open a new terminal window.

### Step 5: Verify the Fix

Test that pyenv is working properly:

```bash
pyenv version
```

You should see your current Python version without any warning messages.

## What Each Line Does

- `export PYENV_ROOT="$HOME/.pyenv"` - Sets the pyenv installation directory
- `[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"` - Adds pyenv binaries to PATH if the directory exists
- `eval "$(pyenv init -)"` - Initializes pyenv and enables shell integration

## Common Issues and Troubleshooting

### Issue: Configuration not taking effect

**Solution:** Make sure you've added the configuration to the correct files:
- For **interactive** shells: `~/.zshrc` (zsh) or `~/.bashrc` (bash)
- For **login** shells: `~/.zprofile` (zsh) or `~/.bash_profile` (bash)

### Issue: Pyenv command not found

**Solution:** Verify pyenv is installed:
```bash
ls -la ~/.pyenv
```

If not installed, install pyenv first:
```bash
# Using Homebrew (macOS)
brew install pyenv

# Using curl
curl https://pyenv.run | bash
```

### Issue: Changes not persisting across terminal sessions

**Solution:** Ensure you've added the configuration to both interactive and login shell files as shown above.

## Verification Commands

After setup, these commands should work without warnings:

```bash
# Check pyenv version
pyenv --version

# List available Python versions
pyenv install --list

# Check current Python version
pyenv version

# List installed Python versions
pyenv versions
```

## Additional Resources

- [Pyenv Official Documentation](https://github.com/pyenv/pyenv)
- [Shell Configuration Files Guide](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv)

---

## Project Context

This fix was applied to the AI-forum project to ensure proper Python version management with pyenv.

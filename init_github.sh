#!/bin/bash
# Initialize Even CS Agent for GitHub

echo "=== Preparing Even CS Agent for GitHub ==="
echo ""

# Navigate to project directory
cd ~/.openclaw/workspace/even-cs-agent

# Initialize Git repository
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo ""
echo "Adding files to Git..."
git add .

# Create initial commit
echo ""
echo "Creating initial commit..."
git commit -m "Initial commit: Even CS Agent v2.1

- Complete pipeline implementation (6 components)
- Knowledge base (5 files, ~35KB)
- Configuration system
- Testing suite (41 tests, 100% pass rate)
- Documentation (README, CONFIG, component docs)
- Learning loop (Escalation → KB injection)

Ready for production deployment."

echo ""
echo "✅ Initial commit created"

# Show status
echo ""
echo "=== Git Status ==="
git status

echo ""
echo "=== Next Steps ==="
echo "1. Create GitHub repository: https://github.com/new"
echo "2. Repository name: even-cs-agent"
echo "3. Description: Intelligent Customer Support Agent for Even Realities | Built on OpenClaw"
echo "4. Public/Private: Your choice"
echo "5. Do NOT initialize with README (we already have one)"
echo ""
echo "6. Add remote:"
echo "   git remote add origin https://github.com/alstonzhuang/even-cs-agent.git"
echo ""
echo "7. Push to GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "=== Ready to push to GitHub! ==="

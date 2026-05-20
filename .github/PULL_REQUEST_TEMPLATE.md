## Description
<!-- Describe your changes in detail here -->
<!-- If this PR fixes an issue, please link it here (e.g., "Fixes #123") -->

## Type of Change
<!-- Check the appropriate box with an "x" -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update (changes to README, docstrings, etc.)
- [ ] 🔨 Refactoring (no functional changes)

## Safety & Security Check
<!-- Since this agent executes system commands, security is critical -->
- [ ] I have ensured that my changes **do not** bypass the Safety Engine (`src/safety.py`).
- [ ] If I added new commands, I have thoroughly tested them for injection vulnerabilities.
- [ ] The `DRY_RUN` flag still accurately prevents execution when turned ON.

## Testing
<!-- Describe how you tested your changes -->
- [ ] I have added new unit tests for my feature/fix (if applicable).
- [ ] All existing tests pass (`pytest tests/`).

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation

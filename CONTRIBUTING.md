# Contributing Guidelines

## Git Workflow

### Commit Message Format
```
type(scope): description

body (optional)

footer (optional)
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(auth): add user authentication system
fix(reporting): handle missing channel error
docs: update README with setup instructions
chore: update dependencies for security patches
```

### Branch Naming
- `feat/feature-name`
- `fix/bug-description`
- `docs/documentation-update`

### Pull Request Process
1. Create feature branch from `main`
2. Make changes with conventional commits
3. Update documentation if needed
4. Create PR with clear description
5. Squash merge to maintain clean history

## Code Standards

### Language Policy
**IMPORTANT**: Use English for all code, comments, docstrings, documentation, commit messages, PR descriptions, and issue titles. This policy applies to developer-facing artifacts; user-facing content (e.g., UI strings, bot responses) may be localized as needed.


### Python
- Follow PEP 8
- Use type hints where possible
- Add docstrings for functions/classes
- Keep functions small and focused

### Discord.py
- Use proper error handling
- Implement permission checks
- Add user feedback for all commands
- Use embeds for rich responses

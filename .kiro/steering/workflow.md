# AI Workflow Guidelines

## Code Quality Standards
- ALWAYS run `make check-ci` before any commit/push
- Apply `make format` if formatting issues exist
- Never push code that fails CI syntax checks
- Use conventional commit messages (feat:, fix:, docs:, etc.)
- Run security checks for sensitive data handling
- Remove obsolete files proactively when identified

## Development Approach
- Focus on foundation completion before adding features
- Test changes locally before pushing
- Create logical, focused commits with clear messages
- Document architectural decisions in steering files

## Communication Style
- Be concise and actionable
- Provide clear next steps
- Explain reasoning behind recommendations
- Ask for clarification when requirements are unclear

## File Organization
- Keep steering rules updated as we learn
- Create specs for complex features
- Clean up obsolete files regularly
- Maintain English-only codebase policy

## Problem-Solving Process
1. Understand the problem clearly
2. Check existing architecture/patterns
3. Propose solution with reasoning
4. Implement with quality checks
5. Test and verify functionality
6. Document if needed
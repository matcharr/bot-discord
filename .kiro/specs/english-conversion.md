# English Documentation Conversion Spec

## Overview
Convert all remaining French documentation, comments, and messages to English across the Discord bot codebase to improve international collaboration and maintainability.

## Requirements

### Functional Requirements
- **FR1**: All user-facing messages must be in English
- **FR2**: All code comments must be in English  
- **FR3**: All documentation files must be in English
- **FR4**: All script output messages must be in English
- **FR5**: All error messages must be in English

### Non-Functional Requirements
- **NFR1**: Maintain existing functionality during conversion
- **NFR2**: Preserve original meaning and context
- **NFR3**: Use clear, professional English
- **NFR4**: Follow consistent terminology throughout

## Scope

### In Scope
- Script files in `scripts/` directory
- Documentation files in `docs/` directory  
- Configuration file comments
- Log messages and user output
- Error messages and warnings

### Out of Scope
- Core Python code (already in English)
- Test data content (can remain as test fixtures)
- Git commit history
- External dependencies

## Current Status

### ✅ Completed
- Core database layer (`project/database/`)
- Main management script (`scripts/db-manage.sh`)
- Environment configuration files (`.env.*`)
- Docker compose configuration
- Main TODO.md updates
- `docs/git-workflow.md` - ✅ Converted to English
- `scripts/setup-git-hooks.sh` - ✅ Converted to English
- `scripts/cleanup-branches.sh` - ✅ Converted to English
- `scripts/new-branch.sh` - ✅ Converted to English

### ✅ Recently Completed
- `scripts/verify-setup.sh` - ✅ Converted to English
- Removed `TEMP_DB_MIGRATION_PLAN.md` (temporary file with French content)

### ❌ Remaining
- Final verification scan completed - no significant French content found

## Implementation Plan

### Phase 1: Complete Script Conversion
**Target**: All scripts in `scripts/` directory
**Files**:
- `scripts/verify-setup.sh` (finish conversion)
- `scripts/setup-git-hooks.sh`
- `scripts/cleanup-branches.sh`
- `scripts/new-branch.sh`

**Tasks**:
1. Convert all French log messages to English
2. Convert all French comments to English
3. Convert all French user prompts to English
4. Update help text and usage instructions

### Phase 2: Documentation Conversion
**Target**: All documentation in `docs/` directory
**Files**:
- `docs/DATABASE.md`
- `docs/SETUP_CHECKLIST.md`
- `docs/SETUP_NO_DOCKER.md`
- `docs/README.md`
- `docs/git-workflow.md`

**Tasks**:
1. Convert all French headings to English
2. Convert all French content to English
3. Update code examples and commands
4. Maintain technical accuracy

### Phase 3: Validation & Testing
**Target**: Ensure conversion quality
**Tasks**:
1. Run conversion verification script
2. Test all scripts still function correctly
3. Verify documentation accuracy
4. Update any missed French content

## Acceptance Criteria

### Script Conversion
- [ ] All log messages display in English
- [ ] All user prompts are in English
- [ ] All help text is in English
- [ ] All error messages are in English
- [ ] Scripts maintain full functionality

### Documentation Conversion  
- [ ] All headings are in English
- [ ] All body content is in English
- [ ] All code examples work correctly
- [ ] Technical accuracy is maintained
- [ ] Consistent terminology is used

### Quality Assurance
- [ ] No French text detected by verification script
- [ ] All scripts execute without errors
- [ ] Documentation is clear and professional
- [ ] Consistent English terminology throughout

## Translation Guidelines

### Terminology Standards
- "Base de données" → "Database"
- "Avertissement" → "Warning"
- "Utilisateur" → "User"
- "Serveur" → "Server/Guild"
- "Modération" → "Moderation"
- "Sécurité" → "Security"
- "Chiffrement" → "Encryption"
- "Développement" → "Development"
- "Production" → "Production"
- "Test" → "Test"

### Message Tone
- Professional but friendly
- Clear and concise
- Consistent with existing English content
- Appropriate for developer audience

### Technical Accuracy
- Preserve all technical details
- Maintain command examples exactly
- Keep file paths and URLs unchanged
- Ensure code snippets remain functional

## Deliverables

1. **Converted Scripts**: All scripts in `scripts/` directory with English messages
2. **Converted Documentation**: All files in `docs/` directory in English
3. **Verification Report**: Confirmation that no French content remains
4. **Updated Conversion Guide**: Final status in `docs/ENGLISH_CONVERSION.md`

## Success Metrics

- **0 French strings** detected by verification script
- **100% script functionality** maintained after conversion
- **Clear documentation** that international developers can follow
- **Consistent terminology** across all files

## Dependencies

- Access to all source files
- Ability to test scripts after conversion
- French-to-English translation accuracy
- Preservation of technical functionality

## Risks & Mitigation

### Risk: Loss of Technical Accuracy
**Mitigation**: Careful review of technical terms and testing of all examples

### Risk: Breaking Script Functionality  
**Mitigation**: Test each script after conversion to ensure it still works

### Risk: Inconsistent Terminology
**Mitigation**: Use standardized terminology guide and review for consistency

## Timeline

- **Phase 1**: Script conversion - 1 session
- **Phase 2**: Documentation conversion - 1 session  
- **Phase 3**: Validation & testing - 1 session

Total estimated effort: 3 focused work sessions
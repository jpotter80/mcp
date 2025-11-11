# Phase 1 Implementation Prompt for Next Session

## Context
The MCP project is being restructured into a multi-server architecture. Phase 1 establishes the foundation: directory structure, configuration templates, and updated .gitignore.

## Current State
- Main branch is clean and up-to-date
- All planning documentation complete (RESTRUCTURING_PLAN.md, PHASE_1_QUICKSTART.md, etc.)
- Ready to implement Phase 1

## Task: Execute Phase 1

### Objective
Create directory structure, configuration templates, and .gitignore updates as foundation for all subsequent restructuring phases.

### Branch
`restructure/01-directory-structure-and-config`

### Instructions to Follow
1. Reference: `/home/james/mcp/PHASE_1_QUICKSTART.md` (Step-by-Step Instructions section)
2. Execute all steps in sequence (Steps 1-10):
   - Create feature branch
   - Create directory structure
   - Update .gitignore
   - Create configuration templates (processing_config.yaml, server_config.yaml)
   - Create requirements.txt
   - Create README.md files
   - Update .memory.md (verify it's correct)
   - Commit changes with clear message
   - Verify and push
   - Create pull request

### Key Files to Create
- `servers/mojo-manual-mcp/config/processing_config.yaml`
- `servers/mojo-manual-mcp/config/server_config.yaml`
- `servers/mojo-manual-mcp/requirements.txt`
- `shared/README.md`
- `servers/mojo-manual-mcp/README.md`

### Verification Checklist
- [ ] All directories created (use `find shared servers docs tools -type d`)
- [ ] .gitignore properly updated (excludes shared/build/, *.db, *.ducklake, etc.)
- [ ] Both YAML config files are valid (test with Python yaml.safe_load)
- [ ] requirements.txt has correct packages
- [ ] README files created with helpful content
- [ ] Git commit message is clear and references Phase 1
- [ ] Branch pushed to origin
- [ ] Ready for PR review

### Success Criteria
- All 10 steps completed successfully
- No errors during verification
- Git branch clean with single logical commit
- PR created and ready for review

### Resources
- PHASE_1_QUICKSTART.md — Step-by-step guide
- RESTRUCTURING_PLAN.md — Detailed reference
- .github/.memory.md — Project decisions

### If Issues Arise
- Refer to "Common Issues & Solutions" section in PHASE_1_QUICKSTART.md
- Check that all directories exist before creating files
- Validate YAML syntax before committing
- Ensure .gitignore syntax is correct

---

**Start with**: `git checkout -b restructure/01-directory-structure-and-config`

**Follow**: PHASE_1_QUICKSTART.md Steps 1-10 in order

**Complete when**: PR created and ready for review

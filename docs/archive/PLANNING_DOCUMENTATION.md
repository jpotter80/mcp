# MCP Multi-Server Architecture: Complete Planning Documentation

## 📋 Documents Overview

This folder contains complete planning and implementation documentation for restructuring the MCP project into a multi-server architecture.

### Quick Navigation

| Document | Purpose | Read Time | Audience |
|----------|---------|-----------|----------|
| **IMPLEMENTATION_SUMMARY.md** | High-level overview and quick reference | 5-10 min | Everyone |
| **PHASE_1_QUICKSTART.md** | Step-by-step instructions for Phase 1 | 10-15 min | Ready to implement |
| **RESTRUCTURING_PLAN.md** | Comprehensive 40+ page detailed guide | 30-45 min | Implementation leads |
| **.github/.memory.md** | Concise project memory and decisions | 3-5 min | Quick reference |

---

## 🎯 Project Goal

Transform the Mojo MCP project into a **self-contained, distributable multi-server architecture** that:
- Supports multiple documentation sources (Mojo, DuckDB, etc.)
- Can be deployed independently via GitHub
- Works with or without pixi
- Updates automatically from upstream sources
- Follows standardized naming conventions and configuration patterns

---

## ✅ What You're Getting

### 1. Comprehensive Planning (Complete)
- ✅ Architecture design refined based on your clarifications
- ✅ 8-phase implementation strategy with git branches
- ✅ All design decisions documented and ratified
- ✅ Configuration templates provided
- ✅ Naming conventions standardized

### 2. Detailed Implementation Guide (Complete)
- ✅ Phase-by-phase breakdown with code examples
- ✅ Git branch workflows
- ✅ Python code changes needed (file-by-file)
- ✅ Automation scripts (build, scaffold, sync)
- ✅ Testing and validation strategies

### 3. Supporting Documentation (Complete)
- ✅ Multi-format processor support planned
- ✅ Non-pixi user support documented
- ✅ Documentation update automation designed
- ✅ Configuration parameter reference
- ✅ Deployment workflows

### 4. Quick Start Guide (Complete)
- ✅ Phase 1 step-by-step instructions
- ✅ Directory structure to create
- ✅ Configuration template examples
- ✅ Common issues and solutions

---

## 📌 Key Decisions Ratified

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Configuration | YAML files | Human-readable, version-controllable, supports variable substitution |
| Server Code | Per-server copy | Complete independence, no shared imports at runtime |
| Build Artifacts | `/shared/build/` | Keeps workspace clean, easy to exclude from git |
| Format Support | Pluggable processors | Extensible, supports MDX + Markdown + future formats |
| Non-Pixi Support | `requirements.txt` + `pyproject.toml` | Standard Python packaging, maximum compatibility |
| Doc Updates | Script + GitHub Actions | Automated, traceable, integrates with CI/CD |
| Git Strategy | 8 phases, separate branches | Safe, reviewable, easy to rollback |

---

## 🗂️ Directory Structure (After Restructuring)

```
/home/james/mcp/                    # Development repository
├── shared/                          # Build-time infrastructure (dev-time only)
│   ├── preprocessing/               # Reusable doc processing
│   ├── embedding/                   # Reusable embeddings & indexing
│   ├── templates/                   # Code templates
│   └── build/                       # Ephemeral artifacts
│
├── source-documentation/            # Doc sources
│   ├── mojo/manual/                # Mojo manual
│   ├── duckdb/docs/                # DuckDB docs (future)
│   └── [more tools...]
│
├── servers/                         # Distributable MCP servers
│   ├── mojo-manual-mcp/            # First MCP
│   │   ├── runtime/                # Server + DB + search
│   │   ├── config/                 # YAML configs
│   │   └── requirements.txt
│   └── [more MCPs...]
│
├── docs/                           # Project documentation
├── tools/                          # Build & automation scripts
└── pixi.toml                       # Root workspace config
```

---

## 🚀 How to Use These Documents

### If You Want the Quick Overview
**→ Read: IMPLEMENTATION_SUMMARY.md** (5-10 minutes)
- High-level architecture
- What was addressed
- Next steps

### If You're Ready to Implement Phase 1
**→ Read: PHASE_1_QUICKSTART.md** (10-15 minutes, then execute)
- Step-by-step instructions
- Copy-paste ready commands
- Verification steps

### If You Need Complete Details
**→ Read: RESTRUCTURING_PLAN.md** (30-45 minutes as reference)
- All 8 phases detailed
- Code examples for each change
- Testing strategies
- Rollback procedures

### If You Need Quick Reference
**→ Read: .github/.memory.md** (3-5 minutes, bookmark it)
- Concise summary
- Architecture overview
- Key conventions
- Environment variables

---

## 📅 Implementation Timeline

### Immediate (This Week)
- [ ] Review all documents
- [ ] Ask clarifying questions if needed
- [ ] Approve to proceed with Phase 1

### Phase 1 (30-45 min)
- [ ] Create directories and config templates
- [ ] Update .gitignore
- [ ] Create PR

### Phases 2-3 (2 hours per phase)
- [ ] Multi-format processor support
- [ ] Parameterize build scripts

### Phases 4-5 (2 hours per phase)
- [ ] Move build infrastructure
- [ ] Organize Mojo server

### Phases 6-8 (1.5 hours per phase)
- [ ] Create tooling
- [ ] Update documentation
- [ ] Final testing

**Total: ~2-3 weeks with sequential phases** (or faster if parallelized)

---

## 🔄 Git Workflow

Each phase is a separate branch:

```bash
# Start Phase 1
git checkout -b restructure/01-directory-structure-and-config
# ... make changes following PHASE_1_QUICKSTART.md ...
git commit
git push
# Create PR

# After merge, start Phase 2
git checkout main
git pull
git checkout -b restructure/02-multi-format-doc-support
# ... continue ...
```

---

## 📚 What Each Phase Does

| Phase | Name | What It Does |
|-------|------|--------------|
| 1 | Directory Setup | Creates structure, config templates, .gitignore |
| 2 | Multi-Format | Adds pluggable processor factory |
| 3 | Parameterization | Adds --config CLI args to scripts |
| 4 | Move Infrastructure | Moves build code to `/shared/` |
| 5 | Organize Mojo | Creates `/servers/mojo-manual-mcp/` structure |
| 6 | Tooling | Creates helper scripts |
| 7 | Documentation | Moves docs, creates guides |
| 8 | Testing | Final validation and cleanup |

---

## 🛠️ Key Files to Create

### Phase 1 (Foundation)
- `.gitignore` — Updated
- `servers/mojo-manual-mcp/config/processing_config.yaml` — New
- `servers/mojo-manual-mcp/config/server_config.yaml` — New
- `servers/mojo-manual-mcp/requirements.txt` — New
- Various README.md files — New

### Phases 2-3 (Architecture)
- `shared/preprocessing/src/processor_factory.py` — New
- `shared/preprocessing/src/config_loader.py` — New
- `shared/preprocessing/src/markdown_processor.py` — New

### Phases 4-5 (Restructure)
- Move existing files to new locations
- Update Python imports and paths

### Phases 6-8 (Tooling & Docs)
- `tools/build_mcp.sh` — New
- `tools/scaffold_new_mcp.sh` — New
- `tools/sync_documentation.sh` — New
- `docs/QUICKSTART.md` — New
- And more documentation files

---

## ✨ Benefits After Restructuring

### For Development
- ✅ Clear separation of build infrastructure and runtime
- ✅ Easy to add new MCP servers with scaffold script
- ✅ Configuration-driven, no hardcoded paths
- ✅ Support for multiple documentation formats

### For Distribution
- ✅ Each server can be cloned/submoduled independently
- ✅ Users without pixi can still use the servers
- ✅ Minimal dependencies required
- ✅ Stand-alone servers complete and self-contained

### For Maintenance
- ✅ Automated documentation updates from upstream
- ✅ Clear naming conventions
- ✅ YAML-based configuration (version-controllable)
- ✅ Easy to understand project structure

### For Future Expansion
- ✅ Add DuckDB, PostgreSQL docs with same pattern
- ✅ Scaffold new MCPs in minutes
- ✅ Share build infrastructure while keeping servers isolated
- ✅ Potential to publish servers as separate Python packages

---

## 📞 Questions Addressed

### "How do I update docs from upstream?"
**→** Use `tools/sync_documentation.sh` to pull from GitHub repos like modularml/mojo
**→** GitHub Actions can automate this weekly
**→** See RESTRUCTURING_PLAN.md Phase 6 for details

### "How do non-pixi users run the server?"
**→** Clone the server, create venv, pip install from requirements.txt
**→** Everything they need is included
**→** See RESTRUCTURING_PLAN.md for complete non-pixi guide

### "Can I distribute each server separately?"
**→** Yes! Each server is completely self-contained
**→** Can be separate GitHub repos or submodules
**→** Users get server code + DB + search engine

### "What about multiple doc formats?"
**→** Pluggable processor architecture handles MDX, Markdown, others
**→** Configuration specifies format per server
**→** See Phase 2 for implementation details

### "How do I add a new MCP?"
**→** Use `tools/scaffold_new_mcp.sh tool_name doc_type`
**→** Copy config templates, adjust processing params
**→** Build with standard pipeline
**→** See RESTRUCTURING_PLAN.md Phase 6

---

## 🎓 Learning Path

### New to the Project?
1. Read IMPLEMENTATION_SUMMARY.md
2. Skim RESTRUCTURING_PLAN.md sections 1-2
3. Ask questions!

### Ready to Implement?
1. Read PHASE_1_QUICKSTART.md
2. Follow step-by-step instructions
3. Reference RESTRUCTURING_PLAN.md as needed

### Need Detailed Info?
1. Start with RESTRUCTURING_PLAN.md
2. Focus on specific phases relevant to your changes
3. Use config templates as references

### Quick Lookup?
1. Check .memory.md for key info
2. Refer to naming conventions
3. Check environment variables section

---

## ✅ Success Checklist

- [ ] All documents reviewed
- [ ] Architecture decisions understood
- [ ] Naming conventions clear
- [ ] Git workflow plan understood
- [ ] Ready to start Phase 1
- [ ] Questions asked and answered
- [ ] Team aligned on approach

---

## 🚦 Ready to Proceed?

### Start with Phase 1:

```bash
# Open Phase 1 guide
open PHASE_1_QUICKSTART.md

# Or read it:
cat PHASE_1_QUICKSTART.md | less

# When ready, create the branch:
git checkout -b restructure/01-directory-structure-and-config

# Follow the step-by-step instructions in PHASE_1_QUICKSTART.md
```

---

## 📖 Additional References

- **Copilot Instructions**: `.github/copilot-instructions.md` — Project guidance
- **Current Architecture**: `docs/ARCHITECTURE.md` (after Phase 7)
- **Development Guide**: `docs/DEVELOPMENT.md` (after Phase 7)
- **Quick Start**: `docs/QUICKSTART.md` (after Phase 7)

---

## 🎉 Completion Indicators

When you've successfully completed the restructuring:

✅ `/shared/` contains build-time infrastructure  
✅ `/servers/mojo-manual-mcp/` is self-contained  
✅ All scripts use YAML configuration  
✅ Both pixi and non-pixi workflows work  
✅ Can create new MCPs with scaffold script  
✅ Can sync docs from upstream  
✅ Documentation is comprehensive  
✅ Git history is clean and logical  

---

**Questions? Review the appropriate document above or refer to RESTRUCTURING_PLAN.md for comprehensive details.**

**Ready to start? Begin with PHASE_1_QUICKSTART.md**

Phase 4 Execution Guide: Wire Preprocessing to config_loader and Fix ${PROJECT_ROOT} Paths
For Next Session’s AI Model

Quick Phase 3 Recap (Current State)
As of restructure/03-parameterize-build-scripts:

Embedding scripts (embedding/*.py) are parameterized with:
--mcp-name and optional --config (where applicable).
Paths follow the build layout (e.g. shared/build/processed_docs/{mcp_name}/...).
Root pixi.toml has:
mojo-process, mojo-generate-embeddings, mojo-consolidate, mojo-load, mojo-index, mojo-build.
README.md documents the embedding pipeline.
config_loader.py exists at config_loader.py and supports ${SERVER_ROOT} / ${PROJECT_ROOT} substitution.
Preprocessing run (pixi run mojo-process) successfully processes 45 docs and validates output, but:
The log still prints ${PROJECT_ROOT} literally.
The actual output directory is mojo (incorrect).
Reason: the preprocessing pipeline uses preprocessing/src/utils.load_config (plain YAML) instead of shared.preprocessing.src.config_loader.load_config_with_substitution.
Goal of Phase 4: Move preprocessing onto the shared config loader so ${PROJECT_ROOT} and ${SERVER_ROOT} work correctly, fix the output paths, and keep behavior otherwise identical.

Phase 4 Objectives
Switch the preprocessing pipeline to use config_loader.py:

All ${VAR} placeholders in YAML should be correctly substituted at runtime.
base_directory and any other ${PROJECT_ROOT} / ${SERVER_ROOT} values must resolve to real paths (e.g. mojo).
Preserve existing behavior:

Source discovery (45 docs) must still work.
Chunking, metadata extraction, manifest generation, and validation logic must remain unchanged.
New behavior should be purely about path resolution and config wiring.
Keep Phase 3 contract intact:

pixi run mojo-process should still be the main entry point.
Embedding pipeline (mojo-generate-embeddings, etc.) should not require further edits in this phase.
Files and Components Involved
Current loader (plain YAML)
utils.py


def load_config(config_path: str = "preprocessing/config/processing_config.yaml") -> Dict:    """Load configuration from YAML file."""    with open(config_path, "r") as f:        return yaml.safe_load(f)
Used by pipeline.py:


from .utils import load_config, ......class DocumentProcessingPipeline:    def __init__(self, config_path: str = "preprocessing/config/processing_config.yaml"):        self.config = load_config(config_path)        self.base_dir = Path(self.config["output"]["base_directory"])        self.source_dir = Path(self.config["source"]["directory"])        ...
Desired loader (with substitution)
config_loader.py (already implemented):


from shared.preprocessing.src.config_loader import load_config_with_substitution
Resolves the config path relative to project root.
Detects server_root from servers/{name}/config/....
Walks up to find PROJECT_ROOT (parent containing .git or shared).
Performs variable substitution for ${SERVER_ROOT}, ${PROJECT_ROOT}, and environment variables.
Current server config
processing_config.yaml:


source:  directory: "source-documentation/mojo/manual"output:  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mojo"  raw_dir: "raw"  metadata_dir: "metadata"  chunks_dir: "chunks"  manifest_file: "manifest.json"
Note: source.directory is currently literal (no ${PROJECT_ROOT}) and works; output.base_directory still uses ${PROJECT_ROOT} and is currently treated literally by load_config.

Step-by-Step Tasks
Task 1: Wire DocumentProcessingPipeline to config_loader
In pipeline.py:

Replace:


from .utils import (    load_config,    save_json,    save_jsonl,    create_directory_structure,    get_file_list,    generate_document_id,)
With (or add):


from .utils import (    save_json,    save_jsonl,    create_directory_structure,    get_file_list,    generate_document_id,)from shared.preprocessing.src.config_loader import load_config_with_substitution
Update DocumentProcessingPipeline.__init__:

Replace:


def __init__(self, config_path: str = "preprocessing/config/processing_config.yaml"):    self.config = load_config(config_path)
With:


def __init__(self, config_path: str = "preprocessing/config/processing_config.yaml"):    # Use shared config loader so ${PROJECT_ROOT}/${SERVER_ROOT} are substituted    self.config = load_config_with_substitution(config_path)
Update init_directories:

Currently:


def init_directories(config: Dict | None = None) -> None:    if config is None:        config = load_config()    base_dir = Path(config["output"]["base_directory"])    ...
Change to:


from shared.preprocessing.src.config_loader import load_config_with_substitutiondef init_directories(config: Dict | None = None, config_path: str = "preprocessing/config/processing_config.yaml") -> None:    if config is None:        config = load_config_with_substitution(config_path)    base_dir = Path(config["output"]["base_directory"])    ...
And in DocumentProcessingPipeline.__init__, call:


init_directories(self.config, config_path)
Goal: Ensure any time the pipeline initializes directories, it uses the substituted config.

Task 2: Normalize processing_config.yaml to use variables consistently
Adjust processing_config.yaml to use ${PROJECT_ROOT} for both source and output, now that substitution will work:


source:  directory: "${PROJECT_ROOT}/source-documentation/mojo/manual"
and keep:


output:  base_directory: "${PROJECT_ROOT}/shared/build/processed_docs/mojo"
Verify load_config_with_substitution("servers/mojo-manual-mcp/config/processing_config.yaml") returns a dict where:

config["source"]["directory"] == "/home/james/mcp/source-documentation/mojo/manual" (or equivalent OS path).
config["output"]["base_directory"] == "/home/james/mcp/shared/build/processed_docs/mojo".
The easiest way (Phase 4) is to add a tiny debug script or one-off python -c snippet, but keep that script out of git or behind a debug flag.

Task 3: Ensure no stale references to load_config
Search for load_config( in preprocessing/src/* and ensure all production paths that care about ${PROJECT_ROOT} / ${SERVER_ROOT} use load_config_with_substitution instead.

It’s acceptable to keep load_config for purely internal/testing configs that don’t use variables, but all server-driven configs (servers/*/config/*.yaml) should be routed through the shared loader.

Task 4: Re-run Phase 3 pipeline on test/restructure
On the testing branch (test/restructure):

Ensure Phase 4 changes are present (merge/rebase from restructure/04-... once created).

Run:


pixi run mojo-process
Confirm in the logs:

Output directory prints as an absolute path, e.g.:


✓ Created fresh output directories in /home/james/mcp/shared/build/processed_docs/mojo
No ${PROJECT_ROOT} appears in logs.

Summary and validation still pass.

Optionally check that the directories under shared/build/processed_docs/mojo/{raw,metadata,chunks} look sane and contain 45 docs worth of artifacts.

Out of Scope for Phase 4
Do not:

Change the embedding scripts or their paths again (they are already parameterized and using build correctly).
Move preprocessing modules to preprocessing entirely (that’s a later phase).
Change the structure of processing_config.yaml beyond what’s needed for substitution.
Adjust the MCP server runtime or DuckDB search behavior.
Success Criteria for Phase 4
Phase 4 is done when:

pipeline.py and init_directories use load_config_with_substitution from config_loader.py.

processing_config.yaml uses ${PROJECT_ROOT} (and/or ${SERVER_ROOT}) safely.

Running:


pixi run mojo-process
on test/restructure:

Processes 45 docs (or expected count).
Writes outputs under mojo (no ${PROJECT_ROOT} literal).
Prints a correct summary.
Passes validation.
No behavior regressions in chunk counts, manifest layout, or downstream embedding steps.

Notes for the Next Model
The RuntimeWarning from runpy is unrelated to the zero-file issue earlier; the real problem was that load_config did not perform substitution.
After Phase 4, all future MCP servers’ processing configs should be designed assuming ${PROJECT_ROOT} / ${SERVER_ROOT} will be resolved via config_loader.py.
Treat this phase as wiring the preprocessing side to the same config system already used by the embedding side in Phase 3.

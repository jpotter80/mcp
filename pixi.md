pixi
# Description

The pixi command is the main entry point for the Pixi CLI.

# Usage

pixi [OPTIONS] [COMMAND]
# Subcommands
## Command	Description
add	    Adds dependencies to the workspace
auth	Login to prefix.dev or anaconda.org servers to access private channels
build	Workspace configuration
clean	Cleanup the environments
completion	Generates a completion script for a shell
config	Configuration management
exec	Run a command and install it in a temporary environment
global	Subcommand for global package management actions
info	Information about the system, workspace and environments for the current machine
init	Creates a new workspace
import	Imports a file into an environment in an existing workspace.
install	Install an environment, both updating the lockfile and installing the environment
list	List workspace's packages
lock	Solve environment and update the lock file without installing the environments
reinstall	Re-install an environment, both updating the lockfile and re-installing the environment
remove	Removes dependencies from the workspace
run	Runs task in the pixi environment
search	Search a conda package
self-update	Update pixi to the latest version or a specific version
shell	Start a shell in a pixi environment, run exit to leave the shell
shell-hook	Print the pixi environment activation script
task	Interact with tasks in the workspace
tree	Show a tree of workspace dependencies
update	The update command checks if there are newer versions of the dependencies and updates the pixi.lock file and environments accordingly
upgrade	Checks if there are newer versions of the dependencies and upgrades them in the lockfile and manifest file
upload	Upload a conda package
workspace	Modify the workspace configuration file through the command line
Global Options#
--help (-h)
Display help information
--verbose (-v)
Increase logging verbosity (-v for warnings, -vv for info, -vvv for debug, -vvvv for trace)
--quiet (-q)
Decrease logging verbosity (quiet mode)
--color <COLOR>
Whether the log needs to be colored
env: PIXI_COLOR
default: auto
options: always, never, auto
--no-progress
Hide all progress bars, always turned on if stderr is not a terminal
env: PIXI_NO_PROGRESS
default: false
--list
List all installed commands (built-in and extensions)
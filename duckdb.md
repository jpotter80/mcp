# CLI Client
The latest version of the DuckDB CLI client is 1.3.2.

## Installation
The DuckDB CLI (Command Line Interface) is a single, dependency-free executable. It is precompiled for Windows, Mac, and Linux for both the stable version and for nightly builds produced by GitHub Actions. Please see the installation page under the CLI tab for download links.

The DuckDB CLI is based on the SQLite command line shell, so CLI-client-specific functionality is similar to what is described in the SQLite documentation (although DuckDB's SQL syntax follows PostgreSQL conventions with a few exceptions).

DuckDB has a tldr page, which summarizes the most common uses of the CLI client. If you have tldr installed, you can display it by running tldr duckdb.

## Getting Started
Once the CLI executable has been downloaded, unzip it and save it to any directory. Navigate to that directory in a terminal and enter the command duckdb to run the executable. If in a PowerShell or POSIX shell environment, use the command ./duckdb instead.

## Usage
The typical usage of the duckdb command is the following:

```shell
duckdb ⟨OPTIONS⟩ ⟨FILENAME⟩
```

## Options
The OPTIONS part encodes arguments for the CLI client. Common options include:

-csv: sets the output mode to CSV
-json: sets the output mode to JSON
-readonly: open the database in read-only mode (see concurrency in DuckDB)

For a full list of options, see the command line arguments page.

## In-Memory vs. Persistent Database
When no FILENAME argument is provided, the DuckDB CLI will open a temporary in-memory database. You will see DuckDB's version number, the information on the connection and a prompt starting with a D.

```shell
duckdb
```
```shell
DuckDB v1.3.2 (Ossivalis) 0b83e5d2f6
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
D
```

To open or create a persistent database, simply include a path as a command line argument:

```shell
duckdb my_database.duckdb
```
## Running SQL Statements in the CLI
Once the CLI has been opened, enter a SQL statement followed by a semicolon, then hit enter and it will be executed. Results will be displayed in a table in the terminal. If a semicolon is omitted, hitting enter will allow for multi-line SQL statements to be entered.

```sql
SELECT 'quack' AS my_column;
```

my_column
---
quack

The CLI supports all of DuckDB's rich SQL syntax including SELECT, CREATE, and ALTER statements.

## Editor Features
The CLI supports autocompletion, and has sophisticated editor features and syntax highlighting on certain platforms.

## Exiting the CLI
To exit the CLI, press Ctrl+D if your platform supports it. Otherwise, press Ctrl+C or use the .exit command. If you used a persistent database, DuckDB will automatically checkpoint (save the latest edits to disk) and close. This will remove the .wal file (the write-ahead log) and consolidate all of your data into the single-file database.

## Dot Commands
In addition to SQL syntax, special dot commands may be entered into the CLI client. To use one of these commands, begin the line with a period (.) immediately followed by the name of the command you wish to execute. Additional arguments to the command are entered, space separated, after the command. If an argument must contain a space, either single or double quotes may be used to wrap that parameter. Dot commands must be entered on a single line, and no whitespace may occur before the period. No semicolon is required at the end of the line.

Frequently-used configurations can be stored in the file ~/.duckdbrc, which will be loaded when starting the CLI client. See the Configuring the CLI section below for further information on these options.

Tip
To prevent the DuckDB CLI client from reading the ~/.duckdbrc file, start it as follows:

```shell
duckdb -init /dev/null
```

Below, we summarize a few important dot commands. To see all available commands, see the dot commands page or use the .help command.

### Opening Database Files
In addition to connecting to a database when opening the CLI, a new database connection can be made by using the .open command. If no additional parameters are supplied, a new in-memory database connection is created. This database will not be persisted when the CLI connection is closed.

```shell
.open
```

The .open command optionally accepts several options, but the final parameter can be used to indicate a path to a persistent database (or where one should be created). The special string :memory: can also be used to open a temporary in-memory database.

```sql
.open persistent.duckdb
```

Warning
.open closes the current database. To keep the current database, while adding a new database, use the ATTACH statement.

One important option accepted by .open is the --readonly flag. This disallows any editing of the database. To open in read only mode, the database must already exist. This also means that a new in-memory database can't be opened in read only mode since in-memory databases are created upon connection.

```shell
.open --readonly preexisting.duckdb
```

### Output Formats
The .mode dot command may be used to change the appearance of the tables returned in the terminal output. These include the default duckbox mode, csv and json mode for ingestion by other tools, markdown and latex for documents, and insert mode for generating SQL statements.

### Writing Results to a File
By default, the DuckDB CLI sends results to the terminal's standard output. However, this can be modified using either the .output or .once commands. For details, see the documentation for the output dot command.

### Reading SQL from a File
The DuckDB CLI can read both SQL commands and dot commands from an external file instead of the terminal using the .read command. This allows for a number of commands to be run in sequence and allows command sequences to be saved and reused.

The .read command requires only one argument: the path to the file containing the SQL and/or commands to execute. After running the commands in the file, control will revert back to the terminal. Output from the execution of that file is governed by the same .output and .once commands that have been discussed previously. This allows the output to be displayed back to the terminal, as in the first example below, or out to another file, as in the second example.

In this example, the file select_example.sql is located in the same directory as duckdb.exe and contains the following SQL statement:

```sql
SELECT *
FROM generate_series(5);
```

To execute it from the CLI, the .read command is used.

```shell
.read select_example.sql
```

The output below is returned to the terminal by default. The formatting of the table can be adjusted using the .output or .once commands.

```shell
| generate_series |
|----------------:|
| 0               |
| 1               |
| 2               |
| 3               |
| 4               |
| 5               |
```

Multiple commands, including both SQL and dot commands, can also be run in a single .read command. In this example, the file write_markdown_to_file.sql is located in the same directory as duckdb.exe and contains the following commands:

```sql
.mode markdown
.output series.md
SELECT *
FROM generate_series(5);
```

To execute it from the CLI, the .read command is used as before.

```shell
.read write_markdown_to_file.sql
```

In this case, no output is returned to the terminal. Instead, the file series.md is created (or replaced if it already existed) with the markdown-formatted results shown here:

```shell
| generate_series |
|----------------:|
| 0               |
| 1               |
| 2               |
| 3               |
| 4               |
| 5               |
```

## Configuring the CLI
Several dot commands can be used to configure the CLI. On startup, the CLI reads and executes all commands in the file ~/.duckdbrc, including dot commands and SQL statements. This allows you to store the configuration state of the CLI. You may also point to a different initialization file using the -init.

### Setting a Custom Prompt
As an example, a file in the same directory as the DuckDB CLI named prompt.sql will change the DuckDB prompt to be a duck head and run a SQL statement. Note that the duck head is built with Unicode characters and does not work in all terminal environments (e.g., in Windows, unless running with WSL and using the Windows Terminal).

```shell
.prompt '⚫◗ '
```

To invoke that file on initialization, use this command:

```shell
duckdb -init prompt.sql
```

This outputs:

```shell
-- Loading resources from prompt.sql
v⟨version⟩ ⟨git_hash⟩
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
⚫◗
```

## Non-Interactive Usage
To read/process a file and exit immediately, redirect the file contents in to duckdb:

```shell
duckdb < select_example.sql
```

To execute a command with SQL text passed in directly from the command line, call duckdb with two arguments: the database location (or :memory:), and a string with the SQL statement to execute.

```shell
duckdb :memory: "SELECT 42 AS the_answer"
```

## Loading Extensions
To load extensions, use DuckDB's SQL INSTALL and LOAD commands as you would other SQL statements.

```sql
INSTALL fts;
LOAD fts;
```

For details, see the Extension docs.

## Reading from stdin and Writing to stdout
When in a Unix environment, it can be useful to pipe data between multiple commands. DuckDB is able to read data from stdin as well as write to stdout using the file location of stdin (/dev/stdin) and stdout (/dev/stdout) within SQL commands, as pipes act very similarly to file handles.

This command will create an example CSV:

```sql
COPY (SELECT 42 AS woot UNION ALL SELECT 43 AS woot) TO 'test.csv' (HEADER);
```

First, read a file and pipe it to the duckdb CLI executable. As arguments to the DuckDB CLI, pass in the location of the database to open, in this case, an in-memory database, and a SQL command that utilizes /dev/stdin as a file location.

```shell
cat test.csv | duckdb -c "SELECT * FROM read_csv('/dev/stdin')"
```

```shell
woot
---
42
---
43
```

To write back to stdout, the copy command can be used with the /dev/stdout file location.

```shell
cat test.csv | \
    duckdb -c "COPY (SELECT * FROM read_csv('/dev/stdin')) TO '/dev/stdout' WITH (FORMAT csv, HEADER)"
```

```shell
woot
42
43
```

## Reading Environment Variables
The getenv function can read environment variables.

### Examples
To retrieve the home directory's path from the HOME environment variable, use:

```sql
SELECT getenv('HOME') AS home;
```

```shell
home
---
/Users/user_name
```

The output of the getenv function can be used to set configuration options. For example, to set the NULL order based on the environment variable DEFAULT_NULL_ORDER, use:

```sql
SET default_null_order = getenv('DEFAULT_NULL_ORDER');
```

### Restrictions for Reading Environment Variables
The getenv function can only be run when the enable_external_access option is set to true (the default setting). It is only available in the CLI client and is not supported in other DuckDB clients.

## Prepared Statements
The DuckDB CLI supports executing prepared statements in addition to regular SELECT statements. To create and execute a prepared statement in the CLI client, use the PREPARE clause and the EXECUTE statement.

# Command Line Arguments
The table below summarizes DuckDB's command line options. To list all command line options, use the command:

```shell
duckdb -help
```

For a list of dot commands available in the CLI shell, see the Dot Commands page.

Argument	Description
-append	Append the database to the end of the file
-ascii	Set output mode to ascii
-bail	Stop after hitting an error
-batch	Force batch I/O
-box	Set output mode to box
-column	Set output mode to column
-cmd COMMAND	Run COMMAND before reading stdin
-c COMMAND	Run COMMAND and exit
-csv	Set output mode to csv
-echo	Print commands before execution
-f FILENAME	Run the script in FILENAME and exit. Note that the ~/.duckdbrc is read and executed first (if it exists)
-init FILENAME	Run the script in FILENAME upon startup (instead of ~/.duckdbrc)
-header	Turn headers on
-help	Show this message
-html	Set output mode to HTML
-interactive	Force interactive I/O
-json	Set output mode to json
-line	Set output mode to line
-list	Set output mode to list
-markdown	Set output mode to markdown
-newline SEP	Set output row separator. Default: \n
-nofollow	Refuse to open symbolic links to database files
-noheader	Turn headers off
-no-stdin	Exit after processing options instead of reading stdin
-nullvalue TEXT	Set text string for NULL values. Default: NULL
-quote	Set output mode to quote
-readonly	Open the database read-only. This option also supports attaching to remote databases via HTTPS
-s COMMAND	Run COMMAND and exit
-separator SEP	Set output column separator to SEP. Default: |
-table	Set output mode to table
-ui	Loads and starts the DuckDB UI. If the UI is not yet installed, it installs the ui extension
-unsigned	Allow loading of unsigned extensions. This option is intended to be used for developing extensions. Consult the Securing DuckDB page for guidelines on how set up DuckDB in a secure manner
-version	Show DuckDB version

## Passing a Sequence of Arguments
Note that the CLI arguments are processed in order, similarly to the behavior of the SQLite CLI. For example:

```shell
duckdb -csv -c 'SELECT 42 AS hello' -json -c 'SELECT 84 AS world'
```

Returns the following:

```shell
hello
42
[{"world":84}]
```

# Dot Commands
Dot commands are available in the DuckDB CLI client. To use one of these commands, begin the line with a period (.) immediately followed by the name of the command you wish to execute. Additional arguments to the command are entered, space separated, after the command. If an argument must contain a space, either single or double quotes may be used to wrap that parameter. Dot commands must be entered on a single line, and no whitespace may occur before the period. No semicolon is required at the end of the line. To see available commands, use the .help command.

List of Dot Commands
Command	Description
.bail on/off	Stop after hitting an error. Default: off
.binary on/off	Turn binary output on or off. Default: off
.cd DIRECTORY	Change the working directory to DIRECTORY
.changes on/off	Show number of rows changed by SQL
.columns	Column-wise rendering of query results
.constant COLOR	Sets the syntax highlighting color used for constant values
.constantcode CODE	Sets the syntax highlighting terminal code used for constant values
.databases	List names and files of attached databases
.echo on/off	Turn command echo on or off
.exit CODE	Exit this program with return-code CODE
.headers on/off	Turn display of headers on or off. Does not apply to duckbox mode
.help -all PATTERN	Show help text for PATTERN
.highlight on/off	Toggle syntax highlighting in the shell on / off. See the query syntax highlighting section for more details
.highlight_colors COMPONENT COLOR	Configure the color of each component in (duckbox only). See the result syntax highlighting section for more details
.highlight_results on/off	Toggle highlighting in result tables on / off (duckbox only). See the result syntaxx highlighting section for more details
.import FILE TABLE	Import data from FILE into TABLE
.indexes TABLE	Show names of indexes
.keyword COLOR	Sets the syntax highlighting color used for keywords
.keywordcode CODE	Sets the syntax highlighting terminal code used for keywords
.large_number_rendering all/footer/off	Toggle readable rendering of large numbers (duckbox only, default: footer)
.log FILE/off	Turn logging on or off. FILE can be stderr / stdout
.maxrows COUNT	Sets the maximum number of rows for display. Only for duckbox mode
.maxwidth COUNT	Sets the maximum width in characters. 0 defaults to terminal width. Only for duckbox mode
.mode MODE TABLE	Set output mode
.multiline	Set multi-line mode (default)
.nullvalue STRING	Use STRING in place of NULL values. Default: NULL
.once OPTIONS FILE	Output for the next SQL command only to FILE
.open OPTIONS FILE	Close existing database and reopen FILE
.output FILE	Send output to FILE or stdout if FILE is omitted
.print STRING...	Print literal STRING
.prompt MAIN CONTINUE	Replace the standard prompts
.quit	Exit this program
.read FILE	Read input from FILE
.rows	Row-wise rendering of query results (default)
.safe_mode	Activates safe mode
.schema PATTERN	Show the CREATE statements matching PATTERN
.separator COL ROW	Change the column and row separators
.shell CMD ARGS...	Run CMD with ARGS... in a system shell
.show	Show the current values for various settings
.singleline	Set single-line mode
.system CMD ARGS...	Run CMD with ARGS... in a system shell
.tables TABLE	List names of tables matching LIKE pattern TABLE
.timer on/off	Turn SQL timer on or off. SQL statements separated by ; but not separated via newline are measured together
.width NUM1 NUM2 ...	Set minimum column widths for columnar output

## Using the .help Command
The .help text may be filtered by passing in a text string as the first argument.

```shell
.help m
```

```shell
.maxrows COUNT           Sets the maximum number of rows for display (default: 40). Only for duckbox mode.
.maxwidth COUNT          Sets the maximum width in characters. 0 defaults to terminal width. Only for duckbox mode.
.mode MODE ?TABLE?       Set output mode
```

## .output: Writing Results to a File
By default, the DuckDB CLI sends results to the terminal's standard output. However, this can be modified using either the .output or .once commands. Pass in the desired output file location as a parameter. The .once command will only output the next set of results and then revert to standard out, but .output will redirect all subsequent output to that file location. Note that each result will overwrite the entire file at that destination. To revert back to standard output, enter .output with no file parameter.

In this example, the output format is changed to markdown, the destination is identified as a Markdown file, and then DuckDB will write the output of the SQL statement to that file. Output is then reverted to standard output using .output with no parameter.

```shell
.mode markdown
.output my_results.md
SELECT 'taking flight' AS output_column;
.output
SELECT 'back to the terminal' AS displayed_column;
```

The file my_results.md will then contain:

```shell
| output_column |
|---------------|
| taking flight |
```

The terminal will then display:

```shell
|   displayed_column   |
|----------------------|
| back to the terminal |
```

A common output format is CSV, or comma separated values. DuckDB supports SQL syntax to export data as CSV or Parquet, but the CLI-specific commands may be used to write a CSV instead if desired.

```shell
.mode csv
.once my_output_file.csv
SELECT 1 AS col_1, 2 AS col_2
UNION ALL
SELECT 10 AS col1, 20 AS col_2;
```

The file my_output_file.csv will then contain:

```shell
col_1,col_2
1,2
10,20
```

By passing special options (flags) to the .once command, query results can also be sent to a temporary file and automatically opened in the user's default program. Use either the -e flag for a text file (opened in the default text editor), or the -x flag for a CSV file (opened in the default spreadsheet editor). This is useful for more detailed inspection of query results, especially if there is a relatively large result set. The .excel command is equivalent to .once -x.

```shell
.once -e
SELECT 'quack' AS hello;
```

The results then open in the default text file editor of the system, for example:

cli_docs_output_to_text_editor

Tip
macOS users can copy the results to their clipboards using pbcopy by using .once to output to pbcopy via a pipe: .once |pbcopy

Combining this with the .headers off and .mode lines options can be particularly effective.

## Querying the Database Schema
All DuckDB clients support querying the database schema with SQL, but the CLI has additional dot commands that can make it easier to understand the contents of a database. The .tables command will return a list of tables in the database. It has an optional argument that will filter the results according to a LIKE pattern.

```sql
CREATE TABLE swimmers AS SELECT 'duck' AS animal;
CREATE TABLE fliers AS SELECT 'duck' AS animal;
CREATE TABLE walkers AS SELECT 'duck' AS animal;
.tables
```

```shell
fliers    swimmers  walkers
```

For example, to filter to only tables that contain an l, use the LIKE pattern %l%.

```shell
.tables %l%
```

```shell
fliers   walkers
```

The .schema command will show all of the SQL statements used to define the schema of the database.

```shell
.schema
```

```sql
CREATE TABLE fliers (animal VARCHAR);
CREATE TABLE swimmers (animal VARCHAR);
CREATE TABLE walkers (animal VARCHAR);
```

## Syntax Highlighters
The DuckDB CLI client has a syntax highlighter for the SQL queries and another for the duckbox-formatted result tables.

## Configuring the Query Syntax Highlighter
By default the shell includes support for syntax highlighting. The CLI's syntax highlighter can be configured using the following commands.

To turn off the highlighter:

```shell
.highlight off
```

To turn on the highlighter:

```shell
.highlight on
```

To configure the color used to highlight constants:

```shell
.constant [red|green|yellow|blue|magenta|cyan|white|brightblack|brightred|brightgreen|brightyellow|brightblue|brightmagenta|brightcyan|brightwhite]
```

```shell
.constantcode ⟨terminal_code⟩
```

For example:

```shell
.constantcode 033[31m
```

To configure the color used to highlight keywords:

```shell
.keyword [red|green|yellow|blue|magenta|cyan|white|brightblack|brightred|brightgreen|brightyellow|brightblue|brightmagenta|brightcyan|brightwhite]
```

```shell
.keywordcode ⟨terminal_code⟩
```

For example:

```shell
.keywordcode 033[31m
```

## Configuring the Result Syntax Highlighter
By default, the result highlighting makes a few small modifications:

- Bold column names
- NULL values are greyed out
- Layout elements are grayed out

The highlighting of each of the components can be customized using the .highlight_colors command. For example:

```shell
.highlight_colors layout red
.highlight_colors column_type yellow
.highlight_colors column_name yellow bold_underline
.highlight_colors numeric_value cyan underline
.highlight_colors temporal_value red bold
.highlight_colors string_value green bold
.highlight_colors footer gray
```

The result highlighting can be disabled using .highlight_results off.

## Shorthands
DuckDB's CLI allows using shorthands for dot commands. Once a sequence of characters can unambiguously completed to a dot command or an argument, the CLI (silently) autocompletes them. For example:

```shell
.mo ma
```

Is equivalent to:

```shell
.mode markdown
```

Tip
Avoid using shorthands in SQL scripts to improve readability and ensure that the scripts and futureproof.

## Importing Data from CSV
_*Deprecated*_
This feature is only included for compatibility reasons and may be removed in the future. Use the read_csv function or the COPY statement to load CSV files.

# Output Formats
The .mode dot command may be used to change the appearance of the tables returned in the terminal output. In addition to customizing the appearance, these modes have additional benefits. This can be useful for presenting DuckDB output elsewhere by redirecting the terminal output to a file. Using the insert mode will build a series of SQL statements that can be used to insert the data at a later point. The markdown mode is particularly useful for building documentation and the latex mode is useful for writing academic papers.

## List of Output Formats

Mode	Description
ascii	Columns/rows delimited by 0x1F and 0x1E
box	Tables using unicode box-drawing characters
csv	Comma-separated values
column	Output in columns (See .width)
duckbox	Tables with extensive features (default)
html	HTML <table> code
insert TABLE	SQL insert statements for TABLE
json	Results in a JSON array
jsonlines	Results in a NDJSON
latex	LaTeX tabular environment code
line	One value per line
list	Values delimited by |
markdown	Markdown table format
quote	Escape answers as for SQL
table	ASCII-art table
tabs	Tab-separated values
tcl	TCL list elements
trash	No output

## Changing the Output Format
Use the vanilla .mode dot command to query the appearance currently in use.

```shell
.mode
```

```shell
current output mode: duckbox
```

Use the .mode dot command with an argument to set the output format.

```shell
.mode markdown
SELECT 'quacking intensifies' AS incoming_ducks;
```

```shell
|    incoming_ducks    |
|----------------------|
| quacking intensifies |
```

The output appearance can also be adjusted with the .separator command. If using an export mode that relies on a separator (csv or tabs for example), the separator will be reset when the mode is changed. For example, .mode csv will set the separator to a comma (,). Using .separator "|" will then convert the output to be pipe-separated.

```shell
.mode csv
SELECT 1 AS col_1, 2 AS col_2
UNION ALL
SELECT 10 AS col1, 20 AS col_2;
```

```shell
col_1,col_2
1,2
10,20
.separator "|"
SELECT 1 AS col_1, 2 AS col_2
UNION ALL
SELECT 10 AS col1, 20 AS col_2;
```

```shell
col_1|col_2
1|2
10|20
```

## duckbox Mode
By default, DuckDB renders query results in duckbox mode, which is a feature-rich ASCII-art style output format.

The duckbox mode supports the large_number_rendering option, which allows human-readable rendering of large numbers. It has three levels:

- off – All numbers are printed using regular formatting.
- footer (default) – Large numbers are augmented with the human-readable format. Only applies to single-row results.
- all - All large numbers are replaced with the human-readable format.

See the following examples:

```shell
.large_number_rendering off
SELECT pi() * 1_000_000_000 AS x;
```

```shell
┌───────────────────┐
│         x         │
│      double       │
├───────────────────┤
│ 3141592653.589793 │
└───────────────────┘
```

```shell
.large_number_rendering footer
SELECT pi() * 1_000_000_000 AS x;
```

```shell
┌───────────────────┐
│         x         │
│      double       │
├───────────────────┤
│ 3141592653.589793 │
│  (3.14 billion)   │
└───────────────────┘
```

```shell
.large_number_rendering all
SELECT pi() * 1_000_000_000 AS x;
```

```shell
┌──────────────┐
│      x       │
│    double    │
├──────────────┤
│ 3.14 billion │
└──────────────┘
```

# Editing
The linenoise-based CLI editor is currently only available for macOS and Linux.

DuckDB's CLI uses a line-editing library based on linenoise, which has shortcuts that are based on Emacs mode of readline. Below is a list of available commands.

## Moving
Key	Action
- Left	Move back a character
- Right	Move forward a character
- Up	Move up a line. When on the first line, move to previous history entry
- Down	Move down a line. When on last line, move to next history entry
- Home	Move to beginning of buffer
- End	Move to end of buffer
- Ctrl+Left	Move back a word
- Ctrl+Right	Move forward a word
- Ctrl+A	Move to beginning of buffer
- Ctrl+B	Move back a character
- Ctrl+E	Move to end of buffer
- Ctrl+F	Move forward a character
- Alt+Left	Move back a word
- Alt+Right	Move forward a word

## History
Key	Action
- Ctrl+P	Move to previous history entry
- Ctrl+N	Move to next history entry
- Ctrl+R	Search the history
- Ctrl+S	Search the history
- Alt+<	Move to first history entry
- Alt+>	Move to last history entry
- Alt+N	Search the history
- Alt+P	Search the history

## Changing Text
Key	Action
- Backspace	Delete previous character
- Delete	Delete next character
- Ctrl+D	Delete next character. When buffer is empty, end editing
- Ctrl+H	Delete previous character
- Ctrl+K	Delete everything after the cursor
- Ctrl+T	Swap current and next character
- Ctrl+U	Delete all text
- Ctrl+W	Delete previous word
- Alt+C	Convert next word to titlecase
- Alt+D	Delete next word
- Alt+L	Convert next word to lowercase
- Alt+R	Delete all text
- Alt+T	Swap current and next word
- Alt+U	Convert next word to uppercase
- Alt+Backspace	Delete previous word
- Alt+\	Delete spaces around cursor

## Completing
Key	Action
- Tab	Autocomplete. When autocompleting, cycle to next entry
- Shift+Tab	When autocompleting, cycle to previous entry
- Esc+Esc	When autocompleting, revert autocompletion

## Miscellaneous
Key	Action
- Enter	Execute query. If query is not complete, insert a newline at the end of the buffer
- Ctrl+J	Execute query. If query is not complete, insert a newline at the end of the buffer
- Ctrl+C	Cancel editing of current query
- Ctrl+G	Cancel editing of current query
- Ctrl+L	Clear screen
- Ctrl+O	Cancel editing of current query
- Ctrl+X	Insert a newline after the cursor
- Ctrl+Z	Suspend CLI and return to shell, use fg to re-open

## External Editor Mode
Use .edit or \e to open a query in an external text editor.

- When entered alone, it opens the previous command for editing.
- When used inside a multi-line command, it opens the current command in the editor.

The editor is taken from the first set environment variable among DUCKDB_EDITOR, EDITOR or VISUAL (in that order). If none are set, vi is used.

This feature is only available in the linenoise-based CLI editor, which is currently supported on macOS and Linux.

## Using Read-Line
If you prefer, you can use rlwrap to use read-line directly with the shell. Then, use Shift+Enter to insert a newline and Enter to execute the query:

```shell
rlwrap --substitute-prompt="D " duckdb -batch
```

# Safe Mode
The DuckDB CLI client supports “safe mode”. In safe mode, the CLI is prevented from accessing external files other than the database file that it was initially connected to and prevented from interacting with the host file system.

This has the following effects:

- The following dot commands are disabled:
.cd
.excel
.import
.log
.once
.open
.output
.read
.sh
.system

- Auto-complete no longer scans the file system for files to suggest as auto-complete targets.
- The getenv function is disabled.
- The enable_external_access option is set to false. This implies that:
  - ATTACH cannot attach to a database in a file.
  - COPY cannot read to or write from files.
  - Functions such as read_csv, read_parquet, read_json, etc. cannot read from an external source.
  
Once safe mode is activated, it cannot be deactivated in the same DuckDB CLI session.

For more information on running DuckDB in secure environments, see the “Securing DuckDB” page.




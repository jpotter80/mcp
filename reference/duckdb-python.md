---
github_repository: https://github.com/duckdb/duckdb-python
layout: docu
redirect_from:
- /docs/api/python
- /docs/api/python/
- /docs/api/python/overview
- /docs/api/python/overview/
- /docs/clients/python/overview
title: Python API
---

> The latest stable version of the DuckDB Python client is {{ site.current_duckdb_version }}.

## Installation

The DuckDB Python API can be installed using [pip](https://pip.pypa.io): `pip install duckdb`. Please see the [installation page]({% link install/index.html %}?environment=python) for details. It is also possible to install DuckDB using [conda](https://docs.conda.io): `conda install python-duckdb -c conda-forge`.

**Python version:**
DuckDB requires Python 3.9 or newer.

## Basic API Usage

The most straight-forward manner of running SQL queries using DuckDB is using the `duckdb.sql` command.

```python
import duckdb

duckdb.sql("SELECT 42").show()
```

This will run queries using an **in-memory database** that is stored globally inside the Python module. The result of the query is returned as a **Relation**. A relation is a symbolic representation of the query. The query is not executed until the result is fetched or requested to be printed to the screen.

Relations can be referenced in subsequent queries by storing them inside variables, and using them as tables. This way queries can be constructed incrementally.

```python
import duckdb

r1 = duckdb.sql("SELECT 42 AS i")
duckdb.sql("SELECT i * 2 AS k FROM r1").show()
```

## Data Input

DuckDB can ingest data from a wide variety of formats – both on-disk and in-memory. See the [data ingestion page]({% link docs/stable/clients/python/data_ingestion.md %}) for more information.

```python
import duckdb

duckdb.read_csv("example.csv")                # read a CSV file into a Relation
duckdb.read_parquet("example.parquet")        # read a Parquet file into a Relation
duckdb.read_json("example.json")              # read a JSON file into a Relation

duckdb.sql("SELECT * FROM 'example.csv'")     # directly query a CSV file
duckdb.sql("SELECT * FROM 'example.parquet'") # directly query a Parquet file
duckdb.sql("SELECT * FROM 'example.json'")    # directly query a JSON file
```

### DataFrames

DuckDB can directly query Pandas DataFrames, Polars DataFrames and Arrow tables.
Note that these are read-only, i.e., editing these tables via [`INSERT`]({% link docs/stable/sql/statements/insert.md %}) or [`UPDATE` statements]({% link docs/stable/sql/statements/update.md %}) is not possible.

#### Pandas

To directly query a Pandas DataFrame, run:

```python
import duckdb
import pandas as pd

pandas_df = pd.DataFrame({"a": [42]})
duckdb.sql("SELECT * FROM pandas_df")
```

```text
┌───────┐
│   a   │
│ int64 │
├───────┤
│    42 │
└───────┘
```

#### Polars

To directly query a Polars DataFrame, run:

```python
import duckdb
import polars as pl

polars_df = pl.DataFrame({"a": [42]})
duckdb.sql("SELECT * FROM polars_df")
```

```text
┌───────┐
│   a   │
│ int64 │
├───────┤
│    42 │
└───────┘
```

#### PyArrow

To directly query a PyArrow table, run:

```python
import duckdb
import pyarrow as pa

arrow_table = pa.Table.from_pydict({"a": [42]})
duckdb.sql("SELECT * FROM arrow_table")
```

```text
┌───────┐
│   a   │
│ int64 │
├───────┤
│    42 │
└───────┘
```

## Result Conversion

DuckDB supports converting query results efficiently to a variety of formats. See the [result conversion page]({% link docs/stable/clients/python/conversion.md %}) for more information.

```python
import duckdb

duckdb.sql("SELECT 42").fetchall()   # Python objects
duckdb.sql("SELECT 42").df()         # Pandas DataFrame
duckdb.sql("SELECT 42").pl()         # Polars DataFrame
duckdb.sql("SELECT 42").arrow()      # Arrow Table
duckdb.sql("SELECT 42").fetchnumpy() # NumPy Arrays
```

## Writing Data to Disk

DuckDB supports writing Relation objects directly to disk in a variety of formats. The [`COPY` statement]({% link docs/stable/sql/statements/copy.md %}) can be used to write data to disk using SQL as an alternative.

```python
import duckdb

duckdb.sql("SELECT 42").write_parquet("out.parquet") # Write to a Parquet file
duckdb.sql("SELECT 42").write_csv("out.csv")         # Write to a CSV file
duckdb.sql("COPY (SELECT 42) TO 'out.parquet'")      # Copy to a Parquet file
```

## Connection Options

Applications can open a new DuckDB connection via the `duckdb.connect()` method.

### Using an In-Memory Database

When using DuckDB through `duckdb.sql()`, it operates on an **in-memory** database, i.e., no tables are persisted on disk.
Invoking the `duckdb.connect()` method without arguments returns a connection, which also uses an in-memory database:

```python
import duckdb

con = duckdb.connect()
con.sql("SELECT 42 AS x").show()
```

### Persistent Storage

The `duckdb.connect(dbname)` creates a connection to a **persistent** database.
Any data written to that connection will be persisted, and can be reloaded by reconnecting to the same file, both from Python and from other DuckDB clients.

```python
import duckdb

# create a connection to a file called 'file.db'
con = duckdb.connect("file.db")
# create a table and load data into it
con.sql("CREATE TABLE test (i INTEGER)")
con.sql("INSERT INTO test VALUES (42)")
# query the table
con.table("test").show()
# explicitly close the connection
con.close()
# Note: connections also closed implicitly when they go out of scope
```

You can also use a context manager to ensure that the connection is closed:

```python
import duckdb

with duckdb.connect("file.db") as con:
    con.sql("CREATE TABLE test (i INTEGER)")
    con.sql("INSERT INTO test VALUES (42)")
    con.table("test").show()
    # the context manager closes the connection automatically
```

### Configuration

The `duckdb.connect()` accepts a `config` dictionary, where [configuration options]({% link docs/stable/configuration/overview.md %}#configuration-reference) can be specified. For example:

```python
import duckdb

con = duckdb.connect(config = {'threads': 1})
```

### Connection Object and Module

The connection object and the `duckdb` module can be used interchangeably – they support the same methods. The only difference is that when using the `duckdb` module a global in-memory database is used.

> If you are developing a package designed for others to use, and use DuckDB in the package, it is recommend that you create connection objects instead of using the methods on the `duckdb` module. That is because the `duckdb` module uses a shared global database – which can cause hard to debug issues if used from within multiple different packages.

### Using Connections in Parallel Python Programs

The `DuckDBPyConnection` object is not thread-safe. If you would like to write to the same database from multiple threads, create a cursor for each thread with the [`DuckDBPyConnection.cursor()` method]({% link docs/stable/clients/python/reference/index.md %}#duckdb.DuckDBPyConnection.cursor).

## Loading and Installing Extensions

DuckDB's Python API provides functions for installing and loading [extensions]({% link docs/stable/extensions/overview.md %}), which perform the equivalent operations to running the `INSTALL` and `LOAD` SQL commands, respectively. An example that installs and loads the [`spatial` extension]({% link docs/stable/core_extensions/spatial/overview.md %}) looks like follows:

```python
import duckdb

con = duckdb.connect()
con.install_extension("spatial")
con.load_extension("spatial")
```

### Community Extensions

To load [community extensions]({% link community_extensions/index.md %}), use the `repository="community"` argument with the `install_extension` method.

For example, install and load the `h3` community extension as follows:

```python
import duckdb

con = duckdb.connect()
con.install_extension("h3", repository="community")
con.load_extension("h3")
```

### Unsigned Extensions

To load [unsigned extensions]({% link docs/stable/extensions/overview.md %}#unsigned-extensions), use the `config = {"allow_unsigned_extensions": "true"}` argument with the `duckdb.connect()` method.

---
layout: docu
redirect_from:
- /docs/api/python/data_ingestion
- /docs/api/python/data_ingestion/
- /docs/clients/python/data_ingestion
title: Data Ingestion
---

This page contains examples for data ingestion to Python using DuckDB. First, import the DuckDB page:

```python
import duckdb
```

Then, proceed with any of the following sections.

## CSV Files

CSV files can be read using the `read_csv` function, called either from within Python or directly from within SQL. By default, the `read_csv` function attempts to auto-detect the CSV settings by sampling from the provided file.

Read from a file using fully auto-detected settings:

```python
duckdb.read_csv("example.csv")
```

Read multiple CSV files from a folder:

```python
duckdb.read_csv("folder/*.csv")
```

Specify options on how the CSV is formatted internally:

```python
duckdb.read_csv("example.csv", header = False, sep = ",")
```

Override types of the first two columns:

```python
duckdb.read_csv("example.csv", dtype = ["int", "varchar"])
```

Directly read a CSV file from within SQL:

```python
duckdb.sql("SELECT * FROM 'example.csv'")
```

Call `read_csv` from within SQL:

```python
duckdb.sql("SELECT * FROM read_csv('example.csv')")
```

See the [CSV Import]({% link docs/stable/data/csv/overview.md %}) page for more information.

## Parquet Files

Parquet files can be read using the `read_parquet` function, called either from within Python or directly from within SQL.

Read from a single Parquet file:

```python
duckdb.read_parquet("example.parquet")
```

Read multiple Parquet files from a folder:

```python
duckdb.read_parquet("folder/*.parquet")
```

Read a Parquet file over [https]({% link docs/stable/core_extensions/httpfs/overview.md %}):

```python
duckdb.read_parquet("https://some.url/some_file.parquet")
```

Read a list of Parquet files:

```python
duckdb.read_parquet(["file1.parquet", "file2.parquet", "file3.parquet"])
```

Directly read a Parquet file from within SQL:

```python
duckdb.sql("SELECT * FROM 'example.parquet'")
```

Call `read_parquet` from within SQL:

```python
duckdb.sql("SELECT * FROM read_parquet('example.parquet')")
```

See the [Parquet Loading]({% link docs/stable/data/parquet/overview.md %}) page for more information.

## JSON Files

JSON files can be read using the `read_json` function, called either from within Python or directly from within SQL. By default, the `read_json` function will automatically detect if a file contains newline-delimited JSON or regular JSON, and will detect the schema of the objects stored within the JSON file.

Read from a single JSON file:

```python
duckdb.read_json("example.json")
```

Read multiple JSON files from a folder:

```python
duckdb.read_json("folder/*.json")
```

Directly read a JSON file from within SQL:

```python
duckdb.sql("SELECT * FROM 'example.json'")
```

Call `read_json` from within SQL:

```python
duckdb.sql("SELECT * FROM read_json_auto('example.json')")
```

## Directly Accessing DataFrames and Arrow Objects

DuckDB is automatically able to query certain Python variables by referring to their variable name (as if it was a table).
These types include the following: Pandas DataFrame, Polars DataFrame, Polars LazyFrame, NumPy arrays, [relations]({% link docs/stable/clients/python/relational_api.md %}), and Arrow objects.

Only variables that are visible to Python code at the location of the `sql()` or `execute()` call can be used in this manner.
Accessing these variables is made possible by [replacement scans]({% link docs/stable/clients/c/replacement_scans.md %}). To disable replacement scans entirely, use:

```sql
SET python_enable_replacements = false;
```

DuckDB supports querying multiple types of Apache Arrow objects including [tables](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html), [datasets](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Dataset.html), [RecordBatchReaders](https://arrow.apache.org/docs/python/generated/pyarrow.ipc.RecordBatchStreamReader.html), and [scanners](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Scanner.html). See the Python [guides]({% link docs/stable/guides/overview.md %}#python-client) for more examples.

```python
import duckdb
import pandas as pd

test_df = pd.DataFrame.from_dict({"i": [1, 2, 3, 4], "j": ["one", "two", "three", "four"]})
print(duckdb.sql("SELECT * FROM test_df").fetchall())
```

```text
[(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
```

DuckDB also supports “registering” a DataFrame or Arrow object as a virtual table, comparable to a SQL `VIEW`. This is useful when querying a DataFrame/Arrow object that is stored in another way (as a class variable, or a value in a dictionary). Below is a Pandas example:

If your Pandas DataFrame is stored in another location, here is an example of manually registering it:

```python
import duckdb
import pandas as pd

my_dictionary = {}
my_dictionary["test_df"] = pd.DataFrame.from_dict({"i": [1, 2, 3, 4], "j": ["one", "two", "three", "four"]})
duckdb.register("test_df_view", my_dictionary["test_df"])
print(duckdb.sql("SELECT * FROM test_df_view").fetchall())
```

```text
[(1, 'one'), (2, 'two'), (3, 'three'), (4, 'four')]
```

You can also create a persistent table in DuckDB from the contents of the DataFrame (or the view):

```python
# create a new table from the contents of a DataFrame
con.execute("CREATE TABLE test_df_table AS SELECT * FROM test_df")
# insert into an existing table from the contents of a DataFrame
con.execute("INSERT INTO test_df_table SELECT * FROM test_df")
```

### Pandas DataFrames – `object` Columns

`pandas.DataFrame` columns of an `object` dtype require some special care, since this stores values of arbitrary type.
To convert these columns to DuckDB, we first go through an analyze phase before converting the values.
In this analyze phase a sample of all the rows of the column are analyzed to determine the target type.
This sample size is by default set to 1000.
If the type picked during the analyze step is incorrect, this will result in `Invalid Input Error: Failed to cast value`, in which case you will need to increase the sample size.
The sample size can be changed by setting the `pandas_analyze_sample` config option.

```python
# example setting the sample size to 100k
duckdb.execute("SET GLOBAL pandas_analyze_sample = 100_000")
```

### Registering Objects

You can register Python objects as DuckDB tables using the [`DuckDBPyConnection.register()` function]({% link docs/stable/clients/python/reference/index.md %}#duckdb.DuckDBPyConnection.register).

The precedence of objects with the same name is as follows:

* Objects explicitly registered via `DuckDBPyConnection.register()`
* Native DuckDB tables and views
* [Replacement scans]({% link docs/stable/clients/c/replacement_scans.md %})

---
layout: docu
redirect_from:
- /docs/api/python/conversion
- /docs/api/python/conversion/
- /docs/api/python/result_conversion
- /docs/api/python/result_conversion/
- /docs/clients/python/conversion
title: Conversion between DuckDB and Python
---

This page documents the rules for converting [Python objects to DuckDB](#object-conversion-python-object-to-duckdb) and [DuckDB results to Python](#result-conversion-duckdb-results-to-python).

## Object Conversion: Python Object to DuckDB

This is a mapping of Python object types to DuckDB [Logical Types]({% link docs/stable/sql/data_types/overview.md %}):

* `None` → `NULL`
* `bool` → `BOOLEAN`
* `datetime.timedelta` → `INTERVAL`
* `str` → `VARCHAR`
* `bytearray` → `BLOB`
* `memoryview` → `BLOB`
* `decimal.Decimal` → `DECIMAL` / `DOUBLE`
* `uuid.UUID` → `UUID`

The rest of the conversion rules are as follows.

### `int`

Since integers can be of arbitrary size in Python, there is not a one-to-one conversion possible for ints.
Instead we perform these casts in order until one succeeds:

* `BIGINT`
* `INTEGER`
* `UBIGINT`
* `UINTEGER`
* `DOUBLE`

When using the DuckDB Value class, it's possible to set a target type, which will influence the conversion.

### `float`

These casts are tried in order until one succeeds:

* `DOUBLE`
* `FLOAT`

### `datetime.datetime`

For `datetime` we will check `pandas.isnull` if it's available and return `NULL` if it returns `true`.
We check against `datetime.datetime.min` and `datetime.datetime.max` to convert to `-inf` and `+inf` respectively.

If the `datetime` has tzinfo, we will use `TIMESTAMPTZ`, otherwise it becomes `TIMESTAMP`.

### `datetime.time`

If the `time` has tzinfo, we will use `TIMETZ`, otherwise it becomes `TIME`.

### `datetime.date`

`date` converts to the `DATE` type.
We check against `datetime.date.min` and `datetime.date.max` to convert to `-inf` and `+inf` respectively.

### `bytes`

`bytes` converts to `BLOB` by default, when it's used to construct a Value object of type `BITSTRING`, it maps to `BITSTRING` instead.

### `list`

`list` becomes a `LIST` type of the “most permissive” type of its children, for example:

```python
my_list_value = [
    12345,
    "test"
]
```

Will become `VARCHAR[]` because 12345 can convert to `VARCHAR` but `test` can not convert to `INTEGER`.

```sql
[12345, test]
```

### `dict`

The `dict` object can convert to either `STRUCT(...)` or `MAP(..., ...)` depending on its structure.
If the dict has a structure similar to:

```python
import duckdb

my_map_dict = {
    "key": [
        1, 2, 3
    ],
    "value": [
        "one", "two", "three"
    ]
}

duckdb.values(my_map_dict)
```

Then we'll convert it to a `MAP` of key-value pairs of the two lists zipped together.
The example above becomes a `MAP(INTEGER, VARCHAR)`:

```text
┌─────────────────────────┐
│ {1=one, 2=two, 3=three} │
│  map(integer, varchar)  │
├─────────────────────────┤
│ {1=one, 2=two, 3=three} │
└─────────────────────────┘
```

If the dict is returned by a [function]({% link docs/stable/clients/python/function.md %}), 
the function will return a `MAP`, therefore the function `return_type` has to be specified. Providing
a return type which cannot convert to `MAP` will raise an error:
```python
import duckdb
duckdb_conn = duckdb.connect()

def get_map() -> dict[str,list[str]|list[int]]:
    return {
        "key": [
            1, 2, 3
        ],
        "value": [
            "one", "two", "three"
        ]
    }

duckdb_conn.create_function("get_map", get_map, return_type=dict[int, str])

duckdb_conn.sql("select get_map()").show()

duckdb_conn.create_function("get_map_error", get_map)

duckdb_conn.sql("select get_map_error()").show()
```
 ```text
┌─────────────────────────┐
│        get_map()        │
│  map(bigint, varchar)   │
├─────────────────────────┤
│ {1=one, 2=two, 3=three} │
└─────────────────────────┘

ConversionException: Conversion Error: Type VARCHAR can't be cast as UNION(u1 VARCHAR[], u2 BIGINT[]). VARCHAR can't be implicitly cast to any of the union member types: VARCHAR[], BIGINT[]
```

> The names of the fields matter and the two lists need to have the same size.

Otherwise we'll try to convert it to a `STRUCT`.

```python
import duckdb

my_struct_dict = {
    1: "one",
    "2": 2,
    "three": [1, 2, 3],
    False: True
}

duckdb.values(my_struct_dict)
```
Becomes:

```text
┌────────────────────────────────────────────────────────────────────┐
│      {'1': 'one', '2': 2, 'three': [1, 2, 3], 'False': true}       │
│ struct("1" varchar, "2" integer, three integer[], "false" boolean) │
├────────────────────────────────────────────────────────────────────┤
│ {'1': one, '2': 2, 'three': [1, 2, 3], 'False': true}              │
└────────────────────────────────────────────────────────────────────┘
```

If the dict is returned by a [function]({% link docs/stable/clients/python/function.md %}), 
the function will return a `MAP`, due to [automatic conversion]({% link docs/stable/clients/python/types.md %}#dictkey_type-value_type).
To return a `STRUCT`, the `return_type` has to be provided:
```python
import duckdb
from duckdb.typing import BOOLEAN, INTEGER, VARCHAR
from duckdb import list_type, struct_type

duckdb_conn = duckdb.connect()

my_struct_dict = {
    1: "one",
    "2": 2,
    "three": [1, 2, 3],
    False: True
}

def get_struct() -> dict[str|int|bool,str|int|list[int]|bool]:
    return my_struct_dict

duckdb_conn.create_function("get_struct_as_map", get_struct)

duckdb_conn.sql("select get_struct_as_map()").show()

duckdb_conn.create_function("get_struct", get_struct, return_type=struct_type({
    1: VARCHAR,
    "2": INTEGER,
    "three": list_type(duckdb.typing.INTEGER),
    False: BOOLEAN
}))

duckdb_conn.sql("select get_struct()").show()
```

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                         get_struct_as_map()                                          │
│ map(union(u1 varchar, u2 bigint, u3 boolean), union(u1 varchar, u2 bigint, u3 bigint[], u4 boolean)) │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ {1=one, 2=2, three=[1, 2, 3], false=true}                                                            │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                            get_struct()                            │
│ struct("1" varchar, "2" integer, three integer[], "false" boolean) │
├────────────────────────────────────────────────────────────────────┤
│ {'1': one, '2': 2, 'three': [1, 2, 3], 'False': true}              │
└────────────────────────────────────────────────────────────────────┘
```
> Every `key` of the dictionary is converted to string.

### `tuple`

`tuple` converts to `LIST` by default, when it's used to construct a Value object of type `STRUCT` it will convert to `STRUCT` instead.

### `numpy.ndarray` and `numpy.datetime64`

`ndarray` and `datetime64` are converted by calling `tolist()` and converting the result of that.

## Result Conversion: DuckDB Results to Python

DuckDB's Python client provides multiple additional methods that can be used to efficiently retrieve data.

### NumPy

* `fetchnumpy()` fetches the data as a dictionary of NumPy arrays

### Pandas

* `df()` fetches the data as a Pandas DataFrame
* `fetchdf()` is an alias of `df()`
* `fetch_df()` is an alias of `df()`
* `fetch_df_chunk(vector_multiple)` fetches a portion of the results into a DataFrame. The number of rows returned in each chunk is the vector size (2048 by default) * vector_multiple (1 by default).

### Apache Arrow

* `arrow()` fetches the data as an [Arrow table](https://arrow.apache.org/docs/python/generated/pyarrow.Table.html)
* `fetch_arrow_table()` is an alias of `arrow()`
* `fetch_record_batch(chunk_size)` returns an [Arrow record batch reader](https://arrow.apache.org/docs/python/generated/pyarrow.ipc.RecordBatchStreamReader.html) with `chunk_size` rows per batch

### Polars

* `pl()` fetches the data as a Polars DataFrame

### Examples

Below are some examples using this functionality. See the [Python guides]({% link docs/stable/guides/overview.md %}#python-client) for more examples.

Fetch as Pandas DataFrame:

```python
df = con.execute("SELECT * FROM items").fetchdf()
print(df)
```

```text
       item   value  count
0     jeans    20.0      1
1    hammer    42.2      2
2    laptop  2000.0      1
3  chainsaw   500.0     10
4    iphone   300.0      2
```

Fetch as dictionary of NumPy arrays:

```python
arr = con.execute("SELECT * FROM items").fetchnumpy()
print(arr)
```

```text
{'item': masked_array(data=['jeans', 'hammer', 'laptop', 'chainsaw', 'iphone'],
             mask=[False, False, False, False, False],
       fill_value='?',
            dtype=object), 'value': masked_array(data=[20.0, 42.2, 2000.0, 500.0, 300.0],
             mask=[False, False, False, False, False],
       fill_value=1e+20), 'count': masked_array(data=[1, 2, 1, 10, 2],
             mask=[False, False, False, False, False],
       fill_value=999999,
            dtype=int32)}
```

Fetch as an Arrow table. Converting to Pandas afterwards just for pretty printing:

```python
tbl = con.execute("SELECT * FROM items").fetch_arrow_table()
print(tbl.to_pandas())
```

```text
       item    value  count
0     jeans    20.00      1
1    hammer    42.20      2
2    laptop  2000.00      1
3  chainsaw   500.00     10
4    iphone   300.00      2
```

---
layout: docu
redirect_from:
- /docs/api/python/dbapi
- /docs/api/python/dbapi/
- /docs/clients/python/dbapi
title: Python DB API
---

The standard DuckDB Python API provides a SQL interface compliant with the [DB-API 2.0 specification described by PEP 249](https://www.python.org/dev/peps/pep-0249/) similar to the [SQLite Python API](https://docs.python.org/3.7/library/sqlite3.html).

## Connection

To use the module, you must first create a `DuckDBPyConnection` object that represents a connection to a database.
This is done through the [`duckdb.connect`]({% link docs/stable/clients/python/reference/index.md %}#duckdb.connect) method.

The 'config' keyword argument can be used to provide a `dict` that contains key->value pairs referencing [settings]({% link docs/stable/configuration/overview.md %}#configuration-reference) understood by DuckDB.

### In-Memory Connection

The special value `:memory:` can be used to create an **in-memory database**. Note that for an in-memory database no data is persisted to disk (i.e., all data is lost when you exit the Python process).

#### Named In-memory Connections

The special value `:memory:` can also be postfixed with a name, for example: `:memory:conn3`.
When a name is provided, subsequent `duckdb.connect` calls will create a new connection to the same database, sharing the catalogs (views, tables, macros etc.).

Using `:memory:` without a name will always create a new and separate database instance.

### Default Connection

By default we create an (unnamed) **in-memory-database** that lives inside the `duckdb` module.
Every method of `DuckDBPyConnection` is also available on the `duckdb` module, this connection is what's used by these methods.

The special value `:default:` can be used to get this default connection.

### File-Based Connection

If the `database` is a file path, a connection to a persistent database is established.
If the file does not exist the file will be created (the extension of the file is irrelevant and can be `.db`, `.duckdb` or anything else).

#### `read_only` Connections

If you would like to connect in read-only mode, you can set the `read_only` flag to `True`. If the file does not exist, it is **not** created when connecting in read-only mode.
Read-only mode is required if multiple Python processes want to access the same database file at the same time.

```python
import duckdb

duckdb.execute("CREATE TABLE tbl AS SELECT 42 a")
con = duckdb.connect(":default:")
con.sql("SELECT * FROM tbl")
# or
duckdb.default_connection().sql("SELECT * FROM tbl")
```

```text
┌───────┐
│   a   │
│ int32 │
├───────┤
│    42 │
└───────┘
```

```python
import duckdb

# to start an in-memory database
con = duckdb.connect(database = ":memory:")
# to use a database file (not shared between processes)
con = duckdb.connect(database = "my-db.duckdb", read_only = False)
# to use a database file (shared between processes)
con = duckdb.connect(database = "my-db.duckdb", read_only = True)
# to explicitly get the default connection
con = duckdb.connect(database = ":default:")
```

If you want to create a second connection to an existing database, you can use the `cursor()` method. This might be useful for example to allow parallel threads running queries independently. A single connection is thread-safe but is locked for the duration of the queries, effectively serializing database access in this case.

Connections are closed implicitly when they go out of scope or if they are explicitly closed using `close()`. Once the last connection to a database instance is closed, the database instance is closed as well.

## Querying

SQL queries can be sent to DuckDB using the `execute()` method of connections. Once a query has been executed, results can be retrieved using the `fetchone` and `fetchall` methods on the connection. `fetchall` will retrieve all results and complete the transaction. `fetchone` will retrieve a single row of results each time that it is invoked until no more results are available. The transaction will only close once `fetchone` is called and there are no more results remaining (the return value will be `None`). As an example, in the case of a query only returning a single row, `fetchone` should be called once to retrieve the results and a second time to close the transaction. Below are some short examples:

```python
# create a table
con.execute("CREATE TABLE items (item VARCHAR, value DECIMAL(10, 2), count INTEGER)")
# insert two items into the table
con.execute("INSERT INTO items VALUES ('jeans', 20.0, 1), ('hammer', 42.2, 2)")

# retrieve the items again
con.execute("SELECT * FROM items")
print(con.fetchall())
# [('jeans', Decimal('20.00'), 1), ('hammer', Decimal('42.20'), 2)]

# retrieve the items one at a time
con.execute("SELECT * FROM items")
print(con.fetchone())
# ('jeans', Decimal('20.00'), 1)
print(con.fetchone())
# ('hammer', Decimal('42.20'), 2)
print(con.fetchone()) # This closes the transaction. Any subsequent calls to .fetchone will return None
# None
```

The `description` property of the connection object contains the column names as per the standard.

### Prepared Statements

DuckDB also supports [prepared statements]({% link docs/stable/sql/query_syntax/prepared_statements.md %}) in the API with the `execute` and `executemany` methods. The values may be passed as an additional parameter after a query that contains `?` or `$1` (dollar symbol and a number) placeholders. Using the `?` notation adds the values in the same sequence as passed within the Python parameter. Using the `$` notation allows for values to be reused within the SQL statement based on the number and index of the value found within the Python parameter. Values are converted according to the [conversion rules]({% link docs/stable/clients/python/conversion.md %}#object-conversion-python-object-to-duckdb).

Here are some examples. First, insert a row using a [prepared statement]({% link docs/stable/sql/query_syntax/prepared_statements.md %}):

```python
con.execute("INSERT INTO items VALUES (?, ?, ?)", ["laptop", 2000, 1])
```

Second, insert several rows using a [prepared statement]({% link docs/stable/sql/query_syntax/prepared_statements.md %}):

```python
con.executemany("INSERT INTO items VALUES (?, ?, ?)", [["chainsaw", 500, 10], ["iphone", 300, 2]] )
```

Query the database using a [prepared statement]({% link docs/stable/sql/query_syntax/prepared_statements.md %}):

```python
con.execute("SELECT item FROM items WHERE value > ?", [400])
print(con.fetchall())
```

```text
[('laptop',), ('chainsaw',)]
```

Query using the `$` notation for a [prepared statement]({% link docs/stable/sql/query_syntax/prepared_statements.md %}) and reused values:

```python
con.execute("SELECT $1, $1, $2", ["duck", "goose"])
print(con.fetchall())
```

```text
[('duck', 'duck', 'goose')]
```

> Warning Do *not* use `executemany` to insert large amounts of data into DuckDB. See the [data ingestion page]({% link docs/stable/clients/python/data_ingestion.md %}) for better options.

## Named Parameters

Besides the standard unnamed parameters, like `$1`, `$2` etc., it's also possible to supply named parameters, like `$my_parameter`.
When using named parameters, you have to provide a dictionary mapping of `str` to value in the `parameters` argument.
An example use is the following:

```python
import duckdb

res = duckdb.execute("""
    SELECT
        $my_param,
        $other_param,
        $also_param
    """,
    {
        "my_param": 5,
        "other_param": "DuckDB",
        "also_param": [42]
    }
).fetchall()
print(res)
```

```text
[(5, 'DuckDB', [42])]
```

---
layout: docu
redirect_from:
- /docs/api/python/relational_api
- /docs/api/python/relational_api/
- /docs/clients/python/relational_api

title: Relational API
---

<!-- Generated by scripts/generate_python_relational_docs.py -->

<!-- markdownlint-disable MD001 -->



The Relational API is an alternative API that can be used to incrementally construct queries. 
The API is centered around `DuckDBPyRelation` nodes. The relations can be seen as symbolic representations of SQL queries. 

## Lazy Evaluation

The relations do not hold any data – and nothing is executed – until [a method that triggers execution](#output) is called.

For example, we create a relation, which loads 1 billion rows:

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("from range(1_000_000_000)")
```
At the moment of execution, `rel` does not hold any data and no data is retrieved from the database.

By calling `rel.show()` or simply printing `rel` on the terminal, the first 10K rows are fetched.
If there are more than 10K rows, the output window will show >9999 rows (as the amount of rows in the relation is unknown).

By calling an [output](#output) method, the data is retrieved and stored in the specified format:

```python
rel.to_table("example_rel")

# 100% ▕████████████████████████████████████████████████████████████▏ 
```



## Relation Creation 

This section contains the details on how a relation is created.         The methods are [lazy evaluated](#lazy-evaluation).

| Name | Description |
|:--|:-------|
| [`from_arrow`](#from_arrow) | Create a relation object from an Arrow object |
| [`from_csv_auto`](#from_csv_auto) | Create a relation object from the CSV file in 'name' |
| [`from_df`](#from_df) | Create a relation object from the DataFrame in df |
| [`from_parquet`](#from_parquet) | Create a relation object from the Parquet files |
| [`from_query`](#from_query) | Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is. |
| [`query`](#query) | Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is. |
| [`read_csv`](#read_csv) | Create a relation object from the CSV file in 'name' |
| [`read_json`](#read_json) | Create a relation object from the JSON file in 'name' |
| [`read_parquet`](#read_parquet) | Create a relation object from the Parquet files |
| [`sql`](#sql) | Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is. |
| [`table`](#table) | Create a relation object for the named table |
| [`table_function`](#table_function) | Create a relation object from the named table function with given parameters |
| [`values`](#values) | Create a relation object from the passed values |
| [`view`](#view) | Create a relation object for the named view |

#### `from_arrow`

##### Signature

```python
from_arrow(self: _duckdb.DuckDBPyConnection, arrow_object: object) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from an Arrow object

##### Parameters

- **arrow_object** : pyarrow.Table, pyarrow.RecordBatch
                            
	Arrow object to create a relation from

##### Example

```python
import duckdb
import pyarrow as pa

ids = pa.array([1], type=pa.int8())
texts = pa.array(['a'], type=pa.string())
example_table = pa.table([ids, texts], names=["id", "text"])

duckdb_conn = duckdb.connect()

rel = duckdb_conn.from_arrow(example_table)

rel.show()
```

##### Result

```text
┌──────┬─────────┐
│  id  │  text   │
│ int8 │ varchar │
├──────┼─────────┤
│    1 │ a       │
└──────┴─────────┘
```

----

#### `from_csv_auto`

##### Signature

```python
from_csv_auto(self: _duckdb.DuckDBPyConnection, path_or_buffer: object, **kwargs) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the CSV file in 'name'

**Aliases**: [`read_csv`](#read_csv)

##### Parameters

- **path_or_buffer** : Union[str, StringIO, TextIOBase]
                            
	Path to the CSV file or buffer to read from.
- **header** : Optional[bool], Optional[int]
                            
	Row number(s) to use as the column names, or None if no header.
- **compression** : Optional[str]
                            
	Compression type (e.g., 'gzip', 'bz2').
- **sep** : Optional[str]
                            
	Delimiter to use; defaults to comma.
- **delimiter** : Optional[str]
                            
	Alternative delimiter to use.
- **dtype** : Optional[Dict[str, str]], Optional[List[str]]
                            
	Data types for columns.
- **na_values** : Optional[str], Optional[List[str]]
                            
	Additional strings to recognize as NA/NaN.
- **skiprows** : Optional[int]
                            
	Number of rows to skip at the start.
- **quotechar** : Optional[str]
                            
	Character used to quote fields.
- **escapechar** : Optional[str]
                            
	Character used to escape delimiter or quote characters.
- **encoding** : Optional[str]
                            
	Encoding to use for UTF when reading/writing.
- **parallel** : Optional[bool]
                            
	Enable parallel reading.
- **date_format** : Optional[str]
                            
	Format to parse dates.
- **timestamp_format** : Optional[str]
                            
	Format to parse timestamps.
- **sample_size** : Optional[int]
                            
	Number of rows to sample for schema inference.
- **all_varchar** : Optional[bool]
                            
	Treat all columns as VARCHAR.
- **normalize_names** : Optional[bool]
                            
	Normalize column names to lowercase.
- **null_padding** : Optional[bool]
                            
	Enable null padding for rows with missing columns.
- **names** : Optional[List[str]]
                            
	List of column names to use.
- **lineterminator** : Optional[str]
                            
	Character to break lines on.
- **columns** : Optional[Dict[str, str]]
                            
	Column mapping for schema.
- **auto_type_candidates** : Optional[List[str]]
                            
	List of columns for automatic type inference.
- **max_line_size** : Optional[int]
                            
	Maximum line size in bytes.
- **ignore_errors** : Optional[bool]
                            
	Ignore parsing errors.
- **store_rejects** : Optional[bool]
                            
	Store rejected rows.
- **rejects_table** : Optional[str]
                            
	Table name to store rejected rows.
- **rejects_scan** : Optional[str]
                            
	Scan to use for rejects.
- **rejects_limit** : Optional[int]
                            
	Limit number of rejects stored.
- **force_not_null** : Optional[List[str]]
                            
	List of columns to force as NOT NULL.
- **buffer_size** : Optional[int]
                            
	Buffer size in bytes.
- **decimal** : Optional[str]
                            
	Character to recognize as decimal point.
- **allow_quoted_nulls** : Optional[bool]
                            
	Allow quoted NULL values.
- **filename** : Optional[bool], Optional[str]
                            
	Add filename column or specify filename.
- **hive_partitioning** : Optional[bool]
                            
	Enable Hive-style partitioning.
- **union_by_name** : Optional[bool]
                            
	Union files by column name instead of position.
- **hive_types** : Optional[Dict[str, str]]
                            
	Hive types for columns.
- **hive_types_autocast** : Optional[bool]
                            
	Automatically cast Hive types.
- **connection** : DuckDBPyConnection
                            
	DuckDB connection to use.

##### Example

```python
import csv
import duckdb

duckdb_conn = duckdb.connect()

with open('code_example.csv', 'w', newline='') as csvfile:
    fieldnames = ['id', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'id': '1', 'text': 'a'})

rel = duckdb_conn.from_csv_auto("code_example.csv")

rel.show()
```

##### Result

```text
┌───────┬─────────┐
│  id   │  text   │
│ int64 │ varchar │
├───────┼─────────┤
│     1 │ a       │
└───────┴─────────┘
```

----

#### `from_df`

##### Signature

```python
from_df(self: _duckdb.DuckDBPyConnection, df: pandas.DataFrame) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the DataFrame in df

##### Parameters

- **df** : pandas.DataFrame
                            
	A pandas DataFrame to be converted into a DuckDB relation.

##### Example

```python
import duckdb
import pandas as pd

df = pd.DataFrame(data = {'id': [1], "text":["a"]})

duckdb_conn = duckdb.connect()

rel = duckdb_conn.from_df(df)

rel.show()
```

##### Result

```text
┌───────┬─────────┐
│  id   │  text   │
│ int64 │ varchar │
├───────┼─────────┤
│     1 │ a       │
└───────┴─────────┘
```

----

#### `from_parquet`

##### Signature

```python
from_parquet(*args, **kwargs)
Overloaded function.

1. from_parquet(self: _duckdb.DuckDBPyConnection, file_glob: str, binary_as_string: bool = False, *, file_row_number: bool = False, filename: bool = False, hive_partitioning: bool = False, union_by_name: bool = False, compression: object = None) -> _duckdb.DuckDBPyRelation

Create a relation object from the Parquet files in file_glob

2. from_parquet(self: _duckdb.DuckDBPyConnection, file_globs: collections.abc.Sequence[str], binary_as_string: bool = False, *, file_row_number: bool = False, filename: bool = False, hive_partitioning: bool = False, union_by_name: bool = False, compression: object = None) -> _duckdb.DuckDBPyRelation

Create a relation object from the Parquet files in file_globs
```

##### Description

Create a relation object from the Parquet files

**Aliases**: [`read_parquet`](#read_parquet)

##### Parameters

- **file_glob** : str
                            
	File path or glob pattern pointing to Parquet files to be read.
- **binary_as_string** : bool, default: False
                            
	Interpret binary columns as strings instead of blobs.
- **file_row_number** : bool, default: False
                            
	Add a column containing the row number within each file.
- **filename** : bool, default: False
                            
	Add a column containing the name of the file each row came from.
- **hive_partitioning** : bool, default: False
                            
	Enable automatic detection of Hive-style partitions in file paths.
- **union_by_name** : bool, default: False
                            
	Union Parquet files by matching column names instead of positions.
- **compression** : object
                            
	Optional compression codec to use when reading the Parquet files.

##### Example

```python
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

ids = pa.array([1], type=pa.int8())
texts = pa.array(['a'], type=pa.string())
example_table = pa.table([ids, texts], names=["id", "text"])

pq.write_table(example_table, "code_example.parquet")

duckdb_conn = duckdb.connect()

rel = duckdb_conn.from_parquet("code_example.parquet")

rel.show()
```

##### Result

```text
┌──────┬─────────┐
│  id  │  text   │
│ int8 │ varchar │
├──────┼─────────┤
│    1 │ a       │
└──────┴─────────┘
```

----

#### `from_query`

##### Signature

```python
from_query(self: _duckdb.DuckDBPyConnection, query: object, *, alias: str = '', params: object = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is.

**Aliases**: [`query`](#query), [`sql`](#sql)

##### Parameters

- **query** : object
                            
	The SQL query or subquery to be executed and converted into a relation.
- **alias** : str, default: ''
                            
	Optional alias name to assign to the resulting relation.
- **params** : object
                            
	Optional query parameters to be used in the SQL query.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.from_query("from range(1,2) tbl(id)")

rel.show()
```

##### Result

```text
┌───────┐
│  id   │
│ int64 │
├───────┤
│     1 │
└───────┘
```

----

#### `query`

##### Signature

```python
query(self: _duckdb.DuckDBPyConnection, query: object, *, alias: str = '', params: object = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is.

**Aliases**: [`from_query`](#from_query), [`sql`](#sql)

##### Parameters

- **query** : object
                            
	The SQL query or subquery to be executed and converted into a relation.
- **alias** : str, default: ''
                            
	Optional alias name to assign to the resulting relation.
- **params** : object
                            
	Optional query parameters to be used in the SQL query.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.query("from range(1,2) tbl(id)")

rel.show()
```

##### Result

```text
┌───────┐
│  id   │
│ int64 │
├───────┤
│     1 │
└───────┘
```

----

#### `read_csv`

##### Signature

```python
read_csv(self: _duckdb.DuckDBPyConnection, path_or_buffer: object, **kwargs) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the CSV file in 'name'

**Aliases**: [`from_csv_auto`](#from_csv_auto)

##### Parameters

- **path_or_buffer** : Union[str, StringIO, TextIOBase]
                            
	Path to the CSV file or buffer to read from.
- **header** : Optional[bool], Optional[int]
                            
	Row number(s) to use as the column names, or None if no header.
- **compression** : Optional[str]
                            
	Compression type (e.g., 'gzip', 'bz2').
- **sep** : Optional[str]
                            
	Delimiter to use; defaults to comma.
- **delimiter** : Optional[str]
                            
	Alternative delimiter to use.
- **dtype** : Optional[Dict[str, str]], Optional[List[str]]
                            
	Data types for columns.
- **na_values** : Optional[str], Optional[List[str]]
                            
	Additional strings to recognize as NA/NaN.
- **skiprows** : Optional[int]
                            
	Number of rows to skip at the start.
- **quotechar** : Optional[str]
                            
	Character used to quote fields.
- **escapechar** : Optional[str]
                            
	Character used to escape delimiter or quote characters.
- **encoding** : Optional[str]
                            
	Encoding to use for UTF when reading/writing.
- **parallel** : Optional[bool]
                            
	Enable parallel reading.
- **date_format** : Optional[str]
                            
	Format to parse dates.
- **timestamp_format** : Optional[str]
                            
	Format to parse timestamps.
- **sample_size** : Optional[int]
                            
	Number of rows to sample for schema inference.
- **all_varchar** : Optional[bool]
                            
	Treat all columns as VARCHAR.
- **normalize_names** : Optional[bool]
                            
	Normalize column names to lowercase.
- **null_padding** : Optional[bool]
                            
	Enable null padding for rows with missing columns.
- **names** : Optional[List[str]]
                            
	List of column names to use.
- **lineterminator** : Optional[str]
                            
	Character to break lines on.
- **columns** : Optional[Dict[str, str]]
                            
	Column mapping for schema.
- **auto_type_candidates** : Optional[List[str]]
                            
	List of columns for automatic type inference.
- **max_line_size** : Optional[int]
                            
	Maximum line size in bytes.
- **ignore_errors** : Optional[bool]
                            
	Ignore parsing errors.
- **store_rejects** : Optional[bool]
                            
	Store rejected rows.
- **rejects_table** : Optional[str]
                            
	Table name to store rejected rows.
- **rejects_scan** : Optional[str]
                            
	Scan to use for rejects.
- **rejects_limit** : Optional[int]
                            
	Limit number of rejects stored.
- **force_not_null** : Optional[List[str]]
                            
	List of columns to force as NOT NULL.
- **buffer_size** : Optional[int]
                            
	Buffer size in bytes.
- **decimal** : Optional[str]
                            
	Character to recognize as decimal point.
- **allow_quoted_nulls** : Optional[bool]
                            
	Allow quoted NULL values.
- **filename** : Optional[bool], Optional[str]
                            
	Add filename column or specify filename.
- **hive_partitioning** : Optional[bool]
                            
	Enable Hive-style partitioning.
- **union_by_name** : Optional[bool]
                            
	Union files by column name instead of position.
- **hive_types** : Optional[Dict[str, str]]
                            
	Hive types for columns.
- **hive_types_autocast** : Optional[bool]
                            
	Automatically cast Hive types.
- **connection** : DuckDBPyConnection
                            
	DuckDB connection to use.

##### Example

```python
import csv
import duckdb

duckdb_conn = duckdb.connect()

with open('code_example.csv', 'w', newline='') as csvfile:
    fieldnames = ['id', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'id': '1', 'text': 'a'})

rel = duckdb_conn.read_csv("code_example.csv")

rel.show()
```

##### Result

```text
┌───────┬─────────┐
│  id   │  text   │
│ int64 │ varchar │
├───────┼─────────┤
│     1 │ a       │
└───────┴─────────┘
```

----

#### `read_json`

##### Signature

```python
read_json(self: _duckdb.DuckDBPyConnection, path_or_buffer: object, *, columns: typing.Optional[object] = None, sample_size: typing.Optional[object] = None, maximum_depth: typing.Optional[object] = None, records: typing.Optional[str] = None, format: typing.Optional[str] = None, date_format: typing.Optional[object] = None, timestamp_format: typing.Optional[object] = None, compression: typing.Optional[object] = None, maximum_object_size: typing.Optional[object] = None, ignore_errors: typing.Optional[object] = None, convert_strings_to_integers: typing.Optional[object] = None, field_appearance_threshold: typing.Optional[object] = None, map_inference_threshold: typing.Optional[object] = None, maximum_sample_files: typing.Optional[object] = None, filename: typing.Optional[object] = None, hive_partitioning: typing.Optional[object] = None, union_by_name: typing.Optional[object] = None, hive_types: typing.Optional[object] = None, hive_types_autocast: typing.Optional[object] = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the JSON file in 'name'

##### Parameters

- **path_or_buffer** : object
                            
	File path or file-like object containing JSON data to be read.
- **columns** : object
                            
	Optional list of column names to project from the JSON data.
- **sample_size** : object
                            
	Number of rows to sample for inferring JSON schema.
- **maximum_depth** : object
                            
	Maximum depth to which JSON objects should be parsed.
- **records** : str
                            
	Format string specifying whether JSON is in records mode.
- **format** : str
                            
	Format of the JSON data (e.g., 'auto', 'newline_delimited').
- **date_format** : object
                            
	Format string for parsing date fields.
- **timestamp_format** : object
                            
	Format string for parsing timestamp fields.
- **compression** : object
                            
	Compression codec used on the JSON data (e.g., 'gzip').
- **maximum_object_size** : object
                            
	Maximum size in bytes for individual JSON objects.
- **ignore_errors** : object
                            
	If True, skip over JSON records with parsing errors.
- **convert_strings_to_integers** : object
                            
	If True, attempt to convert strings to integers where appropriate.
- **field_appearance_threshold** : object
                            
	Threshold for inferring optional fields in nested JSON.
- **map_inference_threshold** : object
                            
	Threshold for inferring maps from JSON object patterns.
- **maximum_sample_files** : object
                            
	Maximum number of files to sample for schema inference.
- **filename** : object
                            
	If True, include a column with the source filename for each row.
- **hive_partitioning** : object
                            
	If True, enable Hive partitioning based on directory structure.
- **union_by_name** : object
                            
	If True, align JSON columns by name instead of position.
- **hive_types** : object
                            
	If True, use Hive types from directory structure for schema.
- **hive_types_autocast** : object
                            
	If True, automatically cast data types to match Hive types.

##### Example

```python
import duckdb
import json

with open("code_example.json", mode="w") as f:
    json.dump([{'id': 1, "text":"a"}], f)
    
duckdb_conn = duckdb.connect()

rel = duckdb_conn.read_json("code_example.json")

rel.show()
```

##### Result

```text
┌───────┬─────────┐
│  id   │  text   │
│ int64 │ varchar │
├───────┼─────────┤
│     1 │ a       │
└───────┴─────────┘
```

----

#### `read_parquet`

##### Signature

```python
read_parquet(*args, **kwargs)
Overloaded function.

1. read_parquet(self: _duckdb.DuckDBPyConnection, file_glob: str, binary_as_string: bool = False, *, file_row_number: bool = False, filename: bool = False, hive_partitioning: bool = False, union_by_name: bool = False, compression: object = None) -> _duckdb.DuckDBPyRelation

Create a relation object from the Parquet files in file_glob

2. read_parquet(self: _duckdb.DuckDBPyConnection, file_globs: collections.abc.Sequence[str], binary_as_string: bool = False, *, file_row_number: bool = False, filename: bool = False, hive_partitioning: bool = False, union_by_name: bool = False, compression: object = None) -> _duckdb.DuckDBPyRelation

Create a relation object from the Parquet files in file_globs
```

##### Description

Create a relation object from the Parquet files

**Aliases**: [`from_parquet`](#from_parquet)

##### Parameters

- **file_glob** : str
                            
	File path or glob pattern pointing to Parquet files to be read.
- **binary_as_string** : bool, default: False
                            
	Interpret binary columns as strings instead of blobs.
- **file_row_number** : bool, default: False
                            
	Add a column containing the row number within each file.
- **filename** : bool, default: False
                            
	Add a column containing the name of the file each row came from.
- **hive_partitioning** : bool, default: False
                            
	Enable automatic detection of Hive-style partitions in file paths.
- **union_by_name** : bool, default: False
                            
	Union Parquet files by matching column names instead of positions.
- **compression** : object
                            
	Optional compression codec to use when reading the Parquet files.

##### Example

```python
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

ids = pa.array([1], type=pa.int8())
texts = pa.array(['a'], type=pa.string())
example_table = pa.table([ids, texts], names=["id", "text"])

pq.write_table(example_table, "code_example.parquet")

duckdb_conn = duckdb.connect()

rel = duckdb_conn.read_parquet("code_example.parquet")

rel.show()
```

##### Result

```text
┌──────┬─────────┐
│  id  │  text   │
│ int8 │ varchar │
├──────┼─────────┤
│    1 │ a       │
└──────┴─────────┘
```

----

#### `sql`

##### Signature

```python
sql(self: _duckdb.DuckDBPyConnection, query: object, *, alias: str = '', params: object = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Run a SQL query. If it is a SELECT statement, create a relation object from the given SQL query, otherwise run the query as-is.

**Aliases**: [`from_query`](#from_query), [`query`](#query)

##### Parameters

- **query** : object
                            
	The SQL query or subquery to be executed and converted into a relation.
- **alias** : str, default: ''
                            
	Optional alias name to assign to the resulting relation.
- **params** : object
                            
	Optional query parameters to be used in the SQL query.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("from range(1,2) tbl(id)")

rel.show()
```

##### Result

```text
┌───────┐
│  id   │
│ int64 │
├───────┤
│     1 │
└───────┘
```

----

#### `table`

##### Signature

```python
table(self: _duckdb.DuckDBPyConnection, table_name: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object for the named table

##### Parameters

- **table_name** : str
                            
	Name of the table to create a relation from.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

duckdb_conn.sql("create table code_example as select * from range(1,2) tbl(id)")

rel = duckdb_conn.table("code_example")

rel.show()
```

##### Result

```text
┌───────┐
│  id   │
│ int64 │
├───────┤
│     1 │
└───────┘
```

----

#### `table_function`

##### Signature

```python
table_function(self: _duckdb.DuckDBPyConnection, name: str, parameters: object = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the named table function with given parameters

##### Parameters

- **name** : str
                            
	Name of the table function to call.
- **parameters** : object
                            
	Optional parameters to pass to the table function.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

duckdb_conn.sql("""
    create macro get_record_for(x) as table
    select x*range from range(1,2)
""")

rel = duckdb_conn.table_function(name="get_record_for", parameters=[1])

rel.show()
```

##### Result

```text
┌───────────────┐
│ (1 * "range") │
│     int64     │
├───────────────┤
│             1 │
└───────────────┘
```

----

#### `values`

##### Signature

```python
values(self: _duckdb.DuckDBPyConnection, *args) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object from the passed values

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.values([1, 'a'])

rel.show()
```

##### Result

```text
┌───────┬─────────┐
│ col0  │  col1   │
│ int32 │ varchar │
├───────┼─────────┤
│     1 │ a       │
└───────┴─────────┘
```

----

#### `view`

##### Signature

```python
view(self: _duckdb.DuckDBPyConnection, view_name: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Create a relation object for the named view

##### Parameters

- **view_name** : str
                            
	Name of the view to create a relation from.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

duckdb_conn.sql("create table code_example as select * from range(1,2) tbl(id)")

rel = duckdb_conn.view("code_example")

rel.show()
```

##### Result

```text
┌───────┐
│  id   │
│ int64 │
├───────┤
│     1 │
└───────┘
```

## Relation Definition Details 

This section contains the details on how to inspect a relation.

| Name | Description |
|:--|:-------|
| [`alias`](#alias) | Get the name of the current alias |
| [`columns`](#columns) | Return a list containing the names of the columns of the relation. |
| [`describe`](#describe) | Gives basic statistics (e.g., min, max) and if NULL exists for each column of the relation. |
| [`description`](#description) | Return the description of the result |
| [`dtypes`](#dtypes) | Return a list containing the types of the columns of the relation. |
| [`explain`](#explain) | explain(self: _duckdb.DuckDBPyRelation, type: _duckdb.ExplainType = 'standard') -> str |
| [`query`](#query-1) | Run the given SQL query in sql_query on the view named virtual_table_name that refers to the relation object |
| [`set_alias`](#set_alias) | Rename the relation object to new alias |
| [`shape`](#shape) | Tuple of # of rows, # of columns in relation. |
| [`show`](#show) | Display a summary of the data |
| [`sql_query`](#sql_query) | Get the SQL query that is equivalent to the relation |
| [`type`](#type) | Get the type of the relation. |
| [`types`](#types) | Return a list containing the types of the columns of the relation. |

#### `alias`

##### Description

Get the name of the current alias

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.alias
```


##### Result

```text
unnamed_relation_43c808c247431be5
```

----

#### `columns`

##### Description

Return a list containing the names of the columns of the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.columns
```


##### Result

```text
 ['id', 'description', 'value', 'created_timestamp']
```

----

#### `describe`

##### Signature

```python
describe(self: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Gives basic statistics (e.g., min, max) and if NULL exists for each column of the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.describe()
```


##### Result

```text
┌─────────┬──────────────────────────────────────┬─────────────────┬────────────────────┬────────────────────────────┐
│  aggr   │                  id                  │   description   │       value        │     created_timestamp      │
│ varchar │               varchar                │     varchar     │       double       │          varchar           │
├─────────┼──────────────────────────────────────┼─────────────────┼────────────────────┼────────────────────────────┤
│ count   │ 9                                    │ 9               │                9.0 │ 9                          │
│ mean    │ NULL                                 │ NULL            │                5.0 │ NULL                       │
│ stddev  │ NULL                                 │ NULL            │ 2.7386127875258306 │ NULL                       │
│ min     │ 08fdcbf8-4e53-4290-9e81-423af263b518 │ value is even   │                1.0 │ 2025-04-09 15:41:20.642+02 │
│ max     │ fb10390e-fad5-4694-91cb-e82728cb6f9f │ value is uneven │                9.0 │ 2025-04-09 15:49:20.642+02 │
│ median  │ NULL                                 │ NULL            │                5.0 │ NULL                       │
└─────────┴──────────────────────────────────────┴─────────────────┴────────────────────┴────────────────────────────┘ 
```

----

#### `description`

##### Description

Return the description of the result

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.description
```


##### Result

```text
[('id', 'UUID', None, None, None, None, None),
 ('description', 'STRING', None, None, None, None, None),
 ('value', 'NUMBER', None, None, None, None, None),
 ('created_timestamp', 'DATETIME', None, None, None, None, None)]  
```

----

#### `dtypes`

##### Description

Return a list containing the types of the columns of the relation.

**Aliases**: [`types`](#types)

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.dtypes
```


##### Result

```text
 [UUID, VARCHAR, BIGINT, TIMESTAMP WITH TIME ZONE]
```

----

#### `explain`

##### Description

explain(self: _duckdb.DuckDBPyRelation, type: _duckdb.ExplainType = 'standard') -> str

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.explain()
```


##### Result

```text
┌───────────────────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             id            │
│        description        │
│           value           │
│     created_timestamp     │
│                           │
│          ~9 Rows          │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           RANGE           │
│    ────────────────────   │
│      Function: RANGE      │
│                           │
│          ~9 Rows          │
└───────────────────────────┘

```

----

#### `query`

##### Signature

```python
query(self: _duckdb.DuckDBPyRelation, virtual_table_name: str, sql_query: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Run the given SQL query in sql_query on the view named virtual_table_name that refers to the relation object

##### Parameters

- **virtual_table_name** : str
                            
	The name to assign to the current relation when referenced in the SQL query.
- **sql_query** : str
                            
	The SQL query string that uses the virtual table name to query the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.query(virtual_table_name="rel_view", sql_query="from rel")

duckdb_conn.sql("show rel_view")
```


##### Result

```text
┌───────────────────┬──────────────────────────┬─────────┬─────────┬─────────┬─────────┐
│    column_name    │       column_type        │  null   │   key   │ default │  extra  │
│      varchar      │         varchar          │ varchar │ varchar │ varchar │ varchar │
├───────────────────┼──────────────────────────┼─────────┼─────────┼─────────┼─────────┤
│ id                │ UUID                     │ YES     │ NULL    │ NULL    │ NULL    │
│ description       │ VARCHAR                  │ YES     │ NULL    │ NULL    │ NULL    │
│ value             │ BIGINT                   │ YES     │ NULL    │ NULL    │ NULL    │
│ created_timestamp │ TIMESTAMP WITH TIME ZONE │ YES     │ NULL    │ NULL    │ NULL    │
└───────────────────┴──────────────────────────┴─────────┴─────────┴─────────┴─────────┘
```

----

#### `set_alias`

##### Signature

```python
set_alias(self: _duckdb.DuckDBPyRelation, alias: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Rename the relation object to new alias

##### Parameters

- **alias** : str
                            
	The alias name to assign to the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.set_alias('abc').select('abc.id')
```


##### Result

```text
In the SQL query, the alias will be `abc`
```

----

#### `shape`

##### Description

Tuple of # of rows, # of columns in relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.shape
```


##### Result

```text
(9, 4)
```

----

#### `show`

##### Signature

```python
show(self: _duckdb.DuckDBPyRelation, *, max_width: typing.Optional[typing.SupportsInt] = None, max_rows: typing.Optional[typing.SupportsInt] = None, max_col_width: typing.Optional[typing.SupportsInt] = None, null_value: typing.Optional[str] = None, render_mode: object = None) -> None
```

##### Description

Display a summary of the data

##### Parameters

- **max_width** : int
                            
	Maximum display width for the entire output in characters.
- **max_rows** : int
                            
	Maximum number of rows to display.
- **max_col_width** : int
                            
	Maximum number of characters to display per column.
- **null_value** : str
                            
	String to display in place of NULL values.
- **render_mode** : object
                            
	Render mode for displaying the output.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.show()
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 642ea3d7-793d-4867-a759-91c1226c25a0 │ value is uneven │     1 │ 2025-04-09 15:41:20.642+02 │
│ 6817dd31-297c-40a8-8e40-8521f00b2d08 │ value is even   │     2 │ 2025-04-09 15:42:20.642+02 │
│ 45143f9a-e16e-4e59-91b2-3a0800eed6d6 │ value is uneven │     3 │ 2025-04-09 15:43:20.642+02 │
│ fb10390e-fad5-4694-91cb-e82728cb6f9f │ value is even   │     4 │ 2025-04-09 15:44:20.642+02 │
│ 111ced5c-9155-418e-b087-c331b814db90 │ value is uneven │     5 │ 2025-04-09 15:45:20.642+02 │
│ 66a870a6-aef0-4085-87d5-5d1b35d21c66 │ value is even   │     6 │ 2025-04-09 15:46:20.642+02 │
│ a7e8e796-bca0-44cd-a269-1d71090fb5cc │ value is uneven │     7 │ 2025-04-09 15:47:20.642+02 │
│ 74908d48-7f2d-4bdd-9c92-1e7920b115b5 │ value is even   │     8 │ 2025-04-09 15:48:20.642+02 │
│ 08fdcbf8-4e53-4290-9e81-423af263b518 │ value is uneven │     9 │ 2025-04-09 15:49:20.642+02 │
└──────────────────────────────────────┴─────────────────┴───────┴────────────────────────────┘
```

----

#### `sql_query`

##### Signature

```python
sql_query(self: _duckdb.DuckDBPyRelation) -> str
```

##### Description

Get the SQL query that is equivalent to the relation

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.sql_query()
```


##### Result

```sql
SELECT 
    gen_random_uuid() AS id, 
    concat('value is ', CASE  WHEN ((mod("range", 2) = 0)) THEN ('even') ELSE 'uneven' END) AS description, 
    "range" AS "value", 
    (now() + CAST(concat("range", ' ', 'minutes') AS INTERVAL)) AS created_timestamp 
FROM "range"(1, 10)
```

----

#### `type`

##### Description

Get the type of the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.type
```


##### Result

```text
QUERY_RELATION
```

----

#### `types`

##### Description

Return a list containing the types of the columns of the relation.

**Aliases**: [`dtypes`](#dtypes)

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.types
```


##### Result

```text
[UUID, VARCHAR, BIGINT, TIMESTAMP WITH TIME ZONE]
```

## Transformation 

This section contains the methods which can be used to chain queries.        The methods are [lazy evaluated](#lazy-evaluation).

| Name | Description |
|:--|:-------|
| [`aggregate`](#aggregate) | Compute the aggregate aggr_expr by the optional groups group_expr on the relation |
| [`apply`](#apply) | Compute the function of a single column or a list of columns by the optional groups on the relation |
| [`cross`](#cross) | Create cross/cartesian product of two relational objects |
| [`except_`](#except_) | Create the set except of this relation object with another relation object in other_rel |
| [`filter`](#filter) | Filter the relation object by the filter in filter_expr |
| [`insert`](#insert) | Inserts the given values into the relation |
| [`insert_into`](#insert_into) | Inserts the relation object into an existing table named table_name |
| [`intersect`](#intersect) | Create the set intersection of this relation object with another relation object in other_rel |
| [`join`](#join) | Join the relation object with another relation object in other_rel using the join condition expression in join_condition. Types supported are 'inner', 'left', 'right', 'outer', 'semi' and 'anti' |
| [`limit`](#limit) | Only retrieve the first n rows from this relation object, starting at offset |
| [`map`](#map) | Calls the passed function on the relation |
| [`order`](#order) | Reorder the relation object by order_expr |
| [`project`](#project) | Project the relation object by the projection in project_expr |
| [`select`](#select) | Project the relation object by the projection in project_expr |
| [`sort`](#sort) | Reorder the relation object by the provided expressions |
| [`union`](#union) | Create the set union of this relation object with another relation object in other_rel |
| [`update`](#update) | Update the given relation with the provided expressions |

#### `aggregate`

##### Signature

```python
aggregate(self: _duckdb.DuckDBPyRelation, aggr_expr: object, group_expr: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Compute the aggregate aggr_expr by the optional groups group_expr on the relation

##### Parameters

- **aggr_expr** : str, list[Expression]
                            
	The list of columns and aggregation functions.
- **group_expr** : str, default: ''
                            
	The list of columns to be included in `group_by`. If `None`, `group by all` is applied.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.aggregate('max(value)')
```


##### Result

```text
┌──────────────┐
│ max("value") │
│    int64     │
├──────────────┤
│            9 │
└──────────────┘
        
```

----

#### `apply`

##### Signature

```python
apply(self: _duckdb.DuckDBPyRelation, function_name: str, function_aggr: str, group_expr: str = '', function_parameter: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Compute the function of a single column or a list of columns by the optional groups on the relation

##### Parameters

- **function_name** : str
                            
	Name of the function to apply over the relation.
- **function_aggr** : str
                            
	The list of columns to apply the function over.
- **group_expr** : str, default: ''
                            
	Optional SQL expression for grouping.
- **function_parameter** : str, default: ''
                            
	Optional parameters to pass into the function.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.apply(
    function_name="count", 
    function_aggr="id", 
    group_expr="description",
    projected_columns="description"
)
```


##### Result

```text
┌─────────────────┬───────────┐
│   description   │ count(id) │
│     varchar     │   int64   │
├─────────────────┼───────────┤
│ value is uneven │         5 │
│ value is even   │         4 │
└─────────────────┴───────────┘
```

----

#### `cross`

##### Signature

```python
cross(self: _duckdb.DuckDBPyRelation, other_rel: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Create cross/cartesian product of two relational objects

##### Parameters

- **other_rel** : duckdb.duckdb.DuckDBPyRelation
                            
	Another relation to perform a cross product with.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.cross(other_rel=rel.set_alias("other_rel"))
```


##### Result

```text
┌─────────────────────────────┬─────────────────┬───────┬───────────────────────────┬──────────────────────────────────────┬─────────────────┬───────┬───────────────────────────┐
│             id              │   description   │ value │     created_timestamp     │                  id                  │   description   │ value │     created_timestamp     │
│            uuid             │     varchar     │ int64 │ timestamp with time zone  │                 uuid                 │     varchar     │ int64 │ timestamp with time zone  │
├─────────────────────────────┼─────────────────┼───────┼───────────────────────────┼──────────────────────────────────────┼─────────────────┼───────┼───────────────────────────┤
│ cb2b453f-1a06-4f5e-abe1-b…  │ value is uneven │     1 │ 2025-04-10 09:53:29.78+02 │ cb2b453f-1a06-4f5e-abe1-bfd413581bcf │ value is uneven │     1 │ 2025-04-10 09:53:29.78+02 │
...
```

----

#### `except_`

##### Signature

```python
except_(self: _duckdb.DuckDBPyRelation, other_rel: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Create the set except of this relation object with another relation object in other_rel

##### Parameters

- **other_rel** : duckdb.duckdb.DuckDBPyRelation
                            
	The relation to subtract from the current relation (set difference).

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.except_(other_rel=rel.set_alias("other_rel"))
```


##### Result

```text
The relation query is executed twice, therefore generating different ids and timestamps:
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ f69ed6dd-a7fe-4de2-b6af-1c2418096d69 │ value is uneven │     3 │ 2025-04-10 11:43:05.711+02 │
│ 08ad11dc-a9c2-4aaa-9272-760b27ad1f5d │ value is uneven │     7 │ 2025-04-10 11:47:05.711+02 │
...
```

----

#### `filter`

##### Signature

```python
filter(self: _duckdb.DuckDBPyRelation, filter_expr: object) -> _duckdb.DuckDBPyRelation
```

##### Description

Filter the relation object by the filter in filter_expr

##### Parameters

- **filter_expr** : str, Expression
                            
	The filter expression to apply over the relation.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.filter("value = 2")
```


##### Result

```text
┌──────────────────────────────────────┬───────────────┬───────┬───────────────────────────┐
│                  id                  │  description  │ value │     created_timestamp     │
│                 uuid                 │    varchar    │ int64 │ timestamp with time zone  │
├──────────────────────────────────────┼───────────────┼───────┼───────────────────────────┤
│ b0684ab7-fcbf-41c5-8e4a-a51bdde86926 │ value is even │     2 │ 2025-04-10 09:54:29.78+02 │
└──────────────────────────────────────┴───────────────┴───────┴───────────────────────────┘
```

----

#### `insert`

##### Signature

```python
insert(self: _duckdb.DuckDBPyRelation, values: object) -> None
```

##### Description

Inserts the given values into the relation

##### Parameters

- **values** : object
                            
	A tuple of values matching the relation column list, to be inserted.

##### Example

```python
import duckdb

from datetime import datetime
from uuid import uuid4

duckdb_conn = duckdb.connect()

duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
).to_table("code_example")

rel = duckdb_conn.table("code_example")

rel.insert(
    (
        uuid4(), 
        'value is even',
        10, 
        datetime.now()
    )
)

rel.filter("value = 10")
```

##### Result

```text
┌──────────────────────────────────────┬───────────────┬───────┬───────────────────────────────┐
│                  id                  │  description  │ value │       created_timestamp       │
│                 uuid                 │    varchar    │ int64 │   timestamp with time zone    │
├──────────────────────────────────────┼───────────────┼───────┼───────────────────────────────┤
│ c6dfab87-fae6-4213-8f76-1b96a8d179f6 │ value is even │    10 │ 2025-04-10 10:02:24.652218+02 │
└──────────────────────────────────────┴───────────────┴───────┴───────────────────────────────┘
```

----

#### `insert_into`

##### Signature

```python
insert_into(self: _duckdb.DuckDBPyRelation, table_name: str) -> None
```

##### Description

Inserts the relation object into an existing table named table_name

##### Parameters

- **table_name** : str
                            
	The table name to insert the data into. The relation must respect the column order of the table.

##### Example

```python
import duckdb

from datetime import datetime
from uuid import uuid4

duckdb_conn = duckdb.connect()

duckdb_conn.sql("""
        select
            gen_random_uuid() as id,
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value,
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
).to_table("code_example")

rel = duckdb_conn.values(
    [
        uuid4(),
        'value is even',
        10,
        datetime.now()
    ]
)

rel.insert_into("code_example")

duckdb_conn.table("code_example").filter("value = 10")
```

##### Result

```text
┌──────────────────────────────────────┬───────────────┬───────┬───────────────────────────────┐
│                  id                  │  description  │ value │       created_timestamp       │
│                 uuid                 │    varchar    │ int64 │   timestamp with time zone    │
├──────────────────────────────────────┼───────────────┼───────┼───────────────────────────────┤
│ 271c5ddd-c1d5-4638-b5a0-d8c7dc9e8220 │ value is even │    10 │ 2025-04-10 14:29:18.616379+02 │
└──────────────────────────────────────┴───────────────┴───────┴───────────────────────────────┘
```

----

#### `intersect`

##### Signature

```python
intersect(self: _duckdb.DuckDBPyRelation, other_rel: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Create the set intersection of this relation object with another relation object in other_rel

##### Parameters

- **other_rel** : duckdb.duckdb.DuckDBPyRelation
                            
	The relation to intersect with the current relation (set intersection).

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.intersect(other_rel=rel.set_alias("other_rel"))
```


##### Result

```text
The relation query is executed once with `rel` and once with `other_rel`,
therefore generating different ids and timestamps:
┌──────┬─────────────┬───────┬──────────────────────────┐
│  id  │ description │ value │    created_timestamp     │
│ uuid │   varchar   │ int64 │ timestamp with time zone │
├──────┴─────────────┴───────┴──────────────────────────┤
│                        0 rows                         │
└───────────────────────────────────────────────────────┘
```

----

#### `join`

##### Signature

```python
join(self: _duckdb.DuckDBPyRelation, other_rel: _duckdb.DuckDBPyRelation, condition: object, how: str = 'inner') -> _duckdb.DuckDBPyRelation
```

##### Description

Join the relation object with another relation object in other_rel using the join condition expression in join_condition. Types supported are 'inner', 'left', 'right', 'outer', 'semi' and 'anti'

Depending on how the `condition` parameter is provided, the JOIN clause generated is:
- `USING`

```python
import duckdb

duckdb_conn = duckdb.connect()

rel1 = duckdb_conn.sql("select range as id, concat('dummy 1', range) as text from range(1,10)")
rel2 = duckdb_conn.sql("select range as id, concat('dummy 2', range) as text from range(5,7)")

rel1.join(rel2, condition="id", how="inner").sql_query()
```
with following SQL:

```sql
SELECT * 
FROM (
        SELECT "range" AS id, 
            concat('dummy 1', "range") AS "text" 
        FROM "range"(1, 10)
    ) AS unnamed_relation_41bc15e744037078 
INNER JOIN (
        SELECT "range" AS id, 
        concat('dummy 2', "range") AS "text" 
        FROM "range"(5, 7)
    ) AS unnamed_relation_307e245965aa2c2b 
USING (id)
```
- `ON`

```python
import duckdb

duckdb_conn = duckdb.connect()

rel1 = duckdb_conn.sql("select range as id, concat('dummy 1', range) as text from range(1,10)")
rel2 = duckdb_conn.sql("select range as id, concat('dummy 2', range) as text from range(5,7)")

rel1.join(rel2, condition=f"{rel1.alias}.id = {rel2.alias}.id", how="inner").sql_query()
```

with the following SQL:

```sql
SELECT * 
FROM (
        SELECT "range" AS id, 
            concat('dummy 1', "range") AS "text" 
        FROM "range"(1, 10)
    ) AS unnamed_relation_41bc15e744037078 
INNER JOIN (
        SELECT "range" AS id, 
        concat('dummy 2', "range") AS "text" 
        FROM "range"(5, 7)
    ) AS unnamed_relation_307e245965aa2c2b 
ON ((unnamed_relation_41bc15e744037078.id = unnamed_relation_307e245965aa2c2b.id))
```

> `NATURAL`, `POSITIONAL` and `ASOF` joins are not provided by the relational API.
> `CROSS` joins are provided through the [cross method](#cross). 


##### Parameters

- **other_rel** : duckdb.duckdb.DuckDBPyRelation
                            
	The relation to join with the current relation.
- **condition** : object
                            
	The join condition, typically a SQL expression or the duplicated column name to join on.
- **how** : str, default: 'inner'
                            
	The type of join to perform: 'inner', 'left', 'right', 'outer', 'semi' and 'anti'.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.set_alias("rel").join(
    other_rel=rel.set_alias("other_rel"), 
    condition="rel.id = other_rel.id",
    how="left"
)

rel.count("*")
```


##### Result

```text
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│            9 │
└──────────────┘
```

----

#### `limit`

##### Signature

```python
limit(self: _duckdb.DuckDBPyRelation, n: typing.SupportsInt, offset: typing.SupportsInt = 0) -> _duckdb.DuckDBPyRelation
```

##### Description

Only retrieve the first n rows from this relation object, starting at offset

##### Parameters

- **n** : int
                            
	The maximum number of rows to return.
- **offset** : int, default: 0
                            
	The number of rows to skip before starting to return rows.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.limit(1)
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 4135597b-29e7-4cb9-a443-41f3d54f25df │ value is uneven │     1 │ 2025-04-10 10:52:03.678+02 │
└──────────────────────────────────────┴─────────────────┴───────┴────────────────────────────┘
```

----

#### `map`

##### Signature

```python
map(self: _duckdb.DuckDBPyRelation, map_function: collections.abc.Callable, *, schema: typing.Optional[object] = None) -> _duckdb.DuckDBPyRelation
```

##### Description

Calls the passed function on the relation

##### Parameters

- **map_function** : Callable
                            
	A Python function that takes a DataFrame and returns a transformed DataFrame.
- **schema** : object, default: None
                            
	Optional schema describing the structure of the output relation.

##### Example

```python
import duckdb
from pandas import DataFrame

def multiply_by_2(df: DataFrame):
    df["id"] = df["id"] * 2
    return df

duckdb_conn = duckdb.connect()
rel = duckdb_conn.sql("select range as id, 'dummy' as text from range(1,3)")

rel.map(multiply_by_2, schema={"id": int, "text": str})
```

##### Result

```text
┌───────┬─────────┐
│  id   │  text   │
│ int64 │ varchar │
├───────┼─────────┤
│     2 │ dummy   │
│     4 │ dummy   │
└───────┴─────────┘
```

----

#### `order`

##### Signature

```python
order(self: _duckdb.DuckDBPyRelation, order_expr: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Reorder the relation object by order_expr

##### Parameters

- **order_expr** : str
                            
	SQL expression defining the ordering of the result rows.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.order("value desc").limit(1, offset=4)
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 55899131-e3d3-463c-a215-f65cb8aef3bf │ value is uneven │     5 │ 2025-04-10 10:56:03.678+02 │
└──────────────────────────────────────┴─────────────────┴───────┴────────────────────────────┘
```

----

#### `project`

##### Signature

```python
project(self: _duckdb.DuckDBPyRelation, *args, groups: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Project the relation object by the projection in project_expr

**Aliases**: [`select`](#select)

##### Parameters

- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.project("description").limit(1)
```


##### Result

```text
┌─────────────────┐
│   description   │
│     varchar     │
├─────────────────┤
│ value is uneven │
└─────────────────┘
```

----

#### `select`

##### Signature

```python
select(self: _duckdb.DuckDBPyRelation, *args, groups: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Project the relation object by the projection in project_expr

**Aliases**: [`project`](#project)

##### Parameters

- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.select("description").limit(1)
```


##### Result

```text
┌─────────────────┐
│   description   │
│     varchar     │
├─────────────────┤
│ value is uneven │
└─────────────────┘
```

----

#### `sort`

##### Signature

```python
sort(self: _duckdb.DuckDBPyRelation, *args) -> _duckdb.DuckDBPyRelation
```

##### Description

Reorder the relation object by the provided expressions

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.sort("description")
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 5e0dfa8c-de4d-4ccd-8cff-450dabb86bde │ value is even   │     6 │ 2025-04-10 16:52:15.605+02 │
│ 95f1ad48-facf-4a84-a971-0a4fecce68c7 │ value is even   │     2 │ 2025-04-10 16:48:15.605+02 │
...
```

----

#### `union`

##### Signature

```python
union(self: _duckdb.DuckDBPyRelation, union_rel: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Create the set union of this relation object with another relation object in other_rel
>The union is `union all`. In order to retrieve distinct values, apply [distinct](#distinct).

##### Parameters

- **union_rel** : duckdb.duckdb.DuckDBPyRelation
                            
	The relation to union with the current relation (set union).

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.union(union_rel=rel)

rel.count("*")
```


##### Result

```text
┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│           18 │
└──────────────┘
```

----

#### `update`

##### Signature

```python
update(self: _duckdb.DuckDBPyRelation, set: object, *, condition: object = None) -> None
```

##### Description

Update the given relation with the provided expressions

##### Parameters

- **set** : object
                            
	Mapping of columns to new values for the update operation.
- **condition** : object, default: None
                            
	Optional condition to filter which rows to update.

##### Example

```python
import duckdb

from duckdb import ColumnExpression

duckdb_conn = duckdb.connect()

duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
).to_table("code_example")

rel = duckdb_conn.table("code_example")

rel.update(set={"description":None}, condition=ColumnExpression("value") == 1)

# the update is executed on the table, but not reflected on the relationship
# the relationship has to be recreated to retrieve the modified data
rel = duckdb_conn.table("code_example")

rel.show()
```

##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 66dcaa14-f4a6-4a55-af3b-7f6aa23ab4ad │ NULL            │     1 │ 2025-04-10 16:54:49.317+02 │
│ c6a18a42-67fb-4c95-827b-c966f2f95b88 │ value is even   │     2 │ 2025-04-10 16:55:49.317+02 │
...
```

## Functions 

This section contains the functions which can be applied to a relation,         in order to get a (scalar) result. The functions are [lazy evaluated](#lazy-evaluation).

| Name | Description |
|:--|:-------|
| [`any_value`](#any_value) | Returns the first non-null value from a given column |
| [`arg_max`](#arg_max) | Finds the row with the maximum value for a value column and returns the value of that row for an argument column |
| [`arg_min`](#arg_min) | Finds the row with the minimum value for a value column and returns the value of that row for an argument column |
| [`avg`](#avg) | Computes the average on a given column |
| [`bit_and`](#bit_and) | Computes the bitwise AND of all bits present in a given column |
| [`bit_or`](#bit_or) | Computes the bitwise OR of all bits present in a given column |
| [`bit_xor`](#bit_xor) | Computes the bitwise XOR of all bits present in a given column |
| [`bitstring_agg`](#bitstring_agg) | Computes a bitstring with bits set for each distinct value in a given column |
| [`bool_and`](#bool_and) | Computes the logical AND of all values present in a given column |
| [`bool_or`](#bool_or) | Computes the logical OR of all values present in a given column |
| [`count`](#count) | Computes the number of elements present in a given column |
| [`cume_dist`](#cume_dist) | Computes the cumulative distribution within the partition |
| [`dense_rank`](#dense_rank) | Computes the dense rank within the partition |
| [`distinct`](#distinct) | Retrieve distinct rows from this relation object |
| [`favg`](#favg) | Computes the average of all values present in a given column using a more accurate floating point summation (Kahan Sum) |
| [`first`](#first) | Returns the first value of a given column |
| [`first_value`](#first_value) | Computes the first value within the group or partition |
| [`fsum`](#fsum) | Computes the sum of all values present in a given column using a more accurate floating point summation (Kahan Sum) |
| [`geomean`](#geomean) | Computes the geometric mean over all values present in a given column |
| [`histogram`](#histogram) | Computes the histogram over all values present in a given column |
| [`lag`](#lag) | Computes the lag within the partition |
| [`last`](#last) | Returns the last value of a given column |
| [`last_value`](#last_value) | Computes the last value within the group or partition |
| [`lead`](#lead) | Computes the lead within the partition |
| [`list`](#list) | Returns a list containing all values present in a given column |
| [`max`](#max) | Returns the maximum value present in a given column |
| [`mean`](#mean) | Computes the average on a given column |
| [`median`](#median) | Computes the median over all values present in a given column |
| [`min`](#min) | Returns the minimum value present in a given column |
| [`mode`](#mode) | Computes the mode over all values present in a given column |
| [`n_tile`](#n_tile) | Divides the partition as equally as possible into num_buckets |
| [`nth_value`](#nth_value) | Computes the nth value within the partition |
| [`percent_rank`](#percent_rank) | Computes the relative rank within the partition |
| [`product`](#product) | Returns the product of all values present in a given column |
| [`quantile`](#quantile) | Computes the exact quantile value for a given column |
| [`quantile_cont`](#quantile_cont) | Computes the interpolated quantile value for a given column |
| [`quantile_disc`](#quantile_disc) | Computes the exact quantile value for a given column |
| [`rank`](#rank) | Computes the rank within the partition |
| [`rank_dense`](#rank_dense) | Computes the dense rank within the partition |
| [`row_number`](#row_number) | Computes the row number within the partition |
| [`select_dtypes`](#select_dtypes) | Select columns from the relation, by filtering based on type(s) |
| [`select_types`](#select_types) | Select columns from the relation, by filtering based on type(s) |
| [`std`](#std) | Computes the sample standard deviation for a given column |
| [`stddev`](#stddev) | Computes the sample standard deviation for a given column |
| [`stddev_pop`](#stddev_pop) | Computes the population standard deviation for a given column |
| [`stddev_samp`](#stddev_samp) | Computes the sample standard deviation for a given column |
| [`string_agg`](#string_agg) | Concatenates the values present in a given column with a separator |
| [`sum`](#sum) | Computes the sum of all values present in a given column |
| [`unique`](#unique) | Returns the distinct values in a column. |
| [`value_counts`](#value_counts) | Computes the number of elements present in a given column, also projecting the original column |
| [`var`](#var) | Computes the sample variance for a given column |
| [`var_pop`](#var_pop) | Computes the population variance for a given column |
| [`var_samp`](#var_samp) | Computes the sample variance for a given column |
| [`variance`](#variance) | Computes the sample variance for a given column |

#### `any_value`

##### Signature

```python
any_value(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the first non-null value from a given column

##### Parameters

- **column** : str
                            
	The column name from which to retrieve any value.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.any_value('id')
```


##### Result

```text
┌──────────────────────────────────────┐
│            any_value(id)             │
│                 uuid                 │
├──────────────────────────────────────┤
│ 642ea3d7-793d-4867-a759-91c1226c25a0 │
└──────────────────────────────────────┘
```

----

#### `arg_max`

##### Signature

```python
arg_max(self: _duckdb.DuckDBPyRelation, arg_column: str, value_column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Finds the row with the maximum value for a value column and returns the value of that row for an argument column

##### Parameters

- **arg_column** : str
                            
	The column name for which to find the argument maximizing the value.
- **value_column** : str
                            
	The column name containing values used to determine the maximum.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.arg_max(arg_column="value", value_column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────────────┐
│   description   │ arg_max("value", "value") │
│     varchar     │           int64           │
├─────────────────┼───────────────────────────┤
│ value is uneven │                         9 │
│ value is even   │                         8 │
└─────────────────┴───────────────────────────┘
```

----

#### `arg_min`

##### Signature

```python
arg_min(self: _duckdb.DuckDBPyRelation, arg_column: str, value_column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Finds the row with the minimum value for a value column and returns the value of that row for an argument column

##### Parameters

- **arg_column** : str
                            
	The column name for which to find the argument minimizing the value.
- **value_column** : str
                            
	The column name containing values used to determine the minimum.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.arg_min(arg_column="value", value_column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────────────┐
│   description   │ arg_min("value", "value") │
│     varchar     │           int64           │
├─────────────────┼───────────────────────────┤
│ value is even   │                         2 │
│ value is uneven │                         1 │
└─────────────────┴───────────────────────────┘
```

----

#### `avg`

##### Signature

```python
avg(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the average on a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the average on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.avg('value')
```


##### Result

```text
┌──────────────┐
│ avg("value") │
│    double    │
├──────────────┤
│          5.0 │
└──────────────┘
 
```

----

#### `bit_and`

##### Signature

```python
bit_and(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the bitwise AND of all bits present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform the bitwise AND aggregation on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.select("description, value::bit as value_bit")

rel.bit_and(column="value_bit", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────────────────────────────────────┐
│   description   │                        bit_and(value_bit)                        │
│     varchar     │                               bit                                │
├─────────────────┼──────────────────────────────────────────────────────────────────┤
│ value is uneven │ 0000000000000000000000000000000000000000000000000000000000000001 │
│ value is even   │ 0000000000000000000000000000000000000000000000000000000000000000 │
└─────────────────┴──────────────────────────────────────────────────────────────────┘    
```

----

#### `bit_or`

##### Signature

```python
bit_or(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the bitwise OR of all bits present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform the bitwise OR aggregation on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.select("description, value::bit as value_bit")

rel.bit_or(column="value_bit", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────────────────────────────────────┐
│   description   │                        bit_or(value_bit)                         │
│     varchar     │                               bit                                │
├─────────────────┼──────────────────────────────────────────────────────────────────┤
│ value is uneven │ 0000000000000000000000000000000000000000000000000000000000001111 │
│ value is even   │ 0000000000000000000000000000000000000000000000000000000000001110 │
└─────────────────┴──────────────────────────────────────────────────────────────────┘    
```

----

#### `bit_xor`

##### Signature

```python
bit_xor(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the bitwise XOR of all bits present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform the bitwise XOR aggregation on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.select("description, value::bit as value_bit")

rel.bit_xor(column="value_bit", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────────────────────────────────────┐
│   description   │                        bit_xor(value_bit)                        │
│     varchar     │                               bit                                │
├─────────────────┼──────────────────────────────────────────────────────────────────┤
│ value is even   │ 0000000000000000000000000000000000000000000000000000000000001000 │
│ value is uneven │ 0000000000000000000000000000000000000000000000000000000000001001 │
└─────────────────┴──────────────────────────────────────────────────────────────────┘
```

----

#### `bitstring_agg`

##### Signature

```python
bitstring_agg(self: _duckdb.DuckDBPyRelation, column: str, min: typing.Optional[object] = None, max: typing.Optional[object] = None, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes a bitstring with bits set for each distinct value in a given column

##### Parameters

- **column** : str
                            
	The column name to aggregate as a bitstring.
- **min** : object, default: None
                            
	Optional minimum bitstring value for aggregation.
- **max** : object, default: None
                            
	Optional maximum bitstring value for aggregation.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.bitstring_agg(column="value", groups="description", projected_columns="description", min=1, max=9)
```


##### Result

```text
┌─────────────────┬────────────────────────┐
│   description   │ bitstring_agg("value") │
│     varchar     │          bit           │
├─────────────────┼────────────────────────┤
│ value is uneven │ 101010101              │
│ value is even   │ 010101010              │
└─────────────────┴────────────────────────┘
```

----

#### `bool_and`

##### Signature

```python
bool_and(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the logical AND of all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform the boolean AND aggregation on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.select("description, mod(value,2)::boolean as uneven")

rel.bool_and(column="uneven", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────┐
│   description   │ bool_and(uneven) │
│     varchar     │     boolean      │
├─────────────────┼──────────────────┤
│ value is even   │ false            │
│ value is uneven │ true             │
└─────────────────┴──────────────────┘
```

----

#### `bool_or`

##### Signature

```python
bool_or(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the logical OR of all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform the boolean OR aggregation on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel = rel.select("description, mod(value,2)::boolean as uneven")

rel.bool_or(column="uneven", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────┐
│   description   │ bool_or(uneven) │
│     varchar     │     boolean     │
├─────────────────┼─────────────────┤
│ value is even   │ false           │
│ value is uneven │ true            │
└─────────────────┴─────────────────┘                
```

----

#### `count`

##### Signature

```python
count(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the number of elements present in a given column

##### Parameters

- **column** : str
                            
	The column name to perform count on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.count("id")
```


##### Result

```text
┌───────────┐
│ count(id) │
│   int64   │
├───────────┤
│         9 │
└───────────┘
```

----

#### `cume_dist`

##### Signature

```python
cume_dist(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the cumulative distribution within the partition

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.cume_dist(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬──────────────────────────────────────────────────────────────┐
│   description   │ value │ cume_dist() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                            double                            │
├─────────────────┼───────┼──────────────────────────────────────────────────────────────┤
│ value is uneven │     1 │                                                          0.2 │
│ value is uneven │     3 │                                                          0.4 │
│ value is uneven │     5 │                                                          0.6 │
│ value is uneven │     7 │                                                          0.8 │
│ value is uneven │     9 │                                                          1.0 │
│ value is even   │     2 │                                                         0.25 │
│ value is even   │     4 │                                                          0.5 │
│ value is even   │     6 │                                                         0.75 │
│ value is even   │     8 │                                                          1.0 │
└─────────────────┴───────┴──────────────────────────────────────────────────────────────┘
```

----

#### `dense_rank`

##### Signature

```python
dense_rank(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the dense rank within the partition

**Aliases**: [`rank_dense`](#rank_dense)

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

 rel.dense_rank(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬───────────────────────────────────────────────────────────────┐
│   description   │ value │ dense_rank() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                             int64                             │
├─────────────────┼───────┼───────────────────────────────────────────────────────────────┤
│ value is even   │     2 │                                                             1 │
│ value is even   │     4 │                                                             2 │
│ value is even   │     6 │                                                             3 │
│ value is even   │     8 │                                                             4 │
│ value is uneven │     1 │                                                             1 │
│ value is uneven │     3 │                                                             2 │
│ value is uneven │     5 │                                                             3 │
│ value is uneven │     7 │                                                             4 │
│ value is uneven │     9 │                                                             5 │
└─────────────────┴───────┴───────────────────────────────────────────────────────────────┘
```

----

#### `distinct`

##### Signature

```python
distinct(self: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Retrieve distinct rows from this relation object

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("select range from range(1,4)")

rel = rel.union(union_rel=rel)

rel.distinct().order("range")
```

##### Result

```text
┌───────┐
│ range │
│ int64 │
├───────┤
│     1 │
│     2 │
│     3 │
└───────┘
```

----

#### `favg`

##### Signature

```python
favg(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the average of all values present in a given column using a more accurate floating point summation (Kahan Sum)

##### Parameters

- **column** : str
                            
	The column name to calculate the average on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.favg(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────┐
│   description   │ favg("value") │
│     varchar     │    double     │
├─────────────────┼───────────────┤
│ value is uneven │           5.0 │
│ value is even   │           5.0 │
└─────────────────┴───────────────┘
```

----

#### `first`

##### Signature

```python
first(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the first value of a given column

##### Parameters

- **column** : str
                            
	The column name from which to retrieve the first value.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.first(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────┐
│   description   │ "first"("value") │
│     varchar     │      int64       │
├─────────────────┼──────────────────┤
│ value is even   │                2 │
│ value is uneven │                1 │
└─────────────────┴──────────────────┘
```

----

#### `first_value`

##### Signature

```python
first_value(self: _duckdb.DuckDBPyRelation, column: str, window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the first value within the group or partition

##### Parameters

- **column** : str
                            
	The column name from which to retrieve the first value.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.first_value(column="value", window_spec="over (partition by description order by value)", projected_columns="description").distinct()
```


##### Result

```text
┌─────────────────┬───────────────────────────────────────────────────────────────────────┐
│   description   │ first_value("value") OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │                                 int64                                 │
├─────────────────┼───────────────────────────────────────────────────────────────────────┤
│ value is even   │                                                                     2 │
│ value is uneven │                                                                     1 │
└─────────────────┴───────────────────────────────────────────────────────────────────────┘
```

----

#### `fsum`

##### Signature

```python
fsum(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sum of all values present in a given column using a more accurate floating point summation (Kahan Sum)

##### Parameters

- **column** : str
                            
	The column name to calculate the sum on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.fsum(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────┐
│   description   │ fsum("value") │
│     varchar     │    double     │
├─────────────────┼───────────────┤
│ value is even   │          20.0 │
│ value is uneven │          25.0 │
└─────────────────┴───────────────┘
```

----

#### `geomean`

##### Signature

```python
geomean(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the geometric mean over all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the geometric mean on.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.geomean(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────┐
│   description   │ geomean("value")  │
│     varchar     │      double       │
├─────────────────┼───────────────────┤
│ value is uneven │ 3.936283427035351 │
│ value is even   │ 4.426727678801287 │
└─────────────────┴───────────────────┘
```

----

#### `histogram`

##### Signature

```python
histogram(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the histogram over all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the histogram on.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.histogram(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────────────┐
│   description   │    histogram("value")     │
│     varchar     │   map(bigint, ubigint)    │
├─────────────────┼───────────────────────────┤
│ value is uneven │ {1=1, 3=1, 5=1, 7=1, 9=1} │
│ value is even   │ {2=1, 4=1, 6=1, 8=1}      │
└─────────────────┴───────────────────────────┘
```

----

#### `lag`

##### Signature

```python
lag(self: _duckdb.DuckDBPyRelation, column: str, window_spec: str, offset: typing.SupportsInt = 1, default_value: str = 'NULL', ignore_nulls: bool = False, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the lag within the partition

##### Parameters

- **column** : str
                            
	The column name to apply the lag function on.
- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **offset** : int, default: 1
                            
	The number of rows to lag behind.
- **default_value** : str, default: 'NULL'
                            
	The default value to return when the lag offset goes out of bounds.
- **ignore_nulls** : bool, default: False
                            
	Whether to ignore NULL values when computing the lag.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.lag(column="description", window_spec="over (order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬───────────────────────────────────────────────────┐
│   description   │ value │ lag(description, 1, NULL) OVER (ORDER BY "value") │
│     varchar     │ int64 │                      varchar                      │
├─────────────────┼───────┼───────────────────────────────────────────────────┤
│ value is uneven │     1 │ NULL                                              │
│ value is even   │     2 │ value is uneven                                   │
│ value is uneven │     3 │ value is even                                     │
│ value is even   │     4 │ value is uneven                                   │
│ value is uneven │     5 │ value is even                                     │
│ value is even   │     6 │ value is uneven                                   │
│ value is uneven │     7 │ value is even                                     │
│ value is even   │     8 │ value is uneven                                   │
│ value is uneven │     9 │ value is even                                     │
└─────────────────┴───────┴───────────────────────────────────────────────────┘
```

----

#### `last`

##### Signature

```python
last(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the last value of a given column

##### Parameters

- **column** : str
                            
	The column name from which to retrieve the last value.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.last(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────┐
│   description   │ "last"("value") │
│     varchar     │      int64      │
├─────────────────┼─────────────────┤
│ value is even   │               8 │
│ value is uneven │               9 │
└─────────────────┴─────────────────┘
```

----

#### `last_value`

##### Signature

```python
last_value(self: _duckdb.DuckDBPyRelation, column: str, window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the last value within the group or partition

##### Parameters

- **column** : str
                            
	The column name from which to retrieve the last value within the window.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.last_value(column="value", window_spec="over (order by description)", projected_columns="description").distinct()
```


##### Result

```text
┌─────────────────┬─────────────────────────────────────────────────┐
│   description   │ last_value("value") OVER (ORDER BY description) │
│     varchar     │                      int64                      │
├─────────────────┼─────────────────────────────────────────────────┤
│ value is uneven │                                               9 │
│ value is even   │                                               8 │
└─────────────────┴─────────────────────────────────────────────────┘
```

----

#### `lead`

##### Signature

```python
lead(self: _duckdb.DuckDBPyRelation, column: str, window_spec: str, offset: typing.SupportsInt = 1, default_value: str = 'NULL', ignore_nulls: bool = False, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the lead within the partition

##### Parameters

- **column** : str
                            
	The column name to apply the lead function on.
- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **offset** : int, default: 1
                            
	The number of rows to lead ahead.
- **default_value** : str, default: 'NULL'
                            
	The default value to return when the lead offset goes out of bounds.
- **ignore_nulls** : bool, default: False
                            
	Whether to ignore NULL values when computing the lead.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.lead(column="description", window_spec="over (order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬────────────────────────────────────────────────────┐
│   description   │ value │ lead(description, 1, NULL) OVER (ORDER BY "value") │
│     varchar     │ int64 │                      varchar                       │
├─────────────────┼───────┼────────────────────────────────────────────────────┤
│ value is uneven │     1 │ value is even                                      │
│ value is even   │     2 │ value is uneven                                    │
│ value is uneven │     3 │ value is even                                      │
│ value is even   │     4 │ value is uneven                                    │
│ value is uneven │     5 │ value is even                                      │
│ value is even   │     6 │ value is uneven                                    │
│ value is uneven │     7 │ value is even                                      │
│ value is even   │     8 │ value is uneven                                    │
│ value is uneven │     9 │ NULL                                               │
└─────────────────┴───────┴────────────────────────────────────────────────────┘
```

----

#### `list`

##### Signature

```python
list(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns a list containing all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to aggregate values into a list.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.list(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────┐
│   description   │  list("value")  │
│     varchar     │     int64[]     │
├─────────────────┼─────────────────┤
│ value is even   │ [2, 4, 6, 8]    │
│ value is uneven │ [1, 3, 5, 7, 9] │
└─────────────────┴─────────────────┘
```

----

#### `max`

##### Signature

```python
max(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the maximum value present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the maximum value of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

 rel.max(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────┐
│   description   │ max("value") │
│     varchar     │    int64     │
├─────────────────┼──────────────┤
│ value is even   │            8 │
│ value is uneven │            9 │
└─────────────────┴──────────────┘
```

----

#### `mean`

##### Signature

```python
mean(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the average on a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the mean value of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.mean(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────┐
│   description   │ avg("value") │
│     varchar     │    double    │
├─────────────────┼──────────────┤
│ value is even   │          5.0 │
│ value is uneven │          5.0 │
└─────────────────┴──────────────┘
```

----

#### `median`

##### Signature

```python
median(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the median over all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the median value of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.median(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────┐
│   description   │ median("value") │
│     varchar     │     double      │
├─────────────────┼─────────────────┤
│ value is even   │             5.0 │
│ value is uneven │             5.0 │
└─────────────────┴─────────────────┘
```

----

#### `min`

##### Signature

```python
min(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the minimum value present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the min value of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.min(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────┐
│   description   │ min("value") │
│     varchar     │    int64     │
├─────────────────┼──────────────┤
│ value is uneven │            1 │
│ value is even   │            2 │
└─────────────────┴──────────────┘
```

----

#### `mode`

##### Signature

```python
mode(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the mode over all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the mode (most frequent value) of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.mode(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────┐
│   description   │ "mode"("value") │
│     varchar     │      int64      │
├─────────────────┼─────────────────┤
│ value is uneven │               1 │
│ value is even   │               2 │
└─────────────────┴─────────────────┘
```

----

#### `n_tile`

##### Signature

```python
n_tile(self: _duckdb.DuckDBPyRelation, window_spec: str, num_buckets: typing.SupportsInt, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Divides the partition as equally as possible into num_buckets

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **num_buckets** : int
                            
	The number of buckets to divide the rows into.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.n_tile(window_spec="over (partition by description)", num_buckets=2, projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬──────────────────────────────────────────┐
│   description   │ value │ ntile(2) OVER (PARTITION BY description) │
│     varchar     │ int64 │                  int64                   │
├─────────────────┼───────┼──────────────────────────────────────────┤
│ value is uneven │     1 │                                        1 │
│ value is uneven │     3 │                                        1 │
│ value is uneven │     5 │                                        1 │
│ value is uneven │     7 │                                        2 │
│ value is uneven │     9 │                                        2 │
│ value is even   │     2 │                                        1 │
│ value is even   │     4 │                                        1 │
│ value is even   │     6 │                                        2 │
│ value is even   │     8 │                                        2 │
└─────────────────┴───────┴──────────────────────────────────────────┘
```

----

#### `nth_value`

##### Signature

```python
nth_value(self: _duckdb.DuckDBPyRelation, column: str, window_spec: str, offset: typing.SupportsInt, ignore_nulls: bool = False, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the nth value within the partition

##### Parameters

- **column** : str
                            
	The column name from which to retrieve the nth value within the window.
- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **offset** : int
                            
	The position of the value to retrieve within the window (1-based index).
- **ignore_nulls** : bool, default: False
                            
	Whether to ignore NULL values when computing the nth value.
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.nth_value(column="value", window_spec="over (partition by description)", projected_columns="description", offset=1)
```


##### Result

```text
┌─────────────────┬───────────────────────────────────────────────────────┐
│   description   │ nth_value("value", 1) OVER (PARTITION BY description) │
│     varchar     │                         int64                         │
├─────────────────┼───────────────────────────────────────────────────────┤
│ value is even   │                                                     2 │
│ value is even   │                                                     2 │
│ value is even   │                                                     2 │
│ value is even   │                                                     2 │
│ value is uneven │                                                     1 │
│ value is uneven │                                                     1 │
│ value is uneven │                                                     1 │
│ value is uneven │                                                     1 │
│ value is uneven │                                                     1 │
└─────────────────┴───────────────────────────────────────────────────────┘
```

----

#### `percent_rank`

##### Signature

```python
percent_rank(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the relative rank within the partition

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.percent_rank(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬─────────────────────────────────────────────────────────────────┐
│   description   │ value │ percent_rank() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                             double                              │
├─────────────────┼───────┼─────────────────────────────────────────────────────────────────┤
│ value is even   │     2 │                                                             0.0 │
│ value is even   │     4 │                                              0.3333333333333333 │
│ value is even   │     6 │                                              0.6666666666666666 │
│ value is even   │     8 │                                                             1.0 │
│ value is uneven │     1 │                                                             0.0 │
│ value is uneven │     3 │                                                            0.25 │
│ value is uneven │     5 │                                                             0.5 │
│ value is uneven │     7 │                                                            0.75 │
│ value is uneven │     9 │                                                             1.0 │
└─────────────────┴───────┴─────────────────────────────────────────────────────────────────┘
```

----

#### `product`

##### Signature

```python
product(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the product of all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the product of.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.product(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────┐
│   description   │ product("value") │
│     varchar     │      double      │
├─────────────────┼──────────────────┤
│ value is uneven │            945.0 │
│ value is even   │            384.0 │
└─────────────────┴──────────────────┘
```

----

#### `quantile`

##### Signature

```python
quantile(self: _duckdb.DuckDBPyRelation, column: str, q: object = 0.5, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the exact quantile value for a given column

##### Parameters

- **column** : str
                            
	The column name to compute the quantile for.
- **q** : object, default: 0.5
                            
	The quantile value to compute (e.g., 0.5 for median).
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.quantile(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────┐
│   description   │ quantile_disc("value", 0.500000) │
│     varchar     │              int64               │
├─────────────────┼──────────────────────────────────┤
│ value is uneven │                                5 │
│ value is even   │                                4 │
└─────────────────┴──────────────────────────────────┘
```

----

#### `quantile_cont`

##### Signature

```python
quantile_cont(self: _duckdb.DuckDBPyRelation, column: str, q: object = 0.5, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the interpolated quantile value for a given column

##### Parameters

- **column** : str
                            
	The column name to compute the continuous quantile for.
- **q** : object, default: 0.5
                            
	The quantile value to compute (e.g., 0.5 for median).
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.quantile_cont(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────┐
│   description   │ quantile_cont("value", 0.500000) │
│     varchar     │              double              │
├─────────────────┼──────────────────────────────────┤
│ value is even   │                              5.0 │
│ value is uneven │                              5.0 │
└─────────────────┴──────────────────────────────────┘
```

----

#### `quantile_disc`

##### Signature

```python
quantile_disc(self: _duckdb.DuckDBPyRelation, column: str, q: object = 0.5, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the exact quantile value for a given column

##### Parameters

- **column** : str
                            
	The column name to compute the discrete quantile for.
- **q** : object, default: 0.5
                            
	The quantile value to compute (e.g., 0.5 for median).
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.quantile_disc(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────────────┐
│   description   │ quantile_disc("value", 0.500000) │
│     varchar     │              int64               │
├─────────────────┼──────────────────────────────────┤
│ value is even   │                                4 │
│ value is uneven │                                5 │
└─────────────────┴──────────────────────────────────┘
```

----

#### `rank`

##### Signature

```python
rank(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the rank within the partition

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.rank(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬─────────────────────────────────────────────────────────┐
│   description   │ value │ rank() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                          int64                          │
├─────────────────┼───────┼─────────────────────────────────────────────────────────┤
│ value is uneven │     1 │                                                       1 │
│ value is uneven │     3 │                                                       2 │
│ value is uneven │     5 │                                                       3 │
│ value is uneven │     7 │                                                       4 │
│ value is uneven │     9 │                                                       5 │
│ value is even   │     2 │                                                       1 │
│ value is even   │     4 │                                                       2 │
│ value is even   │     6 │                                                       3 │
│ value is even   │     8 │                                                       4 │
└─────────────────┴───────┴─────────────────────────────────────────────────────────┘
```

----

#### `rank_dense`

##### Signature

```python
rank_dense(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the dense rank within the partition

**Aliases**: [`dense_rank`](#dense_rank)

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

 rel.rank_dense(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬───────────────────────────────────────────────────────────────┐
│   description   │ value │ dense_rank() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                             int64                             │
├─────────────────┼───────┼───────────────────────────────────────────────────────────────┤
│ value is uneven │     1 │                                                             1 │
│ value is uneven │     3 │                                                             2 │
│ value is uneven │     5 │                                                             3 │
│ value is uneven │     7 │                                                             4 │
│ value is uneven │     9 │                                                             5 │
│ value is even   │     2 │                                                             1 │
│ value is even   │     4 │                                                             2 │
│ value is even   │     6 │                                                             3 │
│ value is even   │     8 │                                                             4 │
└─────────────────┴───────┴───────────────────────────────────────────────────────────────┘
```

----

#### `row_number`

##### Signature

```python
row_number(self: _duckdb.DuckDBPyRelation, window_spec: str, projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the row number within the partition

##### Parameters

- **window_spec** : str
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.row_number(window_spec="over (partition by description order by value)", projected_columns="description, value")
```


##### Result

```text
┌─────────────────┬───────┬───────────────────────────────────────────────────────────────┐
│   description   │ value │ row_number() OVER (PARTITION BY description ORDER BY "value") │
│     varchar     │ int64 │                             int64                             │
├─────────────────┼───────┼───────────────────────────────────────────────────────────────┤
│ value is uneven │     1 │                                                             1 │
│ value is uneven │     3 │                                                             2 │
│ value is uneven │     5 │                                                             3 │
│ value is uneven │     7 │                                                             4 │
│ value is uneven │     9 │                                                             5 │
│ value is even   │     2 │                                                             1 │
│ value is even   │     4 │                                                             2 │
│ value is even   │     6 │                                                             3 │
│ value is even   │     8 │                                                             4 │
└─────────────────┴───────┴───────────────────────────────────────────────────────────────┘
```

----

#### `select_dtypes`

##### Signature

```python
select_dtypes(self: _duckdb.DuckDBPyRelation, types: object) -> _duckdb.DuckDBPyRelation
```

##### Description

Select columns from the relation, by filtering based on type(s)

**Aliases**: [`select_types`](#select_types)

##### Parameters

- **types** : object
                            
	Data type(s) to select columns by. Can be a single type or a collection of types.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.select_dtypes(types=[duckdb.typing.VARCHAR]).distinct()
```


##### Result

```text
┌─────────────────┐
│   description   │
│     varchar     │
├─────────────────┤
│ value is even   │
│ value is uneven │
└─────────────────┘
```

----

#### `select_types`

##### Signature

```python
select_types(self: _duckdb.DuckDBPyRelation, types: object) -> _duckdb.DuckDBPyRelation
```

##### Description

Select columns from the relation, by filtering based on type(s)

**Aliases**: [`select_dtypes`](#select_dtypes)

##### Parameters

- **types** : object
                            
	Data type(s) to select columns by. Can be a single type or a collection of types.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.select_types(types=[duckdb.typing.VARCHAR]).distinct()
```


##### Result

```text
┌─────────────────┐
│   description   │
│     varchar     │
├─────────────────┤
│ value is even   │
│ value is uneven │
└─────────────────┘
```

----

#### `std`

##### Signature

```python
std(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample standard deviation for a given column

**Aliases**: [`stddev`](#stddev), [`stddev_samp`](#stddev_samp)

##### Parameters

- **column** : str
                            
	The column name to calculate the standard deviation for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.std(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────┐
│   description   │ stddev_samp("value") │
│     varchar     │        double        │
├─────────────────┼──────────────────────┤
│ value is uneven │   3.1622776601683795 │
│ value is even   │    2.581988897471611 │
└─────────────────┴──────────────────────┘
```

----

#### `stddev`

##### Signature

```python
stddev(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample standard deviation for a given column

**Aliases**: [`std`](#std), [`stddev_samp`](#stddev_samp)

##### Parameters

- **column** : str
                            
	The column name to calculate the standard deviation for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.stddev(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────┐
│   description   │ stddev_samp("value") │
│     varchar     │        double        │
├─────────────────┼──────────────────────┤
│ value is even   │    2.581988897471611 │
│ value is uneven │   3.1622776601683795 │
└─────────────────┴──────────────────────┘
```

----

#### `stddev_pop`

##### Signature

```python
stddev_pop(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the population standard deviation for a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the standard deviation for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.stddev_pop(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬─────────────────────┐
│   description   │ stddev_pop("value") │
│     varchar     │       double        │
├─────────────────┼─────────────────────┤
│ value is even   │    2.23606797749979 │
│ value is uneven │  2.8284271247461903 │
└─────────────────┴─────────────────────┘
```

----

#### `stddev_samp`

##### Signature

```python
stddev_samp(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample standard deviation for a given column

**Aliases**: [`stddev`](#stddev), [`std`](#std)

##### Parameters

- **column** : str
                            
	The column name to calculate the standard deviation for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.stddev_samp(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────┐
│   description   │ stddev_samp("value") │
│     varchar     │        double        │
├─────────────────┼──────────────────────┤
│ value is even   │    2.581988897471611 │
│ value is uneven │   3.1622776601683795 │
└─────────────────┴──────────────────────┘
```

----

#### `string_agg`

##### Signature

```python
string_agg(self: _duckdb.DuckDBPyRelation, column: str, sep: str = ',', groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Concatenates the values present in a given column with a separator

##### Parameters

- **column** : str
                            
	The column name to concatenate values from.
- **sep** : str, default: ','
                            
	Separator string to use between concatenated values.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.string_agg(column="value", sep=",", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────────────┐
│   description   │ string_agg("value", ',') │
│     varchar     │         varchar          │
├─────────────────┼──────────────────────────┤
│ value is even   │ 2,4,6,8                  │
│ value is uneven │ 1,3,5,7,9                │
└─────────────────┴──────────────────────────┘
```

----

#### `sum`

##### Signature

```python
sum(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sum of all values present in a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the sum for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.sum(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────┐
│   description   │ sum("value") │
│     varchar     │    int128    │
├─────────────────┼──────────────┤
│ value is even   │           20 │
│ value is uneven │           25 │
└─────────────────┴──────────────┘
```

----

#### `unique`

##### Signature

```python
unique(self: _duckdb.DuckDBPyRelation, unique_aggr: str) -> _duckdb.DuckDBPyRelation
```

##### Description

Returns the distinct values in a column.

##### Parameters

- **unique_aggr** : str
                            
	The column to get the distinct values for.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.unique(unique_aggr="description")
```


##### Result

```text
┌─────────────────┐
│   description   │
│     varchar     │
├─────────────────┤
│ value is even   │
│ value is uneven │
└─────────────────┘
```

----

#### `value_counts`

##### Signature

```python
value_counts(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the number of elements present in a given column, also projecting the original column

##### Parameters

- **column** : str
                            
	The column name to count values from.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.value_counts(column="description", groups="description")
```


##### Result

```text
┌─────────────────┬────────────────────┐
│   description   │ count(description) │
│     varchar     │       int64        │
├─────────────────┼────────────────────┤
│ value is uneven │                  5 │
│ value is even   │                  4 │
└─────────────────┴────────────────────┘
```

----

#### `var`

##### Signature

```python
var(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample variance for a given column

**Aliases**: [`variance`](#variance), [`var_samp`](#var_samp)

##### Parameters

- **column** : str
                            
	The column name to calculate the sample variance for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.var(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────┐
│   description   │ var_samp("value") │
│     varchar     │      double       │
├─────────────────┼───────────────────┤
│ value is even   │ 6.666666666666667 │
│ value is uneven │              10.0 │
└─────────────────┴───────────────────┘
```

----

#### `var_pop`

##### Signature

```python
var_pop(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the population variance for a given column

##### Parameters

- **column** : str
                            
	The column name to calculate the population variance for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.var_pop(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬──────────────────┐
│   description   │ var_pop("value") │
│     varchar     │      double      │
├─────────────────┼──────────────────┤
│ value is even   │              5.0 │
│ value is uneven │              8.0 │
└─────────────────┴──────────────────┘
```

----

#### `var_samp`

##### Signature

```python
var_samp(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample variance for a given column

**Aliases**: [`variance`](#variance), [`var`](#var)

##### Parameters

- **column** : str
                            
	The column name to calculate the sample variance for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.var_samp(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────┐
│   description   │ var_samp("value") │
│     varchar     │      double       │
├─────────────────┼───────────────────┤
│ value is even   │ 6.666666666666667 │
│ value is uneven │              10.0 │
└─────────────────┴───────────────────┘
```

----

#### `variance`

##### Signature

```python
variance(self: _duckdb.DuckDBPyRelation, column: str, groups: str = '', window_spec: str = '', projected_columns: str = '') -> _duckdb.DuckDBPyRelation
```

##### Description

Computes the sample variance for a given column

**Aliases**: [`var`](#var), [`var_samp`](#var_samp)

##### Parameters

- **column** : str
                            
	The column name to calculate the sample variance for.
- **groups** : str, default: ''
                            
	Comma-separated list of columns to include in the `group by`.
- **window_spec** : str, default: ''
                            
	Optional window specification for window functions, provided as `over (partition by ... order by ...)`
- **projected_columns** : str, default: ''
                            
	Comma-separated list of columns to include in the result.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.variance(column="value", groups="description", projected_columns="description")
```


##### Result

```text
┌─────────────────┬───────────────────┐
│   description   │ var_samp("value") │
│     varchar     │      double       │
├─────────────────┼───────────────────┤
│ value is even   │ 6.666666666666667 │
│ value is uneven │              10.0 │
└─────────────────┴───────────────────┘
```

## Output 

This section contains the functions which will trigger an SQL execution and retrieve the data.

| Name | Description |
|:--|:-------|
| [`arrow`](#arrow) | Execute and return an Arrow Record Batch Reader that yields all rows |
| [`close`](#close) | Closes the result |
| [`create`](#create) | Creates a new table named table_name with the contents of the relation object |
| [`create_view`](#create_view) | Creates a view named view_name that refers to the relation object |
| [`df`](#df) | Execute and fetch all rows as a pandas DataFrame |
| [`execute`](#execute) | Transform the relation into a result set |
| [`fetch_arrow_reader`](#fetch_arrow_reader) | Execute and return an Arrow Record Batch Reader that yields all rows |
| [`fetch_arrow_table`](#fetch_arrow_table) | Execute and fetch all rows as an Arrow Table |
| [`fetch_df_chunk`](#fetch_df_chunk) | Execute and fetch a chunk of the rows |
| [`fetchall`](#fetchall) | Execute and fetch all rows as a list of tuples |
| [`fetchdf`](#fetchdf) | Execute and fetch all rows as a pandas DataFrame |
| [`fetchmany`](#fetchmany) | Execute and fetch the next set of rows as a list of tuples |
| [`fetchnumpy`](#fetchnumpy) | Execute and fetch all rows as a Python dict mapping each column to one numpy arrays |
| [`fetchone`](#fetchone) | Execute and fetch a single row as a tuple |
| [`pl`](#pl) | Execute and fetch all rows as a Polars DataFrame |
| [`record_batch`](#record_batch) | record_batch(self: object, batch_size: typing.SupportsInt = 1000000) -> object |
| [`tf`](#tf) | Fetch a result as dict of TensorFlow Tensors |
| [`to_arrow_table`](#to_arrow_table) | Execute and fetch all rows as an Arrow Table |
| [`to_csv`](#to_csv) | Write the relation object to a CSV file in 'file_name' |
| [`to_df`](#to_df) | Execute and fetch all rows as a pandas DataFrame |
| [`to_parquet`](#to_parquet) | Write the relation object to a Parquet file in 'file_name' |
| [`to_table`](#to_table) | Creates a new table named table_name with the contents of the relation object |
| [`to_view`](#to_view) | Creates a view named view_name that refers to the relation object |
| [`torch`](#torch) | Fetch a result as dict of PyTorch Tensors |
| [`write_csv`](#write_csv) | Write the relation object to a CSV file in 'file_name' |
| [`write_parquet`](#write_parquet) | Write the relation object to a Parquet file in 'file_name' |

#### `arrow`

##### Signature

```python
arrow(self: _duckdb.DuckDBPyRelation, batch_size: typing.SupportsInt = 1000000) -> pyarrow.lib.RecordBatchReader
```

##### Description

Execute and return an Arrow Record Batch Reader that yields all rows

**Aliases**: [`fetch_arrow_table`](#fetch_arrow_table), [`to_arrow_table`](#to_arrow_table)

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The batch size of writing the data to the Arrow table

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

pa_table = rel.arrow()

pa_table
```


##### Result

```text
pyarrow.Table
id: string
description: string
value: int64
created_timestamp: timestamp[us, tz=Europe/Amsterdam]
----
id: [["3ac9e0ba-8390-4a02-ad72-33b1caea6354","8b844392-1404-4bbc-b731-120f42c8ca27","ca5584ca-8e97-4fca-a295-ae3c16c32f5b","926d071e-5f64-488f-ae02-d19e315f9f5c","aabeedf0-5783-4eff-9963-b3967a6ea5d8","1f20db9a-bee8-4b65-b7e8-e7c36b5b8fee","795c678e-3524-4b52-96ec-7b48c24eeab1","9ffbd403-169f-4fe4-bc41-09751066f1f1","8fdb0a60-29f0-4f5b-afcc-c736a03cd083"]]
description: [["value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven"]]
value: [[1,2,3,4,5,6,7,8,9]]
created_timestamp: [[2025-04-10 09:07:12.614000Z,2025-04-10 09:08:12.614000Z,2025-04-10 09:09:12.614000Z,2025-04-10 09:10:12.614000Z,2025-04-10 09:11:12.614000Z,2025-04-10 09:12:12.614000Z,2025-04-10 09:13:12.614000Z,2025-04-10 09:14:12.614000Z,2025-04-10 09:15:12.614000Z]]
```

----

#### `close`

##### Signature

```python
close(self: _duckdb.DuckDBPyRelation) -> None
```

##### Description

Closes the result

----

#### `create`

##### Signature

```python
create(self: _duckdb.DuckDBPyRelation, table_name: str) -> None
```

##### Description

Creates a new table named table_name with the contents of the relation object

**Aliases**: [`to_table`](#to_table)

##### Parameters

- **table_name** : str
                            
	The name of the table to be created. There shouldn't be any other table with the same name.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.create("table_code_example")

duckdb_conn.table("table_code_example").limit(1)
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 3ac9e0ba-8390-4a02-ad72-33b1caea6354 │ value is uneven │     1 │ 2025-04-10 11:07:12.614+02 │
└──────────────────────────────────────┴─────────────────┴───────┴────────────────────────────┘
```

----

#### `create_view`

##### Signature

```python
create_view(self: _duckdb.DuckDBPyRelation, view_name: str, replace: bool = True) -> _duckdb.DuckDBPyRelation
```

##### Description

Creates a view named view_name that refers to the relation object

**Aliases**: [`to_view`](#to_view)

##### Parameters

- **view_name** : str
                            
	The name of the view to be created.
- **replace** : bool, default: True
                            
	If the view should be created with `CREATE OR REPLACE`. When set to `False`, there shouldn't be another view with the same `view_name`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.create_view("view_code_example", replace=True)

duckdb_conn.table("view_code_example").limit(1)
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 3ac9e0ba-8390-4a02-ad72-33b1caea6354 │ value is uneven │     1 │ 2025-04-10 11:07:12.614+02 │
└──────────────────────────────────────┴─────────────────┴───────┴────────────────────────────┘
```

----

#### `df`

##### Signature

```python
df(self: _duckdb.DuckDBPyRelation, *, date_as_object: bool = False) -> pandas.DataFrame
```

##### Description

Execute and fetch all rows as a pandas DataFrame

**Aliases**: [`fetchdf`](#fetchdf), [`to_df`](#to_df)

##### Parameters

- **date_as_object** : bool, default: False
                            
	If the date columns should be interpreted as Python date objects.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.df()
```


##### Result

```text
                                     id      description  value                created_timestamp
0  3ac9e0ba-8390-4a02-ad72-33b1caea6354  value is uneven      1 2025-04-10 11:07:12.614000+02:00
1  8b844392-1404-4bbc-b731-120f42c8ca27    value is even      2 2025-04-10 11:08:12.614000+02:00
2  ca5584ca-8e97-4fca-a295-ae3c16c32f5b  value is uneven      3 2025-04-10 11:09:12.614000+02:00
...
```

----

#### `execute`

##### Signature

```python
execute(self: _duckdb.DuckDBPyRelation) -> _duckdb.DuckDBPyRelation
```

##### Description

Transform the relation into a result set

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.execute()
```


##### Result

```text
┌──────────────────────────────────────┬─────────────────┬───────┬────────────────────────────┐
│                  id                  │   description   │ value │     created_timestamp      │
│                 uuid                 │     varchar     │ int64 │  timestamp with time zone  │
├──────────────────────────────────────┼─────────────────┼───────┼────────────────────────────┤
│ 3ac9e0ba-8390-4a02-ad72-33b1caea6354 │ value is uneven │     1 │ 2025-04-10 11:07:12.614+02 │
│ 8b844392-1404-4bbc-b731-120f42c8ca27 │ value is even   │     2 │ 2025-04-10 11:08:12.614+02 │
│ ca5584ca-8e97-4fca-a295-ae3c16c32f5b │ value is uneven │     3 │ 2025-04-10 11:09:12.614+02 │
```

----

#### `fetch_arrow_reader`

##### Signature

```python
fetch_arrow_reader(self: _duckdb.DuckDBPyRelation, batch_size: typing.SupportsInt = 1000000) -> pyarrow.lib.RecordBatchReader
```

##### Description

Execute and return an Arrow Record Batch Reader that yields all rows

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The batch size for fetching the data.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

pa_reader = rel.fetch_arrow_reader(batch_size=1)

pa_reader.read_next_batch()
```


##### Result

```text
pyarrow.RecordBatch
id: string
description: string
value: int64
created_timestamp: timestamp[us, tz=Europe/Amsterdam]
----
id: ["e4ab8cb4-4609-40cb-ad7e-4304ed5ed4bd"]
description: ["value is even"]
value: [2]
created_timestamp: [2025-04-10 09:25:51.259000Z]
```

----

#### `fetch_arrow_table`

##### Signature

```python
fetch_arrow_table(self: _duckdb.DuckDBPyRelation, batch_size: typing.SupportsInt = 1000000) -> pyarrow.lib.Table
```

##### Description

Execute and fetch all rows as an Arrow Table

**Aliases**: [`arrow`](#arrow), [`to_arrow_table`](#to_arrow_table)

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The batch size for fetching the data.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.fetch_arrow_table()
```


##### Result

```text
pyarrow.Table
id: string
description: string
value: int64
created_timestamp: timestamp[us, tz=Europe/Amsterdam]
----
id: [["1587b4b0-3023-49fe-82cf-06303ca136ac","e4ab8cb4-4609-40cb-ad7e-4304ed5ed4bd","3f8ad67a-290f-4a22-b41b-0173b8e45afa","9a4e37ef-d8bd-46dd-ab01-51cf4973549f","12baa624-ebc9-45ae-b73e-6f4029e31d2d","56d41292-53cc-48be-a1b8-e1f5d6ca5581","1accca18-c950-47c1-9108-aef8afbd5249","56d8db75-72c4-4d40-90d2-a3c840579c37","e19f6201-8646-401c-b019-e37c42c39632"]]
description: [["value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven"]]
value: [[1,2,3,4,5,6,7,8,9]]
created_timestamp: [[2025-04-10 09:24:51.259000Z,2025-04-10 09:25:51.259000Z,2025-04-10 09:26:51.259000Z,2025-04-10 09:27:51.259000Z,2025-04-10 09:28:51.259000Z,2025-04-10 09:29:51.259000Z,2025-04-10 09:30:51.259000Z,2025-04-10 09:31:51.259000Z,2025-04-10 09:32:51.259000Z]]
```

----

#### `fetch_df_chunk`

##### Signature

```python
fetch_df_chunk(self: _duckdb.DuckDBPyRelation, vectors_per_chunk: typing.SupportsInt = 1, *, date_as_object: bool = False) -> pandas.DataFrame
```

##### Description

Execute and fetch a chunk of the rows

##### Parameters

- **vectors_per_chunk** : int, default: 1
                            
	Number of data chunks to be processed before converting to dataframe.
- **date_as_object** : bool, default: False
                            
	If the date columns should be interpreted as Python date objects.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.fetch_df_chunk()
```


##### Result

```text
                                     id      description  value                created_timestamp
0  1587b4b0-3023-49fe-82cf-06303ca136ac  value is uneven      1 2025-04-10 11:24:51.259000+02:00
1  e4ab8cb4-4609-40cb-ad7e-4304ed5ed4bd    value is even      2 2025-04-10 11:25:51.259000+02:00
2  3f8ad67a-290f-4a22-b41b-0173b8e45afa  value is uneven      3 2025-04-10 11:26:51.259000+02:00
...
```

----

#### `fetchall`

##### Signature

```python
fetchall(self: _duckdb.DuckDBPyRelation) -> list
```

##### Description

Execute and fetch all rows as a list of tuples

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.limit(1).fetchall()
```


##### Result

```text
[(UUID('1587b4b0-3023-49fe-82cf-06303ca136ac'),
  'value is uneven',
  1,
  datetime.datetime(2025, 4, 10, 11, 24, 51, 259000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
```

----

#### `fetchdf`

##### Signature

```python
fetchdf(self: _duckdb.DuckDBPyRelation, *, date_as_object: bool = False) -> pandas.DataFrame
```

##### Description

Execute and fetch all rows as a pandas DataFrame

**Aliases**: [`df`](#df), [`to_df`](#to_df)

##### Parameters

- **date_as_object** : bool, default: False
                            
	If the date columns should be interpreted as Python date objects.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.fetchdf()
```


##### Result

```text
                                     id      description  value                created_timestamp
0  1587b4b0-3023-49fe-82cf-06303ca136ac  value is uneven      1 2025-04-10 11:24:51.259000+02:00
1  e4ab8cb4-4609-40cb-ad7e-4304ed5ed4bd    value is even      2 2025-04-10 11:25:51.259000+02:00
2  3f8ad67a-290f-4a22-b41b-0173b8e45afa  value is uneven      3 2025-04-10 11:26:51.259000+02:00
...
```

----

#### `fetchmany`

##### Signature

```python
fetchmany(self: _duckdb.DuckDBPyRelation, size: typing.SupportsInt = 1) -> list
```

##### Description

Execute and fetch the next set of rows as a list of tuples


>Warning Executing any operation during the retrieval of the data from an [aggregate](#aggregate) relation,
>will close the result set.
>```python
>import duckdb
>
>duckdb_conn = duckdb.connect()
>
>rel = duckdb_conn.sql("""
>       select 
>           gen_random_uuid() as id, 
>           concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
>           range as value, 
>           now() + concat(range,' ', 'minutes')::interval as created_timestamp
>       from range(1, 10)
>    """
>)
>
>agg_rel = rel.aggregate("value")
>
>while res := agg_rel.fetchmany(size=1):
>    print(res)
>    rel.show()
>```


##### Parameters

- **size** : int, default: 1
                            
	The number of records to be fetched.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

while res := rel.fetchmany(size=1):
    print(res)
```


##### Result

```text
[(UUID('cf4c5e32-d0aa-4699-a3ee-0092e900f263'), 'value is uneven', 1, datetime.datetime(2025, 4, 30, 16, 23, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('cec335ac-24ac-49a3-ae9a-bb35f71fc88d'), 'value is even', 2, datetime.datetime(2025, 4, 30, 16, 24, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('2423295d-9bb0-453c-a385-21bdacba03b6'), 'value is uneven', 3, datetime.datetime(2025, 4, 30, 16, 25, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('88806b21-192d-41e7-a293-c789aad636ba'), 'value is even', 4, datetime.datetime(2025, 4, 30, 16, 26, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('05837a28-dacf-4121-88a6-a374aefb8a07'), 'value is uneven', 5, datetime.datetime(2025, 4, 30, 16, 27, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('b9c1f7e9-6156-4554-b80e-67d3b5d810bb'), 'value is even', 6, datetime.datetime(2025, 4, 30, 16, 28, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('4709c7fa-d286-4864-bb48-69748b447157'), 'value is uneven', 7, datetime.datetime(2025, 4, 30, 16, 29, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('30e48457-b103-4fa5-95cf-1c7f0143335b'), 'value is even', 8, datetime.datetime(2025, 4, 30, 16, 30, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
[(UUID('036b7f4b-bd78-4ffb-a351-964d93f267b7'), 'value is uneven', 9, datetime.datetime(2025, 4, 30, 16, 31, 5, 310000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))]
```

----

#### `fetchnumpy`

##### Signature

```python
fetchnumpy(self: _duckdb.DuckDBPyRelation) -> dict
```

##### Description

Execute and fetch all rows as a Python dict mapping each column to one numpy arrays

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.fetchnumpy()
```


##### Result

```text
{'id': array([UUID('1587b4b0-3023-49fe-82cf-06303ca136ac'),
        UUID('e4ab8cb4-4609-40cb-ad7e-4304ed5ed4bd'),
        UUID('3f8ad67a-290f-4a22-b41b-0173b8e45afa'),
        UUID('9a4e37ef-d8bd-46dd-ab01-51cf4973549f'),
        UUID('12baa624-ebc9-45ae-b73e-6f4029e31d2d'),
        UUID('56d41292-53cc-48be-a1b8-e1f5d6ca5581'),
        UUID('1accca18-c950-47c1-9108-aef8afbd5249'),
        UUID('56d8db75-72c4-4d40-90d2-a3c840579c37'),
        UUID('e19f6201-8646-401c-b019-e37c42c39632')], dtype=object),
 'description': array(['value is uneven', 'value is even', 'value is uneven',
        'value is even', 'value is uneven', 'value is even',
        'value is uneven', 'value is even', 'value is uneven'],
       dtype=object),
 'value': array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
 'created_timestamp': array(['2025-04-10T09:24:51.259000', '2025-04-10T09:25:51.259000',
        '2025-04-10T09:26:51.259000', '2025-04-10T09:27:51.259000',
        '2025-04-10T09:28:51.259000', '2025-04-10T09:29:51.259000',
        '2025-04-10T09:30:51.259000', '2025-04-10T09:31:51.259000',
        '2025-04-10T09:32:51.259000'], dtype='datetime64[us]')}
```

----

#### `fetchone`

##### Signature

```python
fetchone(self: _duckdb.DuckDBPyRelation) -> typing.Optional[tuple]
```

##### Description

Execute and fetch a single row as a tuple


>Warning Executing any operation during the retrieval of the data from an [aggregate](#aggregate) relation,
>will close the result set.
>```python
>import duckdb
>
>duckdb_conn = duckdb.connect()
>
>rel = duckdb_conn.sql("""
>       select 
>           gen_random_uuid() as id, 
>           concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
>           range as value, 
>           now() + concat(range,' ', 'minutes')::interval as created_timestamp
>       from range(1, 10)
>    """
>)
>
>agg_rel = rel.aggregate("value")
>
>while res := agg_rel.fetchone():
>    print(res)
>    rel.show()
>```


##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

while res := rel.fetchone():
    print(res)
```


##### Result

```text
(UUID('fe036411-f4c7-4f52-9ddd-80cd2bb56613'), 'value is uneven', 1, datetime.datetime(2025, 4, 30, 12, 59, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('466c9b43-e9f0-4237-8f26-155f259a5b59'), 'value is even', 2, datetime.datetime(2025, 4, 30, 13, 0, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('5755cf16-a94f-41ef-a16d-21e856d71f9f'), 'value is uneven', 3, datetime.datetime(2025, 4, 30, 13, 1, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('05b52c93-bd68-45e1-b02a-a08d682c33d5'), 'value is even', 4, datetime.datetime(2025, 4, 30, 13, 2, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('cf61ef13-2840-4541-900d-f493767d7622'), 'value is uneven', 5, datetime.datetime(2025, 4, 30, 13, 3, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('033e7c68-e800-4ee8-9787-6cf50aabc27b'), 'value is even', 6, datetime.datetime(2025, 4, 30, 13, 4, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('8b8d6545-ff54-45d6-b69a-97edb63dfe43'), 'value is uneven', 7, datetime.datetime(2025, 4, 30, 13, 5, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('7da79dfe-b29c-462b-a414-9d5e3cc80139'), 'value is even', 8, datetime.datetime(2025, 4, 30, 13, 6, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
(UUID('f83ffff2-33b9-4f86-9d14-46974b546bab'), 'value is uneven', 9, datetime.datetime(2025, 4, 30, 13, 7, 8, 912000, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>))
```

----

#### `pl`

##### Signature

```python
pl(self: _duckdb.DuckDBPyRelation, batch_size: typing.SupportsInt = 1000000, *, lazy: bool = False) -> duckdb::PolarsDataFrame
```

##### Description

Execute and fetch all rows as a Polars DataFrame

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The number of records to be fetched per batch.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.pl(batch_size=1)
```


##### Result

```text
shape: (9, 4)
┌─────────────────────────────────┬─────────────────┬───────┬────────────────────────────────┐
│ id                              ┆ description     ┆ value ┆ created_timestamp              │
│ ---                             ┆ ---             ┆ ---   ┆ ---                            │
│ str                             ┆ str             ┆ i64   ┆ datetime[μs, Europe/Amsterdam] │
╞═════════════════════════════════╪═════════════════╪═══════╪════════════════════════════════╡
│ b2f92c3c-9372-49f3-897f-2c86fc… ┆ value is uneven ┆ 1     ┆ 2025-04-10 11:49:51.886 CEST   │
```

----

#### `record_batch`

##### Description

record_batch(self: object, batch_size: typing.SupportsInt = 1000000) -> object

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The batch size for fetching the data.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

pa_batch = rel.record_batch(batch_size=1)

pa_batch.read_next_batch()
```


##### Result

```text
pyarrow.RecordBatch
id: string
description: string
value: int64
created_timestamp: timestamp[us, tz=Europe/Amsterdam]
----
id: ["908cf67c-a086-4b94-9017-2089a83e4a6c"]
description: ["value is uneven"]
value: [1]
created_timestamp: [2025-04-10 09:52:55.249000Z]
```

----

#### `tf`

##### Signature

```python
tf(self: _duckdb.DuckDBPyRelation) -> dict
```

##### Description

Fetch a result as dict of TensorFlow Tensors

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.select("description, value").tf()
```


##### Result

```text
{'description': <tf.Tensor: shape=(9,), dtype=string, numpy=
 array([b'value is uneven', b'value is even', b'value is uneven',
        b'value is even', b'value is uneven', b'value is even',
        b'value is uneven', b'value is even', b'value is uneven'],
       dtype=object)>,
 'value': <tf.Tensor: shape=(9,), dtype=int64, numpy=array([1, 2, 3, 4, 5, 6, 7, 8, 9])>}
```

----

#### `to_arrow_table`

##### Signature

```python
to_arrow_table(self: _duckdb.DuckDBPyRelation, batch_size: typing.SupportsInt = 1000000) -> pyarrow.lib.Table
```

##### Description

Execute and fetch all rows as an Arrow Table

**Aliases**: [`fetch_arrow_table`](#fetch_arrow_table), [`arrow`](#arrow)

##### Parameters

- **batch_size** : int, default: 1000000
                            
	The batch size for fetching the data.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_arrow_table()
```


##### Result

```text
pyarrow.Table
id: string
description: string
value: int64
created_timestamp: timestamp[us, tz=Europe/Amsterdam]
----
id: [["86b2011d-3818-426f-a41e-7cd5c7321f79","07fa4f89-0bba-4049-9acd-c933332a66d5","f2f1479e-f582-4fe4-b82f-9b753b69634c","529d3c63-5961-4adb-b0a8-8249188fc82a","aa9eea7d-7fac-4dcf-8f32-4a0b5d64f864","4852aa32-03f2-40d3-8006-b8213904775a","c0127203-f2e3-4925-9810-655bc02a3c19","2a1356ba-5707-44d6-a492-abd0a67e5efb","800a1c24-231c-4dae-bd68-627654c8a110"]]
description: [["value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven","value is even","value is uneven"]]
value: [[1,2,3,4,5,6,7,8,9]]
created_timestamp: [[2025-04-10 09:54:24.015000Z,2025-04-10 09:55:24.015000Z,2025-04-10 09:56:24.015000Z,2025-04-10 09:57:24.015000Z,2025-04-10 09:58:24.015000Z,2025-04-10 09:59:24.015000Z,2025-04-10 10:00:24.015000Z,2025-04-10 10:01:24.015000Z,2025-04-10 10:02:24.015000Z]]
```

----

#### `to_csv`

##### Signature

```python
to_csv(self: _duckdb.DuckDBPyRelation, file_name: str, *, sep: object = None, na_rep: object = None, header: object = None, quotechar: object = None, escapechar: object = None, date_format: object = None, timestamp_format: object = None, quoting: object = None, encoding: object = None, compression: object = None, overwrite: object = None, per_thread_output: object = None, use_tmp_file: object = None, partition_by: object = None, write_partition_columns: object = None) -> None
```

##### Description

Write the relation object to a CSV file in 'file_name'

**Aliases**: [`write_csv`](#write_csv)

##### Parameters

- **file_name** : str
                            
	The name of the output CSV file.
- **sep** : str, default: ','
                            
	Field delimiter for the output file.
- **na_rep** : str, default: ''
                            
	Missing data representation.
- **header** : bool, default: True
                            
	Whether to write column headers.
- **quotechar** : str, default: '"'
                            
	Character used to quote fields containing special characters.
- **escapechar** : str, default: None
                            
	Character used to escape the delimiter if quoting is set to QUOTE_NONE.
- **date_format** : str, default: None
                            
	Custom format string for DATE values.
- **timestamp_format** : str, default: None
                            
	Custom format string for TIMESTAMP values.
- **quoting** : int, default: csv.QUOTE_MINIMAL
                            
	Control field quoting behavior (e.g., QUOTE_MINIMAL, QUOTE_ALL).
- **encoding** : str, default: 'utf-8'
                            
	Character encoding for the output file.
- **compression** : str, default: auto
                            
	Compression type (e.g., 'gzip', 'bz2', 'zstd').
- **overwrite** : bool, default: False
                            
	When true, all existing files inside targeted directories will be removed (not supported on remote filesystems). Only has an effect when used with `partition_by`.
- **per_thread_output** : bool, default: False
                            
	When `true`, write one file per thread, rather than one file in total. This allows for faster parallel writing.
- **use_tmp_file** : bool, default: False
                            
	Write to a temporary file before renaming to final name to avoid partial writes.
- **partition_by** : list[str], default: None
                            
	List of column names to partition output by (creates folder structure).
- **write_partition_columns** : bool, default: False
                            
	Whether or not to write partition columns into files. Only has an effect when used with `partition_by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_csv("code_example.csv")
```


##### Result

```text
The data is exported to a CSV file, named code_example.csv
```

----

#### `to_df`

##### Signature

```python
to_df(self: _duckdb.DuckDBPyRelation, *, date_as_object: bool = False) -> pandas.DataFrame
```

##### Description

Execute and fetch all rows as a pandas DataFrame

**Aliases**: [`fetchdf`](#fetchdf), [`df`](#df)

##### Parameters

- **date_as_object** : bool, default: False
                            
	If the date columns should be interpreted as Python date objects.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_df()
```


##### Result

```text
                                     id      description  value                created_timestamp
0  e1f79925-60fd-4ee2-ae67-5eff6b0543d1  value is uneven      1 2025-04-10 11:56:04.452000+02:00
1  caa619d4-d79c-4c00-b82e-9319b086b6f8    value is even      2 2025-04-10 11:57:04.452000+02:00
2  64c68032-99b9-4e8f-b4a3-6c522d5419b3  value is uneven      3 2025-04-10 11:58:04.452000+02:00
...
```

----

#### `to_parquet`

##### Signature

```python
to_parquet(self: _duckdb.DuckDBPyRelation, file_name: str, *, compression: object = None, field_ids: object = None, row_group_size_bytes: object = None, row_group_size: object = None, overwrite: object = None, per_thread_output: object = None, use_tmp_file: object = None, partition_by: object = None, write_partition_columns: object = None, append: object = None) -> None
```

##### Description

Write the relation object to a Parquet file in 'file_name'

**Aliases**: [`write_parquet`](#write_parquet)

##### Parameters

- **file_name** : str
                            
	The name of the output Parquet file.
- **compression** : str, default: 'snappy'
                            
	The compression format to use (`uncompressed`, `snappy`, `gzip`, `zstd`, `brotli`, `lz4`, `lz4_raw`).
- **field_ids** : STRUCT
                            
	The field_id for each column. Pass auto to attempt to infer automatically.
- **row_group_size_bytes** : int, default: row_group_size * 1024
                            
	The target size of each row group. You can pass either a human-readable string, e.g., 2MB, or an integer, i.e., the number of bytes. This option is only used when you have issued `SET preserve_insertion_order = false;`, otherwise, it is ignored.
- **row_group_size** : int, default: 122880
                            
	The target size, i.e., number of rows, of each row group.
- **overwrite** : bool, default: False
                            
	If True, overwrite the file if it exists.
- **per_thread_output** : bool, default: False
                            
	When `True`, write one file per thread, rather than one file in total. This allows for faster parallel writing.
- **use_tmp_file** : bool, default: False
                            
	Write to a temporary file before renaming to final name to avoid partial writes.
- **partition_by** : list[str], default: None
                            
	List of column names to partition output by (creates folder structure).
- **write_partition_columns** : bool, default: False
                            
	Whether or not to write partition columns into files. Only has an effect when used with `partition_by`.
- **append** : bool, default: False
                            
	When `True`, in the event a filename pattern is generated that already exists, the path will be regenerated to ensure no existing files are overwritten. Only has an effect when used with `partition_by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_parquet("code_example.parquet")
```


##### Result

```text
The data is exported to a Parquet file, named code_example.parquet
```

----

#### `to_table`

##### Signature

```python
to_table(self: _duckdb.DuckDBPyRelation, table_name: str) -> None
```

##### Description

Creates a new table named table_name with the contents of the relation object

**Aliases**: [`create`](#create)

##### Parameters

- **table_name** : str
                            
	The name of the table to be created. There shouldn't be any other table with the same name.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_table("table_code_example")
```


##### Result

```text
A table, named table_code_example, is created with the data of the relation
```

----

#### `to_view`

##### Signature

```python
to_view(self: _duckdb.DuckDBPyRelation, view_name: str, replace: bool = True) -> _duckdb.DuckDBPyRelation
```

##### Description

Creates a view named view_name that refers to the relation object

**Aliases**: [`create_view`](#create_view)

##### Parameters

- **view_name** : str
                            
	The name of the view to be created.
- **replace** : bool, default: True
                            
	If the view should be created with `CREATE OR REPLACE`. When set to `False`, there shouldn't be another view with the same `view_name`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.to_view("view_code_example", replace=True)
```


##### Result

```text
A view, named view_code_example, is created with the query definition of the relation
```

----

#### `torch`

##### Signature

```python
torch(self: _duckdb.DuckDBPyRelation) -> dict
```

##### Description

Fetch a result as dict of PyTorch Tensors

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.select("value").torch()
```


##### Result

```text
{'value': tensor([1, 2, 3, 4, 5, 6, 7, 8, 9])}
```

----

#### `write_csv`

##### Signature

```python
write_csv(self: _duckdb.DuckDBPyRelation, file_name: str, *, sep: object = None, na_rep: object = None, header: object = None, quotechar: object = None, escapechar: object = None, date_format: object = None, timestamp_format: object = None, quoting: object = None, encoding: object = None, compression: object = None, overwrite: object = None, per_thread_output: object = None, use_tmp_file: object = None, partition_by: object = None, write_partition_columns: object = None) -> None
```

##### Description

Write the relation object to a CSV file in 'file_name'

**Aliases**: [`to_csv`](#to_csv)

##### Parameters

- **file_name** : str
                            
	The name of the output CSV file.
- **sep** : str, default: ','
                            
	Field delimiter for the output file.
- **na_rep** : str, default: ''
                            
	Missing data representation.
- **header** : bool, default: True
                            
	Whether to write column headers.
- **quotechar** : str, default: '"'
                            
	Character used to quote fields containing special characters.
- **escapechar** : str, default: None
                            
	Character used to escape the delimiter if quoting is set to QUOTE_NONE.
- **date_format** : str, default: None
                            
	Custom format string for DATE values.
- **timestamp_format** : str, default: None
                            
	Custom format string for TIMESTAMP values.
- **quoting** : int, default: csv.QUOTE_MINIMAL
                            
	Control field quoting behavior (e.g., QUOTE_MINIMAL, QUOTE_ALL).
- **encoding** : str, default: 'utf-8'
                            
	Character encoding for the output file.
- **compression** : str, default: auto
                            
	Compression type (e.g., 'gzip', 'bz2', 'zstd').
- **overwrite** : bool, default: False
                            
	When true, all existing files inside targeted directories will be removed (not supported on remote filesystems). Only has an effect when used with `partition_by`.
- **per_thread_output** : bool, default: False
                            
	When `true`, write one file per thread, rather than one file in total. This allows for faster parallel writing.
- **use_tmp_file** : bool, default: False
                            
	Write to a temporary file before renaming to final name to avoid partial writes.
- **partition_by** : list[str], default: None
                            
	List of column names to partition output by (creates folder structure).
- **write_partition_columns** : bool, default: False
                            
	Whether or not to write partition columns into files. Only has an effect when used with `partition_by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.write_csv("code_example.csv")
```


##### Result

```text
The data is exported to a CSV file, named code_example.csv
```

----

#### `write_parquet`

##### Signature

```python
write_parquet(self: _duckdb.DuckDBPyRelation, file_name: str, *, compression: object = None, field_ids: object = None, row_group_size_bytes: object = None, row_group_size: object = None, overwrite: object = None, per_thread_output: object = None, use_tmp_file: object = None, partition_by: object = None, write_partition_columns: object = None, append: object = None) -> None
```

##### Description

Write the relation object to a Parquet file in 'file_name'

**Aliases**: [`to_parquet`](#to_parquet)

##### Parameters

- **file_name** : str
                            
	The name of the output Parquet file.
- **compression** : str, default: 'snappy'
                            
	The compression format to use (`uncompressed`, `snappy`, `gzip`, `zstd`, `brotli`, `lz4`, `lz4_raw`).
- **field_ids** : STRUCT
                            
	The field_id for each column. Pass auto to attempt to infer automatically.
- **row_group_size_bytes** : int, default: row_group_size * 1024
                            
	The target size of each row group. You can pass either a human-readable string, e.g., 2MB, or an integer, i.e., the number of bytes. This option is only used when you have issued `SET preserve_insertion_order = false;`, otherwise, it is ignored.
- **row_group_size** : int, default: 122880
                            
	The target size, i.e., number of rows, of each row group.
- **overwrite** : bool, default: False
                            
	If True, overwrite the file if it exists.
- **per_thread_output** : bool, default: False
                            
	When `True`, write one file per thread, rather than one file in total. This allows for faster parallel writing.
- **use_tmp_file** : bool, default: False
                            
	Write to a temporary file before renaming to final name to avoid partial writes.
- **partition_by** : list[str], default: None
                            
	List of column names to partition output by (creates folder structure).
- **write_partition_columns** : bool, default: False
                            
	Whether or not to write partition columns into files. Only has an effect when used with `partition_by`.
- **append** : bool, default: False
                            
	When `True`, in the event a filename pattern is generated that already exists, the path will be regenerated to ensure no existing files are overwritten. Only has an effect when used with `partition_by`.

##### Example

```python
import duckdb

duckdb_conn = duckdb.connect()

rel = duckdb_conn.sql("""
        select 
            gen_random_uuid() as id, 
            concat('value is ', case when mod(range,2)=0 then 'even' else 'uneven' end) as description,
            range as value, 
            now() + concat(range,' ', 'minutes')::interval as created_timestamp
        from range(1, 10)
    """
)

rel.write_parquet("code_example.parquet")
```


##### Result

```text
The data is exported to a Parquet file, named code_example.parquet
```

---
layout: docu
redirect_from:
- /docs/api/python/function
- /docs/api/python/function/
- /docs/clients/python/function
title: Python Function API
---

You can create a DuckDB user-defined function (UDF) from a Python function so it can be used in SQL queries.
Similarly to regular [functions]({% link docs/stable/sql/functions/overview.md %}), they need to have a name, a return type and parameter types.

Here is an example using a Python function that calls a third-party library.

```python
import duckdb
from duckdb.typing import VARCHAR
from faker import Faker

def generate_random_name():
    fake = Faker()
    return fake.name()

duckdb.create_function("random_name", generate_random_name, [], VARCHAR)
res = duckdb.sql("SELECT random_name()").fetchall()
print(res)
```

```text
[('Gerald Ashley',)]
```

## Creating Functions

To register a Python UDF, use the `create_function` method from a DuckDB connection. Here is the syntax:

```python
import duckdb
con = duckdb.connect()
con.create_function(name, function, parameters, return_type)
```

The `create_function` method takes the following parameters:

1. `name` A string representing the unique name of the UDF within the connection catalog.
2. `function` The Python function you wish to register as a UDF.
3. `parameters` Scalar functions can operate on one or more columns. This parameter takes a list of column types used as input.
4. `return_type` Scalar functions return one element per row. This parameter specifies the return type of the function.
5. `type` (optional): DuckDB supports both native Python types and PyArrow Arrays. By default, `type = 'native'` is assumed, but you can specify `type = 'arrow'` to use PyArrow Arrays. In general, using an Arrow UDF will be much more efficient than native because it will be able to operate in batches.
6. `null_handling` (optional): By default, `NULL` values are automatically handled as `NULL`-in `NULL`-out. Users can specify a desired behavior for `NULL` values by setting `null_handling = 'special'`.
7. `exception_handling` (optional): By default, when an exception is thrown from the Python function, it will be re-thrown in Python. Users can disable this behavior, and instead return `NULL`, by setting this parameter to `'return_null'`
8. `side_effects` (optional): By default, functions are expected to produce the same result for the same input. If the result of a function is impacted by any type of randomness, `side_effects` must be set to `True`.

To unregister a UDF, you can call the `remove_function` method with the UDF name:

```python
con.remove_function(name)
```

### Using Partial Functions

DuckDB UDFs can also be created with [Python partial functions](https://docs.python.org/3/library/functools.html#functools.partial).

In the below example, we show how a custom logger will return the concatenation of the execution datetime in ISO format, always followed by 
argument passed at UDF creation and the input parameter provided to the function call:

```python
from datetime import datetime
import duckdb
import functools


def get_datetime_iso_format() -> str:
    return datetime.now().isoformat()


def logger_udf(func, arg1: str, arg2: int) -> str:
    return ' '.join([func(), arg1, str(arg2)])
    
    
with duckdb.connect() as con:
    con.sql("select * from range(10) tbl(id)").to_table("example_table")
    
    con.create_function(
        'custom_logger',
        functools.partial(logger_udf, get_datetime_iso_format, 'logging data')
    )
    rel = con.sql("SELECT custom_logger(id) from example_table;")
    rel.show()

    con.create_function(
        'another_custom_logger',
        functools.partial(logger_udf, get_datetime_iso_format, ':')
    )
    rel = con.sql("SELECT another_custom_logger(id) from example_table;")
    rel.show()
```

```text
┌───────────────────────────────────────────┐
│             custom_logger(id)             │
│                  varchar                  │
├───────────────────────────────────────────┤
│ 2025-03-27T12:07:56.811251 logging data 0 │
│ 2025-03-27T12:07:56.811264 logging data 1 │
│ 2025-03-27T12:07:56.811266 logging data 2 │
│ 2025-03-27T12:07:56.811268 logging data 3 │
│ 2025-03-27T12:07:56.811269 logging data 4 │
│ 2025-03-27T12:07:56.811270 logging data 5 │
│ 2025-03-27T12:07:56.811271 logging data 6 │
│ 2025-03-27T12:07:56.811272 logging data 7 │
│ 2025-03-27T12:07:56.811274 logging data 8 │
│ 2025-03-27T12:07:56.811275 logging data 9 │
├───────────────────────────────────────────┤
│                  10 rows                  │
└───────────────────────────────────────────┘

┌────────────────────────────────┐
│   another_custom_logger(id)    │
│            varchar             │
├────────────────────────────────┤
│ 2025-03-27T12:07:56.812106 : 0 │
│ 2025-03-27T12:07:56.812116 : 1 │
│ 2025-03-27T12:07:56.812118 : 2 │
│ 2025-03-27T12:07:56.812119 : 3 │
│ 2025-03-27T12:07:56.812121 : 4 │
│ 2025-03-27T12:07:56.812122 : 5 │
│ 2025-03-27T12:07:56.812123 : 6 │
│ 2025-03-27T12:07:56.812124 : 7 │
│ 2025-03-27T12:07:56.812126 : 8 │
│ 2025-03-27T12:07:56.812127 : 9 │
├────────────────────────────────┤
│            10 rows             │
└────────────────────────────────┘
```

## Type Annotation

When the function has type annotation it's often possible to leave out all of the optional parameters.
Using `DuckDBPyType` we can implicitly convert many known types to DuckDBs type system.
For example:

```python
import duckdb

def my_function(x: int) -> str:
    return x

duckdb.create_function("my_func", my_function)
print(duckdb.sql("SELECT my_func(42)"))
```

```text
┌─────────────┐
│ my_func(42) │
│   varchar   │
├─────────────┤
│ 42          │
└─────────────┘
```

If only the parameter list types can be inferred, you'll need to pass in `None` as `parameters`.

## `NULL` Handling

By default when functions receive a `NULL` value, this instantly returns `NULL`, as part of the default `NULL`-handling.
When this is not desired, you need to explicitly set this parameter to `"special"`.

```python
import duckdb
from duckdb.typing import BIGINT

def dont_intercept_null(x):
    return 5

duckdb.create_function("dont_intercept", dont_intercept_null, [BIGINT], BIGINT)
res = duckdb.sql("SELECT dont_intercept(NULL)").fetchall()
print(res)
```

```text
[(None,)]
```

With `null_handling="special"`:

```python
import duckdb
from duckdb.typing import BIGINT

def dont_intercept_null(x):
    return 5

duckdb.create_function("dont_intercept", dont_intercept_null, [BIGINT], BIGINT, null_handling="special")
res = duckdb.sql("SELECT dont_intercept(NULL)").fetchall()
print(res)
```

```text
[(5,)]
```

> Always use `null_handling="special"` when the function can return NULL.


```python
import duckdb
from duckdb.typing import VARCHAR


def return_str_or_none(x: str) -> str | None:
    if not x:
        return None
    
    return x

duckdb.create_function(
    "return_str_or_none",
    return_str_or_none,
    [VARCHAR],
    VARCHAR,
    null_handling="special"
)
res = duckdb.sql("SELECT return_str_or_none('')").fetchall()
print(res)
```

```text
[(None,)]
```

## Exception Handling

By default, when an exception is thrown from the Python function, we'll forward (re-throw) the exception.
If you want to disable this behavior, and instead return `NULL`, you'll need to set this parameter to `"return_null"`.

```python
import duckdb
from duckdb.typing import BIGINT

def will_throw():
    raise ValueError("ERROR")

duckdb.create_function("throws", will_throw, [], BIGINT)
try:
    res = duckdb.sql("SELECT throws()").fetchall()
except duckdb.InvalidInputException as e:
    print(e)

duckdb.create_function("doesnt_throw", will_throw, [], BIGINT, exception_handling="return_null")
res = duckdb.sql("SELECT doesnt_throw()").fetchall()
print(res)
```

```console
Invalid Input Error: Python exception occurred while executing the UDF: ValueError: ERROR

At:
  ...(5): will_throw
  ...(9): <module>
```

```text
[(None,)]
```

## Side Effects

By default DuckDB will assume the created function is a *pure* function, meaning it will produce the same output when given the same input.
If your function does not follow that rule, for example when your function makes use of randomness, then you will need to mark this function as having `side_effects`.

For example, this function will produce a new count for every invocation.

```python
def count() -> int:
    old = count.counter;
    count.counter += 1
    return old

count.counter = 0
```

If we create this function without marking it as having side effects, the result will be the following:

```python
con = duckdb.connect()
con.create_function("my_counter", count, side_effects=False)
res = con.sql("SELECT my_counter() FROM range(10)").fetchall()
print(res)
```

```text
[(0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,)]
```

Which is obviously not the desired result, when we add `side_effects=True`, the result is as we would expect:

```python
con.remove_function("my_counter")
count.counter = 0
con.create_function("my_counter", count, side_effects=True)
res = con.sql("SELECT my_counter() FROM range(10)").fetchall()
print(res)
```

```text
[(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,)]
```

## Python Function Types

Currently, two function types are supported, `native` (default) and `arrow`.

### Arrow

If the function is expected to receive arrow arrays, set the `type` parameter to `'arrow'`.

This will let the system know to provide arrow arrays of up to `STANDARD_VECTOR_SIZE` tuples to the function, and also expect an array of the same amount of tuples to be returned from the function.

In general, using an Arrow UDF will be much more efficient than native because it will be able to operate in batches.

```python
import duckdb
import pyarrow as pa
from duckdb.typing import VARCHAR
from pyarrow import compute as pc


def mirror(strings: pa.Array, sep: pa.Array) -> pa.Array:
    assert isinstance(strings, pa.ChunkedArray)
    assert isinstance(sep, pa.ChunkedArray)
    return pc.binary_join_element_wise(strings, pc.ascii_reverse(strings), sep)


duckdb.create_function(
    "mirror",
    mirror,
    [VARCHAR, VARCHAR],
    return_type=VARCHAR,
    type="arrow",
)

duckdb.sql(
    "CREATE OR REPLACE TABLE strings AS SELECT 'hello' AS str UNION ALL SELECT 'world' AS str;"
)
print(duckdb.sql("SELECT mirror(str, '|') FROM strings;").fetchall())
```

```text
[('hello|olleh',), ('world|dlrow',)]
```

### Native

When the function type is set to `native` the function will be provided with a single tuple at a time, and expect only a single value to be returned.
This can be useful to interact with Python libraries that don't operate on Arrow, such as `faker`:

```python
import duckdb

from duckdb.typing import DATE
from faker import Faker

def random_date():
    fake = Faker()
    return fake.date_between()

duckdb.create_function(
    "random_date",
    random_date,
    parameters=[],
    return_type=DATE,
    type="native",
)
res = duckdb.sql("SELECT random_date()").fetchall()
print(res)
```

```text
[(datetime.date(2019, 5, 15),)]
```

---
layout: docu
redirect_from:
- /docs/api/python/types
- /docs/api/python/types/
- /docs/clients/python/types
title: Types API
---

The `DuckDBPyType` class represents a type instance of our [data types]({% link docs/stable/sql/data_types/overview.md %}).

## Converting from Other Types

To make the API as easy to use as possible, we have added implicit conversions from existing type objects to a DuckDBPyType instance.
This means that wherever a DuckDBPyType object is expected, it is also possible to provide any of the options listed below.

### Python Built-Ins

The table below shows the mapping of Python Built-in types to DuckDB type.

<div class="monospace_table"></div>

| Built-in types | DuckDB type |
|:---------------|:------------|
| bool           | BOOLEAN     |
| bytearray      | BLOB        |
| bytes          | BLOB        |
| float          | DOUBLE      |
| int            | BIGINT      |
| str            | VARCHAR     |

### Numpy DTypes

The table below shows the mapping of Numpy DType to DuckDB type.

<div class="monospace_table"></div>

| Type        | DuckDB type |
|:------------|:------------|
| bool        | BOOLEAN     |
| float32     | FLOAT       |
| float64     | DOUBLE      |
| int16       | SMALLINT    |
| int32       | INTEGER     |
| int64       | BIGINT      |
| int8        | TINYINT     |
| uint16      | USMALLINT   |
| uint32      | UINTEGER    |
| uint64      | UBIGINT     |
| uint8       | UTINYINT    |

### Nested Types

#### `list[child_type]`

`list` type objects map to a `LIST` type of the child type.
Which can also be arbitrarily nested.

```python
import duckdb
from typing import Union

duckdb.typing.DuckDBPyType(list[dict[Union[str, int], str]])
```

```text
MAP(UNION(u1 VARCHAR, u2 BIGINT), VARCHAR)[]
```

#### `dict[key_type, value_type]`

`dict` type objects map to a `MAP` type of the key type and the value type.

```python
import duckdb

print(duckdb.typing.DuckDBPyType(dict[str, int]))
```

```text
MAP(VARCHAR, BIGINT)
```

#### `{'a': field_one, 'b': field_two, ..., 'n': field_n}`

`dict` objects map to a `STRUCT` composed of the keys and values of the dict.

```python
import duckdb

print(duckdb.typing.DuckDBPyType({'a': str, 'b': int}))
```

```text
STRUCT(a VARCHAR, b BIGINT)
```

#### `Union[type_1, ... type_n]`

`typing.Union` objects map to a `UNION` type of the provided types.

```python
import duckdb
from typing import Union

print(duckdb.typing.DuckDBPyType(Union[int, str, bool, bytearray]))
```

```text
UNION(u1 BIGINT, u2 VARCHAR, u3 BOOLEAN, u4 BLOB)
```

### Creation Functions

For the built-in types, you can use the constants defined in `duckdb.typing`:

<div class="monospace_table"></div>

| DuckDB type    |
|:---------------|
| BIGINT         |
| BIT            |
| BLOB           |
| BOOLEAN        |
| DATE           |
| DOUBLE         |
| FLOAT          |
| HUGEINT        |
| INTEGER        |
| INTERVAL       |
| SMALLINT       |
| SQLNULL        |
| TIME_TZ        |
| TIME           |
| TIMESTAMP_MS   |
| TIMESTAMP_NS   |
| TIMESTAMP_S    |
| TIMESTAMP_TZ   |
| TIMESTAMP      |
| TINYINT        |
| UBIGINT        |
| UHUGEINT       |
| UINTEGER       |
| USMALLINT      |
| UTINYINT       |
| UUID           |
| VARCHAR        |

For the complex types there are methods available on the `DuckDBPyConnection` object or the `duckdb` module.
Anywhere a `DuckDBPyType` is accepted, we will also accept one of the type objects that can implicitly convert to a `DuckDBPyType`.

#### `list_type` | `array_type`

Parameters:

* `child_type: DuckDBPyType`

#### `struct_type` | `row_type`

Parameters:

* `fields: Union[list[DuckDBPyType], dict[str, DuckDBPyType]]`

#### `map_type`

Parameters:

* `key_type: DuckDBPyType`
* `value_type: DuckDBPyType`

#### `decimal_type`

Parameters:

* `width: int`
* `scale: int`

#### `union_type`

Parameters:

* `members: Union[list[DuckDBPyType], dict[str, DuckDBPyType]]`

#### `string_type`

Parameters:

* `collation: Optional[str]`


---
layout: docu
redirect_from:
- /docs/api/python/expression
- /docs/api/python/expression/
- /docs/clients/python/expression
title: Expression API
---

The `Expression` class represents an instance of an [expression]({% link docs/stable/sql/expressions/overview.md %}).

## Why Would I Use the Expression API?

Using this API makes it possible to dynamically build up expressions, which are typically created by the parser from the query string.
This allows you to skip that and have more fine-grained control over the used expressions.

Below is a list of currently supported expressions that can be created through the API.

## Column Expression

This expression references a column by name.

```python
import duckdb
import pandas as pd

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})
```

Selecting a single column:

```python
col = duckdb.ColumnExpression('a')
duckdb.df(df).select(col).show()
```

```text
┌───────┐
│   a   │
│ int64 │
├───────┤
│     1 │
│     2 │
│     3 │
│     4 │
└───────┘
```

Selecting multiple columns:

```python
col_list = [
        duckdb.ColumnExpression('a') * 10,
        duckdb.ColumnExpression('b').isnull(),
        duckdb.ColumnExpression('c') + 5
    ]
duckdb.df(df).select(*col_list).show()
```

```text
┌──────────┬─────────────┬─────────┐
│ (a * 10) │ (b IS NULL) │ (c + 5) │
│  int64   │   boolean   │  int64  │
├──────────┼─────────────┼─────────┤
│       10 │ false       │      47 │
│       20 │ true        │      26 │
│       30 │ false       │      18 │
│       40 │ false       │      19 │
└──────────┴─────────────┴─────────┘
```

## Star Expression

This expression selects all columns of the input source.

Optionally it's possible to provide an `exclude` list to filter out columns of the table.
This `exclude` list can contain either strings or Expressions.

```python
import duckdb
import pandas as pd

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})

star = duckdb.StarExpression(exclude = ['b'])
duckdb.df(df).select(star).show()
```

```text
┌───────┬───────┐
│   a   │   c   │
│ int64 │ int64 │
├───────┼───────┤
│     1 │    42 │
│     2 │    21 │
│     3 │    13 │
│     4 │    14 │
└───────┴───────┘
```

## Constant Expression

This expression contains a single value.

```python
import duckdb
import pandas as pd

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})

const = duckdb.ConstantExpression('hello')
duckdb.df(df).select(const).show()
```

```text
┌─────────┐
│ 'hello' │
│ varchar │
├─────────┤
│ hello   │
│ hello   │
│ hello   │
│ hello   │
└─────────┘
```

## Case Expression

This expression contains a `CASE WHEN (...) THEN (...) ELSE (...) END` expression.
By default `ELSE` is `NULL` and it can be set using `.else(value = ...)`.
Additional `WHEN (...) THEN (...)` blocks can be added with `.when(condition = ..., value = ...)`.

```python
import duckdb
import pandas as pd
from duckdb import (
    ConstantExpression,
    ColumnExpression,
    CaseExpression
)

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})

hello = ConstantExpression('hello')
world = ConstantExpression('world')

case = \
    CaseExpression(condition = ColumnExpression('b') == False, value = world) \
    .otherwise(hello)
duckdb.df(df).select(case).show()
```

```text
┌──────────────────────────────────────────────────────────┐
│ CASE  WHEN ((b = false)) THEN ('world') ELSE 'hello' END │
│                         varchar                          │
├──────────────────────────────────────────────────────────┤
│ hello                                                    │
│ hello                                                    │
│ world                                                    │
│ hello                                                    │
└──────────────────────────────────────────────────────────┘
```

## Function Expression

This expression contains a function call.
It can be constructed by providing the function name and an arbitrary amount of Expressions as arguments.

```python
import duckdb
import pandas as pd
from duckdb import (
    ConstantExpression,
    ColumnExpression,
    FunctionExpression
)

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})

multiply_by_2 = FunctionExpression('multiply', ColumnExpression('a'), ConstantExpression(2))
duckdb.df(df).select(multiply_by_2).show()
```

```text
┌────────────────┐
│ multiply(a, 2) │
│     int64      │
├────────────────┤
│              2 │
│              4 │
│              6 │
│              8 │
└────────────────┘
```

## SQL Expression

This expression contains any valid SQL expression.

```python
import duckdb
import pandas as pd

from duckdb import SQLExpression

df = pd.DataFrame({
    'a': [1, 2, 3, 4],
    'b': [True, None, False, True],
    'c': [42, 21, 13, 14]
})

duckdb.df(df).filter(
    SQLExpression("b is true")
).select(
    SQLExpression("a").alias("selecting_column_a"),
    SQLExpression("case when a = 1 then 1 else 0 end").alias("selecting_case_expression"),
    SQLExpression("1").alias("constant_numeric_column"),
    SQLExpression("'hello'").alias("constant_text_column")
).aggregate(
    aggr_expr=[
        SQLExpression("SUM(selecting_column_a)").alias("sum_a"), 
        "selecting_case_expression" , 
        "constant_numeric_column", 
        "constant_text_column"
    ],
).show()
```

```text
┌────────┬───────────────────────────┬─────────────────────────┬──────────────────────┐
│ sum_a  │ selecting_case_expression │ constant_numeric_column │ constant_text_column │
│ int128 │           int32           │          int32          │       varchar        │
├────────┼───────────────────────────┼─────────────────────────┼──────────────────────┤
│      4 │                         0 │                       1 │ hello                │
│      1 │                         1 │                       1 │ hello                │
└────────┴───────────────────────────┴─────────────────────────┴──────────────────────┘
```

## Common Operations

The Expression class also contains many operations that can be applied to any Expression type.

| Operation                      | Description                                                                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `.alias(name: str)`            | Applies an alias to the expression                                                                                          |
| `.cast(type: DuckDBPyType)`    | Applies a cast to the provided type on the expression                                                                       |
| `.isin(*exprs: Expression)`    | Creates an [`IN` expression]({% link docs/stable/sql/expressions/in.md %}#in) against the provided expressions as the list         |
| `.isnotin(*exprs: Expression)` | Creates a [`NOT IN` expression]({% link docs/stable/sql/expressions/in.md %}#not-in) against the provided expressions as the list  |
| `.isnotnull()`                 | Checks whether the expression is not `NULL`                                                                                 |
| `.isnull()`                    | Checks whether the expression is `NULL`                                                                                     |

### Order Operations

When expressions are provided to `DuckDBPyRelation.order()`, the following order operations can be applied.

| Operation                      | Description                                                                        |
|--------------------------------|------------------------------------------------------------------------------------|
| `.asc()`                       | Indicates that this expression should be sorted in ascending order                 |
| `.desc()`                      | Indicates that this expression should be sorted in descending order                |
| `.nulls_first()`               | Indicates that the nulls in this expression should precede the non-null values     |
| `.nulls_last()`                | Indicates that the nulls in this expression should come after the non-null values  |



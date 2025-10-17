https://ducklake.select/docs/stable/specification/introduction

# Introduction
This page contains the specification for the DuckLake format, version 0.2.

## Building Blocks
DuckLake requires two main components:

- Catalog database: DuckLake requires a database that supports transactions and primary key constraints as defined by the SQL-92 standard.
- Data storage: The DuckLake specification requires storing the data in Parquet format on file-based storage, such as object storage.

## Catalog Database
DuckLake uses SQL tables and queries to define the catalog information (metadata, statistics, etc.). This specification explains the schema and semantics of these:

- Data Types
- Queries
- Tables

If you are reading this specification for the first time, we recommend starting with the “Queries” page, which introduces the queries used by DuckLake.

# Data Types
DuckLake specifies multiple different data types for field values, and also supports nested types. The types of columns are defined in the column_type field of the ducklake_column table.

## Primitive Types
Type	Description
boolean	True or false
int8	8-bit signed integer
int16	16-bit signed integer
int32	32-bit signed integer
int64	64-bit signed integer
uint8	8-bit unsigned integer
uint16	16-bit unsigned integer
uint32	32-bit unsigned integer
uint64	64-bit unsigned integer
float32	32-bit IEEE 754 floating-point value
float64	64-bit IEEE 754 floating-point value
decimal(P, S)	Fixed-point decimal with precision P and scale S
time	Time of day, microsecond precision
timetz	Time of day, microsecond precision, with time zone
date	Calendar date
timestamp	Timestamp, microsecond precision
timestamptz	Timestamp, microsecond precision, with time zone
timestamp_s	Timestamp, second precision
timestamp_ms	Timestamp, millisecond precision
timestamp_ns	Timestamp, nanosecond precision
interval	Time interval in three different granularities: months, days, and milliseconds
varchar	Text
blob	Binary data
json	JSON
uuid	Universally unique identifier

## Nested Types
DuckLake supports nested types and primitive types. Nested types are defined recursively, i.e., in order to define a column of type INT[] two columns are defined. The top-level column is of type list, which has a child column of type int32.

The following nested types are supported:

Type	Description
list	Collection of values with a single child type
struct	A tuple of typed values
map	A collection of key-value pairs

# Queries

## Reading Data
DuckLake specifies tables and update transactions to modify them. DuckLake is not a black box, all metadata is stored as SQL tables under the user's control. Of course, they can be queried in whichever way is best for a client. Below we describe a small working example to retrieve table data.

The information below is to provide transparency to users and to aid developers making their own implementation of DuckLake. The ducklake DuckDB extension is able to execute those operations in the background.

### Get Current Snapshot
Before anything else we need to find a snapshot ID to be queries. There can be many snapshots in the ducklake_snapshot table. A snapshot ID is a continously increasing number that identifies a snapshot. In most cases, you would query the most recent one like so:

SELECT snapshot_id FROM ducklake_snapshot
WHERE snapshot_id =
    (SELECT max(snapshot_id) FROM ducklake_snapshot);

### List Schemas
A DuckLake catalog can contain many SQL-style schemas, which each can contain many tables. These are listed in the ducklake_schema table. Here's how we get the list of valid schemas for a given snapshot:

SELECT schema_id, schema_name
FROM ducklake_schema
WHERE
    SNAPSHOT_ID >= begin_snapshot AND
    (SNAPSHOT_ID < end_snapshot OR end_snapshot IS NULL);

where

SNAPSHOT_ID is a BIGINT referring to the snapshot_id column in the ducklake_snapshot table

### List Tables
We can list the tables available in a schema for a specific snapshot using the ducklake_table table:

SELECT table_id, table_name
FROM ducklake_table
WHERE
    schema_id = SCHEMA_ID AND
    SNAPSHOT_ID >= begin_snapshot AND
    (SNAPSHOT_ID < end_snapshot OR end_snapshot IS NULL);

where

SCHEMA_ID is a BIGINT referring to the schema_id column in the ducklake_schema table
SNAPSHOT_ID is a BIGINT referring to the snapshot_id column in the ducklake_snapshot table

### Show the Structure of a Table
For each given table, we can list the available top-level columns using the ducklake_column table:

SELECT column_id, column_name, column_type
FROM ducklake_column
WHERE
    table_id = TABLE_ID AND
    parent_column IS NULL AND
    SNAPSHOT_ID >= begin_snapshot AND
    (SNAPSHOT_ID < end_snapshot OR end_snapshot IS NULL)
ORDER BY column_order;

where

TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table
SNAPSHOT_ID is a BIGINT referring to the snapshot_id column in the ducklake_snapshot table
Note
that DuckLake supports nested columns – the filter for parent_column IS NULL only shows the top-level columns.

For the list of supported data types, please refer to the “Data Types” page.

### SELECT
Now that we know the table structure we can query actual data from the Parquet files that store table data. We need to join the list of data files with the list of delete files (if any). There can be at most one delete file per file in a single snapshot.

SELECT data.path AS data_file_path, del.path AS delete_file_path
FROM ducklake_data_file AS data
LEFT JOIN (
    SELECT *
    FROM ducklake_delete_file
    WHERE
        SNAPSHOT_ID >= begin_snapshot AND
        (SNAPSHOT_ID < end_snapshot OR end_snapshot IS NULL)
    ) AS del
USING (data_file_id)
WHERE
    data.table_id = TABLE_ID AND
    SNAPSHOT_ID >= data.begin_snapshot AND
    (SNAPSHOT_ID < data.end_snapshot OR data.end_snapshot IS NULL)
ORDER BY file_order;

where (again)

TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table
SNAPSHOT_ID is a BIGINT referring to the snapshot_id column in the ducklake_snapshot table
Now we have a list of files. In order to reconstruct actual table rows, we need to read all rows from the data_file_path files and remove the rows labeled as deleted in the delete_file_path.

Not all files have to contain all the columns currently defined in the table, some files may also have columns that existed previously but have been removed.

DuckLake also supports changing the schema, see schema evolution.

In DuckLake, paths can be relative to the initially specified data path. Whether path is relative or not is stored in the ducklake_data_file and ducklake_delete_file entries (path_is_relative) to the data_path prefix from ducklake_metadata.

### SELECT with File Pruning
One of the main strengths of Lakehouse formats is the ability to prune files that cannot contain data relevant to the query. The ducklake_file_column_statistics table contains the file-level statistics. We can use the information there to prune the list of files to be read if a filter predicate is given.

We can get a list of all files that are part of a given table like described above. We can then reduce that list to only relevant files by querying the per-file column statistics. For example, for scalar equality we can find the relevant files using the query below:

SELECT data_file_id
FROM ducklake_file_column_statistics
WHERE
    table_id  = TABLE_ID AND
    column_id = COLUMN_ID AND
    (SCALAR >= min_value OR min_value IS NULL) AND
    (SCALAR <= max_value OR max_value IS NULL);

where (again)

TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table.
COLUMN_ID is a BIGINT referring to the column_id column in the ducklake_column table.
SCALAR is the scalar comparision value for the pruning.
Of course, other filter predicates like greater than etc. will require slightly different filtering here.

The minimum and maximum values for each column are stored as strings and need to be cast for correct range filters on numeric columns.

## Writing Data
### Snapshot Creation
Any changes to data stored in DuckLake require the creation of a new snapshot. We need to:

create a new snapshot in ducklake_snapshot and
log the changes a snapshot made in ducklake_snapshot_changes
INSERT INTO ducklake_snapshot (
    snapshot_id,
    snapshot_timestamp,
    schema_version,
    next_catalog_id,
    next_file_id
)
VALUES (
    SNAPSHOT_ID,
    now(),
    SCHEMA_VERSION,
    NEXT_CATALOG_ID,
    NEXT_FILE_ID
);

INSERT INTO ducklake_snapshot_changes (
    snapshot_id,
    snapshot_changes
)
VALUES (
    SNAPSHOT_ID,
    CHANGES
);

where

SNAPSHOT_ID is the new snapshot identifier. This should be max(snapshot_id) + 1.
SCHEMA_VERSION is the schema version for the new snapshot. If any schema changes are made, this needs to be incremented. Otherwise the previous snapshot's schema_version can be re-used.
NEXT_CATALOG_ID gives the next unused identifier for tables, schemas, or views. This only has to be incremented if new catalog entries are created.
NEXT_FILE_ID is the same but for data or delete files.
CHANGES contains a list of changes performed by the snapshot. See the list of possible values in the ducklake_snapshot_changes table's documentation.

### CREATE SCHEMA
A schema is a collection of tables. In order to create a new schema, we can just insert into the ducklake_schema table:

INSERT INTO ducklake_schema (
    schema_id,
    schema_uuid,
    begin_snapshot,
    end_snapshot,
    schema_name
)
VALUES (
    SCHEMA_ID,
    uuid(),
    SNAPSHOT_ID,
    NULL,
    SCHEMA_NAME
);

where

SCHEMA_ID is the new schema identifier. This should be created by incrementing next_catalog_id from the previous snapshot.
SNAPSHOT_ID is the snapshot identifier of the new snapshot as described above.
SCHEMA_NAME is just the name of the new schema.

### CREATE TABLE
Creating a table in a schema is very similar to creating a schema. We insert into the ducklake_table table:

INSERT INTO ducklake_table (
    table_id,
    table_uuid,
    begin_snapshot,
    end_snapshot,
    schema_id,
    table_name
)
VALUES (
    TABLE_ID,
    uuid(),
    SNAPSHOT_ID,
    NULL,
    SCHEMA_ID,
    TABLE_NAME
);

where

TABLE_ID is the new table identifier. This should be created by further incrementing next_catalog_id from the previous snapshot.
SNAPSHOT_ID is the snapshot identifier of the new snapshot as described above.
SCHEMA_ID is a BIGINT referring to the schema_id column in the ducklake_schema table table.
TABLE_NAME is just the name of the new table.
A table needs some columns, we can add columns to the new table by inserting into the ducklake_column table table. For each column to be added, we run the following query:

INSERT INTO ducklake_column (column_id,
    begin_snapshot,
    end_snapshot,
    table_id,
    column_order,
    column_name,
    column_type,
    nulls_allowed
)
VALUES (
    COLUMN_ID,
    SNAPSHOT_ID,
    NULL,
    TABLE_ID,
    COLUMN_ORDER,
    COLUMN_NAME,
    COLUMN_TYPE,
    NULLS_ALLOWED
);

where

COLUMN_ID is the new column identifier. This ID must be unique within the table over its entire life time.
SNAPSHOT_ID is the snapshot identifier of the new snapshot as described above.
TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table.
COLUMN_ORDER is a number that defines where the column is placed in an ordered list of columns.
COLUMN_NAME is just the name of the column.
COLUMN_TYPE is the data type of the column. See the “Data Types” page for details.
NULLS_ALLOWED is a boolean that defines if NULL values can be stored in the column. Typically set to true.
We skipped some complexity in this example around default values and nested types and just left those fields as NULL. See the table schema definition for additional details.

### INSERT
Inserting data into a DuckLake table consists of two main steps: first, we need to write a Parquet file containing the actual row data to storage, and second, we need to register that file in the metadata tables and update global statistics. Let's assume the file has already been written.

INSERT INTO ducklake_data_file (
    data_file_id,
    table_id,
    begin_snapshot,
    end_snapshot,
    path,
    path_is_relative,
    file_format,
    record_count,
    file_size_bytes,
    footer_size,
    row_id_start
)
VALUES (
    DATA_FILE_ID,
    TABLE_ID,
    SNAPSHOT_ID,
    NULL,
    PATH,
    true,
    'parquet',
    RECORD_COUNT,
    FILE_SIZE_BYTES,
    FOOTER_SIZE,
    ROW_ID_START
);

where

DATA_FILE_ID is the new data file identifier. This ID must be unique within the table over its entire life time.
TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table.
SNAPSHOT_ID is the snapshot identifier of the new snapshot as described above.
PATH is the file name relative to the DuckLake data path from the top-level metadata.
RECORD_COUNT is the number of rows in the file.
FILE_SIZE_BYTES is the file size.
FOOTER_SIZE is the position of the Parquet footer. This helps with efficiently reading the file.
ROW_ID_START is the first logical row ID from the file. This number can be read from the ducklake_table_stats table via column next_row_id.
We have omitted some complexity around relative paths, encrypted files, partitioning and partial files in this example. Refer to the ducklake_data_file table documentation for details.

DuckLake also supports changing the schema, see schema evolution.

We will also have to update some statistics in the ducklake_table_stats table and ducklake_table_column_stats table` tables.

UPDATE ducklake_table_stats SET
    record_count = record_count + RECORD_COUNT,
    next_row_id = next_row_id + RECORD_COUNT,
    file_size_bytes = file_size_bytes + FILE_SIZE_BYTES
WHERE table_id = TABLE_ID;

UPDATE ducklake_table_column_stats
SET
    contains_null = contains_null OR NULL_COUNT > 0,
    contains_nan = contains_nan,
    min_value = min(min_value, MIN_VALUE),
    max_value = max(max_value, MAX_VALUE)
WHERE
    table_id  = TABLE_ID AND
    column_id = COLUMN_ID;

INSERT INTO ducklake_file_column_statistics (
    data_file_id,
    table_id,
    column_id,
    value_count,
    null_count,
    min_value,
    max_value,
    contains_nan
)
VALUES (
    DATA_FILE_ID,
    TABLE_ID,
    COLUMN_ID,
    RECORD_COUNT,
    NULL_COUNT,
    MIN_VALUE,
    MAX_VALUE,
    CONTAINS_NAN;
);

where

TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table.
COLUMN_ID is a BIGINT referring to the column_id column in the ducklake_column table.
DATA_FILE_ID is a BIGINT referring to the data_file_id column in the ducklake_data_file table.
RECORD_COUNT is the number of values (including NULL and NaN values) in the file column.
NULL_COUNT is the number of NULL values in the file column.
MIN_VALUE is the minimum value in the file column as a string.
MAX_VALUE is the maximum value in the file column as a string.
FILE_SIZE_BYTES is the size of the new Parquet file.
CONTAINS_NAN is a flag whether the column contains any NaN values. This is only relevant for floating-point types.
This example assumes there are already rows in the table. If there are none, we need to use INSERT instead here. We also skipped the column_size_bytes column here, it can safely be set to NULL.

### DELETE
Deleting data from a DuckLake table consists of two main steps: first, we need to write a Parquet delete file containing the row index to be deleted to storage, and second, we need to register that delete file in the metadata tables. Let's assume the file has already been written.

INSERT INTO ducklake_delete_file (
    delete_file_id,
    table_id,
    begin_snapshot,
    end_snapshot,
    data_file_id,
    path,
    path_is_relative,
    format,
    delete_count,
    file_size_bytes,
    footer_size
)
VALUES (
    DELETE_FILE_ID,
    TABLE_ID,
    SNAPSHOT_ID,
    NULL,
    (DATA_FILE_ID),
    PATH,
    true,
    'parquet',
    DELETE_COUNT,
    FILE_SIZE_BYTES,
    FOOTER_SIZE
);

where

DELETE_FILE_ID is the identifier for the new delete file.
TABLE_ID is a BIGINT referring to the table_id column in the ducklake_table table.
SNAPSHOT_ID is the snapshot identifier of the new snapshot as described above.
DATA_FILE_ID is the identifier of the data file from which the rows are to be deleted.
PATH is the file name relative to the DuckLake data path from the top-level metadata.
DELETE_COUNT is the number of deletion records in the file.
FILE_SIZE_BYTES is the file size.
FOOTER_SIZE is the position of the Parquet footer. This helps with efficiently reading the file.
We have omitted some complexity around relative paths and encrypted files in this example. Refer to the ducklake_delete_file table documentation for details.

DELETE operations also do not require updates to table statistics, as the statistics are maintained as upper bounds, and deletions do not violate these bounds.

### UPDATE
In DuckLake, UPDATE operations are internally implemented as a combination of a DELETE followed by an INSERT. Specifically, the outdated row is marked for deletion, and the updated version of that row is inserted. As a result, the changes to the metadata tables are equivalent to performing a DELETE and an INSERT operation sequentially within the same transaction.

# Tables
DuckLake uses 21 tables to store metadata and to stage data fragments for data inlining. Below we describe all those tables and their semantics.

## Snapshots
ducklake_snapshot
ducklake_snapshot_changes

## DuckLake Schema
ducklake_schema
ducklake_table
ducklake_view
ducklake_column

## Data Files and Tables
ducklake_data_file
ducklake_delete_file
ducklake_files_scheduled_for_deletion
ducklake_inlined_data_tables

## Data File Mapping
ducklake_column_mapping
ducklake_name_mapping

## Statistics
DuckLake supports statistics on the table, column and file level.

ducklake_table_stats
ducklake_table_column_stats
ducklake_file_column_statistics

## Partitioning Information
DuckLake supports defining explicit partitioning.

ducklake_partition_info
ducklake_partition_column
ducklake_file_partition_value

## Auxiliary Tables
ducklake_metadata
ducklake_tag
ducklake_column_tag

## Full Schema Creation Script
Below is the full SQL script to create a DuckLake metadata database, at the latest version at the time of writing (0.2):

```sql
CREATE TABLE ducklake_metadata (key VARCHAR NOT NULL, value VARCHAR NOT NULL, scope VARCHAR, scope_id BIGINT);
CREATE TABLE ducklake_snapshot (snapshot_id BIGINT PRIMARY KEY, snapshot_time TIMESTAMPTZ, schema_version BIGINT, next_catalog_id BIGINT, next_file_id BIGINT);
CREATE TABLE ducklake_snapshot_changes (snapshot_id BIGINT PRIMARY KEY, changes_made VARCHAR);
CREATE TABLE ducklake_schema (schema_id BIGINT PRIMARY KEY, schema_uuid UUID, begin_snapshot BIGINT, end_snapshot BIGINT, schema_name VARCHAR, path VARCHAR, path_is_relative BOOLEAN);
CREATE TABLE ducklake_table (table_id BIGINT, table_uuid UUID, begin_snapshot BIGINT, end_snapshot BIGINT, schema_id BIGINT, table_name VARCHAR, path VARCHAR, path_is_relative BOOLEAN);
CREATE TABLE ducklake_view (view_id BIGINT, view_uuid UUID, begin_snapshot BIGINT, end_snapshot BIGINT, schema_id BIGINT, view_name VARCHAR, dialect VARCHAR, sql VARCHAR, column_aliases VARCHAR);
CREATE TABLE ducklake_tag (object_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT, key VARCHAR, value VARCHAR);
CREATE TABLE ducklake_column_tag (table_id BIGINT, column_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT, key VARCHAR, value VARCHAR);
CREATE TABLE ducklake_data_file (data_file_id BIGINT PRIMARY KEY, table_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT, file_order BIGINT, path VARCHAR, path_is_relative BOOLEAN, file_format VARCHAR, record_count BIGINT, file_size_bytes BIGINT, footer_size BIGINT, row_id_start BIGINT, partition_id BIGINT, encryption_key VARCHAR, partial_file_info VARCHAR, mapping_id BIGINT);
CREATE TABLE ducklake_file_column_statistics (data_file_id BIGINT, table_id BIGINT, column_id BIGINT, column_size_bytes BIGINT, value_count BIGINT, null_count BIGINT, min_value VARCHAR, max_value VARCHAR, contains_nan BOOLEAN);
CREATE TABLE ducklake_delete_file (delete_file_id BIGINT PRIMARY KEY, table_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT, data_file_id BIGINT, path VARCHAR, path_is_relative BOOLEAN, format VARCHAR, delete_count BIGINT, file_size_bytes BIGINT, footer_size BIGINT, encryption_key VARCHAR);
CREATE TABLE ducklake_column (column_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT, table_id BIGINT, column_order BIGINT, column_name VARCHAR, column_type VARCHAR, initial_default VARCHAR, default_value VARCHAR, nulls_allowed BOOLEAN, parent_column BIGINT);
CREATE TABLE ducklake_table_stats (table_id BIGINT, record_count BIGINT, next_row_id BIGINT, file_size_bytes BIGINT);
CREATE TABLE ducklake_table_column_stats (table_id BIGINT, column_id BIGINT, contains_null BOOLEAN, contains_nan BOOLEAN, min_value VARCHAR, max_value VARCHAR);
CREATE TABLE ducklake_partition_info (partition_id BIGINT, table_id BIGINT, begin_snapshot BIGINT, end_snapshot BIGINT);
CREATE TABLE ducklake_partition_column (partition_id BIGINT, table_id BIGINT, partition_key_index BIGINT, column_id BIGINT, transform VARCHAR);
CREATE TABLE ducklake_file_partition_value (data_file_id BIGINT, table_id BIGINT, partition_key_index BIGINT, partition_value VARCHAR);
CREATE TABLE ducklake_files_scheduled_for_deletion (data_file_id BIGINT, path VARCHAR, path_is_relative BOOLEAN, schedule_start TIMESTAMPTZ);
CREATE TABLE ducklake_inlined_data_tables (table_id BIGINT, table_name VARCHAR, schema_version BIGINT);
CREATE TABLE ducklake_column_mapping (mapping_id BIGINT, table_id BIGINT, type VARCHAR);
CREATE TABLE ducklake_name_mapping (mapping_id BIGINT, column_id BIGINT, source_name VARCHAR, target_field_id BIGINT, parent_column BIGINT);
```

## ducklake_column
This table describes the columns that are part of a table, including their types, default values etc.

Column name	Column type	 
column_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
table_id	BIGINT	 
column_order	BIGINT	 
column_name	VARCHAR	 
column_type	VARCHAR	 
initial_default	VARCHAR	 
default_value	VARCHAR	 
nulls_allowed	BOOLEAN	 
parent_column	BIGINT

- column_id is the numeric identifier of the column, which should persist throughout all versions of the column, until it's dropped.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. This version of the column exists starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. This version of the column exists until this snapshot id. If end_snapshot is NULL, this version of the column is currently valid.
- table_id refers to a table_id from the ducklake_table table.
column_order is a number that defines the position of the column in the list of columns. it needs to be unique within a snapshot but does not have to be strictly monotonic (holes are ok).
- column_name is the name of this version of the column, e.g. my_column.
- column_type is the type of this version of the column as defined in the list of data types.
- initial_default is the initial default value as the column is being created e.g. in ALTER TABLE, encoded as a string. Can be NULL.
- default_value is the operational default value as data is being inserted and updated, e.g. in INSERT, encoded as a string. Can be NULL.
- nulls_allowed defines whether NULL values are allowed in this version of the column. Note that default values have to be set if this is set to false.
- parent_column is the column_id of the parent column. This is NULL for top-level and non-nested columns. For example, for STRUCT types, this would refer to the "parent" struct column.

Every ALTER of the column creates a new version of the column, which will use the same column_id.

## ducklake_column_mapping
Mappings contain the information used to map parquet fields to column ids in the absence of field-ids in the Parquet file.

Column name	Column type	 
mapping_id	BIGINT	 
table_id	BIGINT	 
type	VARCHAR	 

- mapping_id is the numeric identifier of the mapping. mapping_id is incremented from next_catalog_id in the ducklake_snapshot table.
- table_id refers to a table_id from the ducklake_table table.
- type defines what method is used to perform the mapping.

The valid type values:

type	Description
map_by_name	Map the columns based on the names in the parquet file

## ducklake_name_mapping
This table contains the information used to map a name to a column_id for a given mapping_id with the map_by_name type.

Column name	Column type	 
mapping_id	BIGINT	 
column_id	BIGINT	 
source_name	VARCHAR	 
target_field_id	BIGINT	 
parent_column	BIGINT	 

- mapping_id refers to a mapping_id from the ducklake_column_mapping table.
- column_id refers to a column_id from the ducklake_column table.
- source_name refers to the name of the field this mapping applies to.
- target_field_id refers to the field-id that a field with the source_name is mapped to.
- parent_column is the column_id of the parent column. This is NULL for top-level and non-nested columns. For example, for STRUCT types, this would refer to the "parent" struct column.

## ducklake_column_tag
Columns can also have tags, those are defined in this table.

Column name	Column type	 
table_id	BIGINT	 
column_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
key	VARCHAR	 
value	VARCHAR	 

- table_id refers to a table_id from the ducklake_table table.
- column_id refers to a column_id from the ducklake_column table.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The tag is valid starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The tag is valid up to but not including this snapshot id. If end_snapshot is NULL, the tag is currently valid.
- key is an arbitrary key string. The key can't be NULL.
- value is the arbitrary value string.

## ducklake_data_file
Data files contain the actual row data.

Column name	Column type	 
data_file_id	BIGINT	Primary Key
table_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
file_order	BIGINT	 
path	VARCHAR	 
path_is_relative	BOOLEAN	 
file_format	VARCHAR	 
record_count	BIGINT	 
file_size_bytes	BIGINT	 
footer_size	BIGINT	 
row_id_start	BIGINT	 
partition_id	BIGINT	 
encryption_key	VARCHAR	 
partial_file_info	VARCHAR	 
mapping_id	BIGINT	 

- data_file_id is the numeric identifier of the file. It is a primary key. data_file_id is incremented from next_file_id in the ducklake_snapshot table.
- table_id refers to a table_id from the ducklake_table table.
begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The file is part of the table starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The file is part of the table up to but not including this snapshot id. If end_snapshot is NULL, the file is currently part of the table.
- file_order is a number that defines the vertical position of the file in the table. it needs to be unique within a snapshot but does not have to be strictly monotonic (holes are ok).
- path is the file path of the data file, e.g. my_file.parquet for a relative path.
- path_is_relative whether the path is relative to the path of the table (true) or an absolute path (false).
- file_format is the storage format of the file. Currently, only parquet is allowed.
- record_count is the number of records (row) in the file.
- file_size_bytes is the size of the file in Bytes.
- footer_size is the size of the file metadata footer, in the case of Parquet the Thrift data. This is an optimization that allows for faster reading of the file.
- row_id_start is the first logical row id in the file. (Every row has a unique row-id that is maintained.)
- partition_id refers to a partition_id from the ducklake_partition_info table.
- encryption_key contains the encryption for the file if encryption is enabled.
- partial_file_info is used when snapshots refer to parts of a file.
- mapping_id refers to a mapping_id from the ducklake_column_mapping table

## ducklake_delete_file
Delete files contains the row ids of rows that are deleted. Each data file will have its own delete file if any deletes are present for this data file.

Column name	Column type	 
delete_file_id	BIGINT	Primary Key
table_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
data_file_id	BIGINT	 
path	VARCHAR	 
path_is_relative	BOOLEAN	 
format	VARCHAR	 
delete_count	BIGINT	 
file_size_bytes	BIGINT	 
footer_size	BIGINT	 
encryption_key	VARCHAR	 

- delete_file_id is the numeric identifier of the delete file. It is a primary key. - delete_file_id is incremented from next_file_id in the ducklake_snapshot table.
- table_id refers to a table_id from the ducklake_table table.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The delete file is part of the table starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The delete file is part of the table up to but not including this snapshot id. If end_snapshot is NULL, the delete file is currently part of the table.
- data_file_id refers to a data_file_id from the ducklake_data_file table.
path is the file name of the delete file, e.g. my_file-deletes.parquet for a relative path.
- path_is_relative whether the path is relative to the path of the table (true) or an absolute path (false).
- format is the storage format of the delete file. Currently, only parquet is allowed.
- delete_count is the number of deletion records in the file.
- file_size_bytes is the size of the file in Bytes.
- footer_size is the size of the file metadata footer, in the case of Parquet the Thrift data. This is an optimization that allows for faster reading of the file.
- encryption_key contains the encryption for the file if encryption is enabled.

## ducklake_file_column_statistics
This table contains column-level statistics for a single data file.

Column name	Column type	 
data_file_id	BIGINT	 
table_id	BIGINT	 
column_id	BIGINT	 
column_size_bytes	BIGINT	 
value_count	BIGINT	 
null_count	BIGINT	 
min_value	VARCHAR	 
max_value	VARCHAR	 
contains_nan	BOOLEAN	 

- data_file_id refers to a data_file_id from the ducklake_data_file table.
- table_id refers to a table_id from the ducklake_table table.
- column_id refers to a column_id from the ducklake_column table.
- column_size_bytes is the byte size of the column.
- value_count is the number of values in the column. This does not have to correspond to the number of records in the file for nested types.
- null_count is the number of values in the column that are NULL.
- min_value contains the minimum value for the column, encoded as a string. This does not have to be exact but has to be a lower bound. The value has to be cast to the actual type for accurate comparision, e.g. on integer types.
- max_value contains the maximum value for the column, encoded as a string. This does not have to be exact but has to be an upper bound. The value has to be cast to the actual type for accurate comparision, e.g. on integer types.
- contains_nan is a flag whether the column contains any NaN values. This is only relevant for floating-point types.

## ducklake_file_partition_value
This table defines which data file belongs to which partition.

Column name	Column type	 
data_file_id	BIGINT	 
table_id	BIGINT	 
partition_key_index	BIGINT	 
partition_value	VARCHAR	 

- data_file_id refers to a data_file_id from the ducklake_data_file table.
- table_id refers to a table_id from the ducklake_table table.
- partition_key_index refers to a partition_key_index from the ducklake_partition_column table.
- partition_value is the value that all the rows in the data file have, encoded as a string.

## ducklake_files_scheduled_for_deletion
Files that are no longer part of any snapshot are scheduled for deletion

Column name	Column type	 
data_file_id	BIGINT	 
path	VARCHAR	 
path_is_relative	BOOLEAN	 
schedule_start	TIMESTAMP	 

- data_file_id refers to a data_file_id from the ducklake_data_file table.
- path is the file name of the file, e.g. my_file.parquet. The file name is either relative to the data_path value in ducklake_metadata or absolute. If relative, the - - path_is_relative field is set to true.
- path_is_relative defines whether the path is absolute or relative, see above.
- schedule_start is a time stamp of when this file was scheduled for deletion.

## ducklake_inlined_data_tables
This table links DuckLake snapshots with inlined data tables.

Column name	Column type	 
table_id	BIGINT	 
table_name	VARCHAR	 
schema_version	BIGINT	 

- table_id refers to a table_id from the ducklake_table table.
- table_name is a string that names the data table for inlined data.
- schema_version refers to a schema version in the ducklake_snapshot table.

## ducklake_metadata
The ducklake_metadata table contains key/value pairs with information about the specific setup of the DuckLake catalog.

Column name	Column type	 
key	VARCHAR	Not NULL
value	VARCHAR	Not NULL
scope	VARCHAR	 
scope_id	BIGINT	 

- key is an arbitrary key string. See below for a list of pre-defined keys. The key can't be NULL.
- value is the arbitrary value string.
- scope defines the scope of the setting.
- scope_id is the id of the item that the setting is scoped to (see the table below) or NULL for the Global scope.

Scope	scope	Description
Global	NULL	The scope of the setting is global for the entire catalog.
Schema	schema	The setting is scoped to the schema_id referenced by scope_id.
Table	table	The setting is scoped to the table_id referenced by scope_id.

Currently, the following values for key are specified:

Name	Description	Notes	Scope(s)
- version	The DuckLake schema version.	 	Global
- table	A string that identifies which program wrote the schema, e.g., DuckDB v1.3.2	 	Global
- data_path	The data path prefix for reading and writing data files, e.g., s3://mybucket/myprefix/	Has to end in /	Global
- encrypted	A boolean that specifies whether data files are encrypted or not.	'true' or 'false'	Global
- data_inlining_row_limit	The maximum amount of rows to inline in a single insert	 	Global, Schema or Table
- target_file_size	The size in bytes to limit a parquet file at for insert and compaction operations	 	Global, Schema or Table
- parquet_row_group_size_bytes	The size in bytes to limit a parquet file rowgroup at for insert and compaction operations	 	Global, Schema or Table
- parquet_row_group_size	The size in number of rows to limit a parquet file rowgroup at for insert and compaction operations	 	Global, Schema or Table
- parquet_compression	The compression used to write parquet files e.g., zstd	uncompressed, snappy, gzip, zstd, brotli, lz4, lz4_raw	Global, Schema or Table
- parquet_compression_level	The compression level used for the selected parquet_compression	 	Global, Schema or Table
- parquet_version	The version of the Parquet standard used to write parquet files	1 or 2	Global, Schema or Table

## ducklake_partition_column
Partitions can refer to one or more columns, possibly with transformations such as hashing or bucketing.

Column name	Column type	 
partition_id	BIGINT	 
table_id	BIGINT	 
partition_key_index	BIGINT	 
column_id	BIGINT	 
transform	VARCHAR	 

- partition_id refers to a partition_id from the ducklake_partition_info table.
- table_id refers to a table_id from the ducklake_table table.
- partition_key_index defines where in the partition key the column is. For example, in a partitioning by (a, b, c) the partition_key_index of b would be 1.
- column_id refers to a column_id from the ducklake_column table.
- transform defines the type of a transform that is applied to the column value, e.g. year.
The table of supported transforms is as follows.

Transform	Source Type(s)	Description	Result Type
- identity	Any	Source value, unmodified	Source type
- year	date, timestamp, timestamptz, timestamp_s, timestamp_ms, timestamp_ns	Extract a date or timestamp year, as years from 1970	int64
- month	date, timestamp, timestamptz, timestamp_s, timestamp_ms, timestamp_ns	Extract a date or timestamp month, as months from 1970-01-01	int64
- day	date, timestamp, timestamptz, timestamp_s, timestamp_ms, timestamp_ns	Extract a date or timestamp day, as days from 1970-01-01	int64
- hour	timestamp, timestamptz, timestamp_s, timestamp_ms, timestamp_ns	Extract a timestamp hour, as hours from 1970-01-01 00:00:00	int64

## ducklake_partition_info

Column name	Column type	 
partition_id	BIGINT	 
table_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 

- partition_id is a numeric identifier for a partition. partition_id is incremented from next_catalog_id in the ducklake_snapshot table.
- table_id refers to a table_id from the ducklake_table table.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The partition is valid starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The partition is valid up to but not including this snapshot id. If end_snapshot is NULL, the partition is currently valid.

## ducklake_schema
This table defines valid schemas.

Column name	Column type	 
schema_id	BIGINT	Primary Key
schema_uuid	UUID	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
schema_name	VARCHAR	 
path	VARCHAR	 
path_is_relative	BOOLEAN	 

- schema_id is the numeric identifier of the schema. schema_id is incremented from next_catalog_id in the ducklake_snapshot table.
- schema_uuid is a UUID that gives a persistent identifier for this schema. The UUID is stored here for compatibility with existing Lakehouse formats.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The schema exists starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The schema exists up to but not including this snapshot id. If end_snapshot is NULL, the schema is currently valid.
- schema_name is the name of the schema, e.g. my_schema.
- path is the data_path of the schema.
- path_is_relative whether the path is relative to the data_path of the catalog (true) or an absolute path (false).

## ducklake_snapshot
This table contains the valid snapshots in a DuckLake.

Column name	Column type	 
snapshot_id	BIGINT	Primary Key
snapshot_time	TIMESTAMP	 
schema_version	BIGINT	 
next_catalog_id	BIGINT	 
next_file_id	BIGINT	 

- snapshot_id is the continuously increasing numeric identifier of the snapshot. It is a primary key and is referred to by various other tables below.
- snapshot_time is the time stamp at which the snapshot was created.
- schema_version is an continously increasing number that is incremented whenever the schema is changed, e.g. by creating a table. This allows for caching of schema information if only data is changed.
- next_catalog_id is a continously increasing number that describes the next identifier for schemas, tables, views, partitions, and column name mappings. This is only changed if one of those entries is created, i.e., the schema is changing.
- next_file_id is a continously increasing number that contains the next id for a data or deletion file to be added. It is only changed if data is being added or deleted, i.e., not for schema changes.

## ducklake_snapshot_changes
This table lists changes that happened in a snapshot for easier conflict detection.

Column name	Column type	 
snapshot_id	BIGINT	Primary Key
changes_made	VARCHAR	 

The ducklake_snapshot_changes table contains a summary of changes made by a snapshot. This table is used during Conflict Resolution to quickly find out if two snapshots have conflicting changesets.

- snapshot_id refers to a snapshot_id from the ducklake_snapshot table.
- changes_made is a comma-separated list of high-level changes made by the snapshot. The values that are contained in this list have the following format:
- created_schema:SCHEMA_NAME – the snapshot created a schema with the given name.
- created_table:TABLE_NAME – the snapshot created a table with the given name.
- created_view:VIEW_NAME – the snapshot created a view with the given name.
- inserted_into_table:TABLE_ID – the snapshot inserted data into the given table.
- deleted_from_table:TABLE_ID – the snapshot deleted data from the given table.
- compacted_table:TABLE_ID – the snapshot run a compaction operation on the given table.
- dropped_schema:SCHEMA_ID – the snapshot dropped the given schema.
- dropped_table:TABLE_ID – the snapshot dropped the given table.
- dropped_view:VIEW_ID – the snapshot dropped the given view.
- altered_table:TABLE_ID – the snapshot altered the given table.
- altered_view:VIEW_ID – the snapshot altered the given view.

Names are written in quoted-format using SQL-style escapes, i.e., the name this "table" contains quotes is written as "this ""table"" contains quotes".

## ducklake_table
This table describes tables. Inception!

Column name	Column type	 
table_id	BIGINT	 
table_uuid	UUID	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
schema_id	BIGINT	 
table_name	VARCHAR	 
path	VARCHAR	 
path_is_relative	BOOLEAN	 

- table_id is the numeric identifier of the table. table_id is incremented from next_catalog_id in the ducklake_snapshot table.
- table_uuid is a UUID that gives a persistent identifier for this table. The UUID is stored here for compatibility with existing Lakehouse formats.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The table exists starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The table exists up to but not including this snapshot id. If end_snapshot is NULL, the table is currently valid.
- schema_id refers to a schema_id from the ducklake_schema table.
- table_name is the name of the table, e.g. my_table.
- path is the data_path of the table.
- path_is_relative whether the path is relative to the path of the schema (true) or an absolute path (false).

## ducklake_table_column_stats
This table contains column-level statistics for an entire table.

Column name	Column type	 
table_id	BIGINT	 
column_id	BIGINT	 
contains_null	BOOLEAN	 
contains_nan	BOOLEAN	 
min_value	VARCHAR	 
max_value	VARCHAR	 

- table_id refers to a table_id from the ducklake_table table.
- column_id refers to a column_id from the ducklake_column table.
- contains_null is a flag whether the column contains any NULL values.
- contains_nan is a flag whether the column contains any NaN values. This is only relevant for floating-point types.
- min_value contains the minimum value for the column, encoded as a string. This does not have to be exact but has to be a lower bound. The value has to be cast to the actual type for accurate comparision, e.g. on integer types.
- max_value contains the maximum value for the column, encoded as a string. This does not have to be exact but has to be an upper bound. The value has to be cast to the actual type for accurate comparision, e.g. on integer types.

## ducklake_table_stats
This table contains table-level statistics.

Column name	Column type	 
table_id	BIGINT	 
record_count	BIGINT	 
next_row_id	BIGINT	 
file_size_bytes	BIGINT	 

- table_id refers to a table_id from the ducklake_table table.
- record_count is the total amount of rows in the table. This can be approximate.
- next_row_id is the row id for newly inserted rows. Used for row lineage tracking.
- file_size_bytes is the total file size of all data files in the table. This can be approximate.

## ducklake_tag
Schemas, tables, and views etc can have tags, those are declared in this table.

Column name	Column type	 
object_id	BIGINT	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
key	VARCHAR	 
value	VARCHAR	 

- object_id refers to a schema_id, table_id etc. from various tables above.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The tag is valid starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The tag is valid up to but not including this snapshot id. If end_snapshot is NULL, the tag is currently valid.
- key is an arbitrary key string. The key can't be NULL.
- value is the arbitrary value string.

## ducklake_view
This table describes SQL-style VIEW definitions.

Column name	Column type	 
view_id	BIGINT	 
view_uuid	UUID	 
begin_snapshot	BIGINT	 
end_snapshot	BIGINT	 
schema_id	BIGINT	 
view_name	VARCHAR	 
dialect	VARCHAR	 
sql	VARCHAR	 
column_aliases	VARCHAR	 

- view_id is the numeric identifier of the view. view_id is incremented from next_catalog_id in the ducklake_snapshot table.
- view_uuid is a UUID that gives a persistent identifier for this view. The UUID is stored here for compatibility with existing Lakehouse formats.
- begin_snapshot refers to a snapshot_id from the ducklake_snapshot table. The view exists starting with this snapshot id.
- end_snapshot refers to a snapshot_id from the ducklake_snapshot table. The view exists up to but not including this snapshot id. If end_snapshot is NULL, the view is currently valid.
- schema_id refers to a schema_id from the ducklake_schema table.
- view_name is the name of the view, e.g. my_view.
- dialect is the SQL dialect of the view definition, e.g. duckdb.
- sql is the SQL string that defines the view, e.g. SELECT * FROM my_table
- column_aliases contains a possible rename of the view columns. Can be NULL if no rename is set.

# Introduction
In DuckDB, DuckLake is supported through the ducklake extension.

## Installation
Install the latest stable DuckDB. (The ducklake extension requires DuckDB v1.3.0 "Ossivalis" or later.)

```sql
INSTALL ducklake;
```

## Configuration
To use DuckLake, you need to make two decisions: which metadata catalog database you want to use and where you want to store those files. In the simplest case, you use a local DuckDB file for the metadata catalog and a local folder on your computer for file storage.

## Creating a New Database
DuckLake databases are created by simply starting to use them with the ATTACH statement. In the simplest case, you can create a local, DuckDB-backed DuckLake like so:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;
USE my_ducklake;
```

This will create a file my_ducklake.ducklake, which is a DuckDB database with the DuckLake schema.

We also use USE so we don't have to prefix all table names with my_ducklake. Once data is inserted, this will also create a folder my_ducklake.ducklake.files in the same directory, where Parquet files are stored.

If you would like to use another directory, you can specify this in the DATA_PATH parameter for ATTACH:

```sql
ATTACH 'ducklake:my_other_ducklake.ducklake' AS my_other_ducklake (DATA_PATH 'some/other/path/');
USE ...;
```

The path is stored in the DuckLake metadata and does not have to be specified again to attach to an existing DuckLake catalog.

Both DATA PATH and the database file path should be relative paths (e.g. ./some/path/ or some/path/). Moreover, for database creation the path needs to exist already, i.e. ATTACH 'ducklake:db/my_ducklake.ducklake' AS my_ducklake; where db needs to be an existing directory.

## Attaching an Existing Database
Attaching to an existing database also uses the ATTACH syntax. For example, to re-connect to the example from the previous section in a new DuckDB session, we can just type:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;
USE my_ducklake;
```

## Using DuckLake
DuckLake is used just like any other DuckDB database. You can create schemas and tables, insert data, update data, delete data, modify table schemas etc.

Note that – similarly to other data lake and lakehouse formats – the DuckLake format does not support indexes, primary keys, foreign keys, and UNIQUE or CHECK constraints.

Don't forget to either specify the database name of the DuckLake explicity or use USE. Otherwise you might inadvertently use the temporary, in-memory database.

## Example
Let's observe what happens in DuckLake when we interact with a dataset. We will use the Netherlands train traffic dataset here.

We use the example DuckLake from above:

```sql
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;
USE my_ducklake;
```

Let's now import the dataset into the a new table:

```sql
CREATE TABLE nl_train_stations AS
    FROM 'https://blobs.duckdb.org/nl_stations.csv';
```

Now Let's peek behind the courtains. The data was just read into a Parquet file, which we can also just query.

```sql
FROM glob('my_ducklake.ducklake.files/**/*');
FROM 'my_ducklake.ducklake.files/**/*.parquet' LIMIT 10;
```

But now lets change some things around. We're really unhappy with the name of the old name of the "Amsterdam Bijlmer ArenA" station now that the stadium has been renamed to "Johan Cruijff ArenA" and everyone here loves Johan. So let's change that.

```sql
UPDATE nl_train_stations SET name_long='Johan Cruijff ArenA' WHERE code = 'ASB';
```

Poof, its changed. We can confirm:

```sql
SELECT name_long FROM nl_train_stations WHERE code = 'ASB';
```

In the background, more files have appeared:

```sql
FROM glob('my_ducklake.ducklake.files/**/*');
```

We now see three files. The original data file, the rows that were deleted, and the rows that were inserted. Like most systems, DuckLake models updates as deletes followed by inserts. The deletes are just a Parquet file, we can query it:

```sql
FROM 'my_ducklake.ducklake.files/**/ducklake-*-delete.parquet';
```

The file should contain a single row that marks row 29 as deleted. A new file has appared that contains the new values for this row.

There are now three snapshots, the table creation, data insertion, and the update. We can query that using the snapshots() function:

```sql
FROM my_ducklake.snapshots();
```

And we can query this table at each point:

```sql
SELECT name_long FROM nl_train_stations AT (VERSION => 1) WHERE code = 'ASB';
SELECT name_long FROM nl_train_stations AT (VERSION => 2) WHERE code = 'ASB';
```

Time travel finally achieved!

## Detaching from a DuckLake
To detach from a DuckLake, make sure that your DuckLake is not your default database, then use the DETACH statement:

```sql
USE memory;
DETACH my_ducklake;
```

## Using DuckLake from a Client
DuckDB works with any DuckDB client that supports DuckDB version 1.3.0.

# List Files
The ducklake_list_files function can be used to list the data files and corresponding delete files that belong to a given table, optionally for a given snapshot.

## Usage

```sql
-- list all files
FROM ducklake_list_files('catalog', 'table_name');
-- get list of files at a specific snapshot_version
FROM ducklake_list_files('catalog', 'table_name', snapshot_version => 2);
-- get list of files at a specific point in time
FROM ducklake_list_files('catalog', 'table_name', snapshot_time => '2025-06-16 15:24:30');
-- get list of files of a table in a specific schema
FROM ducklake_list_files('catalog', 'table_name', schema => 'main');
```

Parameter	Description	Default
- catalog	Name of attached DuckLake catalog	 
- table_name	Name of table to fetch files from	 
- schema	Schema for the table	main
- snapshot_version	If provided, fetch files for a given snapshot id	 
- snapshot_time	If provided, fetch files for a given timestamp	 

## Result
The function returns the following result set.

column_name	column_type
- data_file	VARCHAR
- data_file_size_bytes	UBIGINT
- data_file_footer_size	UBIGINT
- data_file_encryption_key	BLOB
- delete_file	VARCHAR
- delete_file_size_bytes	UBIGINT
- delete_file_footer_size	UBIGINT
- delete_file_encryption_key	BLOB

- If the file has delete files, the corresponding delete file is returned, otherwise these fields are NULL.
- If the database is encrypted, the encryption key must be used to read the file.
- The footer_size refers to the Parquet footer size - this is optionally provided.

# Adding Files

The ducklake_add_data_files function can be used to register existing data files as new files in DuckLake. The files are not copied over - DuckLake is merely made aware of their existence, allowing them to be queried through DuckLake. Adding files in this manner supports regular transactional semantics.

Note
that ownership of the Parquet file is transferred to DuckLake. As such, compaction operations (such as those triggered through merge_adjacent_files or expire_snapshots followed by cleanup_old_files) can cause the files to be deleted by DuckLake.

## Usage

```sql
-- add the file "people.parquet" to the "people" table in "my_ducklake"
CALL ducklake_add_data_files('my_ducklake', 'people', 'people.parquet');
-- add the file - any columns that are present in the table but not in the file will have their default values used when reading
CALL ducklake_add_data_files('my_ducklake', 'people', 'people.parquet', allow_missing => true);
-- add the file - if the file has extra columns in the table they will be ignored (they will not be queryable through DuckLake)
CALL ducklake_add_data_files('my_ducklake', 'people', 'people.parquet', ignore_extra_columns => true);
```

### Missing Columns
When adding files to a table, all columns that are present in the table must be present in the Parquet file, otherwise an error is thrown. The allow_missing option can be used to add the file anyway - in which case any missing columns will be substituted with the initial_default value of the column.

### Extra Columns
When adding files to a table, if there are any columns present that are not present in the table, an error is thrown by default. The ignore_extra_columns option can be used to add the file anyway - any extra columns will be ignored and unreachable.

## Type Mapping
In general, types of columns in the source Parquet file must match the type as defined in the table, otherwise an error is thrown. Types in the Parquet file can be narrower than the type defined in the table. Below is a supported mapping type:

Table Type	Supported Parquet Types
bool	bool
int8	int8
int16	int[8/16], uint8
int32	int[8/16/32], uint[8/16]
int64	int[8/16/32/64], uint[8/16/32]
uint8	uint8
uint16	uint[8/16]
uint32	uint[8/16/32]
uint64	uint[8/16/32/64]
float	float
double	float/double
decimal(P, S)	decimal(P',S'), where P' <= P and S' <= S
blob	blob
varchar	varchar
date	date
time	time
timestamp	timestamp, timestamp_ns
timestamp_ns	timestamp, timestamp_ns
timestamptz	timestamptz

# Unsupported Features
This page describes what is supported in DuckDB and DuckLake in relation to DuckDB standalone (i.e., :memory: or DuckDB file modes). We can make a distinction between:

- What is currently not supported by the DuckLake specification. These are features that you are supported by DuckDB when using DuckDB's native database format but will not work with a DuckLake backend since the specification does not support them.

- What is currently not supported by the ducklake DuckDB extension. These are features that are supported by the DuckLake specification but are not (yet) implemented in the DuckDB extension.

## Unsupported by the DuckLake Specification
Within this group, we are going to make a distinction between what is not supported now but is likely to be supported in the future and what is not supported and is unlikely to be supported.

### Likely to be Supported in the Future
- User defined types

- Geometry/Geospatial types

- Fixed-size arrays, i.e., ARRAY type

- Variant types

- CHECK constraints. Not to be confused with Primary or Foreign Key constraint.

- Scalar and table macros. However, if the catalog DB supports it, there is a workaround.

```sql
  -- Using DuckDB as a catalog, create the macro in the catalog
  USE __ducklake_metadata_my_ducklake;
  CREATE MACRO add_and_multiply(a, b, c) AS (a + b) * c;

  -- Use the macro to create a table in DuckLake
  CREATE TABLE my_ducklake.table_w_macro AS
      SELECT add_and_multiply(1, 2, 3) AS col;
```

- Default values that are not literals. See the following example:

```sql
  -- This is allowed
  CREATE TABLE t1 (id INTEGER, d DATE DEFAULT '2025-08-08');

  -- This is not allowed
  CREATE TABLE t1 (id INTEGER, d DATE DEFAULT now());
```

- Dropping dependencies, such as views, when calling DROP ... CASCADE. Note that this is also a DuckDB limitation.

- Generated columns

### Unlikely to be Supported in the Future
- Indexes

- Primary key or enforced unique constraints and foreign key constraints are unlikely to be supported as these are constraints are prohibitively expensive to enforce in data lake setups. We may consider supporting unenforced primary keys, similar to BigQuery's implementation.

- Sequences

- VARINT type

- BITSTRING type

- UNION type

## Unsupported by the ducklake DuckDB Extension
The following features are currently unsupported by the ducklake DuckDB extension:

- Data inlining is limited to DuckDB catalogs

- MySQL catalogs are not fully supported in the DuckDB extension

- Updates that target the same row multiple times
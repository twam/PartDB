# PartDB

PartDB is a tool written in Python to maintain a small database in the style of
a JSON file of your (electronic) parts. It is meant to be simple and not
optimized for huge amounts of data.

## Database

The database consists of a single JSON file.

The following keys are used for the primary dictionary:

| Key name               | Type    | Description   |
| ---------------------- | ------- | ------------- |
| manufacturerPartNumber | string  |               |
| manufacturerName       | string  |               |
| description            | string  |               |
| quantity               | integer |               |
| distributor            | dict    |               |
| datasheetURL           | string  |               |
| timestampCreated       | float   |               |
| timestampLastModified  | float   |               |

The following keys are used for the distributor dictionary:

| Key name               | Type    | Description   |
| ---------------------- | ------- | ------------- |
| distributorName        | string  |               |
| distributorPartNumber  | string  |               |

# PartDB

[![Travis](http://img.shields.io/travis/twam/PartDB/master.svg)](https://travis-ci.org/twam/PartDB/)
[![Coveralls](https://img.shields.io/coveralls/twam/PartDB.svg)](https://coveralls.io/github/twam/PartDB)
[![GitHub license](https://img.shields.io/github/license/twam/PartDB.svg)]()

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

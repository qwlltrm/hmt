# Simple utility to show time distance in human readable format

## Installation

` pip install git+https://github.com/qwlltrm/hmt `

## Usage

` hmt 2000.01.01  `

This will print number of days since January 1 2000. Input supports different formats like

Jan 1 2000 | 2000/1/1 | 2000-01-01 etc.

It works with future dates too, for example:

` hmt 2100 `

Will give number of days from now to January 1 2100

For more details use ` hmt --help `
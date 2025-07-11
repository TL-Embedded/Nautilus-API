# Command Syntax

The Nautilus uses a subset of standard SCPI commands.

SCPI commands are command-response. Each command and reply is terminated with a carriage return and line feed "\r\n".

# Parameters

The following parameter types are supported

## Boolean [b]

A true or false.

Example: `1` or `0`, `ON` or `OFF`.

## Integer [i]

An ASCII encoded decimal number.

Example: `0` or `23`

## Numeric [u]

An ASCII encoded floating point number with unit suffix.

Example `23mV`, `0.01A`, `6.008kHz`

## String [s]

A string of characters. These must be delimited with quotes.

Example `"nautilus"`, `""`

## Bytes [x]

A string of hex encoded bytes.

Example `0001020304FF`

## Node index [#]

An integer identifier used for indexing command nodes.

This is parsed as per the integer [i], but negative values are not permitted.

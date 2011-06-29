## TEK Oscilloscope USB driver

Using the built in USBTMC driver in the kernel. This scope seems to
have a couple of peculiarities, so document and work around them.

## Goals

+ Correct send/receive commands (no timeouts)
+ Data acquisition and covering all commonly used functions
+ Documentation

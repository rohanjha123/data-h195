# Stata2Python

This package takes in Stata commands and outputs their Python equivalents. It currently supports the following commands: -
- ttest (doing a t-test)
- gen (generating new columns)
- describe (describing the data)
- corr (correlation matrix)
- scatter (make a scatter plot)
- hist (make a histogram)
- reg (run a regression)

Example usage via terminal
```
pip install --upgrade stata2python
python3
>>> from stata2python import convert_s2p
>>> convert_s2p("reg wage exp i.female, vce(cluster education)", "la")
```

The function `convert_s2p` takes in a Stata command as a string, followed by (optionally) the name of a Python DataFrame as a string, and outputs the relevant Python equivalent to the Stata command.
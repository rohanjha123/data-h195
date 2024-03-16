# Stata2Python

The function `stata2python` takes in a Stata command as a string, followed by (optionally) the name of a Python DataFrame as a string, and outputs the relevant Python equivalent to the Stata command. It currently supports the following commands: -
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
>>> from stata2python import stata2python
>>> stata2python("reg wage exp i.female, vce(cluster education)", "la")
```

You can see the implementations of the functions in `src/stata2python/funcs.py`. Please feel free to file issues and pull requests to make improvements to this package. You can find further instructions on how to use this package [here](https://www.econ148.org/textbook/content/01-python_v_stata/syntax.html).
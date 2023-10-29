import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import regex as re

def ttest(df_name, string):
    if "ttest" in string and "by(" in string:
        eq_var = True
        nan_pol = 'propagate'
        df = eval(df_name)
        
        string = string.replace("ttest ", "")
        catvar_split = string.split("(")
        catvar = catvar_split[-1].split(")")[0]
        if catvar_split[-1].split(")")[1].strip() == 'unequal':
            eq_var = False
        catvar_split[0] = "(".join(catvar_split[:-1])
        var = catvar_split[0].split(",")[0]
        if 'if !missing' in var:
            var = var.split(" ")[0]
            nan_pol = 'omit'
        
        catvar_vals = np.unique(df[catvar])
        if len(catvar_vals) != 2:
            raise ValueError(f"The categorical variable ({catvar}) doesn't have 2 groups")
        
        df_1 = df[df[catvar] == catvar_vals[0]]
        df_2 = df[df[catvar] == catvar_vals[1]]
        
        ttest_1a = stats.ttest_ind(df_1[var], df_2[var], equal_var=eq_var, nan_policy=nan_pol)

        tstat_1a = ttest_1a.statistic
        pval_1a = ttest_1a.pvalue

        print("t-stat: {}".format(tstat_1a))
        print("p-value: {}".format(pval_1a))
        
def filter_gen(df_name, string):
    if string.startswith("gen"):
        string = string.replace("gen ", "")
        str_split = string.split("=",1)
        str_split = [x.strip() for x in str_split]
        new_col_name = str_split[0]
        if str_split[1].count("=")>0:
            if str_split[1].startswith("("):
                str_split[1] = str_split[1][1:-1]
            filter_split = str_split[1].split(" ", 1)
            new_string = f"{df_name}['{new_col_name}'] = {df_name}['{filter_split[0]}'] {filter_split[1]}"
            new_string_split = new_string.split(" = ", 1)
            df = eval(df_name)
            df[new_col_name] = eval(new_string_split[1])
            print(new_string)
            return df
        else:
            words_lst = re.findall(r'\w\w+',str_split[1])
            for word in words_lst:
                if word not in ['log']:
                    str_split[1] = str_split[1].replace(word, f"{df_name}['{word}']")
                else:
                    str_split[1] = str_split[1].replace(word, f"np.{word}")
            new_string = f"{df_name}['{new_col_name}'] = {str_split[1]}"
            print(new_string)
            df = eval(df_name)
            df[new_col_name] = eval(str_split[1])
            return df

def corr(df_name, string):
    if string.startswith("pwcorr"):
        string = string.replace("pwcorr ", "")
        words_lst = re.findall(r'[a-zA-Z]+',string)
        df = eval(df_name)
        return df[words_lst].corr()
    
def scatter(df_name, string):
    if string.startswith("twoway"):
        string = string.replace("twoway (","")[:-2]
        command = string.split(",")[0].strip()
        customizations = string.split(",")[1].strip()
        df = eval(df_name)
        if command.startswith("scatter"):
            var_1 = command.split(" ")[1]
            var_2 = command.split(" ")[2]
            plt.scatter(df[var_1], df[var_2])
        customizations_split = customizations.split(")")
        for word in customizations_split:
            word = word.strip()
            if word.startswith("xtitle"):
                xtitle = word.split("(")[1]
                if xtitle.startswith("'"):
                    xtitle = xtitle[1:]
                if xtitle.endswith("'"):
                    xtitle = xtitle[:-1]
                plt.xlabel(xtitle)
            if word.startswith("ytitle"):
                ytitle = word.split("(")[1]
                if ytitle.startswith("'"):
                    ytitle = ytitle[1:]
                if ytitle.endswith("'"):
                    ytitle = ytitle[:-1]
                plt.ylabel(ytitle)

def hist(df_name, string):
    if string.startswith('histogram'):
        string = string.replace('histogram ','')
        str_split = string.split(", ")
        num_bins_change = False
        num_bins = 0
        for word in str_split:
            if word.startswith("bin"):
                num_bins_change = True
                num_bins = int(word.split("(")[1].split(")")[0])
        df = eval(df_name)
        if num_bins_change == False:
            return df.hist(column=str_split[0]);
        else:
            return df.hist(column=str_split[0],bins=num_bins);
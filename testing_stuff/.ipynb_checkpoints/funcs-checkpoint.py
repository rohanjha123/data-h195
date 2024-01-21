import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import regex as re
import statsmodels.api as sm
import statsmodels.formula.api as smf

def ttest(string, df_name = 'df'):
    if "ttest" in string and "by(" in string:
        eq_var = True
        nan_pol = 'propagate'
        
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
        
        print(f"catvar_vals = np.unique({df_name}['{catvar}'])")
        print(f"if len(catvar_vals) != 2:")
        print(f"    raise ValueError(f'The categorical variable ({catvar}) doesn\\'t have 2 groups')")
        
        print(f"df_1 = {df_name}[{df_name}['{catvar}'] == catvar_vals[0]]")
        print(f"df_2 = {df_name}[{df_name}['{catvar}'] == catvar_vals[1]]")
        
        print(f"ttest = stats.ttest_ind(df_1['{var}'], df_2['{var}'], equal_var={eq_var}, nan_policy='{nan_pol}')")
        
        print(f"t_stat = ttest.statistic")
        print(f"p_val = ttest.pvalue")
        print("print(f'T-stat: {t_stat}, P-value: {p_val}')")

def filter_gen(string, df_name='df'):
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
            print(new_string)
        else:
            words_lst = re.findall(r'\w\w+',str_split[1])
            for word in words_lst:
                if word not in ['log']:
                    str_split[1] = str_split[1].replace(word, f"{df_name}['{word}']")
                else:
                    str_split[1] = str_split[1].replace(word, f"np.{word}")
            new_string = f"{df_name}['{new_col_name}'] = {str_split[1]}"
            print(new_string)

def describe(string, df_name='df'):
    if string.startswith('describe'):
        print(f'{df_name}.describe()')
            
def corr(string, df_name='df'):
    if string.startswith("corr"):
        string = string.replace("corr ", "")
        words_lst = re.findall(r'[a-zA-Z]+',string)
        print(f"{df_name}[{words_lst}].corr()")
    
def scatter(string, df_name = 'df'):
    if string.startswith("twoway"):
        string = string.replace("twoway (","")[:-2]
        command = string.split(",")[0].strip()
        customizations = string.split(",")[1].strip()
        df = eval(df_name)
        if command.startswith("scatter"):
            var_1 = command.split(" ")[1]
            var_2 = command.split(" ")[2]
            print(f"plt.scatter({df_name}['{var_1}'], {df_name}['{var_2}']);")
        customizations_split = customizations.split(")")
        for word in customizations_split:
            word = word.strip()
            if word.startswith("xtitle"):
                xtitle = word.split("(")[1]
                if xtitle.startswith("'"):
                    xtitle = xtitle[1:]
                if xtitle.endswith("'"):
                    xtitle = xtitle[:-1]
                print(f"plt.xlabel('{xtitle}');")
            if word.startswith("ytitle"):
                ytitle = word.split("(")[1]
                if ytitle.startswith("'"):
                    ytitle = ytitle[1:]
                if ytitle.endswith("'"):
                    ytitle = ytitle[:-1]
                print(f"plt.ylabel('{ytitle}');")

def hist(string, df_name='df'):
    if string.startswith('histogram'):
        string = string.replace('histogram ','')
        str_split = string.split(", ")
        num_bins_change = False
        num_bins = 0
        for word in str_split:
            if word.startswith("bin"):
                num_bins_change = True
                num_bins = int(word.split("(")[1].split(")")[0])
        if num_bins_change == False:
            print(f"{df_name}.hist(column='{str_split[0]}');")
        else:
            print(f"{df_name}.hist(column='{str_split[0]}',bins={num_bins});")
            
def reg(string, df_name = 'df'):
    string = string[4:]
    first_half, second_half = string, string
    if "," in string:
        first_half = string.split(",")[0]
        second_half = string.split(",")[1]
    if "if" in first_half:
        if_statement = first_half.split("if")[1].strip()
        first_half = first_half.split("if")[0].strip()
        if "=" in if_statement:
            splitted_if = if_statement.split("=")
            print(f"{df_name}_filtered = {df_name}[{df_name}['{splitted_if[0].strip()}'] == {splitted_if[1].strip()}]")
        elif "<" in if_statement:
            splitted_if = if_statement.split("<")
            print(f"{df_name}_filtered = {df_name}[{df_name}['{splitted_if[0].strip()}'] < {splitted_if[1].strip()}]")
        elif ">" in if_statement:
            splitted_if = if_statement.split(">")
            print(f"{df_name}_filtered = {df_name}[{df_name}['{splitted_if[0].strip()}'] > {splitted_if[1].strip()}]")
        else:
            raise ValueError(f'Could not interpret if statement')
        df_name = df_name + "_filtered"
    y_var = first_half.split(" ")[0]
    x_var = "'" + "', '".join(first_half.split(" ")[1:]) + "'"
    if "vce" in second_half and "cluster" in second_half:
        second_half_split = second_half.split("cluster")
        clustering_vars = second_half_split[1][:-1].strip().split(" ")
    if ' ' not in x_var:
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print(f"{df_name}_no_na = {df_name}[[{x_var_temp},'{y_var}']].dropna()")
        else:
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print(f"x_df = {df_name}[{x_var}]")
    elif "i." in x_var:
        print(f"{df_name}_with_dummies = {df_name}.copy()")
        pollution_with_dummies = pollution.copy()
        df_name = df_name + "_with_dummies"
        print(f"x_var = \"{x_var}\"")
        x_var_new = "'" + "', '".join([i.strip("'") for i in x_var.split(", ") if not i.strip("'").startswith("i.")]) + "'"
        print("x_var_new = \"'\" + \"', '\".join([i.strip(\"'\") for i in x_var.split(\", \") if not i.strip(\"'\").startswith(\"i.\")]) + \"'\"")
        print(f"indicator_list = [m.strip(\"'\") for m in x_var.split('i.')[1:]]")
        print("for indicator in indicator_list:")
        print(f"    dummies = pd.get_dummies({df_name}[indicator])")
        print(f"    dummies = dummies.iloc[:,1:]")
        print(f"    dummies.columns = [str(x) + '_' + str(indicator) for x in dummies.columns]")
        print(f"    {df_name} = pd.concat([{df_name},dummies],axis=1)")
        print("    x_var_new = x_var_new + \", '\" + \"', '\".join(dummies.columns) + \"'\"")
        print("x_var = x_var_new")
        indicator_list = [m.strip("'") for m in x_var.split('i.')[1:]]
        for indicator in indicator_list:
            dummies = pd.get_dummies(pollution_with_dummies[indicator])
            dummies = dummies.iloc[:,1:]
            dummies.columns = [str(x) + '_' + str(indicator) for x in dummies.columns]
            pollution_with_dummies = pd.concat([pollution_with_dummies,dummies],axis=1)
            x_var_new = x_var_new + ", '" + "', '".join(dummies.columns) + "'"
        x_var = x_var_new
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print(f"{df_name}_no_na = {df_name}[[{x_var_temp},'{y_var}']].dropna()")
        else:
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print(f"x_df = {df_name}[[{x_var}]]")
    else:
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print(f"{df_name}_no_na = {df_name}[[{x_var_temp},'{y_var}']].dropna()")
        else:
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print(f"x_df = {df_name}[[{x_var}]]")

    print(f"y_df = {df_name}['{y_var}']")
    if 'noconstant' in second_half:
        print("model = sm.OLS(y_df, x_df)")
    else:
        print("model = sm.OLS(y_df, sm.add_constant(x_df))")
    if "vce" not in second_half:
        print("result = model.fit()")
    elif "vce" in second_half and "robust" in second_half:
        print("result = model.fit(cov_type='HC3')")
    elif "vce" in second_half and "cluster" in second_half:
        #print(f"{df_name}{clustering_vars}") # {df_name}{clustering_vars}
        print(f"result = model.fit(cov_type='cluster', cov_kwds={{'groups': {df_name}{clustering_vars}}})")
    else:
        raise ValueError(f'VCE type not recognize')
    print("result.summary()")
import regex as re

def stata2python(string, df_name = 'df'):
    print("import pandas as pd")
    if string.startswith("ttest"):
        ttest(string, df_name)
    elif string.startswith("gen"):
        filter_gen(string, df_name)
    elif string.startswith('describe'):
        describe(string, df_name)
    elif string.startswith("corr"):
        corr(string, df_name)
    elif string.startswith("twoway"):
        scatter(string, df_name)
    elif string.startswith('histogram'):
        hist(string, df_name)
    elif string.startswith('reg'):
        reg(string, df_name)
    else:
        raise ValueError(f'Your function is not supported')
        
def ttest(string, df_name = 'df'):
    print("import numpy as np")
    print("from scipy import stats")
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
    print("### First, we must filter the DataFrame to obtain the right values")
    print(f"catvar_vals = np.unique({df_name}['{catvar}'])")
    print(f"df_1 = {df_name}[{df_name}['{catvar}'] == catvar_vals[0]]")
    print(f"df_2 = {df_name}[{df_name}['{catvar}'] == catvar_vals[1]]")
    print("### Then, we can run our t-test")
    print(f"stats.ttest_ind(df_1['{var}'], df_2['{var}'], equal_var={eq_var}, nan_policy='{nan_pol}')")

def filter_gen(string, df_name='df'):
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
    print(f'{df_name}.describe()')
            
def corr(string, df_name='df'):
    string = string.replace("corr ", "")
    words_lst = re.findall(r'[a-zA-Z]+',string)
    print(f"{df_name}[{words_lst}].corr()")
    
def scatter(string, df_name = 'df'):
    print("import matplotlib.pyplot as plt")
    string = string.replace("twoway (","")[:-2]
    command = string.split(",")[0].strip()
    customizations = string.split(",")[1].strip()
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
    print("import matplotlib.pyplot as plt")
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
    print("import statsmodels.api as sm")
    string = string[4:]
    clustering_vars = ''
    first_half, second_half = string, string
    if "," in string:
        first_half = string.split(",")[0]
        second_half = string.split(",")[1]
    if "if" in first_half:
        print("### We first filter the DataFrame")
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
        print("### We first perform some string manipulations to ensure we are appropripately accounting for strings. ")
        print("### This section seems complicated as this code is meant to be a general-purpose code for converting the Stata commands to Python.")
        print("### You can greatly simplify this step if you know exactly which variables you are interested in; simply extract those variables from the DataFrame directly.")
        print(f"y_var = \"{y_var}\"")
        second_half_split = second_half.split("cluster")
        clustering_vars = second_half_split[1][:-1].strip().split(" ")
        print(f"clustering_vars = {clustering_vars}")
    if ' ' not in x_var:
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[{x_var_temp},'{y_var}']].dropna()")
        else:
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print("### Below, we extract the relevant variables from the DataFrame")
        print(f"x_df = {df_name}[{x_var}]")
    elif "i." in x_var:
        #raise ValueError(f'Indicators are currently not supported')
        print(f"{df_name}_with_dummies = {df_name}.copy()")
        df_name = df_name + "_with_dummies"
        print(f"x_var = \"{x_var}\"")
        x_var_new = "'" + "', '".join([i.strip("'") for i in x_var.split(", ") if not i.strip("'").startswith("i.")]) + "'"
        print("x_var_new = \"'\" + \"', '\".join([i.strip(\"'\") for i in x_var.split(\", \") if not i.strip(\"'\").startswith(\"i.\")]) + \"'\"")
        print("### The below section adds in relevant indicator variables, ensuring they have interpretable names")
        print(f"indicator_list = [m.strip(\"'\") for m in x_var.split('i.')[1:]]")
        print("for indicator in indicator_list:")
        print(f"    dummies = pd.get_dummies({df_name}[indicator])")
        print(f"    dummies = dummies.iloc[:,1:]")
        print(f"    dummies.columns = [str(x) + '_' + str(indicator) for x in dummies.columns]")
        print(f"    {df_name} = pd.concat([{df_name},dummies],axis=1)")
        print("    x_var_new = x_var_new + \", '\" + \"', '\".join(dummies.columns) + \"'\"")
        print("x_var = x_var_new")
        print("### This helps ensure the clustered variables are extracted from the DataFrame")
        print("if clustering_vars:")
        print("    x_var_temp = x_var + \", '\" + \"', '\".join(clustering_vars) + \"'\"")
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print(f"var_list = x_var_temp +\", '\"+ str(y_var) + \"'\"")
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[i.strip(\"'\") for i in var_list.split(\", \")]].dropna()")
        else:
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print("### Below, we extract the relevant variables from the DataFrame")
        print(f"x_df = {df_name}[[i.strip(\"'\") for i in x_var.split(\", \")]]")
    else:
        if clustering_vars:
            x_var_temp = x_var + ", '" + "', '".join(clustering_vars) + "'"
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[{x_var_temp},'{y_var}']].dropna()")
        else:
            print("### Dropping NaN/missing values")
            print(f"{df_name}_no_na = {df_name}[[{x_var},'{y_var}']].dropna()")
        df_name = df_name + "_no_na"
        print("### Below, we extract the relevant variables from the DataFrame")
        print(f"x_df = {df_name}[[{x_var}]]")
    print(f"y_df = {df_name}['{y_var}']")
    print("### We now define the model, fit it to the data and then view a summary of the results")
    if 'noconstant' in second_half:
        print("model = sm.OLS(y_df, x_df)")
    else:
        print("model = sm.OLS(y_df, sm.add_constant(x_df))")
    if "vce" not in second_half:
        print("result = model.fit()")
    elif "vce" in second_half and "robust" in second_half:
        print("result = model.fit(cov_type='HC1')")
    elif "vce" in second_half and "cluster" in second_half:
        print(f"result = model.fit(cov_type='cluster', cov_kwds={{'groups': {df_name}{clustering_vars}}})")
    else:
        raise ValueError(f'VCE type not recognized')
    print("result.summary()")
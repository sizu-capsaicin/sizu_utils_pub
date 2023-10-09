import yaml


def load_income_yml(income_yml_path):
    total_income = 0
    total_bonus = 0
    total_social_insurance = 0
    count_none_income = 0
    count_none_bonus = 0

    with open(income_yml_path, 'r') as income_yml:
        incomes = yaml.safe_load(income_yml)

        for income in incomes.values():
            month_income = income['month_income']
            if month_income['income'] is None:
                month_income['income'] = 0
                count_none_income += 1
            total_income += int(month_income['income'])
            total_social_insurance += month_income['health_insurance'] \
                                        + month_income['employees_pension'] \
                                        + month_income['employee_insurance']

            if 'bonus' in income:
                bonus_income = income['bonus']
                if bonus_income['income'] is None:
                    bonus_income['income'] = 0
                    count_none_bonus += 1
                total_bonus += int(bonus_income['income'])
                total_social_insurance += month_income['health_insurance'] \
                                            + month_income['employees_pension'] \
                                            + month_income['employee_insurance']
        
        # 一旦仮想年収を計算する
        total_income = total_income * 12 / (12 - count_none_income)
        # 一旦仮想ボーナスを計算する
        total_bonus = total_bonus * 2 / (2 - count_none_bonus)

        return total_income + total_bonus, total_social_insurance

def load_tax_yml(tax_yml_path):
    with open('yml/tax.yml', 'r') as tax_yml, open('yml/income.yml', 'r') as income_yml:
        tax = yaml.safe_load(tax_yml)

        additonal_payment = None
        if 'additional_payment' in tax:
            additonal_payment = tax['additional_payment']

        return tax, additonal_payment

def deduct_salary_income(income, income_line_for_year_end_adjustment, rules_for_year_end_adjustment):
    """[to deduct from income and return salary income]
    給与等の収入金額から給与所得控除を差し引いて給与所得金額を返す関数

    Args:
        income (int): total income per year
        abs (_type_): _description_
    """

    if income < income_line_for_year_end_adjustment:
        for rule in rules_for_year_end_adjustment:
            conditions = rule['conditions']
            if conditions[0] <= income < conditions[1]:
                return rule['income']
            
        print('out of rules for year end adjustment: please add conditons')
        exit(1)
    
    print ('out of income line for year end adjustment: please add process in deduct_salary_income()')
    exit(1)
    

def deduct_basic_allowance(income, rules_for_basic_allowance):
    """[to deduct from income]

    Args:
        income (_type_): _description_
        rules_for_basic_allowance (_type_): _description_
    """

    for rule in rules_for_basic_allowance:
        conditions = rule['conditons']
        if conditions[0] < income and conditions[1] is None:
            return rule['deduct']
        if conditions[0] < income < conditions[1]:
            return rule['deduct']
        
    print('out of rules for deduct basic allowance: please add process in deduct_basic_allowance()')
    exit(1)

def calc_income_tax(income, rules_for_income_tax):
    """[to calculate income tax]

    Args:
        income (_type_): _description_
        rules_for_income_tax (_type_): _description_
    """

    for rule in rules_for_income_tax:
        conditions = rule['conditions']
        if conditions[0] < income < conditions[1]:
            return income * rule['tax_ratio']  - rule['deduct']
    
    print('out of rules for income tax: please add condition in calc_income_tax()')
    exit(1)


if __name__ == "__main__":
    income, social_insurance = load_income_yml('yml/income.yml')
    tax, deduct_add_payment = load_tax_yml('yml/tax.yml')

    if deduct_add_payment is not None:
        if 'social_insurance' in deduct_add_payment:
            social_insurance += int(deduct_add_payment['social_insurance'])
            
    print("total income (総所得額): "  + str(income))

    salary_income = deduct_salary_income(income, 
                                        tax['income_line_for_year_end_adjustment'], 
                                        tax['rules_for_year_end_adjustment'])
    print("salary income (給与所得控除): " + str(salary_income))

    basic_allowance = deduct_basic_allowance(income, 
                                            tax['rules_for_basic_allowance'])
    print('basic allowance (基礎控除): ' + str(basic_allowance))

    print('social insurance (社会保険料控除): ' + str(social_insurance))

    taxable_income = salary_income - basic_allowance - social_insurance
    print('taxable income (課税所得): ' + str(taxable_income))

    income_tax = calc_income_tax(taxable_income, tax['rules_for_income_tax'])
    print('income_tax (所得税): ' + str(income_tax))



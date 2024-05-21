# custom_filters.py
from django import template
from num2words import num2words

register = template.Library()

@register.filter(name='intmultiply')
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter(name='add_three_values')
def add_three_values(value, arg):
    return sum(map(float, [value, arg]))


@register.filter(name='number_to_words')
def number_to_words(value):
    return num2words(value, lang='en').title()

@register.filter
def get_date_format(date_string):
    if not date_string:
        return ''
    try:
        tdate = date_string.split('T')[0]
        parts = tdate.split('-')
        return f"{parts[2]}/{parts[1]}/{parts[0][-2:]}"
    except Exception as e:
        return ''
    
@register.filter(name='calc_tax')
def calc_tax(taxable_value, tax_percentage):
    if tax_percentage and taxable_value and tax_percentage > 0:
        return round((taxable_value * tax_percentage)/100,2)
    else:
        return 0
@register.filter
def multiply(value, arg):
    if value and arg:
        return float(value) * float(arg)
    else:
        return None
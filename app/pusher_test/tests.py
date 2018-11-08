from django.test import TestCase


# Create your tests here.

def change(a, b):
    b, a = a, b
    print(b, a)


def print_value(input_data):
    print(input_data)


def multiploy_value(input_data):
    print(input_data*input_data)
    return input_data * input_data

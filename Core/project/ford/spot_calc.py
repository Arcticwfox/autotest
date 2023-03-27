"""
This file defines the process for calculating the Spot function.

@Author: Siwei.Lu
@Date: 2022.11.27
"""


def add_pixel_intensity(ax1, left, up, value, size=6):
    if value is not None:
        ax1.text(left, up, '%.0f' % value, fontdict={'fontsize': size})
    else:
        pass


def signal_value_out_of_range(input_value, input_array):
    if input_value <= input_array[0]:
        input_value = input_array[0]
    elif input_value >= input_array[len(input_array) - 1]:
        input_value = input_array[len(input_array) - 1]
    else:
        input_value = input_value

    return input_value


def get_smooth_site_in_pixel(input_array, var):
    for i in range(len(input_array[0])):  # 从小到大
        if input_array[0][i] != "NU":
            if (float(var) >= float(input_array[1][i])) and (float(var) < float(input_array[0][i])):
                var_site = i
    return var_site


# @parameter: direction: means the direction of iterating
def get_var_in_array_site(input_array, var, direction=0):
    if direction == 0:
        for i in range(len(input_array) - 1):  # 从小到大
            if (float(var) >= float(input_array[i])) and (float(var) < float(input_array[i + 1])):
                var_site = i
            elif float(var) == float(input_array[i + 1]):
                var_site = i
    else:
        for i in range(len(input_array) - 1):  # 从大到小
            if (float(var) <= float(input_array[i])) and (float(var) > float(input_array[i + 1])):
                var_site = i

    return var_site

"""
This file defines the process for calculating the DBL function.

@Author: Siwei.Lu
@Date: 2022.11.27
"""

import numpy as np
from Core.project.ford.parameter_def import *


def dbl_minleft_ang_site(ang_center, min_left_ang):
    if not ang_center:
        site_minL = 0
    else:
        for i in range(len(ang_center)):
            if min_left_ang > ang_center[0]:
                site_minL = 0
            elif min_left_ang < ang_center[-1]:
                site_minL = len(ang_center) - 1
            elif (min_left_ang <= ang_center[i]) and (min_left_ang > ang_center[i + 1]):
                site_minL = i + 1  # R0W_Min_LAng 在数组[ 翻转 ROW 角度中心点]里的位置
                # print("R2_site_minL: ",R2_site_minL)
                break
    return site_minL


def dbl_maxright_ang_site(ang_center, max_right_ang):
    if not ang_center:
        site_maxR = 0
    else:
        for i in range(len(ang_center)):
            if max_right_ang < ang_center[-1]:
                site_maxR = len(ang_center) - 1
            elif max_right_ang > ang_center[0]:
                site_maxR = 0
            elif (max_right_ang < ang_center[i]) and (max_right_ang >= ang_center[i + 1]):
                site_maxR = i  # Row_site_maxR在数组[ 翻转 ROW 角度中心点]里的位置
                # print("R2_site_maxR: ", R2_site_maxR)
                break
    return site_maxR


def deactivated_move_left(actual_intensity, site_max_r, move_ang):
    cal_intensity = actual_intensity.copy()
    intensity = cal_intensity[site_max_r]
    for i in range(move_ang):
        cal_intensity.insert(len(cal_intensity), 0)
        cal_intensity.remove(cal_intensity[0])
    for i in range(site_max_r - move_ang, site_max_r + 1):
        cal_intensity[i] = intensity
    return cal_intensity


def deactivated_move_right(actual_intensity, site_min_l, move_ang):
    cal_intensity = actual_intensity.copy()
    intensity = cal_intensity[site_min_l]
    for i in range(-move_ang):
        cal_intensity.insert(0, 0)
        cal_intensity.pop()
    for i in range(site_min_l, site_min_l - move_ang):
        cal_intensity[i] = intensity
    return cal_intensity


def remain_move_left(actual_intensity, remain_site, remain_intensity, move_ang):
    cal_intensity = actual_intensity.copy()
    for i in range(move_ang):
        cal_intensity.insert(remain_site + 1, remain_intensity)
        cal_intensity.remove(cal_intensity[0])
    return cal_intensity


def remain_move_right(actual_intensity, remain_site, remain_intensity, move_ang):
    cal_intensity = actual_intensity.copy()
    for i in range(move_ang):
        cal_intensity.insert(remain_site, remain_intensity)
        cal_intensity.pop()
    return cal_intensity


def deac_dbl_move_intensity(row_notnull_intensity, row_minR_site, row_minL_site, row_move_ang):
    if not row_notnull_intensity:  # 对应 row 没有配灯
        row_move_intensity = []
    else:
        if row_move_ang > 0:  # move left, use DBL_min_right_ang
            row_move_intensity = deactivated_move_left(row_notnull_intensity, row_minR_site, row_move_ang)
        elif row_move_ang < 0:  # move right, use DBL_min_left_ang
            row_move_intensity = deactivated_move_right(row_notnull_intensity, row_minL_site, row_move_ang)
        elif row_move_ang == 0:
            row_move_intensity = row_notnull_intensity
    return row_move_intensity


def remain_dbl_move_intensity(notnull_intensity, remainL_site, remainR_site, remain_intensity, move_ang):
    if not notnull_intensity:  # 对应 row 没有配灯
        row_move_intensity = []
    else:
        if move_ang > 0:  # move left
            row_move_intensity = remain_move_left(notnull_intensity,
                                                  remainR_site,
                                                  remain_intensity,
                                                  move_ang)
        elif move_ang < 0:  # move right
            row_move_intensity = remain_move_right(notnull_intensity,
                                                   remainL_site,
                                                   remain_intensity,
                                                   -move_ang)
        elif move_ang == 0:
            row_move_intensity = notnull_intensity
    return row_move_intensity


def get_each_row_move_ang(move_angle, dbl_move_max_ang, dbl_move_ang,
                          row_enable):  # dbl_move_max_ang: ROW3 L/R --> ROW1 L/R
    if row_enable == EnableStatus.Enable.value:
        if dbl_move_ang > 0:
            if move_angle >= dbl_move_max_ang[0]:
                row_move_ang = dbl_move_max_ang[0]
            else:
                row_move_ang = move_angle
        elif dbl_move_ang < 0:
            if move_angle >= dbl_move_max_ang[1]:
                row_move_ang = -dbl_move_max_ang[1]
            else:
                row_move_ang = -move_angle
        elif dbl_move_ang == 0:
            row_move_ang = 0
    else:
        row_move_ang = 0

    return row_move_ang


def get_angle_center(input_array):
    ang_center = []
    for rowNum in range(len(input_array[0])):
        if input_array[0][rowNum] != "NU":
            ang_center.append((input_array[0][rowNum] + input_array[1][rowNum]) / 2)
    return ang_center


def get_not_null_index(input_array):
    index = []
    for rowNum in range(len(input_array)):
        if input_array[rowNum] != "NU":
            index.append(rowNum)
    return index


def get_not_null_site_int(input_array, index_array):
    array = []
    for rowNum in range(len(index_array)):
        array.append(input_array[index_array[rowNum]])
    return array


def part_reverse(input_array, re_site):
    array = input_array.copy()
    ang = array[:]
    c = ang[0:re_site]
    c.reverse()
    ang[0:re_site] = c[:]
    return ang


def get_row_ang_center(input_array, re_site):
    site_value = get_part_reverse_array(input_array, re_site)
    row_ang_center = get_angle_center(site_value)

    return row_ang_center


def get_part_reverse_array(input_array, re_site):
    reverse_array = []
    for row in range(len(input_array)):
        reverse_array.append(part_reverse(input_array[row], re_site))

    return reverse_array


def calc_move_angle(input_array, value):
    diff = []
    zero_site = calc_zero_point(input_array, value)

    if not input_array:
        move_dir = "InputArray is NULL"
        move_ang = 0
    else:
        if value > 0:
            move_dir = "Move to Left"
            for i in range(len(input_array)):
                diff.append(abs(input_array[i] - value))
                site = diff.index(min(diff))
            move_ang = zero_site - site
        elif value < 0:
            move_dir = "Move to Right"
            input_array_rev = input_array.copy()
            input_array_rev.reverse()
            for i in range(len(input_array_rev)):
                diff.append(abs(input_array_rev[i] - value))
                site = len(input_array_rev) - diff.index(min(diff)) - 1
            move_ang = site - zero_site
        elif value == 0:
            move_dir = "No Move: "
            move_ang = 0

    return move_dir, move_ang


def calc_zero_point(input_array, value):
    zero_site = 0
    for i in range(len(input_array)):
        if (input_array[-1] <= 0) and (input_array[0] < 0):
            zero_site = 0
        elif (input_array[-1] > 0) and (input_array[0] >= 0):
            zero_site = len(input_array) - 1
        elif (input_array[i] > 0) and (input_array[i + 1] <= 0):
            if value > 0:
                zero_site = i
            elif value < 0:
                zero_site = i + 1
            else:
                zero_site = 0

    return zero_site


def get_after_dbl_intensity(input_intensity, notnull_index):  # 按每行32颗灯的位置排列
    after_dbl_intensity = (np.zeros(32)).tolist()

    if input_intensity:  # 对应 row 有配灯
        after_dbl_intensity = (np.zeros(32)).tolist()
        for i in range(len(notnull_index)):
            after_dbl_intensity[notnull_index[i]] = input_intensity[i]
        after_dbl_intensity = part_reverse(after_dbl_intensity, 16)

    return after_dbl_intensity

#
# inputarray = [4.5, 3.5, 2.5, 1.5]
# inputarray1 = [5, 4, 3, 0.45, 0.35, 0.25, 0.15]

# move_dir, move_ang = calc_move_angle(inputarray1, 0.4)

# inputarray1 = [-3, -4, -5, -6, -7, -8]
# inputarray = np.zeros(5)
# inputarray2 = [9, "NU", 6, 5, 4, 3, 0, -3, -4, "NU", -6, -7]
#
# print(dbl_minleft_ang_site(inputarray, -8))

# print(get_not_null_index(inputarray))
#
# inputarray = [[1, 2, 3, 4, 5, 6], [-1, -2, -3, -4, -5, -6]]
# inputarray1 = [[4, 5, 6], [-5, -4, -6]]
# inputarray[0].extend(inputarray1[0])
# inputarray[1].extend(inputarray1[1])


# row1_move_intensity = [0, 0, 0, 0, 0, 31, 31, 31, 31, 31, 31, 35, 37, 39, 40, 40, 39, 37, 35, 31, 25, 21]
# __sec23_notNull_index = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
# print(get_after_dbl_intensity(row1_move_intensity, __sec23_notNull_index))

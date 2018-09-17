# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 18:29:52 2018

@author: Zoheb0707
"""

import requests
import pandas as pd

student_id_list = [1582283,1402365,1386886,1407986,1493884,1482382,1578352,1116735,1484448,
                   1337211,1475699,1727787,1378711,1620340,1398754]
course_dictionary = {}

user_student_id = int(input('Enter student id: ')) #get student id from user
class_type_needed = '' #get class type from user
new_student = False

#assuming that every student who's taken a class at uw is stored in the db
user_major_list = []
user_course_list = []
if user_student_id not in student_id_list:
    new_student = True
    #ask for intended majors
    #or direct admit majors
    user_major_list = input('Enter a comma separated list of majors/Intended majors: ').split(', ') 
    for i in range(0, len(user_major_list)):
        if user_major_list[i] == 'None':
            user_major_list[i] = None
    #get majors/intended_majors from user. exactly 3

if not new_student:
    student_id_list.remove(user_student_id)
    user_data =  requests.get('https://stark-mountain-17519.herokuapp.com/students/' + 
                                 str(user_student_id)).json()
    user_major_list = [user_data['Major1'], user_data['Major2'], user_data['Major3']]
    user_course_list = list(set(user_data['courses']))

#creating the dataframe to use
def create_dataframe(student_ids):
    data_list = []
    columns = ['student_id', 'major_list', 'course_list']
    for student_id in student_ids:
        json_data = requests.get('https://secure-plains-22276.herokuapp.com/students/' + 
                                 str(student_id)).json()
        major_list = [json_data['Major1'], json_data['Major2'], json_data['Major3']]
        course_list = list(set(json_data['courses']))
        for course in course_list:
            course_dictionary[course] = 0
        data_list.append([student_id, major_list, course_list])
    return pd.DataFrame(data=data_list, columns=columns)

def fill_course_dictionary(data):
    for i in range(0,len(data)):
        course_list = (data.iloc[i])['course_list']
        major_list = (data.iloc[i])['major_list']
        weight = 0
        major_intersection = set(major_list).intersection(set(user_major_list))
        if user_major_list[0] in major_intersection:
            weight += 3
        if user_major_list[1] in major_intersection:
            weight += 2
        if user_major_list[2] in major_intersection:
            weight += 1
        for course in course_list:
            course_dictionary[course] = course_dictionary[course] + weight
    return course_dictionary
            
def identify_courses_and_prerequisites(course_list):
    prerequesite_dict = {}
    for course in course_list:
        course_info = requests.get('https://secure-plains-22276.herokuapp.com/courses/' + 
                                   str(course)).json()
        description = course_info['desc']
        if 'Prerequisite:' not in description:
            prerequesite_dict[course_info['dept_abbrev'] + ' ' + str(course_info['course_number'])]\
            = None
        else:
            remaining_string = description.split('Prerequisite: ')[1]
            all_prerequisites = remaining_string.split('; ')
            last_req = all_prerequisites[len(all_prerequisites) - 1]
            if 'Instructors' in last_req:
                all_prerequisites[len(all_prerequisites) - 1] = all_prerequisites[len(
                        all_prerequisites) 
                - 1].split(' Instructors')[0]
            elif 'Offered' in last_req:
                all_prerequisites[len(all_prerequisites) - 1] = all_prerequisites[len(
                        all_prerequisites) 
                - 1].split(' Offered')[0]
            prerequesite_dict[course_info['dept_abbrev'] + ' ' + str(course_info['course_number'])]\
            = all_prerequisites
    return prerequesite_dict
    
def find_best_courses(course_dictionary):
    best_courses = {}
    for key in sorted(course_dictionary, key=course_dictionary.get, reverse=True)[:6]:
        best_courses.update({key: course_dictionary[key]})
    best_courses = best_courses.keys()
    return best_courses

def print_courses_and_prerequisites(course_info_dict):
    print('Recommended courses are:')
    print()
    for course in course_info_dict.keys():
        if course_info_dict[course] == None:
            print(course + '\nNo prerequesites required.')
            print()
        else:
            print(course + '\nPrerequesites are:')
            prerequisite_list = course_info_dict[course]
            for prerequisite in prerequisite_list:
                print('\t' + prerequisite)
            print()

student_data_frame = create_dataframe(student_id_list)

major_priority_dict = {user_major_list[0]:3, user_major_list[1]:2, user_major_list[2]:1}

#prediction for new user
if new_student:
    elements_to_keep = []
    for i in range(0, len(student_data_frame)):
        if len(set(student_data_frame.iloc[i]['major_list']).intersection(set(
                user_major_list))) > 0:
            elements_to_keep.append(i)
    student_data_frame = student_data_frame.iloc[elements_to_keep]
    course_dictionary = fill_course_dictionary(student_data_frame)
    best_courses = find_best_courses(course_dictionary)
    course_info_dict = identify_courses_and_prerequisites(best_courses)
    print_courses_and_prerequisites(course_info_dict)
else:
    test_major_set = set(user_major_list)
    test_major_set.remove(None)
    if len(user_course_list) <= 9 and len(test_major_set) < 1:
        user_major_list = input('Enter a comma separated list of majors/Intended majors: ').\
        split(', ') 
        for i in range(0, len(user_major_list)):
            if user_major_list[i] == 'None':
                user_major_list[i] = None
        elements_to_keep = []
        for i in range(0, len(student_data_frame)):
            if len(set(student_data_frame.iloc[i]['major_list']).intersection(set(
                    user_major_list))) > 0:
                elements_to_keep.append(i)
        student_data_frame = student_data_frame.iloc[elements_to_keep]
        course_dictionary = fill_course_dictionary(student_data_frame)
        best_courses = find_best_courses(course_dictionary)
        course_info_dict = identify_courses_and_prerequisites(best_courses)
        print_courses_and_prerequisites(course_info_dict)
    elif len(user_course_list) <= 9 and len(test_major_set) >= 1:
        elements_to_keep = []
        for i in range(0, len(student_data_frame)):
            if len(set(student_data_frame.iloc[i]['major_list']).intersection(set(
                    user_major_list))) > 0:
                elements_to_keep.append(i)
        student_data_frame = student_data_frame.iloc[elements_to_keep]
        #use clustering algo to identify closest courses.
        
    elif len(user_course_list) > 9 and len(test_major_set) < 1:
        print()
    else:
        print()
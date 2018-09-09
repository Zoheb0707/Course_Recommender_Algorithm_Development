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

user_student_id = '' #get student id from user
class_type_needed = '' #get class type from user
new_student = False

#assuming that every student who's taken a class at uw is stored in the db
user_major_list = []
user_course_list = []
if user_student_id not in student_id_list:
    new_student = True
    #ask for intended majors
    #or direct admit majors
    user_major_list= [] #get majors from user. exactly 3

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
        json_data = requests.get('https://stark-mountain-17519.herokuapp.com/students/' + 
                                 str(student_id)).json()
        major_list = [json_data['Major1'], json_data['Major2'], json_data['Major3']]
        course_list = list(set(json_data['courses']))
        for course in course_list:
            if course not in course_dictionary.keys:
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
            
def return_courses_and_prerequisites(course_list):
    prerequesite_dict = {}
    for course in course_list:
        course_info = requests.get('https://stark-mountain-17519.herokuapp.com/courses/course').json()
        description = course_info['desc']
        if 'Prerequisite:' not in description:
            prerequesite_dict[course_info['dept_abbrev'] + ' ' + course_info['course_number']] = \
            None
        else:
            remaining_string = description.split['Prerequisite: '][1]
            all_prerequisites = remaining_string.split('; ')
            last_req = all_prerequisites[len(all_prerequisites) - 1]
            if 'Instructors' in last_req:
                all_prerequisites[len(all_prerequisites) - 1] = all_prerequisites[len(all_prerequisites) 
                - 1].split(' Instructors')[0]
            elif 'Offered' in last_req:
                all_prerequisites[len(all_prerequisites) - 1] = all_prerequisites[len(all_prerequisites) 
                - 1].split(' Offered')[0]
            prerequesite_dict[course_info['dept_abbrev'] + ' ' + course_info['course_number']] = \
            all_prerequisites
        return prerequesite_dict
            
student_data_frame = create_dataframe(student_id_list)

major_priority_dict = {user_major_list[1]:3, user_major_list[2]:2, user_major_list[3]:1}

#prediction for new user
if new_student:
    elements_to_keep = []
    for i in range(0, len(student_data_frame)):
        if len(set(student_data_frame.iloc[i]['major_list']).intersects(set(user_major_list))) > 0:
            elements_to_keep.append(i)
    student_data_frame = student_data_frame.iloc[elements_to_keep]
    fill_course_dictionary(student_data_frame)
    #get 6 best courses
    #check prereqs for each course
    #output  
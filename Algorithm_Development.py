# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 18:29:52 2018

@author: Zoheb0707
"""

import requests
import pandas as pd

student_id_list = [] #get list of student ids from the database I think

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

#creating the datafraome to use
def create_dataframe(student_ids):
    data_list = []
    columns = ['student_id', 'major_list', 'course_list']
    for student_id in student_ids:
        json_data = requests.get('https://stark-mountain-17519.herokuapp.com/students/' + 
                                 str(student_id)).json()
        major_list = [json_data['Major1'], json_data['Major2'], json_data['Major3']]
        course_list = list(set(json_data['courses']))
        data_list.append(student_id, major_list, course_list)
    return pd.DataFrame(data=data_list, columns=columns)

student_data_frame = create_dataframe(student_id_list)

#prediction for new user
if new_student:
    student_data_frame = student_data_frame[set(student_data_frame['major_list']).
                                            intersection(set(user_major_list)) == True]
    
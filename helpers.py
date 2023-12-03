import os
import requests
import numpy as np
import pymysql

from flask import redirect, session, request
from pymysql import cursors
from functools import wraps
from typing import Any, List


def database(host='localhost', user='root', password='', db='dietary'):
    try:

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        
        return connection, cursor
    
    except Exception as e:
        print("tidak bisa konek.", e)
        return None, None
    
def login_required(f):
    """
    sumber=:
    https://flask.palletsprojects.com/en/3.0.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def split_list(dictionary, section):
    toList = sorted(list(dictionary.items()))
    split = np.array_split(toList,section)
    splitted = []

    for i in range(section):
        current_split = split[i]
        splitted.append(dict(current_split))

    return splitted

def readable_list(seq: List[Any]) -> str:
    """
    https://stackoverflow.com/a/53981846/19845029
    """
    seq = [str(s) for s in seq]
    if len(seq) < 3:
        return ' and '.join(seq)
    return ', '.join(seq[:-1]) + ', and ' + seq[-1]


def toString(form_list, string):
    list = request.args.getlist(form_list)
    array = []

    for i in list:
        array.append(string+i)

    tostring = "".join(array)

    return list, tostring

def lookup(param):
    try:
        api_key = os.environ.get("API_KEY")
        api_id = os.environ.get("API_ID")
        response = requests.get(
            f"https://api.edamam.com/api/recipes/v2?type=public&app_id={api_id}&app_key={api_key}&q={param}")
        response.raise_for_status()
    except requests.RequestException:
        return None
    try:
        result = response.json()
        hits_dict = result["hits"]
        recipes_list = []
        for index in hits_dict:
            link = index["_links"]["self"]["href"]  
            label = index["recipe"]["label"]
            image = index["recipe"]["image"]
            source = index["recipe"]["source"]
            url = index["recipe"]["url"]  
            dietLabels = list(index["recipe"]["dietLabels"])
            healthLabels = list(index["recipe"]["healthLabels"])
            ingredientLines = list(index["recipe"]["ingredientLines"])
            calories = index["recipe"]["calories"]
            totalTime = index["recipe"]["totalTime"]
            cuisineType = list(index["recipe"]["cuisineType"])
            dishType = list(index["recipe"]["dishType"])
            recipes_list.append(
                {
                    "link": link,
                    "label": label,
                    "image": image,
                    "source": source,
                    "url": url,
                    "dietLabels": dietLabels,
                    "healthLabels": healthLabels,
                    "ingredientLines": ingredientLines,
                    "calories": calories,
                    "totalTime": totalTime,
                    "cuisineType": cuisineType,
                    "dishType": dishType
                })
            
        return recipes_list 
    except (KeyError, TypeError, ValueError):
        return None







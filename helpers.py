import os
import requests
import numpy as np
import pymysql
import asyncio
import aiohttp
import urllib

from flask import redirect, session, request
from pymysql import cursors
from functools import wraps
from typing import Any, List


def database(host='localhost', user='root', password='', db='momonspace'):
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
        api_key = os.getenv("API_KEY_RECIPE")
        api_id = os.getenv("API_ID_RECIPE")
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
    
async def fetch_exercise(session, url, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()

async def fetch_video(session, url, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()

async def lookup_gym(param, method):
    try:
        rapidapi_key = os.getenv("RAPIDAPI_KEY")
        exercise_api_host = os.getenv("EXERCISE_API_HOST")
        video_api_host = os.getenv("VIDEO_API_HOST")
        encoded_param = urllib.parse.quote(param)
        url = f"https://exercisedb.p.rapidapi.com/exercises/{method}/{encoded_param}"
        print(url)
        querystring = {"limit":"15"}
        exercise_headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": exercise_api_host
        }
        
        async with aiohttp.ClientSession() as session:
            response = await fetch_exercise(session, url, exercise_headers, querystring)
            gym_list = []

            tasks = []
            for index in response:
                name = index["name"]
                video_url = "https://youtube-search-and-download.p.rapidapi.com/search"
                video_querystring = {"query": name, "type": "v", "sort": "r"}
                video_headers = {
                    "X-RapidAPI-Key": rapidapi_key,
                    "X-RapidAPI-Host": video_api_host
                }
                tasks.append(fetch_video(session, video_url, video_headers, video_querystring))

            video_results = await asyncio.gather(*tasks)

            for index, video_result in zip(response, video_results):
                videoId = [content["video"]["videoId"] for content in video_result.get("contents", [])]
                gym_list.append({
                    "bodyPart" : index["bodyPart"],
                    "equipment" : index["equipment"],
                    "gifUrl" : index["gifUrl"],
                    "target" : index["target"],
                    "name" : index["name"],
                    "instructions" : list(index["instructions"]),
                    "videoId": videoId
                })
            return gym_list
    except (aiohttp.ClientError, KeyError, TypeError, ValueError) as e:
        print(e)
        return None
    







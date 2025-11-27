from dotenv import load_dotenv
load_dotenv()
import requests
import os 
import json
import numpy as np 
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from groq import Groq


def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model" : "bge-m3",
        "input" : text_list
    })

    embedding = r.json()["embeddings"]
    return embedding

def infrance(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        # "model" : "deepseek-r1",
        "model": "llama3.2",
        "prompt" : prompt,
        "stream" : False
    })
     
    respnse = r.json()["response"]
    return respnse


df  = joblib.load('embedding.joblib')

incoming_query = input("Ask a quections:")
question_embedding = create_embedding([incoming_query])[0]
# print(question_embedding)

similarities = cosine_similarity(np.vstack(df['embedding']), [question_embedding]).flatten()
# print(similarities)

top_result = 3
max_indx = similarities.argsort()[::-1][0:top_result]
# print(max_indx)
new_df = df.loc[max_indx]
# print(new_df[["text", "number", "title"]])



prompt = f'''I am teaching polity course. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title", "number", "start", "end", "text"]].to_json(orient="records")}
---------------------------------
"{incoming_query}"
User asked this question related to the video chunks, you have to answer in a human way (dont mention the above format, its just for you) where and how much content is taught in which video (in which video and at what timestamp) and guide the user to go to that particular video. If user asks unrelated question, tell him that you can only answer questions related to the course
'''


# for index, item in new_df.iterrows():
#     print(index, item["title"], item["number"], item["text"]) 

with open("promt.txt" , "w")as f:
    f.write(prompt)

response = (infrance(prompt))
print(response)

with open("response.txt" , "w")as f:
    f.write(response)


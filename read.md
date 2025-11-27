how to use RAG AI teaching assistence on your data 
# steps 1 = collect all videos where you want 
# then place this all videos in the videos folder  

# step 2 = convert all the videos in mp3 using the videos to mp3 file 

# step 3 = convert all the mp3 files into the small chunks (json) in mp3 to json file 

# step 4 = convert mp3 to vectors 
using the read_chunks file to make the embeddings for a chunks  and save is as a joblib picker 

#   step 5 = prompt generation and feed it to a LLM
read the joblib file and load it in the memory , then create a relavent proment as per the user query and feed to LLM


How to use RAG AI teaching assistance on your data

Step 1 = Collect all videos where you want
Then, place all videos in the videos folder
step 2 = convert all the videos in mp3 using the videos to mp3 file
step 3 = convert all the mp3 files into the small chunks (json) in mp3 to json file
step 4 = convert mp3 to vectors
using the read_chunks file to make the embeddings for a chunk and save it as a joblib picker

Step 5 = prompt generation and feed it to an LLM
Read the joblib file and load it in the memory, then create a relevant prompt as per the user query and feed it to the LLM

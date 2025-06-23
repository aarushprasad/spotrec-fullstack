import faiss
import pandas as pd
import numpy as np
import pickle
import os

CSV_PATH = "resources/songs.csv"
INDEX_PATH = "faiss_index.index"
ID_MAP_PATH = "id_map.npy"

faiss_index = None
index_to_id = None

def build_faiss_index():
    global faiss_index, index_to_id

    df = pd.read_csv(CSV_PATH)
    df = df.rename(columns={"track_id": "id"})
    df = df[["id", "danceability", "energy", "valence", "tempo"]].dropna()
    index_to_id = df["id"].tolist()

    vectors = df[["danceability", "energy", "valence", "tempo"]].values.astype("float32")
    
    faiss_index = faiss.IndexFlatL2(vectors.shape[1])
    faiss_index.add(vectors)

    faiss.write_index(faiss_index, INDEX_PATH)
    np.save(ID_MAP_PATH, np.array(index_to_id))

    print("FAISS Index built and saved! yay")

def load_faiss_index():
    global faiss_index, index_to_id

    if not os.path.exists(INDEX_PATH) or not os.path.exists(ID_MAP_PATH):
        print("FAISS Index not found, building it fresh...")
        build_faiss_index()
    else:
        faiss_index = faiss.read_index(INDEX_PATH)
        index_to_id = np.load(ID_MAP_PATH).tolist()
        print("FAISS Index and ID map loaded")
def get_index_from_track_id(track_id: str) -> int:
    return index_to_id.index(track_id)
def get_track_id_from_index(index: int) -> str:
    return index_to_id[index]

'''
def get_nearest_neighbors(indices: list[int], k: int = 5) -> list[int]:
    vectors = faiss_index.reconstruct_n(min(indices), len(indices))
    vectors = np.array([faiss_index.reconstruct(i) for i in indices]).astype("float32")

    distances, neighbors = faiss_index.search(vectors, k+1)

    all_neighbors = []
    for i, row in enumerate(neighbors):
        for j in row:
            if j!= indices[i]:
                all_neighbors.append(j)
   return list(set(all_neighbors))
'''

def get_nearest_neighbors(query_vector: np.ndarray, k: int = 5):
    D, I = faiss_index.search(query_vector.astype("float32").reshape(1, -1), k)
    return I[0]

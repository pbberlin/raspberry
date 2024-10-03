'''
https://github.com/mlfoundations/open_clip

https://github.com/rom1504/clip-retrieval
https://github.com/rom1504/clip-retrieval?tab=readme-ov-file


for indexing alone
https://criteo.github.io/autofaiss/getting_started/quantization.html

export CUDA_VISIBLE_DEVICES=
clip-retrieval back --provide_violence_detector True --provide_safety_model True  --clip_model="ViT-L/14" --default_backend="http://localhost:1234/" --port 1234 --indices-paths indices.json --use_arrow True --enable_faiss_memory_mapping True --columns_to_return='["url", "caption", "md5"]'

'''


from clip_retrieval.clip_client import ClipClient, Modality
client = ClipClient(url="https://knn.laion.ai/knn-service", indice_name="laion5B-L-14")


cat_results = client.query(image="cat.jpg")
dog_results = client.query(image="https://example.com/dog.jpg")
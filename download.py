from huggingface_hub import snapshot_download

repo_id = 'NJUDeepEngine/CAEF_llama3.1_8b'
snapshot_download(repo_id=repo_id, local_dir='datasets')
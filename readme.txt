ollama pull mistral
# or use other models: ollama pull neural-chat, ollama pull orca-mini

ollama serve 


pip install -r requirements.txt


python main.py
# or terminal
python cli.py "how to navigate the website"




#Flow:

Query arrives
    ↓
search_with_confidence() calculates score
    ↓
Is score >= 0.85?
    ├─ YES → Return KB answer immediately ⚡ FAST (~5-10ms)
    └─ NO → Call Ollama with context 🤖 ACCURATE (~2-3s)





#steps to run  correctly 

OLLAMA_HOST=0.0.0.0:11435 ollma serve

watch -n 0.5 nvidia-smi 

Source .vene/bin/activate 

python main.py 


sudo su -
apt update
apt upgrade -y
curl -fsSL https://ollama.com/install.sh | sh
ollama pull granite4:350m
ollama pull nomic-embed-text

cd /opt
git clone https://github.com/Antalyse/simple-knowledge-base-AI.git ./simpleKnowledgeBaseAI
cd simpleKnowledgeBaseAI/
chmod +x app.py 
apt install python3.12-venv -y
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 

cp simpleknowledgebase.service /etc/systemd/system/simpleknowledgebase.service
systemctl daemon-reload
systemctl enable simpleknowledgebase.service
systemctl start simpleknowledgebase.service
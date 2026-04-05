cat > setup.sh << 'EOF'
#!/bin/bash

echo "🚀 Memulai instalasi..."
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/xRid2an/TG-Dashboard-Public
cd TG-Dashboard-Public
pip install -r requirements.txt
echo "✅ Selesai! Jalankan: python app.py"
EOF

chmod +x setup.sh

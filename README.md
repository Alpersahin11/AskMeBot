# 🤖 AskMeBot

**AskMeBot**, Flask ile geliştirilmiş bir chatbot uygulamasıdır. Bu bot, daha önceden eğitilmiş veriler üzerinde çalışır ve kullanıcıdan gelen sorulara en uygun cevabı vermeye çalışır. Gelen soruyu gömülü (embedding) temsile çevirir, mevcut veri kümesindeki cevaplarla benzerlik karşılaştırması yapar ve en yakın cevabı seçerek sunar.

---

## 🚀 Özellikler

- Embedding tabanlı doğal dil karşılaştırması
- Önceden eğitilmiş veri seti üzerinden hızlı cevap üretimi
- Flask ile basit web arayüzü
- Kolay kurulum ve kullanım

---

## 🧠 Çalışma Mantığı

1. Uygulama başlangıcında belirli bir Soru-Cevap veri seti yüklenir.
2. Bu veri setindeki tüm sorular embedding’lere dönüştürülür.
3. Kullanıcının yazdığı soru da embedding'e dönüştürülür.
4. En yakın eşleşen embedding seçilir.
5. Eşleşen embedding’e karşılık gelen cevap kullanıcıya sunulur.

---

## 📁 Proje Yapısı

AskMeBot/
├── app.py # Flask uygulaması ve yönlendirmeler
├── data/
│ └── qa_pairs.json # Örnek soru-cevap veri seti
├── embeddings.py # Embedding oluşturma ve benzerlik analizi
├── utils.py # Yardımcı fonksiyonlar
├── requirements.txt # Proje bağımlılıkları
└── README.md # Bu belge




---

## ⚙️ Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/Alpersahin11/AskMeBot.git
cd AskMeBot
Sanal ortam oluşturun ve bağımlılıkları kurun:

bash
Kopyala
Düzenle
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
Uygulamayı çalıştırın:

bash

python app.py
Tarayıcınızda şu adrese gidin: http://127.0.0.1:5000

💬 Örnek Kullanım
Kullanıcı: AskMeBot nedir?
Bot: AskMeBot, daha önceden eğitilmiş verilerle çalışan bir Flask tabanlı sohbet robotudur.

🧩 Gereksinimler
Python 3.8 veya üzeri

Flask

NumPy

scikit-learn 

Tüm bağımlılıklar requirements.txt dosyasında belirtilmiştir.

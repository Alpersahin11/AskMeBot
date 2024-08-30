from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import pyodbc

# SQLite veritabanı bağlantısı oluşturma
def connect_db():
    conn = pyodbc.connect("#VERİ TABANI AYARLARI")
    conn.autocommit = True  # Otomatik commit ayarı
    return conn


def get_hocalar():
    conn = connect_db()
    cursor = conn.cursor()

    # Hocalar tablosundan sadece isim, soyisim v<e uzmanlık alanlarını al
    cursor.execute('SELECT isim, soyisim, uzmanlik FROM Hocalar')
    hocalar = cursor.fetchall()

    # Bağlantıyı kapat
    conn.close()

    return hocalar

def tek_hoca(aranan):
    conn = connect_db()
    cursor = conn.cursor()

    # Hocalar tablosundan sadece isim, soyisim ve uzmanlık alanlarını al
    cursor.execute('SELECT isim, soyisim, uzmanlik FROM Hocalar WHERE isim = ?', (aranan,))
    hocalar = cursor.fetchall()

    # Bağlantıyı kapat
    conn.close()
    print(hocalar)
    print("=basarılır")

    return hocalar

app = Flask(__name__)
app.secret_key = 's3cr3t'  # Gizli anahtar, session'ı güvenli hale getirir
model = joblib.load('islemci_modeli2.pkl')
veri_seti = pd.read_csv('birlesik_dosya.csv')

onerilen_kelimeler = veri_seti['Soru'].values.tolist()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if request.form.get('form1_submit') == 'Submit':

            username = request.form['new_username']
            email = request.form['e_posta']
            password = request.form['new_password']

            # Veritabanına kullanıcıyı ekleme
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                           (username, email, password))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))  # Giriş sayfasına yönlendir
        elif request.form.get('form2_submit') == 'Submit':
            username = request.form['username']
            password = request.form['password']

            # Veritabanından kullanıcıyı sorgula
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()


            if user:
                # Kullanıcı bulundu, giriş yap ve giris_TRUE sayfasına yönlendir
                session['username'] = username
                conn.close()
                return redirect(url_for('giris_TRUE'))
            else:
                cursor.execute('SELECT * FROM Hocalar WHERE email = ? AND sifre = ?', (username, password))
                user = cursor.fetchone()

                if user:

                    session['username'] = user.isim
                    session['hoca_eposta'] = user.email
                    cursor = conn.cursor()
                    cursor.execute("""SELECT TOP 1
    M.id,
    M.icerik,
	M.gonderen_kisi,
    CASE
        WHEN M.gonderen_kisi = 'hoca' THEN H.isim
        ELSE U.username
    END AS gonderici_isim,
    CASE
        WHEN M.gonderen_kisi = 'hoca' THEN Us.username
        ELSE Hs.isim
    END AS alici_isim
FROM Mesajlar M
LEFT JOIN Users U ON M.gonderen_id = U.id
LEFT JOIN Hocalar H ON M.gonderen_id = H.id
LEFT JOIN Users Us ON M.alici_id = Us.id
LEFT JOIN Hocalar Hs ON M.alici_id = Hs.id
WHERE (M.alici_id = ? AND M.gonderen_kisi = 'users') OR (M.gonderen_id = ? AND M.gonderen_kisi = 'hoca')
ORDER BY M.id DESC;


""",user.id,user.id)

                    messages = cursor.fetchall()
                    print(messages)

                    conn.close()

                    print()
                    return render_template('hoca_ana.html', messages=messages)
                else:
                    conn.close()
                    return "Kullanıcı adı veya şifre hatalı. Lütfen tekrar deneyin."

    return render_template('AskMeBot.html', onerilen_kelimeler=onerilen_kelimeler)

@app.route('/uzmanlar',methods=["GET",'POST'])
def uzman():
    if request.method == 'GET':
        hocalar = get_hocalar()
        selected_hoca = request.form.get('hoca', '')

        return render_template('uzmanlar.html',hocalar = hocalar)

    if request.method == 'POST':
        selected_hoca = request.form.get('hoca', '')

        hocalar = tek_hoca(selected_hoca.split()[0])

        return render_template('uzman_kisi.html', hocalar=hocalar)


@app.route('/ozel_ogr_msj', methods=["GET", 'POST'])
def ozel_ogr_msj():
    if request.method == 'POST':
        try:
            print("dene1")
            mesaj = request.form['message']
            print("dene2")
            username = request.form['hoca_index']
            print("deneme1111111",username)
            hoca_str = username.split()
            print(hoca_str)

            # İlk parantezi kaldır
            print("tek hocaya girildi")
            hoca = tek_hoca(hoca_str[0])
            print(hoca)
            print("tek hocaya geldi")
            username = session.get('username')
            print(hoca)
            print(username)
            print("mesaj atmadan önce")
            print(username, hoca_str, mesaj, "öğrenci")
            mesaj_at(username, hoca_str, mesaj, "öğrenci")
            print("mesaj atıldı başarıyla")
            hoca = tek_hoca(username.split()[0])
            kullanici = session.get('username')
            print(hoca_str)
            print("mesaj gelmeden önce")
            sohbet = mesajlari_getir(kullanici,hoca_str , "ogr")
            print("mesaj gelmeden sonra")
            print(hoca, username, mesaj, sohbet)

            return render_template('ozel_mesaj_ogr.html',
                                   hoca=hoca, kullanici=username, mesaj=mesaj, sohbet=sohbet)
        except:
            username = request.form['name']

            print("except oldu ")
            print(username.split()[0])
            hoca = tek_hoca(username.split()[0])
            print(hoca, username)
            kullanici = session.get('username')
            print("dene", hoca, kullanici)
            sohbet = mesajlari_getir(kullanici, hoca[0], "ogr")



            return render_template('ozel_mesaj_ogr.html',
                                   hoca=username, kullanici=kullanici, sohbet=sohbet)

    if request.method == 'GET':
        hoca = request.form['name']
        print(hoca)


        return render_template('ozel_mesaj.html', hoca=hoca, kullanici=username)


@app.route('/mesaj_grup', methods=['GET', 'POST'])
def mesaj_grup():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()

        username = session.get('username')


        user_id = request.form['user_id']
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]


        cursor.execute("SELECT * FROM Mesajlar WHERE (gonderen_id = ?) OR (alici_id = ?)",
                       (user_id, user_id))

        messages_1_to_2 = cursor.fetchall()


        return render_template('mesaj_grup.html',hocalar = get_hocalar())


@app.route('/ogr_mesaj_grup', methods=['GET', 'POST'])
def ogr_mesaj_grup():
    if request.method == 'POST':
        conn = connect_db()
        cursor = conn.cursor()

        username = session.get('username')

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("""WITH SonMesajlar AS (
    SELECT 
        MAX(id) AS son_mesaj_id
    FROM 
        Mesajlar 
    WHERE 
        (gonderen_id = ? AND gonderen_kisi = 'users') OR (alici_id = ? AND gonderen_kisi = 'hoca')
    GROUP BY 
        gonderen_id, alici_id, gonderen_kisi
)
SELECT 
    m.gonderen_id, 
    m.alici_id, 
    m.gonderen_kisi, 
    m.icerik
FROM 
    Mesajlar m
    INNER JOIN SonMesajlar s ON m.id = s.son_mesaj_id;""",
                       (user_id, user_id,))

        messages = cursor.fetchall()
        print(messages)




        return render_template('ogr_mesaj_grup.html', hocalar=get_hocalar())

    if request.method == 'GET':
        conn = connect_db()
        cursor = conn.cursor()

        username = session.get('username')

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("""WITH SonMesajlar AS (
    SELECT 
        MAX(id) AS son_mesaj_id
    FROM 
        Mesajlar 
    WHERE 
        (gonderen_id = ? AND gonderen_kisi = 'users') OR (alici_id = ? AND gonderen_kisi = 'hoca')
    GROUP BY 
        gonderen_id, alici_id, gonderen_kisi
)
SELECT 
    m.id,
    m.gonderen_id, 
    m.alici_id, 
    m.gonderen_kisi, 
    m.icerik
FROM 
    Mesajlar m
    INNER JOIN SonMesajlar s ON m.id = s.son_mesaj_id;""",
                       (user_id, user_id,))

        messages = cursor.fetchall()
        print(messages)
        geri = filter_messages2(messages)
        geri = list(geri)
        print(geri)

        son_hal = []
        for i in geri:
            i = list(i)
            if i[3] == "hoca      ":
                cursor.execute('SELECT * FROM Hocalar WHERE id = ?', (i[1]))
                isim = cursor.fetchone()
                i[1] = str(isim[1] + " " + isim[2])

            if i[3] == 'users     ':
                cursor.execute('SELECT * FROM Hocalar WHERE id = ?', (i[2]))
                isim = cursor.fetchone()
                i[2] = str(isim[1] + " " + isim[2])
            son_hal.append(i)


        print(son_hal)
        return render_template('ogr_mesaj_grup.html', messages =son_hal)


def filter_messages2(rows):
    # Mesajları gönderici-alıcı çiftlerine göre grupla
    pairs = {}
    for row in rows:
        # Row nesnesini tuple'a dönüştür
        msg = tuple(row)
        index, sender_id, receiver_id, sender, content = msg
        pair = (min(sender_id, receiver_id), max(sender_id, receiver_id))  # Çifti küçükten büyüğe sırala
        # Eğer çift zaten listedeyse, en büyük indeksli mesajı al
        if pair in pairs:
            current_index, _ = pairs[pair]  # Mevcut en büyük indeksli mesajın indeksi ve içeriği
            if index > current_index:
                pairs[pair] = (index, msg)  # Daha büyük bir indeksli mesaj varsa güncelle
        else:
            pairs[pair] = (index, msg)

    # Sadece birbirinin tersi olan çiftler arasından en büyük indeksli mesajları al
    result_list = [msg for _, msg in pairs.values()]

    result_list = list(result_list)
    # Listeyi indekslere göre sırala
    result_list.sort(key=lambda x: x[0], reverse=True)
    return result_list



def filter_messages(rows):
    # Mesajları gönderici-alıcı çiftlerine göre grupla
    pairs = {}
    for row in rows:
        # Row nesnesini tuple'a dönüştür
        msg = tuple(row)
        index, sender_id, receiver_id, sender, content = msg
        pair = (sender_id, receiver_id)
        if pair not in pairs:
            pairs[pair] = []
        pairs[pair].append(msg)

    # Sonuç listesi için bir set oluştur
    result_set = set()

    for pair in pairs:
        # Aynı çift için tüm mesajları al
        msgs = pairs[pair]
        # Eğer aynı çiftten birden fazla mesaj varsa, indeksleri kontrol et
        if len(msgs) > 1:
            # Mesajları indekslerine göre sırala
            msgs.sort(key=lambda x: x[0], reverse=True)
            # En büyük indeksli mesajı koru
            result_set.add(msgs[0])
        else:
            result_set.add(msgs[0])

    # Set'i listeye dönüştür ve döndür
    result_list = list(result_set)
    # Listeyi indekslere göre sırala
    result_list.sort(key=lambda x: x[0], reverse=True)

    return result_list
def mesajlari_getir(kim,kime,dgr):
    conn = connect_db()
    cursor = conn.cursor()
    kime = kime

    if dgr == "ogr":
        cursor.execute("SELECT id FROM users WHERE (username = ?)", (kim))
        kullanici_bilgisi = cursor.fetchone()


        cursor.execute("SELECT id FROM Hocalar WHERE (isim = ?) AND (soyisim = ?)", (kime[0], kime[1]))
        hoca_bilgisi = cursor.fetchone()

        cursor.execute("SELECT * FROM Mesajlar WHERE ((gonderen_id = ?) AND (alici_id = ?)) OR ((gonderen_id = ?) AND (alici_id = ?)) ",
                       (int(kullanici_bilgisi[0]),int(hoca_bilgisi[0]),
                                int(hoca_bilgisi[0]),int(kullanici_bilgisi[0])))
        mesaj = cursor.fetchall()

        return mesaj

    elif dgr == "hoca":

        cursor.execute("SELECT id FROM users WHERE (username = ?)", (kim))
        kullanici_bilgisi = cursor.fetchone()


        cursor.execute("SELECT id FROM Hocalar WHERE (email = ?)", (kime))
        hoca_bilgisi = cursor.fetchone()

        cursor.execute(
            "SELECT * FROM Mesajlar WHERE ((gonderen_id = ?) AND (alici_id = ?)) OR ((gonderen_id = ?) AND (alici_id = ?)) ",
            (int(kullanici_bilgisi[0]), int(hoca_bilgisi[0]),
             int(hoca_bilgisi[0]), int(kullanici_bilgisi[0])))
        mesaj = cursor.fetchall()

        return mesaj

def mesaj_at(kim,kime,mesaj,dgr):

    conn = connect_db()
    cursor = conn.cursor()
    kime = kime



    if dgr == "öğrenci":
        cursor.execute("SELECT id FROM users WHERE (username = ?)",(kim))
        kullanici_bilgisi = cursor.fetchone()


        cursor.execute("SELECT id FROM Hocalar WHERE (isim = ?) AND (soyisim = ?)", (kime[0],kime[1]))
        hoca_bilgisi = cursor.fetchone()


        cursor.execute("INSERT INTO Mesajlar (icerik, gonderen_id, alici_id, gonderen_kisi) VALUES (?, ?, ?, ?)",
                       (mesaj,int(kullanici_bilgisi[0]),int(hoca_bilgisi[0]),'users'))

    elif dgr == "hoca":
        cursor.execute("SELECT id FROM users WHERE (username = ?)", (kime))
        kullanici_bilgisi = cursor.fetchone()


        cursor.execute("SELECT id FROM Hocalar WHERE email = ?", (kim))
        hoca_bilgisi = cursor.fetchone()


        cursor.execute("INSERT INTO Mesajlar (icerik, gonderen_id, alici_id, gonderen_kisi) VALUES (?, ?, ?, ?)",
                       (mesaj, int(hoca_bilgisi[0]), int(kullanici_bilgisi[0]), 'hoca'))

        # Değişiklikleri kaydet
        conn.commit()

        # Bağlantıyı kapat
        conn.close()

@app.route('/hoca_mesaj', methods=["GET",'POST'])
def hoca_mesaj():
    if request.method == 'POST':
        try:
            mesaj = request.form['message']
            ogr = request.form['username']
            hoca_eposta = session.get('hoca_eposta')
            hoca_ad = session.get("username")
            sohbet = mesaj_at(hoca_eposta,ogr,mesaj,"hoca")
            return render_template('ozel_mesaj_hoca.html',
                                   hoca=hoca_ad, kullanici=ogr,mesaj = mesaj,sohbet = sohbet)
        except:
            ogr_ad = request.form['username']
            hoca_posta = session.get('hoca_eposta')
            hoca_ad = session.get('username')
            sohbet = mesajlari_getir(ogr_ad,hoca_posta,"hoca")
            return render_template('ozel_mesaj_hoca.html',
                                   hoca=hoca_ad, kullanici=ogr_ad,sohbet = sohbet)

    if request.method == 'GET':
        username = request.form['hoca_index']
        hoca = tek_hoca(username)
        username = session.get('username')
        return render_template('ozel_mesaj.html',hoca=hoca , kullanici = username)



@app.route('/ozel_mesaj', methods=["GET",'POST'])
def ozel_mesaj():
    if request.method == 'POST':
        try:

            mesaj = request.form['message']

            username = request.form['hoca_index']

            hoca_str = username

            # İlk parantezi kaldır
            hoca_str = hoca_str[1:]

            # Son parantezi kaldır
            hoca_str = hoca_str[:-1]

            # Virgülle ayrılmış değerlere ayır
            hoca_degerleri = hoca_str.split(", ")

            # İlk değeri al
            isim = hoca_degerleri[0][1:-1] # Tek tırnakları kaldır


            hoca = tek_hoca(isim)

            username = session.get('username')

            print(username)
            sohbet = mesaj_at(username,hoca[0],mesaj,"öğrenci")
            sohbet = mesajlari_getir(username, hoca[0], "ogr")
            print(hoca,username,mesaj,sohbet)


            return render_template('ozel_mesaj.html',
                                   hoca=hoca, kullanici=username,mesaj = mesaj,sohbet = sohbet)
        except:
            username = request.form['hoca_index']

            print("except oldu ")

            hoca = tek_hoca(username)
            username = session.get('username')
            print(hoca,username)
            sohbet = mesajlari_getir(username,hoca[0],"ogr")

            return render_template('ozel_mesaj.html',
                                   hoca=hoca, kullanici=username,sohbet = sohbet)

    if request.method == 'GET':
        username = request.form['hoca_index']
        print(username)
        hoca = tek_hoca(username)
        print(hoca)
        username = session.get('username')
        return render_template('ozel_mesaj.html',hoca=hoca , kullanici = username)


@app.route('/process_text', methods=['POST'])
def process_text():
    # Formdan metni al
    text = request.form['text']

    # Metni işle
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(veri_seti['Soru'].values.tolist() + [text])

    # En yakın soruyu bul
    benzerlik_skorlari = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    en_yakin_soru_indexi = benzerlik_skorlari.argmax()
    en_yakin_soru = veri_seti.iloc[en_yakin_soru_indexi]['Soru']

    # Eşik değeri belirle
    esik_degeri = 0.5

    # Eşik değerini aşan bir benzerlik varsa tahmini yap
    if benzerlik_skorlari[0, en_yakin_soru_indexi] > esik_degeri:
        print( benzerlik_skorlari[0, en_yakin_soru_indexi])
        tahmin = model.predict([en_yakin_soru])[0]
        print("Girdiniz, '{}' sorusuna benziyor. Cevap: {}".format(en_yakin_soru, tahmin))
        return render_template('result.html', text=tahmin)
    else:
        print("Girdiniz, veri setindeki herhangi bir soruya benzemiyor.")
        tahmin = "Girdiniz, veri setindeki herhangi bir soruya benzemiyor."
        return render_template('result.html', text=tahmin)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Veritabanına kullanıcıyı ekleme
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))  # Giriş sayfasına yönlendir

    return render_template('kayit.html')

@app.route('/logout')
def logout():
    # Session'dan kullanıcı bilgilerini sil
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/girisTRUE', methods=['GET', 'POST'])
def giris_TRUE():
    if request.method == 'POST':
        text = request.form['soru']

        # Metni işle
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(veri_seti['Soru'].values.tolist() + [text])

        # En yakın soruyu bul
        benzerlik_skorlari = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
        en_yakin_soru_indexi = benzerlik_skorlari.argmax()
        en_yakin_soru = veri_seti.iloc[en_yakin_soru_indexi]['Soru']

        # Eşik değeri belirle
        esik_degeri = 0.5
        username = session.get('username')


        # Eşik değerini aşan bir benzerlik varsa tahmini yap
        if benzerlik_skorlari[0, en_yakin_soru_indexi] > esik_degeri:

            tahmin = model.predict([en_yakin_soru])[0]

            return redirect(url_for('/cevap'),username=username)
        else:

            tahmin = "Girdiniz, veri setindeki herhangi bir soruya benzemiyor."
            return render_template('ask_son.html', text=tahmin,username=username)

    else:
        username = session.get('username')
        return render_template('Ask_me.html', onerilen_kelimeler=onerilen_kelimeler,username=username)


@app.route('/cevap', methods=['GET', 'POST'])
def girisdene():
    text = request.form['soru']

    # Metni işle
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(veri_seti['Soru'].values.tolist() + [text])

    # En yakın soruyu bul
    benzerlik_skorlari = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    en_yakin_soru_indeksleri = benzerlik_skorlari.argsort()[0][-2:]  # En yakın iki indeksi al
    en_yakin_sorular = veri_seti.iloc[en_yakin_soru_indeksleri]['Soru'].tolist()  # İlgili soruları al

    # Eşik değeri belirle
    esik_degeri = 0.8
    username = session.get('username')
    # Eşik değerini aşan bir benzerlik varsa tahmini yap
    if benzerlik_skorlari[0, en_yakin_soru_indeksleri[-1]] > esik_degeri:
        tahmin = model.predict([en_yakin_sorular[-1]])[0]
        print("Girdiniz, '{}' sorusuna benziyor. Cevap: {}".format(en_yakin_sorular[-1], tahmin))
        return render_template("ask_son.html",soru=en_yakin_sorular[-1],tahminler=tahmin,s=1,
                                hocalar = get_hocalar(),username=username)
    else:
        print("En benzer iki soru:")
        for soru in en_yakin_sorular:
            print(soru)

        # Eşik değeri altında olduğunda yapılacak işlemler
        tahminler = [model.predict([soru])[0] for soru in en_yakin_sorular]  # En benzer 2 sorunun tahminlerini al
        return render_template("ask_son.html",soru = en_yakin_sorular, tahminler=tahminler,s=2,
                               hocalar = get_hocalar(),username=username)


if __name__ == '__main__':
    app.run(debug=True)

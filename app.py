import cv2
import psutil
import time
from flask import Flask, render_template, Response, jsonify
import numpy as np

baslangic_zamani = time.time()

app = Flask(__name__)

# System monitoring function
def get_system_data():
    # DÜZELTME: interval=0.1 ekledik, böylece CPU kullanımı %0'dan kurtulacak
    cpu_usage = psutil.cpu_percent(interval=0.1)
    gecen_sure = int(time.time() - baslangic_zamani)
    
    return {
        "cpu": cpu_usage,
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "sure": gecen_sure,
        "gonderilen": 10.5,
        "alinan": 5.2
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guncel_veri')
def guncel_veri():
    return jsonify(get_system_data())

# IDA Optical Tracking Route

@app.route('/vision_feed')
def vision_feed():
    image = cv2.imread('input_image5.jpeg')
    if image is None:
        return "Error: input_image5.jpeg not found!", 404

    # 1. Hazırlık ve Boyutlandırma
    resized_img = cv2.resize(image, (640, 480))
    
    # 2. RENK ANALİZİ (Arka Planda): Turuncu tonlarını bulalım
    hsv = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV)
    alt_turuncu = np.array([0, 100, 100])  # Turuncu alt limit
    ust_turuncu = np.array([20, 255, 255]) # Turuncu üst limit
    maske = cv2.inRange(hsv, alt_turuncu, ust_turuncu)

    # 3. KONTUR BULMA: Turuncu olan yerlerin etrafını saptayalım
    konturlar, _ = cv2.findContours(maske, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 4. GÖRÜNTÜYÜ HAZIRLA: Operatör için Siyah-Beyaz HUD oluştur
    gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    final_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # 5. HEDEFİ İŞARETLE: Eğer turuncu bir şey bulunduysa kare içine al
    # 5. HEDEFİ İŞARETLE: Tüm parçaları tek bir büyük kutuda birleştir
    all_x = []
    all_y = []
    all_w = []
    all_h = []
    target_status = "SEARCHING..."

    for kontur in konturlar:
        if cv2.contourArea(kontur) > 100: # Hassasiyeti biraz artırdık
            x, y, w, h = cv2.boundingRect(kontur)
            all_x.append(x)
            all_y.append(y)
            all_x.append(x + w)
            all_y.append(y + h)
            target_status = "TARGET LOCKED"

    # Eğer en az bir parça bulunduysa, hepsini kapsayan tek bir kutu çiz
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        # --- DÖNGÜ BİTTİ, ŞİMDİ HESAPLIYORUZ ---
        w_pixel = max_x - min_x
        
        f = 500 # Kamera kalibrasyon değeri
        W_real = 8 # Portakalın gerçek genişliği (cm)
        
        distance = (W_real * f) / w_pixel
        distance_m = round(distance / 100, 2)
        
        # Çizim ve Komut işlemleri buradan devam eder...
        cv2.rectangle(final_img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        
        # Mesafeyi ekrana yazdırıyoruz
        cv2.putText(final_img, f"DISTANCE: {distance_m} m", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0 ,0, 0), 2)

        
        # Tek ana kutuyu çiz (Yeşil)
        cv2.rectangle(final_img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        
        # Sol üst köşeye genel koordinatı yazdır
        cv2.putText(final_img, f"X:{min_x} Y:{min_y}", (min_x, min_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    

    else:
        # BURASI YENİ KISIM: Hedef bulunamadığında yapılacaklar
        # 'if' ile aynı hizada (indentation) olmalı!
        
        # 1. Hedef Kaybı Uyarısı (Kırmızı)
        cv2.putText(final_img, "TARGET LOST - SEARCHING...", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
        
        # 2. Güvenli Komut Durumu
        cv2.putText(final_img, "COMMAND: STOP & SCAN", (20, 115), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
    # 5.1 OTONOM DÜMEN TAVSİYESİ (Mantıksal Karar)
    if all_x and all_y:
        # Nesnenin merkezini hesapla
        obj_center_x = int((min_x + max_x) / 2)
        screen_center_x = 640 // 2 # Ekran genişliğinin tam ortası (320)
        
        # Sapma miktarını hesapla
        sapma = obj_center_x - screen_center_x
        
        # Karar Mekanizması
        if sapma < -50: # Nesne merkezden 50 pikselden fazla soldaysa
            command = "STEER LEFT (ISKELE)"
            color = (0, 0, 255) # Uyarı için Kırmızı
        elif sapma > 50: # Nesne merkezden 50 pikselden fazla sağdaysa
            command = "STEER RIGHT (SANCAK)"
            color = (0, 0, 255)
        else: # Nesne merkezdeyse (tolerans dahilinde)
            command = "STAY ON COURSE"
            color = (0, 255, 0) # Güvenli geçiş için Yeşil

        # Ekrana Komutu Yazdır
        cv2.putText(final_img, f"COMMAND: {command}", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Merkeze hayali bir rehber çizgi çekelim (Görsel referans için)
        cv2.line(final_img, (320, 120), (320, 360), (255, 255, 255), 1)    

    # 6. HUD Yazılarını Yaz
    ram_usage = psutil.virtual_memory().percent
    status_text = f"{target_status} - RAM: {ram_usage}%"
    cv2.putText(final_img, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # 7. Paketle ve gönder
    _, buffer = cv2.imencode('.jpg', final_img)
    return Response(buffer.tobytes(), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
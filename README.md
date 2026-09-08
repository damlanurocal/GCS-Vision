# GCS-Vision | Yer Kontrol Merkezi & Optik Hedef Takip Sistemi

GCS-Vision, insansız deniz araçları (İDA) ve otonom platformlar için geliştirilmiş, gerçek zamanlı optik hedef tespiti, mesafe tahmini, otonom rota karar mekanizması ve sistem telemetri takibi sunan Flask tabanlı bir Yer Kontrol Merkezi (GCS) arayüzüdür.

## 🚀 Öne Çıkan Özellikler

* **Optik Hedef Tespiti & Takibi:** OpenCV ve HSV renk uzayı filtreleme teknikleri kullanılarak belirlenen renk tonundaki hedeflerin gerçek zamanlı tespiti ve sınır çizgisi (bounding box) ile kilitlenmesi.
* **Mesafe Tahmini:** Kamera odak uzaklığı ($f$) ve hedefin gerçek boyut parametreleri kullanılarak piksel genişliği üzerinden anlık mesafe hesabı.
* **Otonom Karar & Dümen Komutları:** Hedefin ekran merkezine göre sapma miktarına bağlı olarak otomatik yönlendirme kararları (*STEER LEFT*, *STEER RIGHT*, *STAY ON COURSE*).
* **Güvenli Arama Modu:** Hedef kaybı durumunda otomatik olarak güvenli arama ve tarama moduna (*TARGET LOST - STOP & SCAN*) geçiş.
* **Sistem Telemetri Yayını:** Yer kontrol arayüzüne anlık CPU, RAM, Disk kullanımı ve sistem çalışma süresi verilerinin REST API (`/guncel_veri`) üzerinden aktarılması.
* **Operatör HUD Ekranı:** Siyah-beyaz arka plan üzerinde yüksek kontrastlı yeşil/kırmızı yönlendirme ve telemetri göstergeleri (HUD).

---

## 🛠️ Kullanılan Teknolojiler

* **Python 3.x**
* **Flask** (Web Sunucusu & YKM Arayüzü)
* **OpenCV (`cv2`)** (Görüntü İşleme ve Bilgisayarlı Görü)
* **NumPy** (Matematiksel ve Dizisel Hesaplamalar)
* **Psutil** (Donanım ve Sistem Telemetrisi Takibi)

---

## ⚙️ Kurulum ve Çalıştırma

1. **Repoyu klonlayın:**
   ```bash
   git clone [https://github.com/KULLANICI_ADI/GCS-Vision.git](https://github.com/KULLANICI_ADI/GCS-Vision.git)
   cd GCS-Vision

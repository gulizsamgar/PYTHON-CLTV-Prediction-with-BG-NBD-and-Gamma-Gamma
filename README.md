# Python | BG-NBD ve Gamma-Gamma ile CLTV Tahmini

## Projeye Genel Bakış

**Komut Dosyaları:** [`FLO_CLTV_Prediction`](script/FLO_CLTV_Prediction.py)

**Hedef:** Bu projenin temel hedefi, FLO'nun müşteri veri seti üzerinde BG/NBD ve Gamma-Gamma modellerini kullanarak Müşteri Yaşam Boyu Değeri (CLTV) tahmini yapmak ve bu tahminlere dayanarak müşterileri anlamlı segmentlere ayırarak hedefli pazarlama stratejileri geliştirmek için eyleme dönüştürülebilir içgörüler elde etmektir.

**Açıklama:** Proje, 2020-2021 yılları arasındaki OmniChannel müşteri verilerini kullanarak CLTV metriklerini (Recency, T, Frequency, Monetary Average) hesaplama, BG/NBD modeli ile gelecekteki satın alma sayısını ve Gamma-Gamma modeli ile ortalama işlem değerini tahmin etme adımlarını içermektedir. Bu tahminler birleştirilerek her müşterinin belirli bir zaman dilimi (örneğin 6 ay) için CLTV değeri hesaplanır. Hesaplanan CLTV değerlerine göre müşteriler farklı segmentlere (örneğin A, B, C, D) ayrılır. Ayrıca, oluşturulan segmentlerin özelliklerinin incelenmesi ve belirli pazarlama senaryoları için hedef müşteri kitlelerinin nasıl belirleneceği gösterilmiştir. Tüm CLTV hesaplama ve segmentasyon süreci, tekrar kullanılabilir bir Python fonksiyonu olarak da sunulmuştur.

Kodlar, projenin her adımını anlaşılır bir şekilde takip etmek amacıyla açıklamalı olarak hazırlanmıştır.

---

## İçerik

Proje aşağıdaki ana görevlerden oluşmaktadır:

*   **GÖREV 1: Veriyi Tanıma ve Hazırlama:** Veri setinin yüklenmesi, genel bilgilerin incelenmesi, eksik değer kontrolü ve yeni değişkenlerin (toplam sipariş sayısı, toplam harcama) oluşturulması.
*   **GÖREV 2: CLTV Metriklerinin Hesaplanması:** Recency (İlk ve son sipariş arasındaki süre), T (İlk sipariş ve analiz tarihi arasındaki süre), Frequency (Toplam sipariş sayısı) ve Monetary (Ortalama işlem değeri) gibi CLTV metriklerinin hesaplanması.
*   **GÖREV 3: BG/NBD Modeli ile Gelecek Satın Alma Sayısı Tahmini:** Müşterilerin gelecekte belirli bir zaman diliminde yapması beklenen satın alma sayısının BG/NBD modeli kullanılarak tahmin edilmesi.
*   **GÖREV 4: Gamma-Gamma Modeli ile Ortalama İşlem Değerinin Tahmini:** Müşterilerin gelecekteki her bir işleminde harcaması beklenen ortalama değerin Gamma-Gamma modeli kullanılarak tahmin edilmesi.
*   **GÖREV 5: CLTV Hesaplama:** BG/NBD ve Gamma-Gamma modellerinin çıktılarının birleştirilerek her müşterinin belirli bir zaman dilimi (örneğin 6 ay) için Müşteri Yaşam Boyu Değeri'nin (CLTV) hesaplanması.
*   **GÖREV 6: CLTV'ye Göre Segmentlerin Oluşturulması:** Hesaplanan CLTV değerlerine dayanarak müşterilerin farklı segmentlere ayrılması (örneğin A, B, C, D gibi).
*   **GÖREV 7: Eyleme Dönüştürülebilir İçgörüler:** Oluşturulan CLTV segmentlerinin özelliklerinin incelenmesi ve her bir segmente yönelik özelleştirilmiş pazarlama ve müşteri ilişkileri yönetimi stratejilerinin belirlenmesi.
*   **BONUS: Tüm Süreci Fonksiyonlaştırma:** CLTV hesaplama ve segmentasyon adımlarının tekrar kullanılabilir bir fonksiyon içine alınması.


---

## Beceriler

*   Müşteri Yaşam Boyu Değeri (CLTV) Tahmini (BG/NBD ve Gamma-Gamma Modelleri)
*   Müşteri Segmentasyonu (CLTV Değerlerine Göre)
*   Python ile veri işleme, temizleme ve manipülasyonu (Pandas kütüphanesi)
*   Özellik Mühendisliği
*   İstatistiksel Modelleme
*   Veri Filtreleme ve Seçimi
*   Temel İstatistiksel Analiz (Gruplama ve Özetleme)
*   Fonksiyon Yazma
*   Aykırı Değer Yönetimi

---

## Teknoloji

*   Python (3.x)
*   Python IDE'si PyCharm
*   Google Colab (veya Jupyter Not Defteri)

---

## Araçlar ve Kitaplıklar

*   **Python Programlama:** Temel sözdizimi, fonksiyonlar, koşullu ifadeler, döngüler.
*   **Pandas:** Veri yükleme, işleme, manipülasyonu ve analizi için (DataFrame kullanımı, gruplama, filtreleme, yeni sütun oluşturma).
*   **Numpy:** Sayısal işlemler ve veri manipülasyonu için (Pandas ile entegre kullanımı).
*   **Datetime:** Tarih ve saat verileriyle çalışmak için.
*   **Lifetimes:** BG/NBD ve Gamma-Gamma gibi CLTV tahmin modelleri için.
*   **Scikit-learn:** (MinMaxScaler gibi, potansiyel ölçeklendirme adımları için)

---

## Kullanım

Kodları çalıştırmak için Python 3.x yüklü bir ortamda Google Colab veya Jupyter Not Defteri gibi bir ortam kullanabilirsiniz.

- Gerekli kütüphaneleri (özellikle `lifetimes`) yükleyin ve içe aktarın.
- Veri setini **[`flo_data_20k.csv`](https://github.com/gulizsamgar/PYTHON-CLTV-Prediction-with-BG-NBD-and-Gamma-Gamma/blob/main/dataset/flo_data_20k.csv)** doğru dosya yolunu belirleyerek yükleyin.
- Her bir veri seti bölümündeki kod hücrelerini sırasıyla çalıştırarakveri hazırlığı, CLTV metrikleri hesaplama, modelleri kurma, CLTV hesaplama ve segmentasyon adımlarını takip edin.
- Kod çıktılarındaki analizleri ve sonuçları inceleyin.
- Markdown hücrelerindeki açıklamaları okuyarak yapılan işlemlerin amacını ve sonuçlarını anlayın.
- Farklı analiz senaryoları veya zaman dilimleri için kodları uyarlayarak kendi tahminlerinizi yapın.

---

## Detaylı Açıklamalar

Her görevin detaylı açıklamaları ve kod çıktıları için projenin **[`Jupyter Not Defteri dosyasına (.ipynb)`](FLO_CLTV_Prediction.ipynb)** göz atabilirsiniz.

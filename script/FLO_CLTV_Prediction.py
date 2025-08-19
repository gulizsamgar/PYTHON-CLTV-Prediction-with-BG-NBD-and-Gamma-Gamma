############################################################################################################################
# BG-NBD ve Gamma-Gamma ile CLTV Tahmini
############################################################################################################################

#############################################################################################################################
# İş Problemi (Business Problem)
#############################################################################################################################
# FLO satış ve pazarlama faaliyetleri için roadmap belirlemek istemektedir.
# Şirketin orta uzun vadeli plan yapabilmesi için var olan müşterilerin gelecekte şirkete sağlayacakları potansiyel değerin tahmin edilmesi gerekmektedir.


###############################################################
# Veri Seti Bilgisi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi



##############################################################################################################################
# Kütüphanelerin İçe Aktarılması ve Görüntü Ayarları
##############################################################################################################################

# lifetimes kütüphanesini yükle
!pip install lifetimes

# Gerekli kütüphaneleri import et
import pandas as pd
import datetime as dt
from lifetimes import BetaGeoFitter, GammaGammaFitter
from sklearn.preprocessing import MinMaxScaler

# Pandas gösterim ayarlarını yapılandır
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.options.mode.chained_assignment = None



#############################################################################################################################
# GÖREV 1: VERİYİ TANIMA VE HAZIRLAMA
#############################################################################################################################

###############################################################
# 1. Veri setini içe aktar
###############################################################

# Dosya yolu tanımlanıyor.
file_path = '/content/drive/MyDrive/flo_data_20k.csv'
# CSV dosyasını pandas DataFrame'ine oku.
df_ = pd.read_csv(file_path)
# Orijinal DataFrame'in bir kopyasını oluştur.
df = df_.copy()

# Doğru şekilde yüklendiğini onaylamak için ilk birkaç satırı görüntüle
print("\nFirst 5 rows of dataset:")
print(df.head(), "\n")

###############################################################
# 2. Aykırı değerleri baskılamak için fonksiyonlar
###############################################################

# Aykırı değerler için eşik değerlerini hesaplayan fonksiyon
def outlier_thresholds(dataframe, variable):
    # %1 ve %99 çeyreklerini (quartiles) hesapla
    q1 = dataframe[variable].quantile(0.01)
    q3 = dataframe[variable].quantile(0.99)
    # Çeyrekler arası açıklığı (Interquartile Range - IQR) hesapla
    iqr = q3 - q1
    # Üst eşik değerini hesapla
    up_limit = q3 + 1.5 * iqr
    # Alt eşik değerini hesapla
    low_limit = q1 - 1.5 * iqr
    # Hesaplanan eşik değerlerini döndür (yuvarlanmış)
    return round(low_limit, 0), round(up_limit, 0)

# Aykırı değerleri eşik değerleri ile değiştiren fonksiyon
def replace_with_thresholds(dataframe, variable):
    # Belirtilen değişken için alt ve üst eşik değerlerini al
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # Alt eşiğin altındaki değerleri alt eşik ile değiştir
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    # Üst eşiğin üzerindeki değerleri üst eşik ile değiştir
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


###############################################################
# 3. İlgili değişkenlerde aykırı değer baskılama
###############################################################

# Aykırı değerleri baskılanacak sütunlar
columns = ["order_num_total_ever_online", "order_num_total_ever_offline",
           "customer_value_total_ever_offline", "customer_value_total_ever_online"]

# Belirlenen sütunlarda aykırı değerleri baskıla
for col in columns:
    replace_with_thresholds(df, col)

# İşlem tamamlandı mesajı
print("Outliers handled successfully!")


###############################################################
# 4. Özellik Mühendisliği: Müşteri bazında toplam sipariş sayısı ve toplam harcama
###############################################################

# Online ve offline sipariş sayılarını toplayarak toplam sipariş sayısını hesapla
df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

# Online ve offline harcama değerlerini toplayarak toplam harcama değerini hesapla
df["customer_value_total"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

# Yeni oluşturulan değişkenleri kontrol etmek için DataFrame'in ilk birkaç satırını görüntüle (isteğe bağlı)
display(df.head())



##############################################################################################################################
# GÖREV 2: CLTV METRİKLERİNİN HESAPLANMASI
##############################################################################################################################

###############################################################
# 1. Analiz tarihi: Son alışveriş tarihinden 2 gün sonrası
###############################################################

# 'last_order_date' ve 'first_order_date' sütunlarını datetime formatına çevir
for col in ["last_order_date", "first_order_date"]:
    df[col] = pd.to_datetime(df[col])

# Veri setindeki son sipariş tarihini bul
print("\nLast order date in dataset:")
print(df["last_order_date"].max(),"\n")

# Analiz tarihini belirle (son sipariş tarihinden 2 gün sonrası)
analysis_date = dt.datetime(2021, 6, 1)

###############################################################
# 2. CLTV dataframe oluşturma
###############################################################

# CLTV analizi için yeni DataFrame oluştur
cltv_df = pd.DataFrame()
# Müşteri ID'lerini ekle
cltv_df["customer_id"] = df["master_id"]
# Recency_cltv_weekly hesapla (haftalık)
cltv_df["recency_cltv_weekly"] = ((df["last_order_date"] - df["first_order_date"]).dt.days) / 7
# T_weekly hesapla (haftalık)
cltv_df["T_weekly"] = ((analysis_date - df["first_order_date"]).dt.days) / 7
# Frequency ata (toplam sipariş sayısı)
cltv_df["frequency"] = df["order_num_total"]
# Monetary_cltv_avg hesapla (ortalama işlem değeri)
cltv_df["monetary_cltv_avg"] = df["customer_value_total"] / df["order_num_total"]

# Oluşturulan CLTV DataFrame'inin ilk birkaç satırını görüntüle
print("\nCLTV dataframe created!")
print(cltv_df.head(),"\n")



##############################################################################################################################
# GÖREV 3: BG/NBD ve GAMMA-GAMMA MODELLERİ İLE CLTV HESAPLAMA
##############################################################################################################################

###############################################################
# 1. BG/NBD Modeli
###############################################################

# BG/NBD modelini uydurmadan önce veri hazırlığı
# Sıklığı 0 olan müşterileri çıkar
cltv_df = cltv_df[cltv_df['frequency'] > 0]

# Frequency sütununu integer'a dönüştür
cltv_df['frequency'] = cltv_df['frequency'].astype(int)

# Model uydurmadan önce frequency ve recency_cltv_weekly minimum değerlerini kontrol et
print(f"\nMinimum frequency after filtering: {cltv_df['frequency'].min()}")
print(f"Minimum recency_cltv_weekly after filtering: {cltv_df['recency_cltv_weekly'].min()}")

# Beta-Geometric Negative Binomial Distribution (BG/NBD) modelini başlat
# penalizer_coef, aşırı uyumu (overfitting) önlemek için kullanılan bir düzenlileştirme (regularization) parametresidir.
bgf = BetaGeoFitter(penalizer_coef=0.001)

# BG/NBD modelini veri setine uygula (fit et)
# Model, müşterilerin satın alma sıklığı (frequency), ilk ve son satın alma arasındaki süre (recency_cltv_weekly)
# ve ilk satın alma ile analiz tarihi arasındaki süre (T_weekly) verilerini kullanarak parametrelerini öğrenir.
bgf.fit(cltv_df['frequency'],
        cltv_df['recency_cltv_weekly'],
        cltv_df['T_weekly'])

# Modelin başarıyla kurulduğunu belirten bir mesaj yazdır
print("BG/NBD model fitted successfully!")

###############################################################
# 1.a. 3 aylık satın alma tahmini
###############################################################

# BG/NBD modeli (bgf) kullanarak sonraki 3 ay (12 hafta) için beklenen satın alma sayısını tahmin et
# predict fonksiyonu, modelin öğrendiği parametreleri ve müşterinin recency, frequency, T_weekly değerlerini kullanarak tahmini hesaplar.
cltv_df["exp_sales_3_month"] = bgf.predict(4*3, # 4 hafta/ay * 3 ay = 12 hafta
                                           cltv_df['frequency'],
                                           cltv_df['recency_cltv_weekly'],
                                           cltv_df['T_weekly'])

###############################################################
# 1.b. 6 aylık satın alma tahmini
###############################################################

# BG/NBD modeli (bgf) kullanarak sonraki 6 ay (24 hafta) için beklenen satın alma sayısını tahmin et
cltv_df["exp_sales_6_month"] = bgf.predict(4*6, # 4 hafta/ay * 6 ay = 24 hafta
                                           cltv_df['frequency'],
                                           cltv_df['recency_cltv_weekly'],
                                           cltv_df['T_weekly'])

# Tahmin sütunlarının başarıyla eklendiğini belirten bir mesaj yazdır
print("Expected sales predictions added (3 and 6 months).")

###############################################################
# 2. Gamma-Gamma Modeli
###############################################################

# Gamma-Gamma modelini başlat
# penalizer_coef, aşırı uyumu (overfitting) önlemek için kullanılan bir düzenlileştirme parametresidir.
ggf = GammaGammaFitter(penalizer_coef=0.001) # Using 0.001 as in BG/NBD for consistency, or 0.01 as in original code? Let's stick to 0.01 as in the user's provided code.
ggf = GammaGammaFitter(penalizer_coef=0.01)

# Gamma-Gamma modelini veri setine uygula (fit et)
# Model, müşterilerin sıklığı (frequency) ve ortalama işlem değeri (monetary_cltv_avg) verilerini kullanarak parametrelerini öğrenir.
# monetary_value: Ortalama işlem değeri sütunu
# frequency: Sıklık sütunu
ggf.fit(cltv_df['frequency'],
        cltv_df['monetary_cltv_avg'])

# Gamma-Gamma modelini kullanarak her müşteri için beklenen ortalama işlem değerini tahmin et
# conditional_expected_average_profit fonksiyonu, modelin öğrendiği parametreleri ve müşterinin frequency, monetary_cltv_avg değerlerini kullanarak tahmini hesaplar.
cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                       cltv_df['monetary_cltv_avg'])

# Model uydurma ve ortalama değer tahmininin tamamlandığını belirten mesaj
print("\nGamma-Gamma model fitted and average values predicted!")

###############################################################
# 3. 6 aylık CLTV hesaplama
###############################################################

# BG/NBD ve Gamma-Gamma modellerini kullanarak 6 aylık müşteri yaşam boyu değerini (CLTV) hesapla
# customer_lifetime_value fonksiyonu, iki modelin çıktılarını birleştirerek nihai CLTV'yi tahmin eder.
cltv = ggf.customer_lifetime_value(bgf, # BG/NBD modeli nesnesi
                                   cltv_df['frequency'], # Sıklık sütunu
                                   cltv_df['recency_cltv_weekly'], # Recency sütunu (haftalık)
                                   cltv_df['T_weekly'], # T sütunu (haftalık)
                                   cltv_df['monetary_cltv_avg'], # Ortalama işlem değeri sütunu
                                   time=6,  # CLTV'nin hesaplanacağı zaman dilimi (ay cinsinden)
                                   freq="W",  # Zaman birimi (Weekly - Haftalık)
                                   discount_rate=0.01) # Gelecekteki nakit akışlarının iskonto oranı

# Hesaplanan CLTV değerlerini cltv_df DataFrame'ine yeni bir sütun olarak ekle
cltv_df["cltv"] = cltv

# CLTV hesaplama işleminin tamamlandığını belirten mesaj
print("\n6-month CLTV calculated and added!")

# Hesaplanan CLTV değerlerine göre müşterileri sırala ve en yüksek CLTV'ye sahip ilk 20 müşteriyi görüntüle
print("\nTop 20 customers by CLTV:")
print(cltv_df.sort_values("cltv", ascending=False).head(20), "\n")



##############################################################################################################################
# GÖREV 4: CLTV'ye GÖRE SEGMENTLERİN OLUŞTURULMASI
##############################################################################################################################

###############################################################
# 1. Segmentleme (4 gruba ayırma)
###############################################################

# cltv sütununu çeyrek (quartile) bazında 4 eşit gruba ayırır.
# labels=["D", "C", "B", "A"] ile segmentlere D (en düşük CLTV) den A (en yüksek CLTV) ye doğru etiket atar.
cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])
print("\nCustomers segmented into 4 groups (A-D).")

# Oluşturulan segmentlerin dağılımını (her segmentteki müşteri sayısı) göster
print("\nSegment distribution:")
print(cltv_df["cltv_segment"].value_counts())

# Segmentlenmiş DataFrame'in ilk birkaç satırını görüntüle
print("\nSample of segmented customers:\n")
print(cltv_df.head())



##############################################################################################################################
# BONUS: TÜM SÜRECİ FONKSİYONLAŞTIRMA
##############################################################################################################################

# Tüm CLTV Sürecini Fonksiyonlaştırma
def create_cltv_df(dataframe):
    # 1. Aykırı değerleri baskılama
    columns = ["order_num_total_ever_online", "order_num_total_ever_offline",
               "customer_value_total_ever_offline", "customer_value_total_ever_online"]
    for col in columns:
        replace_with_thresholds(dataframe, col)

    # 2. Yeni değişkenler oluşturma (Toplam sipariş ve toplam harcama)
    dataframe["order_num_total"] = dataframe["order_num_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["customer_value_total"] = dataframe["customer_value_total_ever_offline"] + dataframe["customer_value_total_ever_online"]

    # 3. Tarih sütunlarını datetime formatına dönüştürme
    date_columns = dataframe.columns[dataframe.columns.str.contains("date")]
    dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)

    # 4. Analiz tarihi belirleme
    analysis_date = dt.datetime(2021, 6, 1)

    # 5. CLTV veri yapısı oluşturma (recency, T, frequency, monetary)
    cltv_df = pd.DataFrame()
    cltv_df["customer_id"] = dataframe["master_id"]
    cltv_df["recency_cltv_weekly"] = ((dataframe["last_order_date"] - dataframe["first_order_date"]).dt.days) / 7
    cltv_df["T_weekly"] = ((analysis_date - dataframe["first_order_date"]).dt.days) / 7
    cltv_df["frequency"] = dataframe["order_num_total"]
    cltv_df["monetary_cltv_avg"] = dataframe["customer_value_total"] / dataframe["order_num_total"]

    # Frequency değeri 1'den büyük olan müşterileri filtrele (Model gereksinimi)
    cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

    # Frequency sütununu integer'a dönüştür (Model gereksinimi)
    cltv_df['frequency'] = cltv_df['frequency'].astype(int)


    # 6. BG-NBD Modeli kurma ve tahmin
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'],
            cltv_df['recency_cltv_weekly'],
            cltv_df['T_weekly'])
    cltv_df["exp_sales_3_month"] = bgf.predict(4*3,
                                               cltv_df['frequency'],
                                               cltv_df['recency_cltv_weekly'],
                                               cltv_df['T_weekly'])
    cltv_df["exp_sales_6_month"] = bgf.predict(4*6,
                                               cltv_df['frequency'],
                                               cltv_df['recency_cltv_weekly'],
                                               cltv_df['T_weekly'])

    # 7. Gamma-Gamma Modeli kurma ve tahmin
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    # Monetary değerlerinin pozitif olduğunu kontrol etmeden fit ediliyor (varsayım kontrolü yapılabilir)
    ggf.fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])
    cltv_df["exp_average_value"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                           cltv_df['monetary_cltv_avg'])

    # 8. CLTV Hesaplama (6 aylık)
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df['frequency'],
                                       cltv_df['recency_cltv_weekly'],
                                       cltv_df['T_weekly'],
                                       cltv_df['monetary_cltv_avg'],
                                       time=6,
                                       freq="W",
                                       discount_rate=0.01)
    cltv_df["cltv"] = cltv

    # 9. Segmentleme (4 gruba ayırma)
    cltv_df["cltv_segment"] = pd.qcut(cltv_df["cltv"], 4, labels=["D", "C", "B", "A"])

    return cltv_df

# Fonksiyonu çağırma ve sonucu bir değişkene atama
cltv_result = create_cltv_df(df)
print("\nCLTV process completed successfully!\n")
print(cltv_result.head())



#!/usr/bin/env python3
"""Offline Turkish SMS category model builder. Requires scikit-learn to RETRAIN only.
The iPhone runs inference entirely in Swift, without Python or an API.
Training examples below are synthetic; never paste real private SMS here.
"""
import json, random, re, unicodedata
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

random.seed(20261109)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'Shared'/'sms_model.json'

# Seeded synthetic texts: each section has different message intents. 
TEMPLATES = {
'normal': [
'Merhaba nasılsın bugün görüşebilir miyiz', 'Akşam eve gelince haber ver',
'Yarın saat {hour} toplantımız var', 'Bugün işten sonra kahve içelim mi',
'Gönderdiğin dosyaya baktım teşekkür ederim', 'Yemek hazır geliyorsan haber ver',
'Müsait olunca beni arar mısın', 'Hafta sonu planın var mı',
'Kütüphaneden kitabı aldım', 'Toplantı ertelendi yarın konuşuruz',
'Sipariş verdiğimiz pizzayı beraber yiyeceğiz', 'Mesajını gördüm birazdan döneceğim',
'Doğum günün kutlu olsun iyi ki varsın', 'Otobüs durağında seni bekliyorum',
'Bu akşam maça beraber gidelim', 'Dosyayı mail olarak gönderir misin',
'Tamamdır yarın sabah görüşürüz', 'Teşekkürler iyi çalışmalar',
'Ödevin son halini bana atar mısın', 'Buluşmaya geç kalacağım kusura bakma',
],
'verification': [
'{brand} giriş doğrulama kodunuz {code} kimseyle paylaşmayın',
'{code} tek kullanımlık şifrenizdir lütfen paylaşmayınız',
'{brand} hesabına giriş yapmak için kodunuz {code}',
'İşleminizi onaylamak için doğrulama kodu {code}',
'Güvenlik kodunuz {code} sadece sizin içindir',
'{brand} hesabınız için SMS onay kodu {code}',
'{code} numaralı kod ile oturum açabilirsiniz',
'Şifre yenileme kodunuz {code} süresi 5 dakika',
'Onay kodu {code} lütfen üçüncü kişilerle paylaşmayın',
'{brand} uygulamasına giriş için tek seferlik kod {code}',
'Sayın müşterimiz işlem kodunuz {code}',
'{code} doğrulama şifrenizi kimseyle paylaşmayınız',
],
'banking': [
'{brand} kartınızla {amount} TL tutarında alışveriş yapılmıştır',
'Hesabınıza {amount} TL para transferi gerçekleşmiştir',
'EFT talebiniz başarıyla tamamlandı işlem tutarı {amount} TL',
'Kredi kartınızın dönem borcu {amount} TL son ödeme tarihi yaklaşıyor',
'{brand} hesabınıza {amount} TL ödeme gelmiştir',
'Para çekme işleminiz gerçekleşti {amount} TL',
'Kartınızın hesap kesim özeti hazır',
'{brand} havale işleminiz tamamlandı',
'Faturanız için {amount} TL otomatik ödeme gerçekleştirildi',
'Kredi kartı ekstreniz kullanıma açıldı',
'Vadeli hesabınız için faiz ödemesi hesabınıza aktarıldı',
'{brand} ATM para çekme bildirimi',
],
'delivery': [
'Siparişiniz kargoya teslim edildi takip numaranız {tracking}',
'Kargonuz bugün dağıtıma çıkarılmıştır',
'{shop} siparişiniz hazırlanıyor',
'Paketiniz teslim edilmiştir iyi günler',
'Kurye kapınızda teslimat için sizi bekliyor',
'{shop} alışverişinizin faturası oluşturuldu',
'Gönderiniz şubemize ulaşmıştır',
'Sipariş numarası {tracking} kargoya verildi',
'Teslimatınız bugün {hour} saatinde yapılacak',
'Kargonuz adrese yönlendirildi',
'{shop} siparişinizin durumu güncellendi',
'Paketiniz teslim noktasından alınabilir',
],
'advertising': [
'{shop} mağazasında yüzde {discount} indirim başladı',
'Bu hafta sonuna özel kampanyamızdan yararlanın',
'{shop} yeni sezon fırsatlarını kaçırmayın',
'Alışverişlerde ikinci ürüne indirim kazanın',
'Kupon kodunuzla yüzde {discount} indirim fırsatı',
'Sınırlı süreli kampanya ve özel fiyatlar sizleri bekliyor',
'Yeni ürün koleksiyonumuz şimdi satışta',
'Bu fırsat sadece üyelerimize özel',
'{shop} mağazasından {amount} TL üzeri alışverişe hediye',
'Ücretsiz kargo ve indirimli fiyatlar bugün',
'Yüzde {discount} sezon sonu fırsatları başladı',
'Fırsatları kaçırmayın hemen mağazamızı ziyaret edin',
'İndirim kuponunuzu bugün kullanabilirsiniz',
],
'gambling': [
'Bahis sitesinde yeni üyelere {amount} TL bonus fırsatı',
'Canlı bahis yüksek oranlar ve anlık kazanç',
'Casino slot oyunlarında bedava çevirme hakkı',
'Ücretsiz deneme bonusu şimdi hesabında',
'Yatırımınıza yüzde {discount} hoş geldin bonusu',
'Kupon yap katla kazan bahis oranları yükseldi',
'Günün maçlarında yüksek oranlı bahis fırsatı',
'Çevrim şartsız casino bonusu için giriş yapın',
'Slot oyunlarında jackpot fırsatını kaçırma',
'Bedava bahis bakiyesi hesabınıza yüklendi',
'Yatırım şartsız bonus ile şansını dene',
'Canlı casino ve spor bahisleri tek adreste',
'{amount} TL yatır bonusunu hemen al',
'Bahis hesabını aç hoş geldin bonusun hazır',
'Süper oranlarla maçlara kupon yap',
'Yasadışı bahis reklamı üye ol para kazan',
],
'scam': [
'Hesabınız askıya alınmıştır acilen bağlantıdan doğrulayın',
'Kargonuz teslim edilemedi ek ücret için linke tıklayın',
'Banka hesabınız bloke oldu giriş yaparak şifrenizi güncelleyin',
'İcra dosyanız açıldı ödeme için bağlantıya gidiniz',
'Son uyarı hesabınız kapatılacak hemen işlem yapın',
'Sahte güvenlik bildirimi şifrenizi girmeniz gerekiyor',
'Paketiniz bekletiliyor gümrük ücretini linkten ödeyin',
'Kartınızı kullanıma açmak için bu bağlantıdan giriş yapın',
'Hesabınız ele geçirildi linkten doğrulama yapınız',
'Acil ödeme yapmazsanız hesabınız kapanacaktır',
'Teslimat adresiniz eksik ödeme yaparak tekrar gönderin',
'Adınıza mahkeme dosyası var hemen para yatırın',
'Kazanılan ödülü almak için kart bilgilerinizi gönderin',
'Kredi hesabınız donduruldu şifrenizi yenileyin',
'Güvenlik nedeniyle kimlik bilgilerinizi girmeniz şart',
'Dolandırıcılık şüphesi var hesabınızı linke tıklayıp doğrulayın',
],
}

def normalize(text):
    text = text.lower().replace('ı','i').replace('i\u0307','i')
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return re.findall(r'[a-z0-9]+', text)

def feature_dict(text):
    tokens = normalize(text)
    features = set()
    for token in tokens:
        features.add('w:'+token)
        padded = '^'+token+'$'
        for n in (3,4):
            for i in range(len(padded)-n+1): features.add('c:'+padded[i:i+n])
    for a,b in zip(tokens, tokens[1:]):
        features.add('b:'+a+'_'+b)
    return {k:1 for k in features}

rows=[]
brands=['Banka','Mobil','Güvenlik','Uygulama','Dijital','Hesap']
shops=['Mağaza','Market','Online alışveriş','Teknoloji','Süpermarket']
for category, templates in TEMPLATES.items():
    for t in templates:
        for i in range(18):
            rows.append((t.format(
                code=random.choice(['483921','739482','516238','4928','782633']),
                amount=random.choice(['250','500','1200','3500','7500']),
                hour=random.choice(['9','10','14','18']),
                tracking=random.choice(['AB248341','5048219','8920134']),
                brand=random.choice(brands), shop=random.choice(shops),
                discount=random.choice(['20','30','40','50','60']),
            ), category))
random.shuffle(rows)
train_x=[feature_dict(s) for s,_ in rows]
train_y=[c for _,c in rows]
vec=DictVectorizer(sparse=True, sort=True)
X=vec.fit_transform(train_x)
# Non-probabilistic linear classifier; softmax outputs are indicative, not calibrated.
clf=LogisticRegression(max_iter=2500, C=3.0)
clf.fit(X,train_y)
# Retain all nonzero coefficients. Small, sparse & human-auditable model.
weights={}
for feat, j in vec.vocabulary_.items():
    vals=[round(float(v),5) for v in clf.coef_[:,j]]
    if max(abs(v) for v in vals) >= 0.035:
        weights[feat]=vals
model={'format':1,'modelName':'NOVA SMS Shield Tiny Linear AI','labels':list(clf.classes_),
       'bias':[round(float(x),5) for x in clf.intercept_],
       'weights':dict(sorted(weights.items())),
       'syntheticTrainingSamples':len(rows),'disclaimer':'Synthetic starter data; not validated on real SMS.'}
OUT.write_text(json.dumps(model,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Output',OUT,'size',OUT.stat().st_size, 'features',len(weights),'examples',len(rows))

if __name__ == '__main__':
    trial = [
        'Şifreniz 482921 giriş için doğrulama kodunuz. Kimseyle paylaşmayın',
        '1000 TL yatır 10.000 TL bonus kazan casino ve slot fırsatı',
        'Kargonuz dağıtıma çıktı bugün teslim edilecek',
        'Merhaba işten sonra beni ara',
        'Hesabınız bloke edildi hemen linkten şifrenizi girin',
        'Bu hafta mağazamızda yüzde 50 indirim fırsatları başladı',
        'Kartınızla 1300 TL işlem yapıldı',
        'Siparişiniz teslim edilemedi adres güncellemek için tıklayın',
    ]
    import numpy as np
    for s,p in zip(trial,clf.predict_proba(vec.transform(map(feature_dict,trial)))):
        top=np.argmax(p)
        print(f'{clf.classes_[top]:12s} {p[top]:.2f} | {s}')

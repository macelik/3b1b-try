"""Seslendirme metni.

Her sahne, sırayla okunan satırlardan oluşur. Her satır: (anahtar, metin).
Metin hem altyazı hem de seslendirme için kullanılır; seslendirmeden önce
`tts_text` ile şapkalı harfler vb. TTS motorunun okuyabileceği hâle getirilir.
"""

SCENES = {
    "S01_Duzeltme": [
        ("intro", "İman kelimesini fonetik açıdan incelerken, önceki videolarda yaptığım küçük bir hatayı fark ettim."),
        ("kok", "Kelimenin kökü elif, mîm ve nûn değil; hemze, mîm ve nûndur."),
        ("anlam", "Bu hata, önceki videolarda anlattığımız kök anlamını değiştirmiyor."),
        ("fakat", "Fakat kelimeyi fonetik açıdan incelemeye başladığımızda, elif ile hemze arasındaki fark oldukça önemli hâle geliyor."),
    ],
    "S02_ElifHemze": [
        ("elif", "Çünkü elif; daha açık, yumuşak ve zayıf bir ses."),
        ("hemze", "Hemze ise boğazın en derin bölgesinden çıkan, daha keskin ve kuvvetli bir ses."),
    ],
    "S03_IbnCinni": [
        ("giris", "İşte tam bu noktada, İbn Cinnî'nin dikkat çektiği ses ile mana arasındaki ilişki devreye giriyor."),
        ("uyum", "Ona göre bazen seslerin çıkış yeri, kuvveti ve telaffuz biçimi ile kelimenin taşıdığı anlam arasında dikkat çekici bir uyum bulunuyor."),
    ],
    "S04_Hemze": [
        ("bakalim", "Şimdi bu gözle, iman kelimesine bakalım."),
        ("ilk", "İlk ses: hemze."),
        ("guclu", "Hemze, boğazın en derin bölgesinden çıkan, güçlü ve keskin bir ses."),
        ("tasdik", "Bu kuvvetli ses, imandaki tasdikin silik ve pasif bir kabul değil; güçlü ve kararlı bir başlangıç oluşuyla güzel bir uyum gösteriyor."),
    ],
    "S05_IkiHemze": [
        ("ayrinti", "Üstelik, çok ilginç bir ayrıntı daha var."),
        ("zaten", "Kökün ilk harfi zaten hemze."),
        ("ifal", "Kelime if‘âl bâbına girdiğinde, bir hemze daha ekleniyor."),
        ("amene", "Yani âmene kelimesinin, aslında iki hemzeli bir yapısı var."),
        ("kat", "Bu da kelimenin başındaki o sarsılmaz kuvvetin, bir katmanla adeta ikiye katlandığını gösteriyor."),
    ],
    "S06_Mim": [
        ("ikinci", "İkinci harfimiz: mîm."),
        ("dudak", "Mîm söylenirken iki dudak kapanır; ses içeride toplanır."),
        ("emniyet", "Bu kapanma ve toparlanma hâli, hemze, mîm, nûn kökünün taşıdığı güven ve emniyet anlamıyla dikkat çekici bir uyum gösteriyor."),
        ("siginma", "Nitekim insan da güvene kavuştuğunda; korkudan, şüpheden ve kendisine zarar vereceğini düşündüğü şeylerden uzaklaşıp, güvenli bir alana sığınır."),
        ("muhafaza", "Sanki mîm, sesi dışarıdan içeriye topluyor ve onu güvenli bir alanda muhafaza ediyor."),
    ],
    "S07_Nun": [
        ("son", "Ve son ses: nûn."),
        ("tanim", "İbn Cinnî, nûnu cehrî ve gunneli bir ses olarak tanımlar."),
        ("geniz", "Nûn söylenirken ses bir anda kesilip kaybolmaz; genizde yankılanarak içeriden devam eder."),
        ("kalici", "Bu içten ve devam eden tını da, imanın yalnızca bir anlık tasdik değil; insanın içinde yerleşen, kök salan ve süreklilik kazanan bir hâl oluşuyla güzel bir uyum gösteriyor."),
    ],
    "S08_Yolculuk": [
        ("yolculuk", "Böylece kelimenin sesinde, adeta bir yolculuk görüyoruz."),
        ("y1", "Hemzede, güçlü bir başlangıç;"),
        ("y2", "ikinci hemzeyle, bu kuvvetin pekişmesi;"),
        ("y3", "mîmde, güvene sığınma ve toparlanma;"),
        ("y4", "nûnda ise, içte yerleşip devam eden bir hâl."),
        ("yani", "Yani iman, yalnızca “inandım ve doğruluyorum” demek değil; güçlü bir tasdikle başlayıp güvene dönüşen ve insanın içinde yaşamaya devam eden bir hâl."),
    ],
    "S09_Not": [
        ("not", "Bu, harflerin sözlük anlamı değil; İbn Cinnî'nin ses ile mana arasındaki ilişkiye dair yaklaşımından hareketle yapılan, estetik bir okuma."),
    ],
}

SCENE_ORDER = list(SCENES)

_TTS_MAP = str.maketrans({
    "â": "a", "Â": "A", "î": "i", "Î": "İ", "û": "u", "Û": "U",
    "‘": "'", "’": "'", "“": "", "”": "",
})


# Seslendirme motorunun zorlandığı ifadeler için okunuş düzeltmeleri
_TTS_FIX = {
    "if‘âl": "ifal",
    "harfimiz: mîm": "harfimiz, mim",
    "mîmde, güvene sığınma ve": "mimde, güvene sığınma, ve",
}


def tts_text(text: str) -> str:
    for a, b in _TTS_FIX.items():
        text = text.replace(a, b)
    return text.translate(_TTS_MAP)

# utils/translations.py
"""
Language translations for Coffee Leaf Disease Detection System
Supports: English, Amharic (አማርኛ), Afaan Oromo
"""

TRANSLATIONS = {
    'en': {
        # App title and header
        'app_title': '🌿 Coffee Leaf Disease Detection System',
        'subtitle': 'AI-Powered Diagnosis for Ethiopian Coffee Farmers',
        'accuracy_badge': '🎯 Model Accuracy: 98%',
        
        # Sidebar
        'settings': '⚙️ Settings',
        'select_model': 'Select Model',
        'mobile_net': '🎯 MobileNet Model (98% accuracy)',
        'model_performance': '📊 Model Performance',
        'test_accuracy': 'Test Accuracy',
        'about': 'ℹ️ About',
        'supported_diseases': 'Supported Diseases:',
        'healthy': '✅ Healthy',
        'cercospora': '🍂 Cercospora Leaf Spot',
        'leaf_rust': '⚠️ Coffee Leaf Rust',
        'miner': '🐛 Coffee Leaf Miner',
        'phoma': '🍂 Phoma Leaf Spot',
        'tips': '💡 Tips for Best Results',
        'tip1': '- Use clear, well-lit photos',
        'tip2': '- Focus on the affected leaf area',
        'tip3': '- Avoid blurry or dark images',
        'tip4': '- Capture the leaf against a plain background',
        'supported_formats': '📷 Supported Formats',
        'credits': '🌱 Credits',
        'credit_text': 'Made with ❤️ for Ethiopian Coffee Farmers',
        
        # Main area
        'upload_title': '📤 Upload Coffee Leaf Image',
        'detect_button': '🔍 Detect Disease',
        'diagnosis_results': '📊 Diagnosis Results',
        'low_confidence': '⚠️ Low confidence prediction',
        'confidence': 'Confidence:',
        'severity': 'Severity:',
        'description': 'Description:',
        'treatment': '💊 Treatment:',
        'prevention': '🛡️ Prevention:',
        
        # Disease names
        'disease_healthy': 'Healthy',
        'disease_rust': 'Coffee Leaf Rust',
        'disease_cercospora': 'Cercospora Leaf Spot',
        'disease_phoma': 'Phoma Leaf Spot',
        'disease_miner': 'Coffee Leaf Miner',
        
        # Severity levels
        'severity_none': 'None',
        'severity_moderate': 'Moderate',
        'severity_high': 'High',
        
        # Footer
        'footer': 'For accurate diagnosis, ensure images are clear and well-lit. Consult with local agricultural experts for confirmed diagnosis and treatment plans.',
        
        # Buttons and labels
        'language': '🌐 Language',
        'english': 'English',
        'amharic': 'አማርኛ (Amharic)',
        'afaan_oromo': 'Afaan Oromo',
        'loading': 'Analyzing image with AI...',
        'error': 'Error loading model',
        'no_model': 'No model files found in models/ folder',
        'add_model': 'Please add .h5 model files to the models/ directory'
    },
    
    'am': {
        # App title and header
        'app_title': '🌿 የቡና ቅጠል በሽታ መለያ ሲስተም',
        'subtitle': 'ለኢትዮጵያ ቡና አርሶ አደሮች በአርቲፊሻል ኢንተሊጀንስ የሚሰራ ምርመራ',
        'accuracy_badge': '🎯 የሞዴሉ ትክክለኛነት: 98%',
        
        # Sidebar
        'settings': '⚙️ ቅንብሮች',
        'select_model': 'ሞዴል ይምረጡ',
        'mobile_net': '🎯 ሞባይል ኔት ሞዴል (98% ትክክለኛነት)',
        'model_performance': '📊 የሞዴሉ አፈጻጸም',
        'test_accuracy': 'የሙከራ ትክክለኛነት',
        'about': 'ℹ️ ስለ',
        'supported_diseases': 'የሚታወቁ በሽታዎች:',
        'healthy': '✅ ጤናማ',
        'cercospora': '🍂 ሰርኮስፖራ የቅጠል ነጠብጣብ',
        'leaf_rust': '⚠️ የቡና ዝገት',
        'miner': '🐛 የቡና ቆፋሪ',
        'phoma': '🍂 ፎማ የቅጠል ነጠብጣብ',
        'tips': '💡 ለተሻለ ውጤት ምክሮች',
        'tip1': '- ግልጽ እና በደንብ የበራ ፎቶዎችን ይጠቀሙ',
        'tip2': '- በበሽታው በተጠቃው የቅጠሉ ክፍል ላይ ያተኩሩ',
        'tip3': '- ደብዛዛ ወይም ጨለማ ምስሎችን ያስወግዱ',
        'tip4': '- ቅጠሉን ቀለል ባለ ዳራ ላይ ያንሱ',
        'supported_formats': '📷 የሚደገፉ ቅርጸቶች',
        'credits': '🌱 ምስጋና',
        'credit_text': 'ለኢትዮጵያ ቡና አርሶ አደሮች በፍቅር የተሰራ',
        
        # Main area
        'upload_title': '📤 የቡና ቅጠል ፎቶ ይስቀሉ',
        'detect_button': '🔍 በሽታውን ለይ',
        'diagnosis_results': '📊 የምርመራ ውጤት',
        'low_confidence': '⚠️ ዝቅተኛ ትክክለኛነት ትንበያ',
        'confidence': 'እምነት:',
        'severity': 'ክብደት:',
        'description': 'መግለጫ:',
        'treatment': '💊 ህክምና:',
        'prevention': '🛡️ መከላከያ:',
        
        # Disease names
        'disease_healthy': 'ጤናማ',
        'disease_rust': 'የቡና ዝገት',
        'disease_cercospora': 'ሰርኮስፖራ የቅጠል ነጠብጣብ',
        'disease_phoma': 'ፎማ የቅጠል ነጠብጣብ',
        'disease_miner': 'የቡና ቆፋሪ',
        
        # Severity levels
        'severity_none': 'ምንም',
        'severity_moderate': 'መካከለኛ',
        'severity_high': 'ከፍተኛ',
        
        # Footer
        'footer': 'ትክክለኛ ምርመራ ለማግኘት ፎቶዎች ግልጽ እና በደንብ የበራ መሆን አለባቸው። ለተረጋገጠ ምርመራ እና ህክምና ከአካባቢዎ ግብርና ባለሙያዎች ይጠይቁ።',
        
        # Buttons and labels
        'language': '🌐 ቋንቋ',
        'english': 'እንግሊዝኛ',
        'amharic': 'አማርኛ',
        'afaan_oromo': 'አፋን ኦሮሞ',
        'loading': 'ምስልን በአርቲፊሻል ኢንተሊጀንስ በመተንተን ላይ...',
        'error': 'ሞዴሉን ማስገባት አልተቻለም',
        'no_model': 'በሞዴል አቃፊ ውስጥ ምንም የሞዴል ፋይሎች አልተገኙም',
        'add_model': 'እባክዎ የ.h5 ሞዴል ፋይሎችን በሞዴል ማውጫ ውስጥ ያስገቡ'
    },
    
    'om': {
        # App title and header
        'app_title': '🌿 Sisteemii Dhukkuba Baala Bunaa Addaan Baasuuf Gargaaru ',
        'subtitle': 'Qonnaan Bultoota Buna Itiyoophiyaatiif qorannoo Artiifishaal Intalijansii (AI) irratti hundaae.',
        'accuracy_badge': '🎯 Sirrumma Madooelaa: 98%',
        
        # Sidebar
        'settings': '⚙️ Settings',
        'select_model': 'Moodeela Filadhu',
        'mobile_net': '🎯 Moodeela Netoota Moobiilii (98% sirrumma)',
        'model_performance': '📊 Hojii Moodeelaa',
        'test_accuracy': 'Sirrumma Qorannoo',
        'about': 'ℹ️ Waaee',
        'supported_diseases': 'Dhukkuboota Beekamoo:',
        'healthy': '✅ Fayyaa qaba',
        'cercospora': '🍂 Tuqaa Baalaa Cerkosoporaa',
        'leaf_rust': '⚠️ Dhulluun Bunaa',
        'miner': '🐛 Xuuxxuu Bunaa',
        'phoma': '🍂 Tuqaa Baalaa Foomawwan',
        'tips': '💡 Buaa Gaarii Argachuuf Gorsa murtessoo',
        'tip1': '- Suuraalee ifa taan fi ibsaa gaarii qaban fayyadami.',
        'tip2': '- Kutaa jirmaa ykn baala miidhame irratti xiyyeeffadhu',
        'tip3': '- Suuraawwan ifaa hin qabne ykn duwwaa taate fayyadamuu hin fayyadamin',
        'tip4': '- Baalicha Irratti yeroo suuraa fudhattuu iftoomaa taate itti dhuunfaa irratti qabaadhu',
        'supported_formats': '📷 Bifaalee (Formats) deeggaraman',
        'credits': '🌱 Galatoomi',
        'credit_text': 'Jaalalaan Qonnean Bultoota Buna Itiyoophiyaatiif kan qophaae ❤️',
        
        # Main area
        'upload_title': '📤 Suuraa Baala Bunaa Feeyadhu',
        'detect_button': '🔍 Dhukkuba Adda Baasi',
        'diagnosis_results': '📊 Buata Qorannoo',
        'low_confidence': "⚠️ Raaguun Sirrummaa Ga'eessaa hin taane",
        'confidence': 'Amantaa:',
        'severity': 'Hamma tahee:',
        'description': 'Ibsa:',
        'treatment': '💊 Qoricha:',
        'prevention': '🛡️ Ittisaa:',
        
        # Disease names
        'disease_healthy': 'Fayyaa qaba',
        'disease_rust': 'Dhulluun Bunaa',
        'disease_cercospora': 'Tuqaa Baalaa Cerkosoporaa',
        'disease_phoma': 'Tuqaa Baalaa Foomawwan',
        'disease_miner': 'Xuuxxuu Bunaa',
        
        # Severity levels
        'severity_none': 'Homtuu',
        'severity_moderate': 'Giddu galeessa',
        'severity_high': 'Olaanaa',
        
        # Footer
        'footer': 'Yaala sirrii ta’e argachuuf, suuraaleen ati kaastu ifa fi qulqulluu ta’uu isaanii mirkaneessi. Akkasumas, qorannoo mirkanaa’aa fi dhimma yaalaatiif ogeessota qonnaa naannoo keetii mariisisi.',
        
        # Buttons and labels
        'language': '🌐 Afaan',
        'english': 'Ingiliffa',
        'amharic': 'Amaaraa',
        'afaan_oromo': 'Oromoo',
        'loading': 'Suuraa Lamaan hojiirra oolaa carraa irtifikaalaa ta’een xiinxaluu...',
        'error': 'Moodeela Fe’uu hin danda’u',
        'no_model': 'Faayiliin Moodeela kitaabalee moodeelaa keessatti hin argamu',
        'add_model': 'Mee faayilii moodeela .h5 kitaabalee moodeelatti fe’adhu'

        
    }
}

def get_text(key, language='en'):
    """Get translated text for a given key"""
    if language in TRANSLATIONS:
        return TRANSLATIONS[language].get(key, TRANSLATIONS['en'].get(key, key))
    return TRANSLATIONS['en'].get(key, key)
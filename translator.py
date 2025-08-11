import logging
from googletrans import Translator
from langdetect import detect
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiLanguageSupport:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'it': 'Italian',
            'ko': 'Korean',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'ur': 'Urdu'
        }
        
        # Agricultural terms dictionary for better translation
        self.agriculture_terms = {
            'en': {
                'crop': 'crop',
                'farming': 'farming',
                'agriculture': 'agriculture',
                'soil': 'soil',
                'fertilizer': 'fertilizer',
                'irrigation': 'irrigation',
                'harvest': 'harvest',
                'pesticide': 'pesticide',
                'seed': 'seed',
                'plant': 'plant'
            },
            'hi': {
                'crop': 'फसल',
                'farming': 'खेती',
                'agriculture': 'कृषि',
                'soil': 'मिट्टी',
                'fertilizer': 'उर्वरक',
                'irrigation': 'सिंचाई',
                'harvest': 'फसल काटना',
                'pesticide': 'कीटनाशक',
                'seed': 'बीज',
                'plant': 'पौधा'
            },
            'es': {
                'crop': 'cultivo',
                'farming': 'agricultura',
                'agriculture': 'agricultura',
                'soil': 'suelo',
                'fertilizer': 'fertilizante',
                'irrigation': 'riego',
                'harvest': 'cosecha',
                'pesticide': 'pesticida',
                'seed': 'semilla',
                'plant': 'planta'
            }
        }

    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            detected_lang = detect(text)
            if detected_lang in self.supported_languages:
                return detected_lang
            return 'en'  # Default to English
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'en'

    def translate_text(self, text, target_language='en', source_language='auto'):
        """Translate text to target language"""
        try:
            if source_language == target_language:
                return text
            
            result = self.translator.translate(text, src=source_language, dest=target_language)
            return result.text
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return text  # Return original text if translation fails

    def get_greeting_message(self, language_code='en'):
        """Get greeting message in specified language"""
        greetings = {
            'en': "🌱🌾 Welcome to AgriGenius !! 🌾🌱 Hi there! I'm AgriGenius, your virtual assistant for Agriculture. How can I assist you today?",
            'hi': "🌱🌾 AgriGenius में आपका स्वागत है !! 🌾🌱 नमस्ते! मैं AgriGenius हूं, कृषि के लिए आपका वर्चुअल असिस्टेंट। आज मैं आपकी कैसे सहायता कर सकता हूं?",
            'es': "🌱🌾 ¡¡Bienvenido a AgriGenius!! 🌾🌱 ¡Hola! Soy AgriGenius, tu asistente virtual para la agricultura. ¿Cómo puedo ayudarte hoy?",
            'fr': "🌱🌾 Bienvenue chez AgriGenius !! 🌾🌱 Salut! Je suis AgriGenius, votre assistant virtuel pour l'agriculture. Comment puis-je vous aider aujourd'hui?",
            'de': "🌱🌾 Willkommen bei AgriGenius !! 🌾🌱 Hallo! Ich bin AgriGenius, Ihr virtueller Assistent für die Landwirtschaft. Wie kann ich Ihnen heute helfen?",
            'ar': "🌱🌾 مرحبا بكم في AgriGenius !! 🌾🌱 مرحبا! أنا AgriGenius، مساعدك الافتراضي للزراعة. كيف يمكنني مساعدتك اليوم؟",
            'zh': "🌱🌾 欢迎来到AgriGenius !! 🌾🌱 您好！我是AgriGenius，您的农业虚拟助手。今天我能为您提供什么帮助？",
            'ja': "🌱🌾 AgriGeniusへようこそ !! 🌾🌱 こんにちは！私はAgriGenius、あなたの農業バーチャルアシスタントです。今日はどのようにお手伝いできますか？"
        }
        
        return greetings.get(language_code, greetings['en'])

    def get_language_options(self):
        """Get available language options for frontend"""
        return [{'code': code, 'name': name} for code, name in self.supported_languages.items()]

    def enhance_agricultural_translation(self, text, target_language):
        """Enhance translation with agricultural context"""
        try:
            translated = self.translate_text(text, target_language)
            
            # Replace common agricultural terms with more accurate translations
            if target_language in self.agriculture_terms:
                terms = self.agriculture_terms[target_language]
                for en_term, local_term in terms.items():
                    # Simple replacement - in production, you'd want more sophisticated NLP
                    translated = translated.replace(en_term, local_term)
            
            return translated
        except Exception as e:
            logger.error(f"Error in enhanced translation: {str(e)}")
            return text

# Initialize the translator
multi_lang = MultiLanguageSupport()

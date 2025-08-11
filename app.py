# app.py
from flask import Flask, render_template, request, jsonify
import os
import sys

# Add debug information
print("=== AgriGenius Startup Debug ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

try:
    from chat1 import fetch_website_content, extract_pdf_text, initialize_vector_store
    from chat2 import llm, setup_retrieval_qa
    from translator import multi_lang
    from agri_knowledge import agri_knowledge
    print("✅ Advanced AI modules loaded successfully")
    AI_MODE = True
except ImportError as e:
    print(f"⚠️ Import error with AI modules: {e}")
    AI_MODE = False
    try:
        from simple_chat import fetch_website_content, extract_pdf_text, initialize_vector_store, setup_retrieval_qa
        llm = None
        print("✅ Fallback modules loaded")
        AI_MODE = True
    except ImportError as e2:
        print(f"❌ Critical error: {e2}")
        fetch_website_content = None
        extract_pdf_text = None
        initialize_vector_store = None
        llm = None
        setup_retrieval_qa = None
    
    try:
        from translator import multi_lang
    except ImportError:
        multi_lang = None
        print("⚠️ Translation features not available")
    
    try:
        from agri_knowledge import agri_knowledge
    except ImportError:
        agri_knowledge = None
        print("⚠️ Knowledge base not available")

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Example URLs and PDF files
urls = ["https://mospi.gov.in/4-agricultural-statistics"]   #"https://desagri.gov.in/",
pdf_files = ["Data/Farming Schemes.pdf", "Data/farmerbook.pdf"]

# Initialize the application
def initialize_app():
    if not (fetch_website_content and extract_pdf_text and initialize_vector_store and setup_retrieval_qa):
        logger.error("Required functions not available due to import errors")
        return None, None
        
    try:
        # Fetch content from websites
        logger.info("Fetching website content...")
        website_contents = []
        for url in urls:
            try:
                content = fetch_website_content(url)
                if content:
                    website_contents.append(content)
            except Exception as e:
                logger.warning(f"Failed to fetch content from {url}: {str(e)}")

        # Extract text from PDF files
        logger.info("Extracting PDF content...")
        pdf_texts = []
        for pdf_file in pdf_files:
            try:
                text = extract_pdf_text(pdf_file)
                if text:
                    pdf_texts.append(text)
            except Exception as e:
                logger.warning(f"Failed to extract text from {pdf_file}: {str(e)}")

        # Combine all content into chunks
        all_contents = website_contents + pdf_texts
        
        if not all_contents:
            logger.warning("No content available, creating basic chatbot")
            return None, None

        # Initialize the vector store
        logger.info("Initializing vector store...")
        db = initialize_vector_store(all_contents)
        
        if db is None:
            logger.warning("Failed to initialize vector store, creating basic chatbot")
            return None, None

        # Set up the RetrievalQA chain
        logger.info("Setting up retrieval QA chain...")
        chain = setup_retrieval_qa(db)
        
        return db, chain
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        return None, None

# Initialize the components
print("Starting AgriGenius initialization...")
db, chain = initialize_app()

if chain is not None:
    print("✅ AgriGenius AI system initialized successfully!")
else:
    print("⚠️ AgriGenius running in basic mode - AI features are not available")

# Simple agriculture knowledge base for fallback
SIMPLE_AGRICULTURE_KB = {
    'crops': {
        'wheat': "Wheat grows best in well-drained loamy soil with pH 6.0-7.5. Plant in fall/winter, needs 12-15 inches of water annually. Harvest when grain moisture is 13-14%.",
        'rice': "Rice requires flooded fields or high moisture. Plant in warm weather (75-85°F). Needs 40-70 inches of water. Harvest when grains are golden and firm.",
        'corn': "Corn needs warm weather (60-95°F), well-drained soil with pH 6.0-6.8. Plant after soil reaches 50°F. Requires 20-30 inches of water during growing season.",
        'tomato': "Tomatoes need warm weather (65-85°F), well-drained soil with pH 6.0-6.8. Start indoors 6-8 weeks before last frost. Need consistent watering and support structures."
    },
    'soil': {
        'ph': "Soil pH affects nutrient availability. Most crops prefer pH 6.0-7.0. Test annually and adjust with lime (raise pH) or sulfur (lower pH).",
        'fertility': "Good soil needs organic matter, proper drainage, and balanced nutrients (NPK). Add compost, rotate crops, and test soil every 2-3 years.",
        'preparation': "Prepare soil by tilling 8-12 inches deep, removing weeds, adding organic matter, and ensuring proper drainage before planting."
    },
    'fertilizer': {
        'organic': "Organic fertilizers include compost, manure, bone meal, and fish emulsion. They release nutrients slowly and improve soil structure.",
        'synthetic': "Synthetic fertilizers provide quick nutrients. Common ratios: 10-10-10 (balanced), 20-10-10 (high nitrogen for leafy growth).",
        'timing': "Apply fertilizer based on soil tests and crop needs. Generally: pre-plant, side-dress during growth, and avoid over-fertilizing."
    },
    'pest_control': {
        'ipm': "Integrated Pest Management combines biological, cultural, physical, and chemical controls. Monitor regularly, identify pests correctly, and use least toxic methods first.",
        'organic': "Organic pest control includes beneficial insects, neem oil, diatomaceous earth, crop rotation, and companion planting.",
        'prevention': "Prevent pests through healthy soil, proper spacing, crop rotation, sanitation, and encouraging beneficial insects."
    }
}

def get_smart_agriculture_response(query):
    """Generate intelligent responses for agriculture questions"""
    query_lower = query.lower()
    
    # First check if this is a price/market related query
    price_keywords = ['price', 'cost', 'rate', 'market', 'sell', 'buy', 'mandi', 'wholesale', 'retail', 'मूल्य', 'कीमत', 'दर', 'बाज़ार']
    if any(keyword in query_lower for keyword in price_keywords):
        try:
            from market_api import get_market_price_response
            
            # Extract crop name from query if present
            mentioned_crop = None
            for crop in SIMPLE_AGRICULTURE_KB['crops'].keys():
                if crop in query_lower:
                    mentioned_crop = crop
                    break
            
            if mentioned_crop:
                return get_market_price_response(mentioned_crop)
            else:
                return get_market_price_response("wheat")  # Default to wheat
                
        except ImportError:
            # Fallback if API module not available
            pass
        
        return """💰 **Market Price Information:**

I don't have access to current market prices as they change daily. For up-to-date crop prices, try these resources:

🏪 **Local Markets:**
• Visit your nearest mandi (wholesale market)
• Contact local traders and commission agents
• Check with cooperative societies

📱 **Digital Resources:**
• Government agriculture department websites
• Mobile apps like eNAM, AgriApp, KisanSuvidha
• Commodity exchange websites (MCX, NCDEX)

📺 **News & Media:**
• Agriculture news channels
• Newspaper agriculture sections
• Radio agriculture programs

**Note:** Prices vary by location, quality, season, and market conditions.

Would you like farming advice for growing this crop instead? 🌱"""
    
    # Check for specific crop questions (but not if it was a price query)
    for crop, info in SIMPLE_AGRICULTURE_KB['crops'].items():
        if crop in query_lower:
            return f"🌱 **{crop.title()} Farming Guide:**\n{info}\n\nWould you like to know more about {crop} diseases, fertilizers, or harvesting techniques?"
    
    # Check for soil-related questions
    if any(word in query_lower for word in ['soil', 'ph', 'fertility', 'ground']):
        if 'ph' in query_lower:
            return f"🌍 **Soil pH Information:**\n{SIMPLE_AGRICULTURE_KB['soil']['ph']}\n\nWould you like to know about testing soil pH or adjusting it for specific crops?"
        elif any(word in query_lower for word in ['fertile', 'fertility', 'nutrient']):
            return f"🌍 **Soil Fertility Guide:**\n{SIMPLE_AGRICULTURE_KB['soil']['fertility']}\n\nWant to learn about specific nutrients or composting?"
        else:
            return f"🌍 **Soil Preparation:**\n{SIMPLE_AGRICULTURE_KB['soil']['preparation']}\n\nNeed help with specific soil problems or crop-specific soil requirements?"
    
    # Check for fertilizer questions
    if any(word in query_lower for word in ['fertilizer', 'fertiliser', 'nutrient', 'feed']):
        if 'organic' in query_lower:
            return f"🌿 **Organic Fertilizers:**\n{SIMPLE_AGRICULTURE_KB['fertilizer']['organic']}\n\nInterested in making your own compost or learning about specific organic fertilizers?"
        elif any(word in query_lower for word in ['synthetic', 'chemical', 'npk']):
            return f"⚗️ **Synthetic Fertilizers:**\n{SIMPLE_AGRICULTURE_KB['fertilizer']['synthetic']}\n\nNeed help calculating fertilizer amounts or understanding NPK ratios for your crops?"
        else:
            return f"🌱 **Fertilizer Timing:**\n{SIMPLE_AGRICULTURE_KB['fertilizer']['timing']}\n\nWhat specific crops are you fertilizing? I can provide more targeted advice!"
    
    # Check for pest control questions
    if any(word in query_lower for word in ['pest', 'insect', 'bug', 'disease', 'control']):
        if 'organic' in query_lower:
            return f"🐛 **Organic Pest Control:**\n{SIMPLE_AGRICULTURE_KB['pest_control']['organic']}\n\nWhat specific pests are you dealing with? I can suggest targeted organic solutions!"
        elif 'prevent' in query_lower:
            return f"🛡️ **Pest Prevention:**\n{SIMPLE_AGRICULTURE_KB['pest_control']['prevention']}\n\nWhat crops are you growing? Prevention strategies vary by crop type!"
        else:
            return f"🔬 **Integrated Pest Management:**\n{SIMPLE_AGRICULTURE_KB['pest_control']['ipm']}\n\nAre you dealing with a specific pest problem? Describe the symptoms and affected crops!"
    
    # Weather and climate questions
    if any(word in query_lower for word in ['weather', 'climate', 'temperature', 'rain', 'water']):
        return "🌤️ **Weather & Agriculture:**\nWeather greatly affects farming success. Monitor temperature, rainfall, and seasonal patterns. Most crops need consistent water but avoid waterlogging. Use weather forecasts for planting and harvesting decisions.\n\nWhat's your local climate like? I can suggest suitable crops!"
    
    # Irrigation questions
    if any(word in query_lower for word in ['water', 'irrigation', 'watering']):
        return "💧 **Irrigation Guide:**\nProper watering is crucial! Deep, less frequent watering is usually better than shallow, frequent watering. Consider drip irrigation for efficiency. Water early morning or evening to reduce evaporation.\n\nWhat crops are you watering? Each has different water needs!"
    
    # Seasonal/timing questions
    if any(word in query_lower for word in ['when', 'time', 'season', 'plant', 'harvest']):
        return "📅 **Farming Calendar:**\nTiming depends on your location and crop choice. Generally:\n• **Spring:** Plant warm-season crops after last frost\n• **Summer:** Maintain crops, harvest early varieties\n• **Fall:** Plant cool-season crops, harvest summer crops\n• **Winter:** Plan next year, maintain equipment\n\nWhat's your location and which crops interest you?"
    
    # General farming questions
    if any(word in query_lower for word in ['farm', 'agriculture', 'grow', 'cultivation']):
        return "🚜 **General Farming Tips:**\nSuccessful farming involves: good soil preparation, choosing right crops for your climate, proper timing, regular monitoring, and continuous learning.\n\n**Key Success Factors:**\n• Know your soil and climate\n• Choose appropriate varieties\n• Practice crop rotation\n• Monitor for pests/diseases\n• Keep detailed records\n\nWhat specific aspect of farming would you like to explore?"
    
    # Default engaging response
    return """🌾 **Welcome to AgriGenius!** 🌾

I'm here to help with all your farming questions! I can assist with:

🌱 **Crops:** Wheat, Rice, Corn, Tomatoes, and more
🌍 **Soil:** pH testing, fertility, preparation
🌿 **Fertilizers:** Organic and synthetic options
🐛 **Pest Control:** Natural and chemical solutions  
💧 **Irrigation:** Water management techniques
📅 **Timing:** When to plant and harvest

**Try asking me:**
• "How do I grow tomatoes?"
• "What's the best soil pH for wheat?"
• "How to control pests organically?"
• "When should I plant corn?"

What farming challenge can I help you solve today? 🚜"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    if multi_lang:
        return jsonify({"languages": multi_lang.get_language_options()})
    return jsonify({"languages": [{"code": "en", "name": "English"}]})

@app.route('/greeting', methods=['POST'])
def get_greeting():
    """Get greeting message in specified language"""
    try:
        data = request.get_json()
        language = data.get('language', 'en') if data else 'en'
        
        if multi_lang:
            greeting = multi_lang.get_greeting_message(language)
        else:
            greeting = "🌱🌾 Welcome to AgriGenius !! 🌾🌱 Hi there! I'm AgriGenius, your virtual assistant for Agriculture. How can I assist you today?"
        
        return jsonify({"greeting": greeting})
    except Exception as e:
        logger.error(f"Error getting greeting: {str(e)}")
        return jsonify({"greeting": "Welcome to AgriGenius!"})

@app.route('/ask', methods=['POST'])
def ask():
    try:
        query = request.form['messageText'].strip()
        
        # Detect input language automatically
        detected_language = 'en'
        if multi_lang:
            detected_language = multi_lang.detect_language(query)
            print(f"Detected language: {detected_language}")
        
        # Handle developer questions in multiple languages
        developer_questions = {
            'en': ["who developed you?", "who created you?", "who made you?"],
            'hi': ["आपको किसने बनाया?", "आपका डेवलपर कौन है?", "तुम्हें किसने बनाया है?"],
            'es': ["¿quién te desarrolló?", "¿quién te creó?", "¿quién te hizo?"],
            'fr': ["qui t'a développé?", "qui t'a créé?", "qui t'a fait?"],
            'de': ["wer hat dich entwickelt?", "wer hat dich geschaffen?", "wer hat dich gemacht?"],
            'ar': ["من طورك؟", "من خلقك؟", "من صنعك؟"],
            'bn': ["কে তোমাকে তৈরি করেছে?", "তোমার ডেভেলপার কে?"],
            'ta': ["உன்னை யார் உருவாக்கினார்கள்?", "உன்னை யார் உருவாக்கியது?"],
            'te': ["మిమ్మల్ని ఎవరు అభివృద్ధి చేశారు?", "మిమ్మల్ని ఎవరు సృష్టించారు?"]
        }
        
        # Check if it's a developer question
        is_developer_question = False
        for lang_questions in developer_questions.values():
            if any(q in query.lower() for q in lang_questions):
                is_developer_question = True
                break
        
        if is_developer_question:
            answer = "I was developed by Jayesh Bhandarkar."
            if multi_lang and detected_language != 'en':
                answer = multi_lang.translate_text(answer, detected_language, 'en')
            return jsonify({
                "answer": answer,
                "detectedLanguage": detected_language
            })
        
        # Translate query to English for processing if needed
        english_query = query
        if multi_lang and detected_language != 'en':
            english_query = multi_lang.translate_text(query, 'en', detected_language)
            print(f"Translated query: {english_query}")
        
        if chain is None:
            # Try to get advice from simple knowledge base first
            if agri_knowledge:
                knowledge_answer = agri_knowledge.search_advice(english_query)
                if knowledge_answer:
                    # Translate response back to detected language
                    if multi_lang and detected_language != 'en':
                        knowledge_answer = multi_lang.enhance_agricultural_translation(knowledge_answer, detected_language)
                    return jsonify({
                        "answer": knowledge_answer,
                        "detectedLanguage": detected_language
                    })
            
            # Use smart agriculture response system
            answer = get_smart_agriculture_response(english_query)
            
            # Translate response back to detected language
            if multi_lang and detected_language != 'en':
                answer = multi_lang.enhance_agricultural_translation(answer, detected_language)
            
            return jsonify({
                "answer": answer,
                "detectedLanguage": detected_language
            })
        
        if not english_query:
            answer = "Please enter a question."
            if multi_lang and detected_language != 'en':
                answer = multi_lang.translate_text(answer, detected_language, 'en')
            return jsonify({
                "answer": answer,
                "detectedLanguage": detected_language
            })
        
        # Process the query with the AI model
        response = chain(english_query)
        answer = response['result']
        
        # Translate response back to detected language
        if multi_lang and detected_language != 'en':
            answer = multi_lang.enhance_agricultural_translation(answer, detected_language)
        
        return jsonify({
            "answer": answer,
            "detectedLanguage": detected_language
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        answer = "I apologize, but I'm experiencing technical difficulties. Please try asking your agriculture question again, or consult with local farming experts for immediate assistance."
        
        # Try to detect language and translate error message
        detected_language = 'en'
        if multi_lang and 'messageText' in request.form:
            try:
                detected_language = multi_lang.detect_language(request.form['messageText'])
                if detected_language != 'en':
                    answer = multi_lang.translate_text(answer, detected_language, 'en')
            except:
                pass
            
        return jsonify({
            "answer": answer,
            "detectedLanguage": detected_language
        })

if __name__ == "__main__":
    # Always run the app, even if chain initialization failed
    logger.info("Starting AgriGenius application...")
    print(f"🚀 AgriGenius running in {'AI' if AI_MODE and chain else 'Enhanced Fallback'} mode")
    app.run(debug=True, host='127.0.0.1', port=5000)

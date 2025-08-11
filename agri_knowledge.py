"""
Simple Agricultural Knowledge Base
Provides basic farming advice without requiring AI model
"""

class SimpleAgriKnowledge:
    def __init__(self):
        self.crop_info = {
            'wheat': {
                'planting_season': 'Rabi season (November-December)',
                'harvest_time': '4-6 months after planting',
                'soil_type': 'Well-drained loamy soil with pH 6-7',
                'watering': 'Requires 4-6 irrigations during growth period'
            },
            'rice': {
                'planting_season': 'Kharif season (June-July)',
                'harvest_time': '3-6 months after planting',
                'soil_type': 'Clay or clay loam soil with good water retention',
                'watering': 'Requires continuous standing water in early stages'
            },
            'corn': {
                'planting_season': 'Kharif season (June-July)',
                'harvest_time': '3-4 months after planting',
                'soil_type': 'Well-drained fertile soil with pH 6-6.8',
                'watering': 'Deep watering 1-2 times per week'
            },
            'tomato': {
                'planting_season': 'Year-round with proper care',
                'harvest_time': '2-3 months after transplanting',
                'soil_type': 'Well-drained organic-rich soil with pH 6-6.8',
                'watering': 'Regular watering, avoid overwatering'
            }
        }
        
        self.general_tips = {
            'soil_preparation': [
                'Test soil pH before planting',
                'Add organic compost to improve soil structure',
                'Ensure proper drainage to prevent waterlogging',
                'Till soil to appropriate depth based on crop requirements'
            ],
            'fertilizer_basics': [
                'Use organic fertilizers for long-term soil health',
                'Apply nitrogen for leaf growth, phosphorus for roots, potassium for disease resistance',
                'Follow soil test recommendations for fertilizer amounts',
                'Apply fertilizers at the right growth stages'
            ],
            'pest_management': [
                'Use integrated pest management (IPM) approach',
                'Identify pests correctly before treatment',
                'Encourage beneficial insects in your garden',
                'Rotate crops to break pest cycles'
            ],
            'water_management': [
                'Water early morning or evening to reduce evaporation',
                'Use drip irrigation or soaker hoses for efficiency',
                'Mulch around plants to retain moisture',
                'Check soil moisture before watering'
            ]
        }
        
        self.market_resources = {
            'government_sites': [
                'eNAM (National Agriculture Market): enam.gov.in',
                'Agmarknet: agmarknet.gov.in', 
                'Ministry of Agriculture: agricoop.gov.in',
                'National Sample Survey Office: mospi.gov.in'
            ],
            'mobile_apps': [
                'eNAM App - Official government app',
                'Kisan Suvidha App - Weather, market prices, advisories',
                'AgriApp - Market prices and farming tips',
                'Crop Insurance App - Prices and insurance info'
            ],
            'exchanges': [
                'MCX (Multi Commodity Exchange)',
                'NCDEX (National Commodity & Derivatives Exchange)',
                'Local commodity exchanges'
            ]
        }

    def get_crop_advice(self, crop_name):
        """Get basic advice for a specific crop"""
        crop_name = crop_name.lower().strip()
        if crop_name in self.crop_info:
            info = self.crop_info[crop_name]
            advice = f"For {crop_name.capitalize()}:\n"
            advice += f"• Planting: {info['planting_season']}\n"
            advice += f"• Harvest: {info['harvest_time']}\n"
            advice += f"• Soil: {info['soil_type']}\n"
            advice += f"• Water: {info['watering']}"
            return advice
        return None

    def get_general_advice(self, topic):
        """Get general farming advice"""
        topic = topic.lower().strip()
        
        # Find matching topic
        for key, tips in self.general_tips.items():
            if topic in key or any(word in topic for word in key.split('_')):
                advice = f"Here are some tips for {key.replace('_', ' ')}:\n"
                for i, tip in enumerate(tips, 1):
                    advice += f"{i}. {tip}\n"
                return advice.strip()
        return None

    def search_advice(self, query):
        """Search for relevant advice based on query"""
        query = query.lower()
        
        # First check if this is a price/market query
        price_keywords = ['price', 'cost', 'rate', 'market', 'sell', 'buy', 'मूल्य', 'कीमत', 'दर', 'बाज़ार']
        if any(keyword in query for keyword in price_keywords):
            # Try to get real-time price data
            try:
                from market_api import get_market_price_response
                
                # Extract crop name from query if present
                mentioned_crop = None
                for crop in self.crop_info.keys():
                    if crop in query:
                        mentioned_crop = crop
                        break
                
                if mentioned_crop:
                    # Get live price data
                    return get_market_price_response(mentioned_crop)
                else:
                    # General price query without specific crop
                    return get_market_price_response("wheat")  # Default to wheat
                    
            except ImportError:
                # Fallback to static response if API module not available
                pass
            
            # Fallback static response
            mentioned_crop = None
            for crop in self.crop_info.keys():
                if crop in query:
                    mentioned_crop = crop.capitalize()
                    break
            
            crop_text = f" for {mentioned_crop}" if mentioned_crop else ""
            
            response = f"💰 **Current Market Prices{crop_text}:**\n\n"
            response += "I don't have access to real-time market prices as they change daily. Here are the best sources for current prices:\n\n"
            
            response += "🏪 **Government Resources:**\n"
            for site in self.market_resources['government_sites']:
                response += f"• {site}\n"
            
            response += "\n📱 **Mobile Apps:**\n"  
            for app in self.market_resources['mobile_apps']:
                response += f"• {app}\n"
                
            response += "\n📈 **Commodity Exchanges:**\n"
            for exchange in self.market_resources['exchanges']:
                response += f"• {exchange}\n"
                
            response += "\n💡 **Quick Tips:**\n"
            response += "• Prices vary by location, quality, and season\n"
            response += "• Check multiple sources for best rates\n"
            response += "• Consider local mandi prices vs online rates\n"
            response += "• Factor in transportation costs\n"
            
            if mentioned_crop:
                response += f"\nWould you like farming advice for {mentioned_crop.lower()} instead?"
                
            return response
        
        # Check for specific crops (but not if it's a price query)
        for crop in self.crop_info.keys():
            if crop in query:
                return self.get_crop_advice(crop)
        
        # Check for general topics
        for topic in self.general_tips.keys():
            if any(word in query for word in topic.split('_')):
                return self.get_general_advice(topic)
        
        # Check for common farming terms
        if any(term in query for term in ['plant', 'grow', 'farm', 'खेती', 'फसल', 'किसान']):
            return "For successful farming: Choose the right crops for your climate, prepare soil properly, maintain proper spacing, provide adequate water and nutrients, and monitor for pests and diseases regularly."
        
        if any(term in query for term in ['season', 'when', 'time', 'मौसम', 'कब', 'समय']):
            return "Planting seasons vary by crop and location. Kharif crops (rice, corn) are planted in monsoon (June-July). Rabi crops (wheat, peas) are planted in winter (November-December). Check local agricultural extension services for specific timing in your area."
        
        if any(term in query for term in ['soil', 'मिट्टी', 'भूमि']):
            return "Soil health is crucial for farming. Test soil pH (should be 6-7 for most crops), add organic compost, ensure proper drainage, and avoid overuse of chemical fertilizers. Different crops need different soil types."
        
        if any(term in query for term in ['water', 'irrigation', 'पानी', 'सिंचाई']):
            return "Water management tips: Water early morning or evening, use drip irrigation for efficiency, check soil moisture before watering, and mulch around plants to retain moisture."
        
        if any(term in query for term in ['fertilizer', 'खाद', 'उर्वरक']):
            return "Fertilizer guidance: Use organic fertilizers for long-term soil health, apply NPK (Nitrogen-Phosphorus-Potassium) based on crop needs, follow soil test recommendations, and don't over-fertilize."
        
        return None

# Initialize the knowledge base
agri_knowledge = SimpleAgriKnowledge()

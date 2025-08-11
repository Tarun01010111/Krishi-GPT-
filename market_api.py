"""
Market Price API Integration Module
Fetches real-time crop prices from various sources
"""

import requests
import json
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class MarketPriceAPI:
    def __init__(self):
        self.apis = {
            'agmarknet': 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070',
            'enam': 'https://enam.gov.in/web/resources/market-data',  # Example URL
            'commodity_api': 'https://commodities-api.com/api/latest'  # Example commodity API
        }
        
    def get_agmarknet_prices(self, commodity="Wheat", market="Delhi", limit=10):
        """
        Fetch prices from AgMarkNet API (Government of India)
        """
        try:
            url = self.apis['agmarknet']
            params = {
                'api-key': 'YOUR_API_KEY',  # You need to get this from data.gov.in
                'format': 'json',
                'limit': limit,
                'filters[commodity]': commodity,
                'filters[market]': market
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_agmarknet_data(data)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching AgMarkNet data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing AgMarkNet data: {e}")
            return None
    
    def get_commodity_prices(self, symbols=['WHEAT', 'RICE', 'CORN']):
        """
        Fetch prices from commodity price API
        """
        try:
            # Example using a hypothetical commodity API
            # You would need to sign up for a real API key
            url = "https://api.marketstack.com/v1/eod"  # Example API
            params = {
                'access_key': 'YOUR_API_KEY',
                'symbols': ','.join(symbols),
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching commodity prices: {e}")
            return None
    
    def get_mock_prices(self, crop_name="wheat"):
        """
        Mock API response for demonstration (since we don't have real API keys)
        """
        mock_data = {
            'wheat': {
                'commodity': 'Wheat',
                'market': 'Delhi',
                'price': '₹2,150 per quintal',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'up',
                'change': '+50',
                'min_price': '₹2,100',
                'max_price': '₹2,200',
                'quality': 'FAQ (Fair Average Quality)'
            },
            'rice': {
                'commodity': 'Rice',
                'market': 'Delhi', 
                'price': '₹3,200 per quintal',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'down',
                'change': '-75',
                'min_price': '₹3,150',
                'max_price': '₹3,250',
                'quality': 'Grade A'
            },
            'corn': {
                'commodity': 'Corn/Maize',
                'market': 'Delhi',
                'price': '₹1,850 per quintal',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trend': 'stable',
                'change': '0',
                'min_price': '₹1,800',
                'max_price': '₹1,900',
                'quality': 'Yellow Maize'
            }
        }
        
        crop_name = crop_name.lower().strip()
        return mock_data.get(crop_name, mock_data['wheat'])
    
    def _format_agmarknet_data(self, data):
        """Format AgMarkNet API response"""
        try:
            if 'records' in data and data['records']:
                record = data['records'][0]
                return {
                    'commodity': record.get('commodity', 'Unknown'),
                    'market': record.get('market', 'Unknown'),
                    'price': record.get('modal_price', 'N/A'),
                    'date': record.get('arrival_date', 'N/A'),
                    'min_price': record.get('min_price', 'N/A'),
                    'max_price': record.get('max_price', 'N/A')
                }
        except Exception as e:
            logger.error(f"Error formatting data: {e}")
            return None
    
    def get_price_info(self, crop_name, market="Delhi", use_mock=True):
        """
        Main function to get price information
        """
        if use_mock:
            # Use mock data for demonstration
            return self.get_mock_prices(crop_name)
        else:
            # Try real APIs (when you have API keys)
            price_data = self.get_agmarknet_prices(crop_name, market)
            if not price_data:
                price_data = self.get_commodity_prices([crop_name.upper()])
            return price_data

# Create instance
market_api = MarketPriceAPI()

def get_market_price_response(crop_name, market="Delhi"):
    """
    Get formatted market price response for chatbot
    """
    try:
        price_data = market_api.get_price_info(crop_name, market)
        
        if not price_data:
            return f"Sorry, I couldn't fetch current prices for {crop_name}. Please try again later or check the government websites manually."
        
        trend_emoji = {"up": "📈", "down": "📉", "stable": "➡️"}.get(price_data.get('trend', 'stable'), "➡️")
        
        response = f"💰 **Current Market Price for {price_data['commodity']}:**\n\n"
        response += f"🏪 **Market:** {price_data['market']}\n"
        response += f"💵 **Current Price:** {price_data['price']}\n"
        response += f"📅 **Date:** {price_data['date']}\n"
        response += f"📊 **Trend:** {trend_emoji} {price_data['change']}\n"
        response += f"🔻 **Min Price:** {price_data['min_price']}\n"
        response += f"🔺 **Max Price:** {price_data['max_price']}\n"
        response += f"⭐ **Quality:** {price_data['quality']}\n\n"
        
        response += "📝 **Note:** Prices are indicative and may vary by location and quality.\n"
        response += "For local rates, check your nearest mandi or agricultural market.\n\n"
        response += "Need help with farming this crop? Just ask! 🌾"
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating price response: {e}")
        return "Sorry, I'm having trouble fetching price information right now. Please try again later."

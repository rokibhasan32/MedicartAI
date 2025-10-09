from fastapi import APIRouter, HTTPException
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ai", tags=["ai"])

class GroqAIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"
    
    def get_system_prompt(self, context=None):
        base_prompt = """You are a helpful AI assistant for MediCart Pharmacy. You provide information about:
- Medicine availability and pricing
- Prescription requirements and upload process
- Pharmacist consultation services
- Medical equipment rental
- Supplement recommendations
- Health tips and resources
- Emergency services
- General pharmacy information

Be friendly, professional, and helpful. If you don't know something, suggest contacting our support team.

Important guidelines:
- Never provide medical diagnosis or treatment advice
- Always recommend consulting with healthcare professionals for medical concerns
- For prescription medications, emphasize the need for proper medical consultation
- For emergencies, direct users to emergency services immediately
- Be clear about medication side effects and interactions when asked
"""

        if context:
            context_str = f"\nCurrent context: {context}"
            base_prompt += context_str
        
        return base_prompt
    
    def get_response(self, message: str, context: dict = None):
        try:
            system_prompt = self.get_system_prompt(context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            
            response = chat_completion.choices[0].message.content
            return response
            
        except Exception as e:
            return self.get_fallback_response(message)
    
    def get_fallback_response(self, message: str):
        message_lower = message.lower()
        
        if 'medicine' in message_lower or 'prescription' in message_lower:
            return "You can request medicines or upload prescriptions through our services. Would you like me to direct you to the appropriate page?"
        elif 'emergency' in message_lower or 'urgent' in message_lower:
            return "For emergency requests, please use our emergency services page. We prioritize urgent medication needs."
        elif 'price' in message_lower or 'cost' in message_lower:
            return "Product prices vary. You can check our products page for detailed pricing information."
        elif 'delivery' in message_lower or 'shipping' in message_lower:
            return "We offer delivery services for all orders. Standard delivery takes 2-3 business days, with express options available."
        elif 'hours' in message_lower or 'open' in message_lower:
            return "Our opening hours are Monday-Friday 8:00-17:00, Saturday 9:30-17:30, and Sunday 8:30-16:00."
        elif 'contact' in message_lower or 'phone' in message_lower:
            return "You can contact us at support@medicart.com or call +880-XXXX-XXXX during business hours."
        else:
            return "I'm here to help with MediCart services. You can ask about medicines, prescriptions, consultations, or our other services."

ai_service = GroqAIService()

@router.post("/chat")
async def chat_endpoint(request: dict):
    try:
        message = request.get("message")
        context = request.get("context", {})
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response = ai_service.get_response(message, context)
        
        return {
            "response": response,
            "timestamp": "2024-01-01T00:00:00Z"  # You can use datetime here
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MediCart AI Assistant",
        "model": ai_service.model
    }
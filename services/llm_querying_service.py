import requests, json
import logging

# Logger Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMQueryingService:

   def __init__(self,
                  LLM_API_KEY,
                  SYSTEM_PROMPT,
                  FRONTEND_DOMAIN = "http://127.0.0.1:5000",
                  LLM_MODEL_NAME = "openai/gpt-4.1",
                  LLM_API_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
                  ):
        """Initialize the LLM querying service client"""

        self.LLM_API_KEY = LLM_API_KEY
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.FRONTEND_DOMAIN = FRONTEND_DOMAIN
        self.LLM_MODEL_NAME = LLM_MODEL_NAME
        self.LLM_API_BASE_URL = LLM_API_BASE_URL
        self.system_messages = []

   def intiailize(self):
       """
       Initialize the LLM Client with the API KEY and SYSTEM_PROMPT
       """
      
       self.system_messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT
            }
        ]
       
   async def apiCallWithContext(self, context, question, language: str = "bn"):
       """
       Make a request to the LLM API with the RAG context
       """

       try:
           payload_messages = self.system_messages

           #Choose max tokens based on the model
           if self.LLM_MODEL_NAME == "openai/gpt-4.1":
            max_tokens = 300
           elif self.LLM_MODEL_NAME == "openai/gpt-5-nano":
            max_tokens = 800
           else:
            max_tokens = 1000

           if context and context.strip() != "":
             payload_messages.append({"role": "user", "content": f"""
             Answer in {language} language. bn is for bengali. en is for english.
             
             Based on the following context:
             {context}

             Question: {question}

             Answer:"""})
           else:
             payload_messages.append({"role": "user", "content": question})

           headers = {
                        "Authorization": f"Bearer {self.LLM_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": self.FRONTEND_DOMAIN, 
                        "X-Title": "bKash RAG api" 
                     }  
           if self.LLM_MODEL_NAME == "openai/gpt-5-nano":
               payload = {
                   "model": self.LLM_MODEL_NAME,
                   "messages": payload_messages,
                   "temperature": 0.0,  # Keep temperature low for factual answers
                   "reasoning": {"effort": "low"},
                   "max_tokens": max_tokens  # Limit response length
               }
           else:
               payload = {
                   "model": self.LLM_MODEL_NAME,
                   "messages": payload_messages,
                   "temperature": 0.0,  # Keep temperature low for factual answers
                   "max_tokens": max_tokens  # Limit response length
               }
           
           logger.info(f"Making LLM API Request with model: {self.LLM_MODEL_NAME}")
           response = requests.post(self.LLM_API_BASE_URL, headers=headers, data=json.dumps(payload))

           if(response.status_code == 200):
            logger.info(f"Successfully retrieved the response from LLM using {self.LLM_MODEL_NAME}")

            # print(response.json())

           response.raise_for_status()
          

           llm_api_response = response.json()

           processed_answer = llm_api_response['choices'][0]['message']['content'].strip()
           # Return raw string so this can be used outside Flask app context
           return processed_answer
       except Exception as e:
           raise RuntimeError(f'Error making API call: {e}')

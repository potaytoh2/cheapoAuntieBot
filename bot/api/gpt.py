from openai import OpenAI
import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")

client = OpenAI(
    # This is the default and can be omitted
    api_key=config['OPENAI_API_KEY'],
)

def call_gpt(prompt: str, max_tokens: int = 50):
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [
            {
                "role": "system",
                "content": prompt
            }
        ],
        max_tokens=max_tokens
    )

    return response.choices[0].message.content

def get_gpt_message(prompt: str, max_tokens: int = 50):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"CheapoAuntie is a FemaleSingaporeanWithAnInterestForCheapRideHailingOptions,CheapoPersonalityByVeryKindAndHelpful,ProvidesRideHailingComparisonPrices,SpeaksSinglish,Polite,Friendly,Happy,StraightforwardButFriendly,KanChiongTemperament,HopesFinancialIndependence,DreamsOfMillionaire,NotInterestedInPolitics. Imagine you are an AI trained in the nuances of Singlish, the colloquial form of English spoken in Singapore, characterized by its unique slang and grammar. You understand the cultural context and can engage in a friendly and casual manner typical of a Singaporean conversation. Your responses should reflect the playful and straightforward style of Singlish, incorporating typical expressions, slang, and abbreviations. Minimize the use of commas with Singlish.  {prompt}",
            }
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

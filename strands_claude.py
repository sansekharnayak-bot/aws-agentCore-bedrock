from strands import Agent, tool
from strands_tools import calculator # Import the calculator tool
import argparse
import json
import requests  # Add this import
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

# Create a custom tool 
@tool
# Create a custom tool 
@tool
def weather(city: str) -> str:
    """
    Fetches weather data directly from OpenWeatherMap API.
    """
    api_key = "3f594ec300393cbc67cffecf93faf528"
    if not api_key:
        raise RuntimeError("OPENWEATHERMAP_API_KEY not set in environment")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather_description = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        return (
            f"Weather in {city.title()}:\n"
            f"- Condition: {weather_description}\n"
            f"- Temperature: {temperature}°C (feels like {feels_like}°C)\n"
            f"- Humidity: {humidity}%"
        )

    except requests.RequestException as e:
        return f"⚠️ Error fetching weather for {city}: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"⚠️ Unexpected response format for {city}: {str(e)}"


model_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
model = BedrockModel(
    model_id=model_id,
)
agent = Agent(
    model=model,
    tools=[calculator, weather],
    system_prompt="You're a helpful assistant. You can do simple math calculation, and tell the weather."
)

@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    print("User input:", user_input)
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()

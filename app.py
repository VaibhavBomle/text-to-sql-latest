import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

import chainlit as cl

cl.instrument_openai()

OPNEAI_API_KEY =   os.getenv("OPENAI_API_KEY")
print("OPNEAI_API_KEY : ",OPNEAI_API_KEY)
global client
try:
    client = AsyncOpenAI(api_key=OPNEAI_API_KEY)
except Exception as e:
    raise Exception("Open AI client refused to connect")


# Prompt
template = """STUDENT SQL tables of 5 columns (and columns):
* name,id,address,created_on,created_by

A well-written SQL query that {input}:
```"""

# Creating settings

settings = {
    "model" : "gpt-3.5-turbo",
    "temperature" : 0,
     "max_tokens": 500,
     "top_p" : 1,
     "frequency_penalty" : 0,
     "presence_penalty" : 0,
     "stop": ["```"],
}

# On start of chainlit this message show on chat window
@cl.set_starters
async def starters():
    return [
        cl.Starter(
            label= "Text to SQL",
            message="Write text to make a SQL Query"
        )
    ]

@cl.on_message
async def main(message: cl.Message):
    stream =await client.chat.completions.create(
        messages=[
            {
            "role":"user",
            "content":template.format(input=message.content),
            }
        ],
        stream=True, 
        **settings,
        timeout=60  # Increase this value as needed
    )

    msg = await cl.Message(content="", language="sql").send()

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
    
    await msg.update()
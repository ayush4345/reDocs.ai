import openai
from concurrent.futures import ThreadPoolExecutor
import tiktoken
from dotenv import load_dotenv
import os
import json
import backoff # for exponential backoff

load_dotenv()

os.environ['OPENAI_API'] = os.getenv('OPEN_AI_API')
# Add your own OpenAI API key
openai.api_key = os.environ['OPENAI_API']

def load_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def save_to_file(responses, output_file):
    with open(output_file, 'w') as file:
        for response in responses:
            file.write(response + '\n')

def split_into_chunks(text, tokens=500):
    encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
    words = encoding.encode(text)
    chunks = []
    for i in range(0, len(words), tokens):
        chunks.append(' '.join(encoding.decode(words[i:i + tokens])))
    return chunks

def process_chunks(text, output_file, system_prompt, user_prompt):
    # text = load_text(input_file)
    chunks = split_into_chunks(text)

    # Processes chunks in parallel
    with ThreadPoolExecutor() as executor:
        responses = list(executor.map(lambda chunk: call_openai_api(chunk, system_prompt, user_prompt), chunks))

    save_to_file(responses, output_file)

# Change your OpenAI chat model accordingly, and this is the main function that calls the OpenAI API
@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def call_openai_api(chunk, system_prompt, user_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\n: {chunk}."}
        ],
        max_tokens=5000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0]['message']['content'].strip()


# A function to test out the overall workflow of the app
# Incase you wanna disable this and use the actual GPT-3.5 API, set SHOULD_MOCK_AI_RESPONSE to False

def mock_chunks_gpt(text, output_file):

    response = text
    
    save_to_file(response, output_file)

def ask_gpt_to_generate_tests(prompt_text, output_folder):
    # prompt_text = load_text(file_path)
    # process_chunks(prompt_text, output_file)
    system_prompt = """You are a smart technical writer who understands code and can write documentation for it."""

    user_prompt = """Give me a developers documentation of the following code. Give a brief intro, table of contents, function explanations, dependencies, API specs (if present), schema tables in markdown. Give in markdown format and try to strict to the headings"""
    
    output_file = f'{output_folder}/output.md'
    mock_chunks_gpt(prompt_text, output_file)
    # call_openai_api(prompt_text, system_prompt, user_prompt)




# -----DEPRECATED CODE-----

# @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def call_openai_api_higher_tokens(text, output_file):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a smart technical writer who understands code and can write documentation for it."},
            {"role": "user", "content": f"Give me a developers documentation of the following code. Give a brief intro, table of contents, function explanations, dependencies, API specs (if present), schema tables in markdown. Give in markdown format and try to strict to the headings\n\n: {text}."},
        ],
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    save_to_file(response, output_file)
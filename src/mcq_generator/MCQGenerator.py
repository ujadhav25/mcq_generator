import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableMap, RunnableLambda

# Load environment variables
load_dotenv()
key = os.getenv("GEMINI_API_KEY")

# --- PROMPTS ---
quiz_prompt_template = """
    Text: {text}

    You are an expert MCQ maker. Given the above text, it is your job to \
    create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
    Make sure the questions are not repeated and check all the questions to conform to the text. \
    Format your response like the RESPONSE_JSON below and use it as a guide. \
    Ensure to make {number} MCQs.

    ### RESPONSE_JSON
    {response_json}
"""

review_prompt_template = """
    You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,\
    evaluate the complexity of the questions and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
    If the quiz is not at par with the cognitive and analytical abilities of the students,\
    update the quiz questions which need to be changed and change the tone so that it perfectly fits the students' abilities.

    Quiz_MCQs:
    {quiz}

    Check from an expert English Writer of the above quiz:
"""

quiz_prompt = PromptTemplate.from_template(quiz_prompt_template)
review_prompt = PromptTemplate.from_template(review_prompt_template)

# --- LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=key
)

# Step 1: Generate Quiz
quiz_chain = quiz_prompt | llm

# Step 2: Generate Review (uses quiz output)
review_chain = (
    RunnableLambda(lambda d: {
        "quiz": d["quiz"],
        "subject": d["subject"]
    }) 
    | review_prompt
    | llm
)

# Combined pipeline
generate_evaluate_chain = (
    RunnableMap({
        "quiz": quiz_chain,
        "subject": lambda d: d["subject"]
    })
    | RunnableMap({
        "quiz": lambda d: d["quiz"],
        "review": review_chain
    })
)

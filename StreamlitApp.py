import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcq_generator.utils import read_file, get_table_data
import streamlit as st
from src.mcq_generator.MCQGenerator import generate_evaluate_chain
from src.mcq_generator.logger import logging

#loading response json file
with open('response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

#creating a title for the app
st.title("MCQs Creator Application with LangChain 🦜⛓️")

#Create a form using st.form
with st.form("user_inputs"):
    # file upload
    uploaded_file = st.file_uploader("Upload a PDF ot txt file")

    #Input Fields
    mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)

    #Subject
    subject = st.text_input("Insert Subject", max_chars=20)

    # Quiz Tone
    tone = st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                response = generate_evaluate_chain.invoke({
                    "text": text,
                    "number": mcq_count,
                    "subject":subject,
                    "tone": tone,
                    "response_json": json.dumps(RESPONSE_JSON)
                })

           
                quiz_input_tokens = response['quiz'].usage_metadata['input_tokens']
                quiz_output_tokens = response['quiz'].usage_metadata['output_tokens']
                quiz_total_tokens = response['quiz'].usage_metadata['total_tokens']
                
                quiz_review_input_tokens = response['review'].usage_metadata['input_tokens']
                quiz_review_output_tokens = response['review'].usage_metadata['output_tokens']
                quiz_review_total_tokens = response['review'].usage_metadata['total_tokens']

                quiz = response['quiz'].content.strip().removeprefix("```json").removesuffix("```").strip()

                before_json, json_string = (response['review'].content.split("json")[0].strip().replace("```", ""), response['review'].content.split("json")[1].split("```")[0].strip())

                st.markdown(f"""
                        <ul>
                        <li><b>Quiz</b>
                            <ul>
                            <li>input_tokens: {quiz_input_tokens}</li>
                            <li>output_tokens: {quiz_output_tokens} </li>
                            <li>total_tokens: {quiz_total_tokens}</li>
                            </ul>
                        </li>
                        <li><b>Review Quiz</b>
                            <ul>
                            <li>input_tokens: {quiz_review_input_tokens}</li>
                            <li>output_tokens: {quiz_review_output_tokens} </li>
                            <li>total_tokens: {quiz_review_total_tokens}</li>
                            </ul>
                        </li>
                        </ul>
                        """, 
                    unsafe_allow_html=True
                )

                if quiz is not None:
                    table_data=get_table_data(quiz)
                    if table_data is not None:
                        df=pd.DataFrame(table_data)
                        df.index=df.index+1
                        st.table(df)
                        #Display the review in atext box as well
                        st.text_area(label="Review", value=before_json)
                    else:
                        st.error("Error in the table data")
                        table_data=get_table_data(quiz)

                    table_data=get_table_data(json_string)
                    if json_string is not None:
                        df=pd.DataFrame(table_data)
                        df.index=df.index+1
                        st.table(df)
                    else:
                        st.error("Error in the table data")

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

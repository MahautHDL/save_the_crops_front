import streamlit as st
from streamlit_chat import message
import os # needed for the file paths
import pandas as pd
import requests
import base64
from requests_toolbelt.multipart.encoder import MultipartEncoder
import openai

st.set_page_config(page_title = "Save The Crops",
                   page_icon="🌱",
                   layout = "centered",
                   initial_sidebar_state = "expanded")

# Secrets variables
api_url = os.environ["API_URL"]
openai.api_key = st.secrets["API_OPENAI"]


# construct the relative path of the backgroun image
base_dir = os.path.dirname(os.path.realpath(__file__))
img_path = os.path.join(base_dir, "media", "field.jpg")

def set_bg_image(main_bg):
    '''
    A function to unpack an image from root folder and set as bg.

    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg_ext = "png"

    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}

         </style>
         """,
         unsafe_allow_html=True
     )
set_bg_image(img_path)

def send_image_to_api(image_data, api_url=api_url):
    try:
        multipart_data = MultipartEncoder(
            fields={
                "file": (image_data.name, image_data, "image/jpeg"),
                "plant": selected_species
            }
        )
        headers = {"Content-Type": multipart_data.content_type}

        response = requests.post(api_url, headers=headers, data=multipart_data)
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while sending the image: {e}")
        return None

def api_calling(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message

# This is providing a shaded background so there is more contrast on the buttons and text fields
css_body_container = f'''
<style>
    section [data-testid="stAppViewBlockContainer"] {{background-color:rgba(0, 66, 37, 0.6); padding: 0}}
</style>
'''

st.markdown(css_body_container,unsafe_allow_html=True)

# Create the container
container = st.container(height=1000)

with container:
    st.markdown("<h1 style='text-align: center; font-size: 96px; font-family: Playfair Display;'>Save the Crops.</h1>", unsafe_allow_html=True)

    st.markdown('<p style="text-align: center; font-size: 32px;">What plant are you uploading?</p>', unsafe_allow_html=True)

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;font-size: 24px;}</style>', unsafe_allow_html=True)
    options = st.radio(' ', ('Cashew', 'Cassava', 'Maize', 'Tomato'))

    st.markdown('<p style="text-align: center; font-size: 32px;">Choose an image</p>', unsafe_allow_html=True)

    uploaded_image = st.file_uploader("", type=["jpg", "jpeg", "png"])


    if uploaded_image is not None:
        if not options:  # Check if a specie has been selected
            st.error("Select a species before we can help you out")
        else:
            selected_species = options.lower()  # Get the selected species
        if True:  # replace with the actual condition to check response
            response = send_image_to_api(uploaded_image, api_url)
            if response:
                if response["disease"] == "healthy":
                    text_color = "#071007"
                    message = "Grab a beer, your plants are fine!"
                else:
                    text_color = "#FF2020"
                    message = f"Disease : {response['disease']}"
                    #st.subheader(f"{(response['disease'].capitalize())}")

                st.markdown(f'<p style="text-align: center; color: {text_color}; background-color:white; border-radius: 0.5rem; opacity:60%; font-size: 32px;">{message.capitalize()}</p>', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([0.2, 0.6, 0.2])

                with col1:
                    st.write(' ')

                with col2:
                    st.image(uploaded_image, width=400)

                with col3:
                    st.write(' ')

import os
import json
import requests
from facebook import GraphAPI
import streamlit as st

def generate_facebook_login_url():
    app_id = os.environ['FACEBOOK_APP_ID']
    app_secret = os.environ['FACEBOOK_APP_SECRET']
    redirect_uri = 'https://your_redirect_url'  # Replace with your redirect URL

    # Set the required permissions
    scope = 'email,user_posts'

    login_url = f"https://www.facebook.com/v12.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code"

    return login_url

def main():
    st.title("Facebook Streamlit App")

    st.write("Click the link below to log in with your Facebook account:")
    login_url = generate_facebook_login_url()
    st.write(f"[Login with Facebook]({login_url})")

    st.write("Enter the access token you received after logging in:")
    access_token = st.text_input("Access Token")

    if access_token:
        graph = GraphAPI(access_token)

        try:
            user_info = graph.get_object('me', fields='id,name,email')
            st.write("User Information:")
            st.json(user_info)

            user_posts = graph.get_connections('me', 'posts', fields='id,created_time,message,story', limit=10)
            st.write("User Posts (10 latest):")
            st.json(user_posts)

        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

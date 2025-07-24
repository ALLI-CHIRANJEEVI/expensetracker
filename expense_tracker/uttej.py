import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml

# Configuration for authentication
config = {
    'credentials': {
        'usernames': {
            'user1': {
                'name': 'User One',
                'password': stauth.Hasher(['password1']).generate()[0]  # Replace 'password1' with the actual password
            },
            'user2': {
                'name': 'User Two',
                'password': stauth.Hasher(['password2']).generate()[0]  # Replace 'password2' with the actual password
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'some_signature_key',
        'name': 'some_cookie_name'
    },
    'preauthorized': {
        'emails': []
    }
}

# Save configuration to a file (this is just for demonstration; in practice, you might load this from a secure source)
with open('config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

# Load configuration from file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

# Create an authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Authenticate the user
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Display the main app content only if the user is authenticated
    st.title("Song Recommender")

    data = {
        "Title/URL": ["Shape of You https://www.youtube.com/watch?v=JGwWNGJdvx8", "Bohemian Rhapsody https://www.youtube.com/watch?v=fJ9rUzIMcZQ", "Despacito https://www.youtube.com/watch?v=kJQP7kiw5Fk", "Closer https://www.youtube.com/watch?v=PT2_F-1esPk", 
                     "Old Town Road https://www.youtube.com/watch?v=w2Ov5jzm3j8", "Uptown Funk https://www.youtube.com/watch?v=OPf0YbXqDm0", "Butta Bomma https://www.youtube.com/watch?v=hD4vc_FsRbI", "Samajavaragamana https://www.youtube.com/watch?v=xz8a0QnBmZo",
                     "Inkem Inkem Inkem Kaavaale https://www.youtube.com/watch?v=qE6TTs6y7Vo", "Vachinde https://www.youtube.com/watch?v=7t2OMHhYtFQ", "Neeli Neeli Aakasam https://www.youtube.com/watch?v=_dKUxI0U6Z8", "Ninnila https://www.youtube.com/watch?v=zBXeQbLk20s"],
        "Genre": ["Pop", "Rock", "Latin", "Electronic", "Country", "Funk", "Telugu", 
                  "Telugu", "Telugu", "Telugu", "Telugu", "Telugu"]
    }

    df = pd.DataFrame(data)

    # User Input for Genre Selection
    selected_genre = st.selectbox("Select a Genre", df["Genre"].unique())

    # Filter Songs based on Genre
    filtered_df = df.loc[df["Genre"] == selected_genre]

    # Display Songs
    if filtered_df.empty:
        st.write("No songs found for this genre.")
    else:
        for index, row in filtered_df.iterrows():
            title_url = row["Title/URL"]
            if title_url.startswith("http"):  # Display Youtube Link
                st.write(f"- [{row['Title/URL']}]({row['Title/URL']})")
            else:
                st.write(f"- {row['Title/URL']}")
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

# Logout button
authenticator.logout('Logout', 'sidebar')

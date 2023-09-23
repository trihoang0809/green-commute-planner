import streamlit as st

# Create a select box with some options
selected_option = st.selectbox("Select an option", ["Option 1", "Option 2", "Option 3"])

# Display the selected option
st.write("You selected:", selected_option)

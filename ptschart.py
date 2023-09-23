import plotly.express as px
import streamlit as st


def plot_user_points(days_of_week, user_points):
    # Create a line plot using Plotly Express
    fig = px.line(x=days_of_week, y=user_points, markers=True)
    fig.update_layout(title='Points for each day of the week',
                      xaxis_title='Day of the Week', yaxis_title='Points')

    # Display the plot using Streamlit
    st.plotly_chart(fig)


# Sample data
# days_of_week = ['Monday', 'Tuesday', 'Wednesday',
#                'Thursday', 'Friday', 'Saturday', 'Sunday']
#user_points = [10, 15, 20, 18, 22, 17, 14]

# Call the function to plot the chart
#plot_user_points(days_of_week, user_points)

# PhonePe Pulse Data Visualization and Exploration

This project focuses on extracting, transforming, and visualizing data from the PhonePe Pulse GitHub repository. The goal is to provide insights and information in a user-friendly manner through an interactive dashboard.

## Problem Statement

The PhonePe pulse Github repository contains a large amount of data related to various metrics and statistics. The goal is to extract this data and process it to obtain insights and information that can be visualized in a user-friendly manner.

## Approach

1. **Data Extraction**: Clone the GitHub repository using scripting to fetch the data and store it in a suitable format such as CSV or JSON.
2. **Data Transformation**: Use Python and libraries like Pandas to manipulate and preprocess the data, including cleaning and handling missing values.
3. **Database Insertion**: Utilize the "mysql-connector-python" library to connect to a MySQL database and insert the transformed data using SQL commands.
4. **Dashboard Creation**: Create an interactive dashboard using Streamlit and Plotly libraries in Python. Utilize Plotly's geo-map functions to display data on a map and Streamlit to create a user-friendly interface with dropdown options.
5. **Data Retrieval**: Connect to the MySQL database using the "mysql-connector-python" library to fetch data into a Pandas dataframe, updating the dashboard dynamically.
6. **Deployment**: Ensure the solution is secure, efficient, and user-friendly. Test thoroughly and deploy the dashboard publicly, making it accessible to users.

## Results

The result of this project will be a live geo-visualization dashboard displaying information and insights from the PhonePe Pulse GitHub repository. The dashboard will have at least 10 different dropdown options for users to select various facts and figures to display. The data will be stored in a MySQL database for efficient retrieval, and the dashboard will dynamically update to reflect the latest data.

## Dataset

Dataset Link: [Data Link](https://github.com/PhonePe/pulse#readme)
Inspired From: PhonePe Pulse

## Learning Outcomes

1. Data extraction and processing: Extract data from a repository and preprocess it using Python libraries such as Pandas.
2. Database management: Learn how to use a relational database like MySQL to store and retrieve data efficiently.
3. Visualization and dashboard creation: Utilize libraries like Streamlit and Plotly to create interactive and visually appealing dashboards.
4. Geo visualization: Learn how to create and display data on a map using Plotly's geo map functions.
5. Dynamic updating: Develop a dashboard that dynamically updates based on the latest data in a database.
6. Project development and deployment: Learn how to develop a comprehensive and user-friendly solution, from data extraction to dashboard deployment, ensuring it is secure, efficient, and user-friendly.

By completing this project, you will gain hands-on experience in data extraction, processing, and visualization, as well as working with databases, dashboards, and web development. This project will provide a foundation for further learning and development in these areas, helping you build a portfolio of practical skills.

import json
from PIL import Image
import streamlit as st
import pandas as pd
import mysql.connector as sql
import plotly.express as px
from streamlit_option_menu import option_menu


my_db = sql.connect( 
             host="127.0.0.1",
             user="root",
             database ='Phonepe_db',
             port = 3306,
             password="2369",
              ) 
      
mycursor = my_db.cursor() 

#########################################----RETREIVING TABLE NAME---############################################# 

def get_table_name(table_index):
    my_db = sql.connect( 
             host="127.0.0.1",
             user="root",
             database ='Phonepe_db',
             port = 3306,
             password="2369",
              ) 
      
    mycursor = my_db.cursor() 

    mycursor.execute("SHOW TABLES")

    tables = mycursor.fetchall()

    if 0 <= table_index < len(tables):
        table_name = tables[table_index][0]
    else:
        table_name = None


    return table_name


#########################################----RETREIVING TABLE DATA---############################################# 

def get_table_data(table_name):
    my_db = sql.connect( 
             host="127.0.0.1",
             user="root",
             database ='Phonepe_db',
             port = 3306,
             password="2369",
              ) 
      
    mycursor = my_db.cursor()

    # Fetch years, quarters, and states from the specified table
    query = f"SELECT DISTINCT Year, Quarter, State FROM {table_name}"
    mycursor.execute(query)
    data = mycursor.fetchall()

    years = sorted(set(row[0] for row in data))
    quarters = sorted(set(row[1] for row in data))
    states = sorted(set(row[2] for row in data))


    return years, quarters, states


#########################################----RETREIVING STATE NAMES---############################################# 

def get_states_from_table(table_name):
    my_db = sql.connect( 
             host="127.0.0.1",
             user="root",
             database ='Phonepe_db',
             port = 3306,
             password="2369",
              ) 
      
    mycursor = my_db.cursor() 

    query = f"SELECT DISTINCT State FROM {table_name}"
    mycursor.execute(query)
    states = [row[0] for row in mycursor.fetchall()]

    return states



#########################################----PLOTTING CHARTS---##################################################

# Plotting functions
def plot_bar_chart(df, x, y,title):
    fig = px.bar(df, x=x, y=y, title=title,
                 color_discrete_sequence=px.colors.qualitative.Dark24,
                  height=750, width=700)
    return st.plotly_chart(fig)

# Plotting Country map 
def country_chart(df, x, y, title):  
    fig = px.choropleth(df,
                        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                        locations=x, featureidkey="properties.ST_NM",
                        color=y, color_continuous_scale="Viridis",
                        range_color=(df[y].min(), df[y].max()),
                        hover_name=x, title=title,hover_data=[y],height=800, width=850)
    fig.update_geos(fitbounds="locations", visible=False)  
    return st.plotly_chart(fig)


#Plotting Pie chart
def plot_pie_chart(df, x, y, title):
    fig= px.pie(data_frame = df, names= x, values= y,width= 1500, title = title,  color_discrete_sequence= px.colors.qualitative.Bold, hole= 0.4)
    return st.plotly_chart(fig)


#########################################----DEFINING YEAR & QUARTER USING TABLE DATA---############################# 

def multiselect_states(table_name):
    states = get_states_from_table(table_name)
    state_keys = [f'{table_name}_{state}_{i}' for i, state in enumerate(states)]  # Generate unique keys for each state
    
    selected_states = st.multiselect('Select States:', states, key=f'states_multiselect_{table_name}')
    
    return selected_states




#########################################----DEFINING YEAR & QUARTER USING TABLE DATA---############################# 

def multiselect_years_quarters(years, quarters, table_name):
    table_key = table_name.replace(' ', '_')  # Generate a key based on the table name
    years_key = '_'.join(map(str, years))  # Generate a key based on the years
    quarters_key = '_'.join(map(str, quarters))  # Generate a key based on the quarters
    
    selected_years = st.multiselect('Select years to analyze:', years, default=[min(years)], key=f'years_multiselect_{table_key}_{years_key}')
    selected_quarters = st.multiselect('Select Quarters as well:', quarters, default=[1], key=f'quarters_multiselect_{table_key}_{quarters_key}')
    
    return selected_years, selected_quarters





#########################################----FETCHING DATAFRAME from TABLES ---####################################### 


def fetch_data_from_table(table_name):
    my_db = sql.connect( 
             host="127.0.0.1",
             user="root",
             database ='Phonepe_db',
             port = 3306,
             password="2369",
              ) 
      
    mycursor = my_db.cursor()

 
    query = f"SELECT * FROM {table_name}"
    mycursor.execute(query)


    result = mycursor.fetchall()

   
    df = pd.DataFrame(result, columns=mycursor.column_names)

    return df



#########################################----GENERATING DATA FUNCTIONS ---#########################################

def Transaction_data(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)
    
    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")[["Transaction_count", "Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")

    return x


def Transaction_type_data(table_name, selected_years, selected_quarters, selected_states):

    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & (df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("Transaction_type")[["Transaction_count","Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)

    plot_pie_chart(x_trans, "Transaction_type", "Transaction_amount", f"TRANSACTION AMOUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    plot_pie_chart(x_trans, "Transaction_type", "Transaction_count", f"TRANSACTION COUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    return x




def User_Agg(table_name, selected_years, selected_quarters):
    
    df = fetch_data_from_table(table_name)

    x = df[(df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("Brands")[["Transaction_count"]].sum()
    x_trans.reset_index(inplace=True)

    x_trans["Percentage"] = (x_trans["Transaction_count"] / x_trans["Transaction_count"].sum()) * 100


    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans,"Brands", "Transaction_count" , f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        fig_1= px.bar(x_trans, x= "Brands", y= "Transaction_count",hover_data=["Percentage"],
                      color_discrete_sequence= px.colors.qualitative.Vivid,
                        title= f"TRANSACTION COUNT PER BRAND " ,width= 800)
        st.plotly_chart(fig_1)

        fig_2= px.pie(x_trans, names = "Brands", values = "Transaction_count",hover_data=["Percentage"],
                        title= f"TRANSACTION COUNT PER BRAND",width= 800,  color_discrete_sequence= px.colors.qualitative.Prism, hole= 0.5)
        st.plotly_chart(fig_2)

    return x



def Insurance_data(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)

    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")[["Insurance_count", "Insurance_amount"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    return x


def User_Map(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)

    x = df[(df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")[["Total_users", "App_opens"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Total_users", f"TOTAL USERS in {selected_years} in the Quarter: {selected_quarters}")

    with col2:
        plot_bar_chart(x_trans, "State", "App_opens", f"TOTAL APP OPENS in {selected_years} in the Quarter: {selected_quarters}")

    return x


def User_Map_district(table_name, selected_years, selected_quarters, selected_states):

    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & (df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("District")[["Total_users", "App_opens"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "Total_users", "District", f"TOTAL USERS IN EACH DISTRICT of {selected_states}")

    with col2:
        plot_bar_chart(x_trans, "App_opens", "District", f"TOTAL APP OPENINGS IN EACH DISTRICT of {selected_states}")


def Map_transaction(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)

    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")[["Transaction_count", "Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)

    

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")
    

    return x


def Map_transaction_district(table_name, selected_years, selected_quarters, selected_states):

    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & (df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("District")[["Transaction_count","Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)
    
    plot_pie_chart(x_trans, "District", "Transaction_amount", f"TRANSACTION AMOUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    plot_pie_chart(x_trans, "District", "Transaction_count", f"TRANSACTION COUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    return x

def insurance_user(table_name, selected_years, selected_quarters):
    
    df = fetch_data_from_table(table_name)

    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True) 

    x_trans = x.groupby("State")[["Insurance_count", "Insurance_amount"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    return x

def insurance_user_district(table_name, selected_years, selected_quarters,selected_states):
    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)    
        
    x_trans = x.groupby("District")[["Insurance_count", "Insurance_amount"]].sum()
    x_trans.reset_index(inplace=True)
        

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "Insurance_amount", "District", f"INSURANCE AMOUNT IN EACH DISTRICT of {selected_states}")

    with col2:
        plot_bar_chart(x_trans, "Insurance_count", "District", f"INSURANCE COUNT IN EACH DISTRICT of {selected_states}")
    
    return x



def insurance_top(table_name, selected_years, selected_quarters):
    
    df = fetch_data_from_table(table_name)

    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True) 

    x_trans = x.groupby("State")[["Insurance_count", "Insurance_amount"]].sum()
    x_trans.reset_index(inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Insurance_amount", f"INSURANCE AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Insurance_count", f"INSURANCE COUNT in {', '.join(map(str, selected_years))}")

    return x

def insurance_top_pincode(table_name, selected_years, selected_quarters,selected_states):
    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)    
        
    x_trans = x.groupby("Pincode")[["Insurance_count", "Insurance_amount"]].sum()
    x_trans.reset_index(inplace=True)
        
    fig= px.pie(x_trans, names= "Pincode", values= "Insurance_amount",width= 1800, title =f"TOTAL INSURANCE AMOUNT in PINCODES of {selected_states}",  
                color_discrete_sequence= px.colors.qualitative.Bold, hole= 0.4)
    st.plotly_chart(fig)

    fig_2= px.pie(x_trans, names= "Pincode", values= "Insurance_count",width= 1800, title =f"TOTAL INSURANCE COUNT in PINCODES of {selected_states}",  
                color_discrete_sequence= px.colors.qualitative.Bold, hole= 0.4)
    st.plotly_chart(fig_2)
    
    return x



def User_Top(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)

    x = df[(df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")["Total_users_by_pincode"].sum().reset_index()

    fig = px.bar(x_trans, x="State", y="Total_users_by_pincode", title = f"TOTAL USERS in {selected_years} in the Quarter: {selected_quarters}",
                 color_discrete_sequence=px.colors.qualitative.Set2,
                  height=900, width=1500)
    st.plotly_chart(fig)

    return x


def User_Top_pincode(table_name, selected_years, selected_quarters, selected_states):

    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & (df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("Pincode")["Total_users_by_pincode"].sum().reset_index()

    fig= px.pie(x_trans, names= "Pincode", values= "Total_users_by_pincode",width= 1500, title =f"TOTAL USERS in the PINCODE of {selected_states}",  
                color_discrete_sequence= px.colors.qualitative.Bold, hole= 0.4)
    st.plotly_chart(fig)
    
    return x


def Top_transaction(table_name, selected_years, selected_quarters):

    df = fetch_data_from_table(table_name)

    x = df[df["Year"].isin(selected_years) & df["Quarter"].isin(selected_quarters)]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("State")[["Transaction_count", "Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)

    

    col1, col2 = st.columns(2)
    with col1:
        plot_bar_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        plot_bar_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")

    with col2:
        country_chart(x_trans, "State", "Transaction_amount", f"TRANSACTION AMOUNT in {', '.join(map(str, selected_years))}")
        country_chart(x_trans, "State", "Transaction_count", f"TRANSACTION COUNT in {', '.join(map(str, selected_years))}")
    

    return x


def Top_transaction_pincode(table_name, selected_years, selected_quarters, selected_states):

    df = fetch_data_from_table(table_name)

    x = df[(df["State"].isin(selected_states)) & (df["Year"].isin(selected_years)) & (df["Quarter"].isin(selected_quarters))]
    x.reset_index(drop=True, inplace=True)

    x_trans = x.groupby("Pincode")[["Transaction_count","Transaction_amount"]].sum()
    x_trans.reset_index(inplace=True)
    
    plot_pie_chart(x_trans, "Pincode", "Transaction_amount", f"TRANSACTION AMOUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    plot_pie_chart(x_trans, "Pincode", "Transaction_count", f"TRANSACTION COUNT in {selected_states} for {selected_years} in the Quarter:{selected_quarters}")

    return x




#########################################----GENERAL INSIGHTS---#######################################"


# What is the Total amount of Aggregated Transactions in Top 10 States
def Total_Transaction_amount_state():
    query= f'''select State, SUM(Transaction_amount) AS Transaction_amount
                from aggregated_transactions
                group by State
                order by Transaction_amount DESC
                limit 10;'''

    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)

    st.write(df)

    fig= px.bar(df, x="State", y="Transaction_amount", title="TOP 10 TRANSACTION AMOUNTS PER STATE", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.G10, height= 800,width= 900)
    return st.plotly_chart(fig)


# What are the the Pincodes of Total Top 10 users 
def Pincode_Total_users():
    query= f'''select State, Pincode, sum(total_users_by_pincode) as Total_user_by_pincode
                from top_users
                group by Pincode , State
                order by Total_user_by_pincode Desc
                limit 10;'''
    
    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)
    st.write(df)

    fig= px.bar(df, x="State", y="Total_user_by_pincode", title="TOP 10 PINCODE OF TOTAL TOP USERS", hover_name= "Pincode",
                            color_discrete_sequence=px.colors.qualitative.Light24, height= 800,width= 900)
    return st.plotly_chart(fig)



# What are the the Pincodes of Total Top 10 Transactions and Transaction counts
def Pincode_Total_Insurance_count():
    query= f'''select State, Pincode, sum(Transaction_count) as Total_Count
                from top_transactions
                group by Pincode , State
                order by Total_Count Desc
                limit 10;'''
    
    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)


    col1, col2 = st.columns(2)

    with col1:
        st.write(df)
        fig= px.bar(df, x="State", y="Total_Count", title="TOP 10 INSURANCE COUNTS WITH RESPECTIVE STATE", hover_name= "Pincode",
                            color_discrete_sequence=px.colors.qualitative.Dark24_r, height= 800,width= 900)
        st.plotly_chart(fig)



    query2= f'''select State, Pincode, sum(Transaction_count) as Total_Count, sum(transaction_amount) as Total_Transactions
                from top_transactions
                group by Pincode , State
                order by Total_Transactions Desc
                limit 10;'''
    
    mycursor.execute(query2)
    table2= mycursor.fetchall()
    my_db.commit()

    df2= pd.DataFrame(table2, columns=mycursor.column_names)

    with col2:
        st.write(df2)
        fig2= px.bar(df2, x="State", y="Total_Transactions", title="TOP 10 INSURANCE AMOUNTS WITH RESPECTIVE STATE", hover_name= "Pincode",
                            color_discrete_sequence=px.colors.qualitative.Pastel2, height= 800,width= 900)
        st.plotly_chart(fig2)



# What are the the Districts of Total Top 10 MAP USER Transactions and MAP USER Transaction counts
def District_map_users():
    query= f'''select State, District, sum(Total_users) as Total_Users
                from map_users
                group by District , State
                order by Total_Users Desc
                limit 10;'''
    
    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)


    col1, col2 = st.columns(2)

    with col1:
        st.write(df)
        fig= px.bar(df, x="District", y="Total_Users", title="TOP 10 MAP USERS WITH RESPECTIVE DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Safe, height= 800,width= 900)
        st.plotly_chart(fig)



    query2= f'''select State, District, sum(App_opens) as App_Opens
                from map_users
                group by District , State
                order by App_Opens Desc
                limit 10;'''
                        
    mycursor.execute(query2)
    table2= mycursor.fetchall()
    my_db.commit()

    df2= pd.DataFrame(table2, columns=mycursor.column_names)

    with col2:
        st.write(df2)
        fig2= px.bar(df2, x="District", y="App_Opens", title="TOP 10 APP OPENS WITH RESPECTIVE DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.G10, height= 800,width= 900)
        st.plotly_chart(fig2)


# What are the the Districts of Total Top 10 MAP Transactions and Transaction counts
def District_map_transactions():
    query= f'''select State, District, sum(Transaction_count) as Total_count
                from map_transactions
                group by District , State
                order by Total_count Desc
                limit 10;'''
    
    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)


    col1, col2 = st.columns(2)

    with col1:
        st.write(df)
        fig= px.bar(df, x="District", y="Total_count", title="TOP 10 MAP TRANSCATION COUNT WITH RESPECTIVE DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Set3, height= 800,width= 900)
        st.plotly_chart(fig)



    query2= f'''select State, District, sum(Transaction_count) as Total_count, sum(transaction_amount) as Total_Transactions
                from map_transactions
                group by District , State
                order by Total_Transactions Desc
                limit 10;'''
                        
    mycursor.execute(query2)
    table2= mycursor.fetchall()
    my_db.commit()

    df2= pd.DataFrame(table2, columns=mycursor.column_names)

    with col2:
        st.write(df2)
        fig2= px.bar(df2, x="District", y="Total_Transactions", title="TOP 10 MAP TRANSACTIONS WITH RESPECTIVE DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Vivid, height= 800,width= 900)
        st.plotly_chart(fig2)




# What are the the Districts of Total Top 10 MAP Insurance and Insurance counts
def District_map_insurance():
    query= f'''select State, District, sum(Insurance_count) as Total_count
                from map_insurance
                group by District , State
                order by Total_count Desc
                limit 10;'''
    
    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)


    col1, col2 = st.columns(2)

    with col1:
        st.write(df)
        fig= px.bar(df, x="District", y="Total_count", title="TOP 10 MAP INSURANCE COUNT WITH RESPECTIVE DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Prism, height= 800,width= 900)
        st.plotly_chart(fig)



    query2= f'''select State, District, sum(Insurance_count) as Total_count, sum(Insurance_amount) as Total_Insurance
                from map_insurance
                group by District , State
                order by Total_Transactions Desc
                limit 10;'''
                        
    mycursor.execute(query2)
    table2= mycursor.fetchall()
    my_db.commit()

    df2= pd.DataFrame(table2, columns=mycursor.column_names)

    with col2:
        st.write(df2)
        fig2= px.bar(df2, x="District", y="Total_Transactions", title="TOP 10 MAP INSURANCES WITH DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Antique, height= 800,width= 900)
        st.plotly_chart(fig2)



# What are the States of Total Top 10 Aggregated User Transcation counts
def Total_User_Transaction_count():
    query= f'''select State,  sum(Transaction_count) as Total_count
                from aggregated_users
                group by State
                order by Total_count Desc
                limit 10;'''

    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)

    st.write(df)

    fig= px.bar(df, x="State", y="Total_count", title="TOP 10 USER TRANSACTION COUNTS PER STATE", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Dark24, height= 800,width= 900)
    return st.plotly_chart(fig)


# What are the Mobile Brands of Total Top 10 Aggregated User Transcation counts
def Total_User_Brand_Transaction_count():
    query= f'''select State, Brands,  sum(Transaction_count) as Total_count
                from aggregated_users
                group by Brands, State
                order by Total_count Desc
                limit 10;'''

    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)

    st.write(df)

    fig= px.bar(df, x="Brands", y="Total_count", title="TOP 10 USER TRANSACTION COUNTS PER BRAND", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Plotly, height= 800,width= 900)
    return st.plotly_chart(fig)



# Which Quarter has the highest number of Aggregated Transaction amount
def Total_Agg_Transaction_amount_per_Quarter():
    query= f'''select Quarter,  sum(Transaction_amount) as Total_Transactions
                from aggregated_transactions
                group by Quarter
                order by Total_Transactions 
                limit 10;'''

    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)

    st.write(df)

    fig= px.bar(df, y="Total_Transactions", x="Quarter", title="TOP 10 AGGREGATED TRANSACTION AMOUNT PER QUARTER", hover_name= "Quarter",
                            color_discrete_sequence=px.colors.qualitative.D3, height= 800,width= 900)
    return st.plotly_chart(fig)


# What are the minimum and maximum MAP Transaction amount in all Districts
def min_max_map_transactions():
    query= f'''select District,  State, min(Transaction_amount) as Min_Transactions
                from map_transactions
                group by District,  State
                order by Min_Transactions 
                limit 10;'''

    mycursor.execute(query)
    table= mycursor.fetchall()
    my_db.commit()

    df= pd.DataFrame(table, columns=mycursor.column_names)
    
    col1, col2 = st.columns(2)

    with col1:
        st.write(df)
        fig= px.bar(df, x="District", y="Min_Transactions", title="10 LEAST MAP TRANSACTION AMOUNT IN ALL DISTRICTS", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Bold_r, height= 800,width= 900)
        st.plotly_chart(fig)



    query2= f'''select District,  State, max(Transaction_amount) as Max_Transactions
                from map_transactions
                group by District,  State
                order by Max_Transactions desc
                limit 10;'''
                        
    mycursor.execute(query2)
    table2= mycursor.fetchall()
    my_db.commit()

    df2= pd.DataFrame(table2, columns=mycursor.column_names)

    with col2:
        st.write(df2)
        fig2= px.bar(df2, x="District", y="Max_Transactions", title="TOP 10 MAP INSURANCES WITH DISTRICT", hover_name= "State",
                            color_discrete_sequence=px.colors.qualitative.Bold, height= 800,width= 900)
        st.plotly_chart(fig2)







#########################################----GENERATING STREAMLIT PAGE---############################# 




st.set_page_config(layout= "wide")
st.title('**PHONEPE DATA VISUALIZATION AND EXPLORATION**', anchor = False)

with st.sidebar:
    
    selected = option_menu(menu_title = None,
                          options=["HOME", "EXPLORATION","INSIGHTS"],
                          icons=["house-fill","database-fill","bar-chart-fill" ],
                          default_index = 0,
                          menu_icon="cast",
                          key="navigation_menu",
                          styles={
                                    "font_color": "#DC143C",   
                                    "border": "2px solid #DC143C", 
                                    "padding": "10px 25px"   
                          })


if selected == 'HOME':  
    st.image(Image.open(r"F:\VS Code\Phonepe\v-emhrqu_400x400.png"),width= 100)
    st.subheader("PHONEPE: Indian digital payments and financial services company")

    st.divider()

    st.write("**Welcome to the PhonePe Pulse Data. This application provides insights and analysis of PhonePe data "
            "across various categories such as transactions, users, and insurance.**")
    st.markdown("")
 
    st.markdown("")



    st.video("F:\VS Code\Phonepe\pulse-video.mp4")

    st.divider()

    st.write("Explore the **Exploration** page to analyze aggregated and map data. "
            "Get insights and answers to specific questions on the **Insights** page.")
    st.markdown("")
    st.markdown("")
    st.info("**Navigate through the tabs to explore different analyses and insights.**")


    st.divider()
    st.markdown("Developed by **Kadambi Kashyap**")
        


##########################################---- EXPLORATION PAGE ----##############################################

if selected == 'EXPLORATION':

    tab1,tab2,tab3 = st.tabs([":red[AGGREGATED ANALYSIS]",":red[MAP ANALYSIS]",":red[TOP ANALYSIS]"])

    with tab1:
        SELECT = option_menu(
        menu_title = None,
        options=["💸 AGGREGATED TRANSACTIONS", "👨🏻‍💻 AGGREGATED USERS", "🏥 AGGREGATED INSURANCE"],
        default_index = 0,
        menu_icon="cast",
        orientation="horizontal",
        styles={
                "font_color": "#DC143C",   
                "border": "2px solid #DC143C", 
                "padding": "10px 25px"   
            })
        if SELECT == '💸 AGGREGATED TRANSACTIONS':
            st.header(":red[AGGREGATED ANALYSIS OF TRANSACTIONS]", anchor=False)
            st.divider()

            table_name = get_table_name(1)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)
                

                Transaction_data(table_name, selected_years, selected_quarters)

                st.header("AGGREGATED ANALYSIS WITH STATES")
                st.divider()

                selected_states = multiselect_states(table_name) 

                Transaction_type_data(table_name, selected_years, selected_quarters, selected_states)
            else:
                st.error("Table not found.")



        if SELECT == "👨🏻‍💻 AGGREGATED USERS":
            st.header(":red[AGGREGATED ANALYSIS OF USERS]", anchor = False)
            st.divider()

            table_name = get_table_name(2)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                User_Agg(table_name, selected_years, selected_quarters)
            else:
                st.error("Table not found.")


        if SELECT == "🏥 AGGREGATED INSURANCE":
            st.header(":red[AGGREGATED ANALYSIS OF INSURANCES]", anchor = False)
            st.divider()

            table_name = get_table_name(0)

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                Insurance_data(table_name, selected_years, selected_quarters)
            else:
                st.error("Table not found.")

    with tab2:
        SELECT = option_menu(
                            key="select_menu",
                            menu_title=None,
                            options=["💸 MAP TRANSACTIONS", "👨🏻‍💻 MAP USERS", "🏥 MAP INSURANCE"],
                            default_index=0,
                            menu_icon="cast",
                            orientation="horizontal",
                            styles={
                                "font_color": "#DC143C",
                                "border": "2px solid #DC143C",
                                "padding": "10px 25px"
                            }
                        )

        if SELECT == '💸 MAP TRANSACTIONS':
            
            st.header(":red[MAP ANALYSIS OF TRANSACTIONS]", anchor = False)
            st.divider()
            
            table_name = get_table_name(4)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)
                

                Map_transaction(table_name, selected_years, selected_quarters)

                st.header("MAP ANALYSIS OF TRANSACTIONS WITH DISTRICTS")
                st.divider()

                selected_states = multiselect_states(table_name) 

                Map_transaction_district(table_name, selected_years, selected_quarters, selected_states)
            else:
                st.error("Table not found.")


        if SELECT == "👨🏻‍💻 MAP USERS":
            st.header(":red[MAP ANALYSIS OF USERS]", anchor=False)
            st.divider()
            table_name = get_table_name(5)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                User_Map(table_name, selected_years, selected_quarters)
                  

                st.header(":red[MAP ANALYSIS OF USERS PER DISTRICT]", anchor=False)
                st.divider()

                selected_states = multiselect_states(table_name) 

                User_Map_district(table_name, selected_years, selected_quarters, selected_states)
            else:
                st.error("Table not found.") 

        if SELECT == "🏥 MAP INSURANCE":
            st.header(":red[MAP ANALYSIS OF INSURANCES]", anchor = False)
            st.divider()
            
            table_name = get_table_name(3)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                insurance_user(table_name, selected_years, selected_quarters)


                st.header("MAP ANALYSIS OF INSURANCES PER DISTRICT")
                st.divider()

                selected_states = multiselect_states(table_name) 

                insurance_user_district(table_name, selected_years, selected_quarters,selected_states)

            else:
                st.error("Table not found.") 


    with tab3:
        SELECTED = option_menu(
                            key="select_menu_1",
                            menu_title=None,
                            options=["💸 TOP TRANSACTIONS", "👨🏻‍💻 TOP USERS", "🏥 TOP INSURANCE"],
                            default_index=0,
                            menu_icon="cast",
                            orientation="horizontal",
                            styles={
                                "font_color": "#DC143C",
                                "border": "2px solid #DC143C",
                                "padding": "10px 25px"
                            }
                        )

        if SELECTED == '💸 TOP TRANSACTIONS':
            
            st.header(":red[TOP ANALYSIS OF TRANSACTIONS]", anchor = False)
            st.divider()
            
            table_name = get_table_name(7)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)
                

                Top_transaction(table_name, selected_years, selected_quarters)

                st.header("TOP ANALYSIS OF TRANSACTIONS WITH DISTRICTS")
                st.divider()

                selected_states = multiselect_states(table_name) 

                Top_transaction_pincode(table_name, selected_years, selected_quarters, selected_states)
            else:
                st.error("Table not found.")


        if SELECTED == "👨🏻‍💻 TOP USERS":
            st.header(":red[TOP ANALYSIS OF USERS]", anchor=False)
            st.divider()
            table_name = get_table_name(8)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                User_Top(table_name, selected_years, selected_quarters)
                  

                st.header(":red[TOP ANALYSIS OF USERS PER PINCODE]", anchor=False)
                st.divider()

                selected_states = multiselect_states(table_name) 

                User_Top_pincode(table_name, selected_years, selected_quarters, selected_states)
            else:
                st.error("Table not found.") 

        if SELECTED == "🏥 TOP INSURANCE":
            st.header(":red[TOP ANALYSIS OF INSURANCES]", anchor = False)
            st.divider()
            
            table_name = get_table_name(6)  

            if table_name:
                years, quarters, states = get_table_data(table_name)
                selected_years, selected_quarters = multiselect_years_quarters(years, quarters, table_name)

                insurance_top(table_name, selected_years, selected_quarters)


                st.header("TOP ANALYSIS OF INSURANCES PER PINCODE")
                st.divider()

                selected_states = multiselect_states(table_name) 

                insurance_top_pincode(table_name, selected_years, selected_quarters,selected_states)

            else:
                st.error("Table not found.")


##########################################---- INSIGHTS PAGE ----##############################################
if selected == 'INSIGHTS':
    st.markdown("# ")
    st.subheader(":red[Select one of the options to have insights on Phonepe Data]", anchor=False)
    all_questions = st.selectbox("Please select the Questions",
                           ('1.What is the Total amount of Aggregated Transactions in Top 10 States?',
                           '2.What are the the Pincodes of Total 10 TOP users?',
                           '3.What are the the Pincodes of Total 10 TOP Transactions and TOP Transaction counts?',
                           '4.What are the the Districts of Total Top 10 MAP USER Transactions and MAP USER Transaction counts?',
                           '5.What are the the Districts of Total Top 10 MAP Transactions and Transaction counts?',
                           '6.What are the the Districts of Total Top 10 MAP Insurance and Insurance counts?',
                           '7.What are the States of Total Top 10 Aggregated User Transcation counts?',
                           '8.What are the Mobile Brands of Total Top 10 Aggregated User Transcation counts?',
                           '9.Which Quarter has the highest number of Aggregated Transaction amount?',
                           '10.What are the minimum and maximum MAP Transaction amount in all Districts?',))
    st.divider()

    if all_questions == '1.What is the Total amount of Aggregated Transactions in Top 10 States?':
        Total_Transaction_amount_state()
    
    elif all_questions == '2.What are the the Pincodes of Total 10 TOP users?':
        Pincode_Total_users()

    elif all_questions == '3.What are the the Pincodes of Total 10 TOP Transactions and TOP Transaction counts?':
        Pincode_Total_Insurance_count()

    elif all_questions == '4.What are the the Districts of Total Top 10 MAP USER Transactions and MAP USER Transaction counts?':
        District_map_users()

    elif all_questions == '5.What are the the Districts of Total Top 10 MAP Transactions and Transaction counts?':
        District_map_transactions()

    elif all_questions == '6.What are the the Districts of Total Top 10 MAP Insurance and Insurance counts?':
        District_map_insurance()
    
    elif all_questions == '7.What are the States of Total Top 10 Aggregated User Transcation counts?':
        Total_User_Transaction_count()

    elif all_questions == '8.What are the Mobile Brands of Total Top 10 Aggregated User Transcation counts?':
        Total_User_Brand_Transaction_count()

    elif all_questions == '9.Which Quarter has the highest number of Aggregated Transaction amount?':
        Total_Agg_Transaction_amount_per_Quarter()
    
    elif all_questions == '10.What are the minimum and maximum MAP Transaction amount in all Districts?':
        min_max_map_transactions()





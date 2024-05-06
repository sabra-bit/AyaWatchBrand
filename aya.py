
import sqlite3
import streamlit as st
import time
import pandas as pd
conn = sqlite3.connect('watchBrand.db')
cursor = conn.cursor()

st.set_page_config(page_title="Egyptian watch brand advisor",page_icon="⌚",layout="centered" )


def read_question():
    cursor.execute("""
            SELECT *
            FROM Questions
            WHERE isSelected = 0
            ORDER BY ID ASC
            LIMIT 1
            """ )
    return cursor.fetchone()

with st.sidebar:
    st.header("Egyptian watch brand advisor")
    menu_selection = st.radio("Menu:", ('Search by Reading 📖',"Conduct a dialogue with the Consultant 🧠", "Knowledge Base 💾"))
if menu_selection == "Search by Reading 📖":
    st.title(":blue[dialogue with the Consultant] 📖")
    cursor.execute("SELECT DISTINCT Topic FROM Questions;" )
    topic = cursor.fetchall()
    for top in topic:
        with st.expander(str(top[0])):
            
            Data = cursor.execute("""
                select * FROM Questions 
                WHERE Topic = ?
                """, (str(top[0]),))
            for data in Data:
                st.write(data[1])
                st.caption(data[4])
    

if menu_selection == "Knowledge Base 💾":
    # Create a form
    st.title(":blue[Insert Data Collection] 💾 ")
    with st.form(key="my_form"):
        # Text inputs with labels
        Question = st.text_input(label="Question:")
        Answer = st.text_input(label="Reply:")
        
        Right = st.text_input(label="Expected Answer:")
        st.write("use sign :red[-] for many Expected Answer ex: Yes-No")
        Conclusion = st.text_input(label="Inference:")
        Topic = st.selectbox(
            "Topic:",
            ("Pricing", "Planning", "marketing" ,"Branding"))

        # Submit button
        submitted = st.form_submit_button(label="Store")

    # Process form submission
    if submitted:
        st.write("Submitted Data")
        Questions = [
            (Question,Answer,Right,Conclusion,0,Topic),
        ]
        cursor.executemany("""INSERT INTO Questions (Question,Reply,Rightreply,Inference,isSelected,Topic) 
                           VALUES  (?, ?, ?, ?, ?,?)""", Questions)

        conn.commit()
    cursor.execute("SELECT * FROM Questions")

    # Fetch all rows and column names
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # Create a pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    df

if menu_selection == "Conduct a dialogue with the Consultant 🧠":

    st.title(":blue[dialogue with the Consultant] 🧠")
    st.subheader("Type :red['end'] to relode the session 🔖")
    messages = st.container(height=400)
    data = read_question()

    if 'my_list' not in st.session_state:
        st.session_state['my_list'] = []
    for item in st.session_state['my_list']:
        messages.chat_message("user").write(f"Consultant: {item}")
    if data:

        messages.chat_message("user").write(f":green[Consultant]: {str(data[1])} :red[user]: {str(data[2])}")

    else :
        Conclusion = cursor.execute("SELECT * FROM AnswersX").fetchall()
        if Conclusion:
            
            messages.chat_message("user").write(f":green[Consultant]: Conclusion :")
            for items in Conclusion:
                messages.chat_message("user").write(f":green[Consultant]: {items[0]}.")
        else:
            messages.chat_message("user").write(f":green[Consultant]: can not get answer or tell you advise.")

    col1, col2 = st.columns([7, 1])
    with col1:
        
        user_input = st.text_input("Say something")
    with col2:
        st.write("")
        st.write("")
        submit_button = st.button("Send")

    if submit_button :  # Button clicked
        if  user_input in "end":
            cursor.execute("""
                UPDATE Questions
                SET isSelected = 0
            
                """)
            cursor.execute("DELETE FROM AnswersX")
            # Commit the changes to the database
            conn.commit()
            st.session_state.clear()
            progress_bar = st.progress(0)
            for i in range(50):
                progress_bar.progress(i)
                time.sleep(0.01) 
            st.experimental_rerun()
        elif user_input not in str(data[2]):
            
            messages.chat_message("user").write(f"Sorry, that's not quite right. Try again. The answer should be related to: {str(data[1])}")

        else:
            messages.chat_message("assistant").write(user_input)
            st.session_state['my_list'].append(f"{str(data[1])} > {user_input}")
            # Get further user input after answering correctly

            cursor.execute("""
                UPDATE Questions
                SET isSelected = 1
                WHERE ID = ?
                """, (data[0],))

            # Commit the changes to the database
            conn.commit()
            
            if user_input in data[3].split('-') :
                sql = "INSERT INTO AnswersX (Answers) VALUES (?)"
                cursor.execute(sql, (data[4],))
                conn.commit()

            next_prompt = st.text("Inference")
            progress_bar = st.progress(0)
            for i in range(50):
                progress_bar.progress(i)
                time.sleep(0.01) 
            st.experimental_rerun()
        






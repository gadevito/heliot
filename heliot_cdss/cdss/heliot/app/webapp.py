import streamlit as st
import requests
import json
import pandas as pd


# URL for the REST service
url = "http://localhost:8000/api/allergy_check"


# Title of the Web App
st.title("Heliot DSS POC")

# Create tabs
tab1, tab2 = st.tabs(["Try Heliot", "Load csv"])

with tab1:
    # Input for drug code and allergy
    drug_code = st.text_input("Fill in the drug code:", "043955018")
    allergy = st.text_input("Fill in the ingredient to which the patient is allergic to (empty means no allergy):", "lattosio")

    # Text Area to show the results
    text_area = st.empty()

    if st.button("Submit"):
        payload = {"drug_code": drug_code, "allergy": allergy}
        
        with st.spinner("Loading..."):
            response = requests.post(url, json=payload, stream=True)

            if response.status_code == 200:
                result_text = ""
                tk = {}
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if "data: {\"message\":" in decoded_line:
                            j = decoded_line.rfind("\"}")
                            decoded_line = decoded_line[5:]
                            mess = json.loads(decoded_line)
                            decoded_line = mess['message']
                        result_text += decoded_line 
                        text_area.text_area("Result", result_text, height=400)
                        if "data: {\"input\":" in decoded_line:
                            tokens = decoded_line[5:]
                            tk = json.loads(tokens)
                            print("\nTOKENS", tk['input'], tk['output'], tk['total'])

                st.subheader("Token usage")
                st.json(tk)
            else:
                st.error(f"Error: {response.status_code}")


with tab2:
    st.header("Upload a CSV or Excel file")

    # File uploader
    uploaded_file = st.file_uploader("Choose the CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, dtype={"ID": str, "drug_code": str, "Allergy": str})
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, dtype={"ID": str, "drug_code": str, "Allergy": str})
            else:
                st.error("Error: Unsupported file type.")
                df = None
        except Exception as e:
            st.error(f"Error: Unable to read the file. Please, check the file format.")
            df = None
        
        if df is not None:
            required_columns = {"ID", "drug_code", "Allergy"}
            if not required_columns.issubset(df.columns):
                st.error(f"Error: The file must contain at least the following columns {required_columns}.")
            else:
                df = df[list(required_columns)]  # Keep only required columns
                df["Result"] = ""  # Add a new column for results

                # Update NaN with empty strings
                df = df.fillna("")

                # Convert all columns to strings to avoid JSON compliance issues
                df = df.astype(str)
                
                # Create an interactive data viewer container
                df_container = st.empty()
                
                # Set column configurations
                column_config = {
                    'ID': st.column_config.TextColumn(label="ID"),
                    'drug_code': st.column_config.TextColumn(label="Drug Code"),
                    'Allergy': st.column_config.TextColumn(label="Allergy"),
                    'Result': st.column_config.TextColumn(label="Result", width='large')  # Set the width to large
                }
                
                df_container.dataframe(df, column_config=column_config, use_container_width=True)  # Display the dataframe
                
                # Execute button
                if st.button("Execute"):
                    tkk = {'input':0, 'output':0, 'total':0}
                    for i, row in df.iterrows():
                        payload = {"drug_code": row["drug_code"], "allergy": row["Allergy"]}
                        
                        with st.spinner(f"Processing ID {row['ID']}..."):
                            try:
                                response = requests.post(url, json=payload, stream=True)
                            except requests.exceptions.RequestException as e:
                                st.error(f"Request Error: {e}")
                                continue
                            
                            if response.status_code == 200:
                                result_text = ""
                                tk = {}
                                for line in response.iter_lines():
                                    if line:
                                        decoded_line = line.decode('utf-8')
                                        if "data: {\"message\":" in decoded_line:
                                            j = decoded_line.rfind("\"}")
                                            decoded_line = decoded_line[5:]
                                            mess = json.loads(decoded_line)
                                            decoded_line = mess['message']
                                            result_text += decoded_line 
                                        elif "data: {\"input\":" in decoded_line:
                                            tokens = decoded_line[5:]
                                            tk = json.loads(tokens)
                                            tkk['input'] += tk['input']
                                            tkk['output'] += tk['output']
                                            tkk['total'] += tk['total']

                                        # Update the Result column 
                                        df.at[i, "Result"] = result_text
                                        # Stylize the dataframe with updated data
                                        df_container.dataframe(df, column_config=column_config, use_container_width=True)  # Display the updated dataframe
                                        
                            else:
                                df.at[i, "Result"] = f"Error: {response.status_code}"
                                # Stylize the dataframe with updated data
                                df_container.dataframe(df, column_config=column_config, use_container_width=True)  # Display the updated dataframe
                    st.subheader("Token usage")
                    st.json(tkk)
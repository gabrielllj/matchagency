import streamlit as st
import numpy as np
import pandas as pd
import requests
from io import BytesIO
import re
from datetime import datetime

def map_market_to_region(market, territories_dict):
    """Maps each market to the right region by looping through the territories dictionary."""
    market_countries = set([x.strip() for x in market.split(',')])
    
    # Check for an exact match in the dictionary
    for key in territories_dict:
        key_countries = set([x.strip() for x in key.split(',')])
        if market_countries == key_countries:
            return territories_dict[key]
    
    # If no exact match, check for subset matches
    for key in territories_dict:
        key_countries = set([x.strip() for x in key.split(',')])
        if market_countries.issubset(key_countries):
            return territories_dict[key]
    
    return None

def clean_territory(value):
    # Standardize "South Asia" references
    if "South Asia" in value:
        return "South Asia (incl. Bangladesh, India, Pakistan, Sri Lanka)"
    if 'Perú' in value:
        return "Peru"
    if 'Panamá' in value:
        return 'Panama'
    
    # Remove periods within abbreviations or at the end of words (e.g., "U.S." -> "US", "Canada." -> "Canada")
    value = re.sub(r'\b(\w+)\.(\w+)\b', r'\1\2', value)  # Remove dots within abbreviations like "U.S."
    value = re.sub(r'\.(?=\s|$)', '', value)  # Remove any remaining trailing dots

    # Remove specified words and standalone symbols
    value = re.sub(r'\b(Including|including|and|&|the|The)\b', '', value)  # Removes specific words
    value = re.sub(r'&', '', value)  # Ensure '&' symbol is removed

    # Remove brackets and everything inside
    value = re.sub(r'\[.*?\]|\(.*?\)', '', value)

    # Replace any semicolon with a comma
    value = value.replace(';', ',')

    # Remove any punctuation at the end of the sentence (e.g., comma, period)
    value = re.sub(r'[.,;:!?]$', '', value)  # Removes only the last punctuation if present

    # Remove extra whitespace and return the cleaned text
    return re.sub(r'\s+', ' ', value).strip()  # Ensures single spaces between words

territories = {
    "Africa": "EMEA",
    "ANZ": "Asia Pacific/ APAC",
    "ANZ, APAC, ZA, ME": "Global",
    "ANZ, Hong Kong, Taiwan, Indonesia, Malaysia, Singapore, Thailand": "Asia Pacific/ APAC",
    "APAC": "Asia Pacific/ APAC",
    "Argentina": "LATAM",
    "Argentina, Colombia, Chile, Ecuador, Mexico and Peru": "LATAM",
    "Asia": "Asia Pacific/ APAC",
    "Australia": "Asia Pacific/ APAC",
    "Australia, Canada, France, Germany, Ireland, Poland, Saudi Arabia, UK, United Arab Emirates, USA": "Global",
    "Australia, India, Indonesia, Japan, Malaysia, New Zealand, Sri Lanka, Thailand, Vietnam": "Asia Pacific/ APAC",
    "Australia, Thailand": "Asia Pacific/ APAC",
    "Austria": "EMEA",
    "Austria, Bosnia and Herzegovina, Croatia": "EMEA",
    "Baltics": "EMEA",
    "Belgium": "EMEA",
    "Benelux": "EMEA",
    "Bolivia": "LATAM",
    "Brazil": "LATAM",
    "Bulgaria": "EMEA",
    "Bahrain, Kuwait, Oman, Qatar, Saudi Arabia, United Arab Emirates": "EMEA",
    "C&E Europe": "EMEA",
    "Cambodia": "Asia Pacific/ APAC",
    "Canada": "North America",
    "Canada, Czech Republic, Finland, Turkey": "Global",
    "Chile": "LATAM",
    "China": "Asia Pacific/ APAC",
    "Colombia": "LATAM",
    "Colombia, Peru, Bolivia and Chile": "LATAM",
    "Costa Rica": "LATAM",
    "Costa Rica (Regional Scope)": "LATAM",
    "Croatia": "EMEA",
    "Cyprus": "EMEA",
    "Czech Republic": "EMEA",
    "DACH (Germany, Austria, Switzerland)": "EMEA",
    "Denmark": "EMEA",
    "Denmark, Finland, Norway, Sweden": "EMEA",
    "Dominican Republic": "LATAM",
    "Dubai": "EMEA",
    "Ecuador": "LATAM",
    "Egypt": "EMEA",
    "El Salvador": "LATAM",
    "EMEA": "EMEA",
    "EMEA Regional": "EMEA",
    "Estonia": "EMEA",
    "Europe": "EMEA",
    "Europe, North America": "Global",
    "Finland": "EMEA",
    "Finland, Balticks, Eastern Europe": "EMEA",
    "France": "EMEA",
    "France, Netherlands, Italy, Belgium, Spain, Portugal, Austria, Denmark": "EMEA",
    "France, Spain, Switzerland, Belgium, Germany": "EMEA",
    "France, Sweden": "EMEA",
    "Germany": "EMEA",
    "Germany, Austria": "EMEA",
    "Germany, France, UK": "EMEA",
    "Germany, UK, Australia, Denmark, Sweden, Norway": "Global",
    "Ghana": "EMEA",
    "Global": "Global",
    "Global (excl. USA)": "Global",
    "Global (USA-led)": "Global",
    "Global (US-led)": "Global",
    "Global ex CN": "Global",
    "Global, USA": "Global",
    "Global; prioritiy US, UK, AU": "Global",
    "Greece": "EMEA",
    "Greece, Cyprus": "EMEA",
    "Guatemala": "LATAM",
    "Gulf Cooperation Council": "EMEA",
    "HK, Thailand, Singapore": "Asia Pacific/ APAC",
    "Honduras": "LATAM",
    "Hong Kong": "Asia Pacific/ APAC",
    "Hong Kong, Indonesia, Malaysia, Philippines, Singapore, Thailand": "Asia Pacific/ APAC",
    "Hong Kong, Philippines, Vietnam, Singapore, Malaysia": "Asia Pacific/ APAC",
    "Hungary": "EMEA",
    "Iceland": "EMEA",
    "India": "Asia Pacific/ APAC",
    "Indonesia": "Asia Pacific/ APAC",
    "Iraq": "EMEA",
    "Ireland": "EMEA",
    "Israel": "EMEA",
    "Italy": "EMEA",
    "Japan": "Asia Pacific/ APAC",
    "Jordan": "EMEA",
    "Kazakhstan": "Asia Pacific/ APAC",
    "Kenya": "EMEA",
    "Korea": "Asia Pacific/APAC",
    "LATAM": "LATAM",
    "Latin America": "LATAM",
    "Latvia": "EMEA",
    "Lebanon": "EMEA",
    "Lebanon, MENA": "EMEA",
    "Lithuania": "EMEA",
    "Macedonia": "EMEA",
    "Malaysia": "Asia Pacific/ APAC",
    "Malaysia, South Korea, Taiwan": "Asia Pacific/ APAC",
    "MENA": "EMEA",
    "Mexico": "LATAM",
    "Mexico, Argentina": "LATAM",
    "Mexico, Colombia, Peru, Chile": "LATAM",
    "Miami": "LATAM",
    "Middle East, Middle East Africa": "EMEA",
    "Moldova": "EMEA",
    "Morocco": "EMEA",
    "Multi-city": "Global",
    "Multi-market, Multi-markets": "Global",
    "Myanmar": "Asia Pacific/ APAC",
    "Netherlands": "EMEA",
    "Netherlands, Belgium": "EMEA",
    "New Zealand": "Asia Pacific/ APAC",
    "Nigeria": "EMEA",
    "Nigeria, Ghana, Kenya, Ivory Coast, Uganda, Morocco, Tunisia": "EMEA",
    "North America": "North America",
    "North Africa": "EMEA",
    "Nordics": "EMEA",
    "Norway": "EMEA",
    "Pakistan": "Asia Pacific/ APAC",
    "Panama": "LATAM",
    "Panama, Colombia, Mexico, Spain": "Global",
    "Paraguay": "LATAM",
    "Peru": "LATAM",
    "Peru, Chile, Colombia": "LATAM",
    "Philippines": "Asia Pacific/ APAC",
    "Poland": "EMEA",
    "Portugal": "EMEA",
    "Puerto Rico": "LATAM",
    "Qatar": "EMEA",
    "Romania": "EMEA",
    "Russia": "EMEA",
    "Saudi Arabia": "EMEA",
    "Saudi Arabia, Brazil, Peru, Chile, Algeria, Bulgaria, Bosnia and Herzegovina, Belarus, Mexico, Hong Kong, South Africa, Ecuador, Belgium and France": "Global",
    "Scandinavia": "EMEA",
    "SEA": "Asia Pacific/ APAC",
    "Serbia": "EMEA",
    "Singapore": "Asia Pacific/ APAC",
    "Slovakia": "EMEA",
    "Slovakia, Estonia, Latvia, Malta, Germany, Portugal, Poland": "EMEA",
    "Slovenia": "EMEA",
    "SOCOPAC (Argentina, Colombia, Ecuador, Peru, Panama, Costa Rica, Guatemala)": "LATAM",
    "South Asia (incl. Bangladesh, India, Pakistan, Sri Lanka)": "Asia Pacific/ APAC",
    "South Africa": "EMEA",
    "South Korea": "Asia Pacific/ APAC",
    "Spain": "EMEA",
    "Spain, UK, Italy, France, Greece, Germany": "EMEA",
    "Sri Lanka": "Asia Pacific/ APAC",
    "Sweden": "EMEA",
    "Sweden, Norway, Denmark, Finland": "EMEA",
    "Sweden, Norway, Finland": "EMEA",
    "Switzerland": "EMEA",
    "Switzerland, France": "EMEA",
    "Sub Saharan Africa": "EMEA",
    "Taiwan": "Asia Pacific/ APAC",
    "Thailand": "Asia Pacific/ APAC",
    "Thailand, Laos": "Asia Pacific/ APAC",
    "Turkey": "EMEA",
    "UK": "EMEA",
    "UK, Ireland": "EMEA",
    "UK, Mexico": "Global",
    "Ukraine": "EMEA",
    "United Arab Emirates, UAE": "EMEA",
    "United Arab Emirates, UAE, Kenya, South Africa, Morocco, Nigeria, Turkey, Algeria": "EMEA",
    "Uruguay": "LATAM",
    "Uruguay, El Salvador, Panama, Paraguay, Nicaragua, Honduras, Venezuela, Dominican Republic, Bolivia, Guatemala, Ecuador, Costa Rica, Peru, Argentina, Chile": "LATAM",
    "US": "North America",
    "US, Canada": "North America",
    "US, Canada, LATAM": "Global",
    "US, UK": "Global",
    "Vietnam": "Asia Pacific/ APAC"
}


territory_mapping = {
    "United Arab Emirates": "UAE",
    "Korea": "South Korea",
    "US": "USA",
    "Saudi": "Saudi Arabia"
}


if __name__ == "__main__":
    st.title("Adbrands heehehe")

    uploaded_excel = st.file_uploader("Upload the latest raw data (Media/Creative)", type=["xlsx", "xlsm"])
    uploaded_excel2 = st.file_uploader("Upload the latest Data Mastersheet", type=["xlsx", "xlsm"])
    
    if uploaded_excel is not None:
        file_name = uploaded_excel.name
        st.write("Uploaded file name:", file_name)
        
        if 'Media' in file_name:
            file_type = 'Media'
        else:
            file_type = 'Creative'
    
    # github_xlsx_url = st.text_input("Enter GitHub Excel file URL", 
    #                                 "https://raw.githubusercontent.com/gabrielllj/matchagency/master/agency_match.xlsx")
    # github_xlsx_url2 = st.text_input("Enter GitHub Excel file URL", 
    #                                 "https://raw.githubusercontent.com/gabrielllj/r3automation/master/company_brand.xlsx")

    if 'github_xlsx_url' not in st.session_state:
        st.session_state.github_xlsx_url = "https://raw.githubusercontent.com/gabrielllj/matchagency/master/agency_match.xlsx"
    if 'github_xlsx_url2' not in st.session_state:
        st.session_state.github_xlsx_url2 = "https://raw.githubusercontent.com/gabrielllj/r3automation/master/company_brand.xlsx"
    
    # Use the values from session state directly, without displaying input fields
    github_xlsx_url = st.session_state.github_xlsx_url
    github_xlsx_url2 = st.session_state.github_xlsx_url2

# # Optionally, you can display the URLs if needed
# st.write("GitHub Excel URL 1:", github_xlsx_url)
# st.write("GitHub Excel URL 2:", github_xlsx_url2)
    if uploaded_excel:
        data = pd.read_excel(uploaded_excel, sheet_name= file_type + ' Wins', header=7)
        excel_file = pd.ExcelFile(uploaded_excel2)
        if len(excel_file.sheet_names) > 1:
            master_sheet = pd.read_excel(uploaded_excel2, sheet_name='Main - NEW FORMULAS')
        else:
            master_sheet = pd.read_excel(uploaded_excel2)

        master_sheet['Date'] = pd.to_datetime(master_sheet['Date'], dayfirst=True, errors='coerce')
        master_sheet['Date'] = master_sheet['Date'].dt.strftime('%d/%m/%Y')
        try:
            
            response = requests.get(github_xlsx_url)
            response2 = requests.get(github_xlsx_url2)
            response.raise_for_status()
            response2.raise_for_status()
            agency_matches = pd.read_excel(BytesIO(response.content))
            company_brand = pd.read_excel(BytesIO(response2.content))
            
            
            data.columns = data.columns.str.replace(r'\s+', ' ', regex=True).str.replace(' ', '')
            if file_type == 'Creative':
                data = data[data['YY/N'] == 'N']
            elif file_type == 'Media':
                data = data[data['ConfidentialY/N'] == 'N']
            
            data['Client'] = data['Client'].str.strip()
            data['Agency'] = data['Agency'].str.strip()
            data['Agency'] = data['Agency'].str.title()
            data['Status'] = 'Awarded'
            data['Market'] = data['Market'].astype(str)
            data['Remark'] = data['Remark'].astype(str)
            data['Type of Assignment'] = np.where(data['Remark'].isna(), 'AOR/Project',
                                                    'AOR/Project - ' + data['Remark'])
            data['Type of Assignment'] = data['Type of Assignment'].replace('AOR/Project - nan', 'AOR/Project')
            data['Current Agency Description'] = data['Agency']
            data['Incumbent Agency Description'] = data['Incumbent']
            
            data = data.merge(
                company_brand, 
                how='left', 
                left_on='Client', 
                right_on='OLD BRAND NAME'
            )
            
            data = data.merge(
                agency_matches[['Agency Description', 'Match']], 
                how='left', 
                left_on='Incumbent Agency Description', 
                right_on='Agency Description'
            )
            data = data.rename(columns={'Match': 'Incumbent MATCH'}).drop(columns=['Agency Description'])
            
            data['Current Agency Description'] = data['Current Agency Description'].str.strip()
            data['Current Agency Description'] = data['Current Agency Description'].str.title()
            
            agency_matches['Agency Description'] = agency_matches['Agency Description'].str.strip()
            agency_matches['Agency Description'] = agency_matches['Agency Description'].str.title()
            
            data = data.merge(
                agency_matches[['Agency Description', 'Match']], 
                how='left', 
                left_on='Current Agency Description', 
                right_on='Agency Description'
            )
            data = data.rename(columns={'Match': 'Current Agency MATCH'}).drop(columns=['Agency Description'])
    
            data['Assignment'] = 'Media'
            data['Territory'] = data['Market']
            
            data['Territory'] = data['Territory'].apply(clean_territory)
            data['Territory'] = data['Territory'].replace(territory_mapping)

            data['Market'] = data['Market'].apply(clean_territory)
            data['Market'] = data['Market'].replace(territory_mapping)
            
            data['Region'] = data['Market'].apply(lambda x: map_market_to_region(x, territories))

            data['Est Billings'] = data['Billings(US$k)'].apply(lambda x: "USD${:,.0f}".format(x * 1_000))
            data['Month'] = "Sep"
            data['Month'] = pd.to_datetime(data['Month'] + ' 2024', format='%b %Y')
            data['Month'] = data['Month'].dt.strftime('%d/%m/%Y')
            data['OLD BRAND NAME'] = data['Client']

            
            master = data[['Month', 'OLD BRAND NAME', 'Company', 'Brand', 'Status', 'Assignment', 
                        'Type of Assignment', 'Territory', 'Region', 'Current Agency MATCH', 
                        'Current Agency Description', 'Incumbent MATCH', 'Incumbent Agency Description', 
                        'Category_y', 'Est Billings']]
            
            
            
            master = master.rename(columns={'Category_y': 'Categories Updated', 'Month':'Date', 'Incumbent Agency Description': 'Incumbant Agency Description'})
            
            master['Date'] = pd.to_datetime(master['Date'])
            master['Date'] = master['Date'].dt.strftime('%d/%m/%Y')
            
            current_date = datetime.now()
            formatted_date = current_date.strftime('%m.%d.%y')
            file_name = f"{formatted_date} Assignments_Master Sheet.xlsx"
            
            st.write("Processed Master Data", master)
            
            last_filled_row = master_sheet.shape[0] 
            
            st.write("Last filled row in master_sheet:", last_filled_row)
            combined_data = pd.concat([master_sheet, master], ignore_index=True)
            
            st.write("Combined Data:", combined_data)
            
            @st.cache_data
            def convert_df(data):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    data.to_excel(writer, index=False, sheet_name='Master Data')
                    writer.close()
                output.seek(0)
                return output.getvalue()

            st.download_button(
                label="Download Master Data as Excel",
                data=convert_df(combined_data),
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the file from GitHub: {e}")

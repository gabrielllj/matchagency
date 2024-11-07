import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import re

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
    st.title("Excel Data Processor")

    # Step 1: File Upload for Excel
    uploaded_excel = st.file_uploader("Upload your Excel file (.xlsx or .xlsm)", type=["xlsx", "xlsm"])

    # URL for the agency match Excel file stored in GitHub
    github_xlsx_url = st.text_input("Enter GitHub Excel file URL", 
                                    "https://raw.githubusercontent.com/gabrielllj/matchagency/master/agency_match.xlsx")

    if uploaded_excel:
        # Read the uploaded Excel file
        data = pd.read_excel(uploaded_excel, sheet_name='Media Wins', header=7)

        # Attempt to load agency matches from GitHub URL
        try:
            response = requests.get(github_xlsx_url)
            response.raise_for_status()  # Raise error for bad status codes
            agency_matches = pd.read_excel(BytesIO(response.content))

            # Process the data
            
            
            data.columns = data.columns.str.replace(r'\s+', ' ', regex=True).str.replace(' ', '')
            data['Client'] = data['Client'].str.strip()
            data['Agency'] = data['Agency'].str.strip()
            data['Agency'] = data['Agency'].str.title()
            data['Status'] = 'Awarded'
            data['Market'] = data['Market'].astype(str)
            data['Remark'] = data['Remark'].astype(str)
            data['Type of Assignment'] = 'AOR/Project - ' + data['Remark']
            data['Current Agency Description'] = data['Agency']
            data['Incumbent Agency Description'] = data['Incumbent']
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
            
            # data['Incumbent Agency Description'] = data['Incumbent Agency Description'].str.strip()
            # data['Incumbent Agency Description'] = data['Incumbent Agency Description'].str.title()
            # Merge with agency matches data
            data = data.merge(
                agency_matches[['Agency Description', 'Match']], 
                how='left', 
                left_on='Current Agency Description', 
                right_on='Agency Description'
            )
            data = data.rename(columns={'Match': 'Current Agency MATCH'}).drop(columns=['Agency Description'])
            
            # data = data.merge(
            #     agency_matches[['Agency Description', 'Match']], 
            #     how='left', 
            #     left_on='Incumbent Agency Description', 
            #     right_on='Agency Description'
            # )
            # data = data.rename(columns={'Match': 'Incumbent MATCH'}).drop(columns=['Agency Description'])
            
            data['Assignment'] = 'Media'
            data['Territory'] = data['Market']
            
            data['Territory'] = data['Territory'].apply(clean_territory)
            data['Territory'] = data['Territory'].replace(territory_mapping)

            data['Market'] = data['Market'].apply(clean_territory)
            data['Market'] = data['Market'].replace(territory_mapping)
            
            data['Region2'] = data['Market'].apply(lambda x: map_market_to_region(x, territories))

            data['Categories Updated'] = 'Fill out later'
            data['Est Billings'] = data['Billings(US$k)'].apply(lambda x: "USD${:,.0f}".format(x))
            data = data.drop('Region', axis=1)
            data['Month'] = pd.to_datetime(data['Month'] + ' 2024', format='%b %Y').dt.strftime('%d/%m/%Y')
            data['OLD BRAND NAME'] = data['Client']
            data['Company'] = 'Fill out later'
            data['Brand'] = 'Fill out later'

            
            master = data[['Month', 'OLD BRAND NAME', 'Company', 'Brand', 'Status', 'Assignment', 
                        'Type of Assignment', 'Territory', 'Region2', 'Current Agency MATCH', 
                        'Current Agency Description', 'Incumbent MATCH', 'Incumbent Agency Description', 
                        'Categories Updated', 'Est Billings']]
            
            master = master.rename(columns={'Region2': 'Region'})
            # Display processed data
            st.write("Processed Master Data", master)

            # Function to convert DataFrame to Excel
            @st.cache_data
            def convert_df(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Master Data')
                    writer.close()
                output.seek(0)
                return output.getvalue()

            # Download button for the processed data
            st.download_button(
                label="Download Master Data as Excel",
                data=convert_df(master),
                file_name="master_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching the file from GitHub: {e}")

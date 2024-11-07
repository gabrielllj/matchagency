import streamlit as st
import pandas as pd
from io import BytesIO

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
    "Middle East": "EMEA",
    "Moldova": "EMEA",
    "Morocco": "EMEA",
    "Multi-city": "Global",
    "Multi-market": "Global",
    "Myanmar": "Asia Pacific/ APAC",
    "Netherlands": "EMEA",
    "Netherlands, Belgium": "EMEA",
    "New Zealand": "Asia Pacific/ APAC",
    "Nigeria": "EMEA",
    "Nigeria, Ghana, Kenya, Ivory Coast, Uganda, Morocco, Tunisia": "EMEA",
    "North America": "North America",
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
    "Taiwan": "Asia Pacific/ APAC",
    "Thailand": "Asia Pacific/ APAC",
    "Thailand, Laos": "Asia Pacific/ APAC",
    "Turkey": "EMEA",
    "UK": "EMEA",
    "UK, Ireland": "EMEA",
    "UK, Mexico": "Global",
    "Ukraine": "EMEA",
    "United Arab Emirates": "EMEA",
    "United Arab Emirates, Kenya, South Africa, Morocco, Nigeria, Turkey, Algeria": "EMEA",
    "Uruguay": "LATAM",
    "Uruguay, El Salvador, Panama, Paraguay, Nicaragua, Honduras, Venezuela, Dominican Republic, Bolivia, Guatemala, Ecuador, Costa Rica, Peru, Argentina, Chile": "LATAM",
    "US": "North America",
    "US, Canada": "North America",
    "US, Canada, LATAM": "Global",
    "US, UK": "Global",
    "Vietnam": "Asia Pacific/ APAC"
}

if __name__ == "__main__":
    
    st.title("Excel Data Processor")

    # Step 1: File Upload for Excel
    uploaded_excel = st.file_uploader("Upload your Excel file (.xlsx or .xlsm)", type=["xlsx", "xlsm"])

    # URL for the agency match Excel file stored in GitHub
    github_xlsx_url = st.text_input("https://raw.githubusercontent.com/gabrielllj/matchagency/main/agency_matches.xlsx")

    if uploaded_excel:
        # Read Excel file
        data = pd.read_excel(uploaded_excel, sheet_name='Media Wins', header=7)
        data.columns = data.columns.str.replace(r'\s+', ' ', regex=True).str.replace(' ', '')

        # Data Processing
        data['Client'] = data['Client'].str.strip().str.title()
        data['Agency'] = data['Agency'].str.strip().str.title()
        data['Status'] = 'Awarded'
        data['Market'] = data['Market'].astype(str)
        data['Remark'] = data['Remark'].astype(str)

        data['Type of Assignment'] = 'AOR/Project ' + data['Remark']
        data['Assignment'] = 'Media'
        data['Territory'] = data['Market']
        data['Region2'] = data['Market'].apply(lambda x: map_market_to_region(x, territories))
        data['Current Agency MATCH'] = None
        data['Current Agency Description'] = data['Agency']
        
        # Placeholder columns for future use
        data['Incumbent MATCH'] = 'Fill out later'
        data['Incumbent Agency Description'] = 'Fill out later'
        data['Categories Updated'] = 'Fill out later'
        data['Est Billings'] = data['Billings(US$k)'].apply(lambda x: "USD${:,.0f}".format(x))
        data = data.drop('Region', axis=1, errors='ignore')
        data['Month'] = pd.to_datetime(data['Month'] + ' 2024', format='%b %Y', errors='coerce').dt.strftime('%d/%m/%Y')
        data['OLD BRAND NAME'] = data['Client']
        data['Company'] = 'Fill out later'
        data['Brand'] = 'Fill out later'

        master = data[['Month', 'OLD BRAND NAME', 'Company', 'Brand', 'Status', 'Assignment', 
                        'Type of Assignment', 'Territory', 'Region2', 'Current Agency MATCH', 
                        'Current Agency Description', 'Incumbent MATCH', 'Incumbent Agency Description', 
                        'Categories Updated', 'Est Billings']]

        # Step 3: Load agency matches from GitHub Excel
        if github_xlsx_url:
            try:
                # Read the GitHub Excel file
                agency_matches = pd.read_excel(github_xlsx_url)
                
                # Assuming the Excel has a column named 'Agency Description' for matching
                if 'Agency Description' in agency_matches.columns:
                    # # Perform matching using the DataFrame
                    # def match_agency(agency):
                    #     match_row = agency_matches[agency_matches['Agency Description'].str.lower() == agency.lower()]
                    #     return match_row['Match'].values[0] if not match_row.empty else agency  # return agency if no match found
                    
                    # data['Current Agency MATCH'] = data['Agency'].apply(match_agency)
                    
                    data = data.merge(
                        agency_matches[['Agency Description', 'Match']], 
                        how='left', 
                        left_on='Current Agency Description', 
                        right_on='Agency Description'
                    )
                    data = data.rename(columns={'Match': 'Current Agency MATCH'}).drop(columns=['Agency Description'])
                else:
                    st.error("The uploaded Excel file does not contain 'Agency Description' column.")
            except Exception as e:
                st.error(f"Error loading Excel from GitHub: {e}")

        # Display processed data
        st.write("Processed Master Data", master)

        # Step 4: Download Button for Processed Data
        @st.cache_data
        def convert_df(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Master Data')
                writer.close()  # Close the writer to save the file
            output.seek(0)  # Reset the pointer to the start of the file
            return output.getvalue()

        st.download_button(
            label="Download Master Data as Excel",
            data=convert_df(master),
            file_name="master_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
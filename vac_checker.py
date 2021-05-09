import streamlit as st
from PIL import Image
from fake_useragent import UserAgent
import requests
import pandas as pd

ua = UserAgent()
header = {'User-Agent': str(ua.chrome)}

def run():
    img1 = Image.open('./meta/vac.png')
    img1 = img1.resize((400,400))
    st.image(img1,use_column_width=False)
    st.title("Vaccination Centre Checker")

    st.markdown("<h4 style='text-align: left; color: red;'>* Data is based on Government API</h4>",
                unsafe_allow_html=True)

    ## Area Pin
    area_pin = st.text_input('Enter your Area Pin-Code Eg.380018')

    ## Date
    vac_date = st.date_input("Date")

    ## Age
    age_display = ['18-45','45+']
    age = st.selectbox("Your Age",age_display)

    if st.button("Search"):
        try:
            vac_date = str(vac_date).split('-')
            new_date = vac_date[2]+'-'+vac_date[1]+'-'+vac_date[0]
            age_val = 0
            if age == '18-45':
                age_val = 18
            else:
                age_val = 45
            response = requests.get(
                f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={area_pin}&date={new_date}",
                headers=header)
            data = response.json()
            centers = pd.DataFrame(data.get('centers'))
            if centers.empty:
                st.warning("No centres found for "+new_date+' in '+str(area_pin)+' Check Later!')
            else:
                session_ids = []
                for j, row in centers.iterrows():
                    session = pd.DataFrame(row['sessions'][0])
                    session['center_id'] = centers.loc[j, 'center_id']
                    session_ids.append(session)

                sessions = pd.concat(session_ids, ignore_index=True)
                av_centeres = centers.merge(sessions, on='center_id')
                av_centeres.drop(columns=['sessions', 'session_id', 'lat', 'block_name', 'long','date', 'from', 'to','state_name','district_name','pincode','vaccine_fees'], inplace=True,errors='ignore')
                av_centeres = av_centeres[av_centeres['min_age_limit'] == age_val]
                # print(av_centeres)
                print(av_centeres.columns)
                new_df = av_centeres.copy()
                print(new_df)
                new_df.columns = ['Center_ID', 'Name', 'Address', 'Fee',
       'Availability', 'Minimum Age', 'Vaccine Type', 'Timing']
                new_df = new_df[['Center_ID', 'Name', 'Fee',
       'Availability', 'Minimum Age', 'Vaccine Type', 'Timing','Address']]
                st.dataframe(new_df.assign(hack='').set_index('hack'))
                # if not st.button("Download"):
                #     csv_date = new_date.replace('-', '_')
                #     new_df.to_csv(area_pin+'_'+csv_date+'.csv')
                #     st.success("CSV Downloaded")

        except Exception as e:
            st.error("Something went wrong!!")
            print(e)

run()
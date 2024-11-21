import pandas as pd
from tools import tools

print("Running tracker cron!")

df = tools.sql2pd("tracker_db", "tracker")
dft, ovp = tools.gen_overview_page(df)
tools.create_or_update_page("Tracker", ovp)

for id in dft.id.values.astype(list):
    wt = "[[Category:Tracker]]\n"
    df_c = df[(df.id == id)].copy()
    df_c['datetime'] = pd.to_datetime(df_c['ts'], unit = "s")
    df_c['time'] = df_c['datetime'].dt.strftime('%H:%M')


    conv_date_m  = dft[dft.id == id].ymd.values[0]
    conv_date_h  = dft[dft.id == id].human_date.values[0]

    title = conv_date_m + ":" + id
    wt += f"= {conv_date_h} =\n"

    for i in df_c.index:
        line = ( 
            "<strong>" + df_c.loc[i, "role"] + "</strong>"
            " <small>(" +  df_c.loc[i, "time"] + "):</small> " +  
            "<markdown>" + df_c.loc[i, "text"] + "</markdown>" +
            df_c.loc[i, "buttons"] + "\n\n\n" )
        
        wt += line

    tools.create_or_update_page(title, wt)

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta


def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    columns = [field['id'] for field in data['fields']]

    print("id columns: ", columns)
    
    df = pd.DataFrame(data['records'], columns=columns)

    print("df:")
    print(df)
    
    return df

def clean_data_labels(df):
    df['ARAC_DURUMU'] = df['ARAC_DURUMU'].str.replace('ARIZALI', 'Arızalı')
    df['ARAC_DURUMU'] = df['ARAC_DURUMU'].str.replace('KAZALI', 'Kazalı')
    df['ARAC_DURUMU'] = df['ARAC_DURUMU'].str.replace('Hasarlı', 'Kazalı')
    
    df['HAVA_DURUMU'] = df['HAVA_DURUMU'].str.replace('AÇIK', 'Açık')

    print("clean df:")
    print(df)
    
    return df

def calculate_intervention_time(df):
    df['TARIH'] = pd.to_datetime(df['TARIH'])

    print("datetime to date:")
    print(df)
    
    df['BILDIRIM_SAATI'] = pd.to_datetime(df['BILDIRIM_SAATI'], format='%H:%M:%S').dt.time
    df['MUDAHALE_SAATI'] = pd.to_datetime(df['MUDAHALE_SAATI'], format='%H:%M:%S').dt.time
    
    df['BILDIRIM_DATETIME'] = pd.to_datetime(df['TARIH'].dt.date.astype(str) + ' ' + df['BILDIRIM_SAATI'].astype(str))
    df['MUDAHALE_DATETIME'] = pd.to_datetime(df['TARIH'].dt.date.astype(str) + ' ' + df['MUDAHALE_SAATI'].astype(str))
    
    df['MUDAHALE_SURE_DK'] = (df['MUDAHALE_DATETIME'] - df['BILDIRIM_DATETIME']).dt.total_seconds() / 60
    
    df = df[(df['MUDAHALE_SURE_DK'] >= 0) & (df['MUDAHALE_SURE_DK'] <= 300)]
    
    print("dates parsed as hours parsed and interval added df:")
    print(df)
    
    return df

def add_weekly_analysis(df):
    df['YIL'] = df['TARIH'].dt.year
    df['HAFTA'] = df['TARIH'].dt.isocalendar().week
    df['HAFTA_YIL'] = df['YIL'].astype(str) + '-W' + df['HAFTA'].astype(str).str.zfill(2)
    
    df['GUN_ADI'] = df['TARIH'].dt.day_name()
    df['GUN_ADI_TR'] = df['GUN_ADI'].map({
        'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday',
        'Thursday': 'Thursday', 'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'
    })
    
    return df

def create_intervention_time_visualization(df):
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Towing Services - Intervention Time Analysis', fontsize=16, fontweight='bold')
    fig.canvas.manager.set_window_title('Intervention Time Analysis')
    
    axes[0,0].hist(df['MUDAHALE_SURE_DK'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].axvline(df['MUDAHALE_SURE_DK'].mean(), color='red', linestyle='--', 
                     label=f'Average: {df["MUDAHALE_SURE_DK"].mean():.1f} min')
    axes[0,0].axvline(df['MUDAHALE_SURE_DK'].median(), color='green', linestyle='--', 
                     label=f'Median: {df["MUDAHALE_SURE_DK"].median():.1f} min')
    axes[0,0].set_xlabel('Intervention Time (minutes)')
    axes[0,0].set_ylabel('Frequency')
    axes[0,0].set_title('Intervention Time Distribution')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    df.boxplot(column='MUDAHALE_SURE_DK', by='ARAC_DURUMU', ax=axes[0,1])
    axes[0,1].set_title('Intervention Times by Vehicle Status')
    axes[0,1].set_xlabel('Vehicle Status')
    axes[0,1].set_ylabel('Intervention Time (minutes)')
    axes[0,1].grid(True, alpha=0.3)
    
    ilce_sure = df.groupby('ILCE')['MUDAHALE_SURE_DK'].mean().sort_values(ascending=True)
    ilce_sure.plot(kind='barh', ax=axes[1,0], color='lightcoral')
    axes[1,0].set_title('Average Intervention Times by District')
    axes[1,0].set_xlabel('Average Intervention Time (minutes)')
    axes[1,0].grid(True, alpha=0.3)
    
    hava_sure = df.groupby('HAVA_DURUMU')['MUDAHALE_SURE_DK'].mean().sort_values(ascending=True)
    hava_sure.plot(kind='bar', ax=axes[1,1], color='lightgreen')
    axes[1,1].set_title('Average Intervention Times by Weather')
    axes[1,1].set_xlabel('Weather Condition')
    axes[1,1].set_ylabel('Average Intervention Time (minutes)')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def create_weekly_analysis(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Towing Services - Weekly Analysis', fontsize=16, fontweight='bold')
    fig.canvas.manager.set_window_title('Weekly Analysis')
    
    haftalik_sure = df.groupby('HAFTA_YIL')['MUDAHALE_SURE_DK'].mean().reset_index()
    haftalik_sure = haftalik_sure.sort_values('HAFTA_YIL')
    
    axes[0,0].plot(range(len(haftalik_sure)), haftalik_sure['MUDAHALE_SURE_DK'], 
                   marker='o', linewidth=1, markersize=6, color='blue')
    axes[0,0].set_title('Weekly Average Intervention Times')
    axes[0,0].set_xlabel('Week')
    axes[0,0].set_ylabel('Average Intervention Time (minutes)')
    axes[0,0].grid(True, alpha=0.3)
    axes[0,0].tick_params(axis='x', rotation=45)
    
    step = max(1, len(haftalik_sure) // 10)
    axes[0,0].set_xticks(range(0, len(haftalik_sure), step))
    axes[0,0].set_xticklabels(haftalik_sure['HAFTA_YIL'].iloc[::step], rotation=45)
    
    haftalik_sayı = df.groupby('HAFTA_YIL').size().reset_index()
    haftalik_sayı = haftalik_sayı.sort_values('HAFTA_YIL')
    
    axes[0,1].bar(range(len(haftalik_sayı)), haftalik_sayı[0], color='orange', alpha=0.7)
    axes[0,1].set_title('Weekly Total Towing Count')
    axes[0,1].set_xlabel('Week')
    axes[0,1].set_ylabel('Total Towing Count')
    axes[0,1].grid(True, alpha=0.3)
    axes[0,1].tick_params(axis='x', rotation=45)
    
    axes[0,1].set_xticks(range(0, len(haftalik_sayı), step))
    axes[0,1].set_xticklabels(haftalik_sayı['HAFTA_YIL'].iloc[::step], rotation=45)
    
    gun_sure = df.groupby('GUN_ADI_TR')['MUDAHALE_SURE_DK'].mean()
    gun_sirasi = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    gun_sure = gun_sure.reindex(gun_sirasi)
    
    gun_sure.plot(kind='bar', ax=axes[1,0], color='purple', alpha=0.7)
    axes[1,0].set_title('Average Intervention Times by Day of Week')
    axes[1,0].set_xlabel('Day of Week')
    axes[1,0].set_ylabel('Average Intervention Time (minutes)')
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].grid(True, alpha=0.3)
    
    haftalik_sure['MA_3'] = haftalik_sure['MUDAHALE_SURE_DK'].rolling(window=3).mean()
    haftalik_sure['MA_5'] = haftalik_sure['MUDAHALE_SURE_DK'].rolling(window=5).mean()
    
    axes[1,1].plot(range(len(haftalik_sure)), haftalik_sure['MUDAHALE_SURE_DK'], 
                   alpha=0.5, label='Weekly Average', color='lightblue')
    axes[1,1].plot(range(len(haftalik_sure)), haftalik_sure['MA_3'], 
                   linewidth=2, label='3-Week Moving Average', color='red')
    axes[1,1].plot(range(len(haftalik_sure)), haftalik_sure['MA_5'], 
                   linewidth=2, label='5-Week Moving Average', color='green')
    axes[1,1].set_title('Intervention Time Trend Analysis')
    axes[1,1].set_xlabel('Week')
    axes[1,1].set_ylabel('Intervention Time (minutes)')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    axes[1,1].tick_params(axis='x', rotation=45)
    
    axes[1,1].set_xticks(range(0, len(haftalik_sure), step))
    axes[1,1].set_xticklabels(haftalik_sure['HAFTA_YIL'].iloc[::step], rotation=45)
    
    plt.tight_layout()
    plt.show()

def main():
    df = load_data()
    
    df = clean_data_labels(df)
    
    df = calculate_intervention_time(df)
    
    df = add_weekly_analysis(df)
    
    create_intervention_time_visualization(df)
    create_weekly_analysis(df)
    
if __name__ == "__main__":
    main()








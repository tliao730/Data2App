# main.py
import matplotlib.pyplot as plt
from core import DataFrame

def main():
    # 1. 載入資料 (Ingestion)
    print("正在載入資料...")
    # 使用我們定義的 from_csv，它底層會呼叫 io_module.load_csv_advanced
    df = DataFrame.from_csv('spotify_songs.csv')
    print(f"成功載入 {df.row_count} 筆資料。")
    
    # 簡單檢視前幾筆資料 (Optional)
    # print(df.head())

    # 2. 資料處理與聚合 (Processing)
    print("正在進行分組聚合分析...")
    
    # 根據 'playlist_genre' 分組
    grouped_genre = df.groupby('playlist_genre')
    
    # 計算：平均受歡迎度 (mean) 和 歌曲數量 (count)
    genre_stats = grouped_genre.aggregate({
        'track_popularity': 'mean',
        'track_id': 'count'  # 用 track_id 來計算數量
    })

    # 3. 準備繪圖資料 (Extraction for Plotting)
    # 因為我們的 DataFrame 是自己寫的，沒有內建 plot，所以把資料拿出來給 matplotlib 用
    genres = genre_stats['playlist_genre']
    avg_popularity = genre_stats['track_popularity_mean']
    song_counts = genre_stats['track_id_count']

    # 4. 視覺化 (Visualization)
    plt.style.use('ggplot') # 設定好看的樣式
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 左圖：平均受歡迎度
    ax1.bar(genres, avg_popularity, color='skyblue', edgecolor='black')
    ax1.set_title('Average Track Popularity by Genre')
    ax1.set_xlabel('Genre')
    ax1.set_ylabel('Avg Popularity')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_ylim(0, 100) # 受歡迎度通常是 0-100

    # 右圖：歌曲數量分佈
    ax2.bar(genres, song_counts, color='salmon', edgecolor='black')
    ax2.set_title('Number of Songs by Genre')
    ax2.set_xlabel('Genre')
    ax2.set_ylabel('Count')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()
    
    # 顯示或存檔
    output_file = 'genre_analysis.png'
    plt.savefig(output_file)
    print(f"分析完成！圖表已儲存為 {output_file}")
    plt.show()

if __name__ == "__main__":
    main()
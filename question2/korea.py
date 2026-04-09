import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. CSV 파일 읽기 (CP949 인코딩 권장, utf-8은 깨질 수 있음)
    df = pd.read_csv('kosis.csv', encoding='cp949')

    # 컬럼 확인
    print("컬럼 확인:", df.columns)

    # 2. '일반가구원' 컬럼만 남기고 필요없는 컬럼 제거
    df = df[['성별', '연령별', '시점', '일반가구원']].copy()

    # 3. '일반가구원' 숫자형으로 변환
    df['일반가구원'] = pd.to_numeric(df['일반가구원'], errors='coerce')

    # 4. 2015년 이후 데이터만 사용
    df = df[df['시점'] >= 2015]

    # 5. 남자/여자 연도별 합계
    gender_df = df.groupby(['성별', '시점'])['일반가구원'].sum().unstack()
    print("\n남자/여자 연도별 일반가구원 통계")
    print(gender_df)

    # 6. 연령별 연도별 합계
    age_df = df.groupby(['연령별', '시점'])['일반가구원'].sum().unstack()
    print("\n연령별 연도별 일반가구원 통계")
    print(age_df)

    # 7. 성별 꺾은선 그래프
    gender_df.T.plot(figsize=(10, 5), marker='o')
    plt.title('성별 연도별 일반가구원 변화')
    plt.xlabel('연도')
    plt.ylabel('인구수')
    plt.grid(True)
    plt.show()

    # 8. 연령별 꺾은선 그래프
    age_df.T.plot(figsize=(12, 6), marker='o')
    plt.title('연령별 연도별 일반가구원 변화')
    plt.xlabel('연도')
    plt.ylabel('인구수')
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
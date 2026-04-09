import csv
import pandas as pd
import matplotlib.pyplot as plt


def load_csv_to_list(file_name):
    data = []
    with open(file_name, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data


def merge_data(train_data, test_data):
    return train_data + test_data


def convert_to_dataframe(data):
    return pd.DataFrame(data)


def check_total_count(df):
    print('전체 데이터 수 :', len(df))


def find_correlation(df):
    df = df.copy()

    df['Transported'] = df['Transported'].apply(lambda x: 1 if str(x) == 'True' else 0)

    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
    df['RoomService'] = pd.to_numeric(df['RoomService'], errors='coerce')
    df['FoodCourt'] = pd.to_numeric(df['FoodCourt'], errors='coerce')
    df['ShoppingMall'] = pd.to_numeric(df['ShoppingMall'], errors='coerce')
    df['Spa'] = pd.to_numeric(df['Spa'], errors='coerce')
    df['VRDeck'] = pd.to_numeric(df['VRDeck'], errors='coerce')

    numeric_df = df.select_dtypes(include=['float64', 'int64'])

    correlation = numeric_df.corr()['Transported'].sort_values(ascending=False)

    print('\n[Transported와 상관관계]')
    print(correlation)


def age_group_analysis(df):
    df = df.copy()

    df['Transported'] = df['Transported'].apply(lambda x: 1 if str(x) == 'True' else 0)
    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    bins = [0, 10, 20, 30, 40, 50, 60, 70, 100]
    labels = ['10대 이하', '10대', '20대', '30대', '40대', '50대', '60대', '70대 이상']

    df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels)

    result = df.groupby('AgeGroup')['Transported'].mean()

    print('\n[연령대별 Transported 비율]')
    print(result)

    result.plot(kind='bar')
    plt.title('연령대별 Transported 비율')
    plt.xlabel('연령대')
    plt.ylabel('비율')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def destination_age_distribution(df):
    df = df.copy()

    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

    bins = [0, 20, 40, 60, 80]
    labels = ['~20', '21~40', '41~60', '61~']

    df['AgeGroup'] = pd.cut(df['Age'], bins=bins, labels=labels)

    result = df.groupby(['Destination', 'AgeGroup']).size().unstack()

    result.plot(kind='bar', stacked=True)
    plt.title('Destination별 연령대 분포')
    plt.xlabel('Destination')
    plt.ylabel('인원 수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    train_data = load_csv_to_list('train.csv')
    test_data = load_csv_to_list('test.csv')

    merged_data = merge_data(train_data, test_data)

    df = convert_to_dataframe(merged_data)
    train_df = convert_to_dataframe(train_data)

    check_total_count(df)

    find_correlation(train_df)
    age_group_analysis(train_df)

    destination_age_distribution(df)


if __name__ == '__main__':
    main()
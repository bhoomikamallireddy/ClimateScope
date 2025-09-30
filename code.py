import pandas as pd
df = pd.read_csv("data/GlobalWeatherRepository.csv")

print(df.head())
print(df.info())       # column info
print(df.describe())
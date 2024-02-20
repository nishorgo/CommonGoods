import pandas as pd
from statsmodels.tsa.holtwinters import SimpleExpSmoothing 


def exp_smoothing_forecast():
    df = pd.read_excel('Product demand.xlsx')
    forecast_dict = {}

    for _, row in df.iterrows():
        product = row.iloc[0]
        data = pd.Series(row[2:]).to_numpy().astype(float)
        model = SimpleExpSmoothing(data)
        model_fit = model.fit(smoothing_level=0.2, optimized=False)
        forecast = model_fit.forecast(1)
        forecast_dict[product] = forecast

    return forecast_dict
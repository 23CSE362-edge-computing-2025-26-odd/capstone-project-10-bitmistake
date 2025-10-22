import warnings
import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt  # <-- added for plotting
warnings.filterwarnings('ignore')

def simulate_patient(id, freq, length):
    '''
    Simulate a single patient's CGM time series.
    '''
    np.random.seed(id)
    
    ts = pd.date_range(
        start=pd.Timestamp(datetime.date.today()) - pd.Timedelta(days=length),
        end=pd.Timestamp(datetime.date.today()) - pd.Timedelta(minutes=freq),
        freq=f'{freq}T'
    )
    
    gl = np.random.uniform(low=70, high=180)
    gl += sm.tsa.arma_generate_sample(
        ar=np.r_[1, - np.array([.75, -.25])],
        ma=np.r_[1, np.array([.65, .35])],
        scale=10.,
        nsample=len(ts)
    )
    
    def simulate_timestamps(hours):
        fn = lambda date: datetime.datetime.combine(
            date=date,
            time=datetime.time(
                hour=np.random.choice(a=hours),
                minute=np.random.choice(a=np.arange(start=freq, stop=60, step=freq))
            )
        )
        return [fn(date) for date in ts.to_series().dt.date.unique()]
    
    # upward spikes
    gl[ts.to_series().isin(simulate_timestamps(hours=[6, 7, 8]))] = np.random.uniform(low=180, high=400, size=length)
    gl[ts.to_series().isin(simulate_timestamps(hours=[12, 13, 14]))] = np.random.uniform(low=180, high=400, size=length)
    gl[ts.to_series().isin(simulate_timestamps(hours=[18, 19, 20]))] = np.random.uniform(low=180, high=400, size=length)
    
    # downward spikes
    gl[ts.to_series().isin(simulate_timestamps(hours=[9, 10, 11]))] = np.random.uniform(low=20, high=70, size=length)
    gl[ts.to_series().isin(simulate_timestamps(hours=[15, 16, 17]))] = np.random.uniform(low=20, high=70, size=length)
    gl[ts.to_series().isin(simulate_timestamps(hours=[21, 22, 23]))] = np.random.uniform(low=20, high=70, size=length)
    
    # smooth
    gl = gaussian_filter1d(input=gl, sigma=3)
    
    # missing values
    gl[np.random.randint(low=0, high=len(ts), size=int(0.1 * len(ts)))] = np.nan
    
    return pd.DataFrame({'id': id, 'ts': ts, 'gl': gl})


def simulate_patients(freq, length, num):
    '''
    Simulate multiple patients' CGM time series.
    '''
    data = pd.concat([simulate_patient(id, freq, length) for id in range(num)], axis=0)
    data = data.set_index('ts').groupby(by='id')['gl'].resample(f'{freq}T').last().reset_index()
    return data


# ------------------ Run Simulation and Plot ------------------
if __name__ == "__main__":
    # Example: 2 patients, 2 days, 15-min intervals
    df = simulate_patients(freq=15, length=2, num=2)

    # Plot each patient's glucose series
    plt.figure(figsize=(12, 6))
    for pid in df['id'].unique():
        patient_data = df[df['id'] == pid]
        plt.plot(patient_data['ts'], patient_data['gl'], marker='o', label=f'Patient {pid}')

    plt.title("Simulated Glucose Levels")
    plt.xlabel("Time")
    plt.ylabel("Glucose (mg/dL)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

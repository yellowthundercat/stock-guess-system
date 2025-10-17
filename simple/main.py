import json
import os
import sys

import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from attribute_finder.resources import get_anomaly_signal, get_company_list, get_company_p, get_invested_companies, get_recommend_price

company_file_name = os.path.join(os.path.dirname(__file__),  'companies.json')
company_insight_file_name = os.path.join(os.path.dirname(__file__),  'companies_insight.csv')
signal_file_name = os.path.join(os.path.dirname(__file__),  'signals.csv')

def main():
    print('Hello, World!')
    # update each 3 month
    # store_company_list()

    # update each week
    store_company_insight()
    # store_anomaly()


# store company list to json file: companies.json
def store_company_list():
    with open(company_file_name, 'r') as f:
        data = json.load(f)
        old_all_company = data['all_company']
        old_invested_company = data['invested_company']
        old_extended_company = data['extended_company']
    
    invested_company = get_invested_companies()
    all_company = get_company_list(min_equity=1000, min_volume=0.5)

    extended_company = []
    for c in all_company:
        if c not in invested_company:
            predict = get_recommend_price(c)    
            if predict > 0:
                extended_company.append(c)

    new_invested_company = [c for c in invested_company.keys() if c not in old_invested_company]
    new_all_company = [c for c in all_company if c not in old_all_company]
    new_extended_company = [c for c in extended_company if c not in old_extended_company]
    removed_invested_company = [c for c in old_invested_company.keys() if c not in invested_company]
    removed_all_company = [c for c in old_all_company if c not in all_company]
    removed_extended_company = [c for c in old_extended_company if c not in extended_company]
    if new_invested_company:
        print('New invested company:', new_invested_company)
    if new_all_company:
        print('New all company:', new_all_company)
    if new_extended_company:
        print('New extended company:', new_extended_company)
    if removed_invested_company:
        print('Removed invested company:', removed_invested_company)
    if removed_all_company:
        print('Removed all company:', removed_all_company)
    if removed_extended_company:
        print('Removed extended company:', removed_extended_company)

    with open(company_file_name, 'w') as f:
        json.dump({
            'all_company': all_company,
            'invested_company': invested_company,
            'extended_company': extended_company
        }, f)

# store company insight to csv file: companies_insight.csv
def store_company_insight():
    with open(company_file_name, 'r') as f:
        data = json.load(f)
        # all_company = data['all_company']
        invested_company: dict = data['invested_company']
        extended_company = data['extended_company']
    company_names = []
    pes = []
    avg_pes = []
    pbs = []
    avg_pbs = []
    lowest_weekly_change = []
    lowest_monthly_change = []
    delta_ma_200s = []
    funds = []
    recommend_prices = []
    current_prices = []
    predict_upsides = []
    merge_company = list(invested_company.keys()) + extended_company
    merge_company.sort()
    for c in merge_company:
        try:
            current_pe, current_pb, avg_pe, avg_pb, price, lowest_week, lowest_month, delta_ma_200 = get_company_p(c)
            company_names.append(c)
            pes.append(round(current_pe, 2))
            avg_pes.append(round(avg_pe, 2))
            pbs.append(round(current_pb, 2))
            avg_pbs.append(round(avg_pb, 2))
            funds.append(invested_company.get(c, 0))
            recommend = round(get_recommend_price(c, price), 2)
            recommend_prices.append(recommend)
            current_prices.append(price)
            predict = round((recommend - price) / price, 4)
            predict_upsides.append(predict)
            lowest_weekly_change.append(round((price - lowest_week) / lowest_week, 4))
            lowest_monthly_change.append(round((price - lowest_month) / lowest_month, 4))
            delta_ma_200s.append(round(delta_ma_200, 4))
        except Exception as e:
            print('Error:', c, e)
            continue

    df = pd.DataFrame({
        'Company': company_names,
        'P/E': pes,
        'AVG P/E': avg_pes,
        'P/B': pbs,
        'AVG P/B': avg_pbs,
        'Fund': funds,
        'Analysis': recommend_prices,
        'Current Price': current_prices,
        'Lowest Weekly Change': lowest_weekly_change,
        'Lowest Monthly Change': lowest_monthly_change,
        'Delta MA 200': delta_ma_200s,
        'Predict Upside': predict_upsides
    })
    df.to_csv(company_insight_file_name, index=False)

# store anomaly signal to csv file: signals.csv
def store_anomaly():
    cache_file = os.path.join(os.path.dirname(__file__),  'cache.json')
    with open(company_file_name, 'r') as f:
        data = json.load(f)
        all_company = data['all_company']
        invested_company: dict = data['invested_company']
        extended_company = data['extended_company']

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            names = cache['names']
            volume_spikes = cache['volume_spikes']
            volume_increases = cache['volume_increases']
            rsi_30s = cache['rsi_30s']
            rsi_70s = cache['rsi_70s']
            macd_crosses = cache['macd_crosses']
            total_signals = cache['total_signals']
            checked = cache['checked']
            is_invested = cache['is_invested']
    else:
        names = []
        volume_spikes = []
        volume_increases = []
        rsi_30s = []
        rsi_70s = []
        macd_crosses = []
        total_signals = []
        checked = []
        is_invested = []
    
    co = 0
    merge_company = list(invested_company.keys()) + extended_company
    merge_company.sort()
    for c in merge_company:
        if c in checked:
            continue

        is_volume_spike, is_volume_increase, is_rsi_30, is_rsi_70, is_macd_cross = get_anomaly_signal(c)
        checked.append(c)
        signal = int(is_volume_spike > 0) + int(is_volume_increase > 0)  + int(is_rsi_30) + int(is_rsi_70)
        if signal >= 1:
            names.append(c)
            volume_spikes.append(round(is_volume_spike, 4))
            volume_increases.append(round(is_volume_increase, 4))
            rsi_30s.append(is_rsi_30)
            rsi_70s.append(is_rsi_70)
            macd_crosses.append(is_macd_cross)
            total_signals.append(signal)
            if c in invested_company or c in extended_company:
                is_invested.append(True)
            else:
                is_invested.append(False)
            print('Anomaly signal:', c, signal)
        
        co += 1
        if co % 10 == 0:
            with open(cache_file, 'w') as f:
                json.dump({
                    'names': names,
                    'volume_spikes': volume_spikes,
                    'volume_increases': volume_increases,
                    'rsi_30s': rsi_30s,
                    'rsi_70s': rsi_70s,
                    'macd_crosses': macd_crosses,
                    'total_signals': total_signals,
                    'checked': checked,
                    'is_invested': is_invested
                }, f)
        
    df = pd.DataFrame({
        'Company': names,
        'Volume Spike': volume_spikes,
        'Volume Increase': volume_increases,
        'RSI 30': rsi_30s,
        'RSI 70': rsi_70s,
        'MACD Cross': macd_crosses,
        'Is Invested': is_invested,
        'Total Signals': total_signals
    })
    df.to_csv(signal_file_name, index=False)
    # delete cache file when done
    os.remove(cache_file)

if __name__ == '__main__':
	main()

# main()
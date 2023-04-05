import finplot as fplt

def plot_olhcv(df, show = True, volume = "volume"):

    df["volume"] = df[volume]

    # create two plots
    ax, ax2 = fplt.create_plot(rows=2)

    # plot candle sticks
    candle_src = fplt.PandasDataSource(
        df[['open', 'close', 'high', 'low']])
    fplt.candlestick_ochl(candle_src, ax=ax)

    # finally a volume bar chart in our second plot
    volume_src = fplt.PandasDataSource(df[['open', 'close', 'volume']])
    fplt.volume_ocv(volume_src, ax=ax2)

    if show:
        return fplt.show()
    return fplt
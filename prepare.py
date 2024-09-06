import numpy as np
import pandas as pd


DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/"
    "master/csse_covid_19_data/csse_covid_19_time_series/"
    "time_series_covid19_{kind}_{group}.csv"
)
REPLACE_AREA = {
    "Korea, South": "South Korea",
    "Taiwan*": "Taiwan",
    "Burma": "Myanmar",
    "Holy See": "Vatican City",
    "Diamond Princess": "Cruise Ship",
    "Grand Princess": "Cruise Ship",
    "MS Zaandam": "Cruise Ship",
}
GROUPS = "world", "usa"
KINDS = "deaths", "cases"


class PrepareData:

    def __init__(self, download_new=True):
        self.download_new = download_new

    def download_data(self, group, kind):
        group_change_dict = {"world": "global", "usa": "US"}
        kind_change_dict = {"deaths": "deaths", "cases": "confirmed"}
        group = group_change_dict[group]
        kind = kind_change_dict[kind]
        df = pd.read_csv(DOWNLOAD_URL.format(kind=kind, group=group))
        return df

    def write_data(self, data, directory, **kwargs):
        for name, df in data.items():
            df.to_csv(f"{directory}/{name}.csv", **kwargs)

    def read_local_data(self, group, kind):
        name = f"{group}_{kind}"
        return pd.read_csv(f"data/raw/{name}.csv")

    def select_columns(self, df):
        cols = df.columns
        areas = ["Country/Region", "Province_State"]
        is_area = cols.isin(areas)

        has_two_slashes = cols.str.count("/") == 2
        filt = is_area | has_two_slashes
        return df.loc[:, filt]

    def update_areas(self, df):
        area_col = df.columns[0]
        df[area_col] = df[area_col].replace(REPLACE_AREA)
        df = df[df[area_col] != "US"]
        return df

    def group_area(self, df):
        grouping_col = df.columns[0]
        return df.groupby(grouping_col).sum()

    def transpose_to_ts(self, df):
        df = df.T
        df.index = pd.to_datetime(df.index)
        return df

    def fix_bad_data(self, df):
        mask = df < df.cummax()
        df = df.mask(mask).interpolate().round(0).astype("int64")
        return df

    def run(self):
        data = {}
        for group in GROUPS:
            for kind in KINDS:
                if self.download_new:
                    df = self.download_data(group, kind)
                else:
                    df = self.read_local_data(group, kind)
                df = self.select_columns(df)
                df = self.update_areas(df)
                df = self.group_area(df)
                df = self.transpose_to_ts(df)
                df = self.fix_bad_data(df)
                data[f"{group}_{kind}"] = df
        return data


def combine_all_data(cm, dm):
    world_cases_d = cm.combined_daily["world_cases"]
    usa_cases_d = cm.combined_daily["usa_cases"]
    world_deaths_d = dm.combined_daily["world_deaths"]
    usa_deaths_d = dm.combined_daily["usa_deaths"]

    world_cases_d = world_cases_d.assign(USA=usa_cases_d.sum(axis=1))
    world_deaths_d = world_deaths_d.assign(USA=usa_deaths_d.sum(axis=1))

    world_cases_c = cm.combined_cumulative["world_cases"]
    usa_cases_c = cm.combined_cumulative["usa_cases"]
    world_deaths_c = dm.combined_cumulative["world_deaths"]
    usa_deaths_c = dm.combined_cumulative["usa_deaths"]

    world_cases_c = world_cases_c.assign(USA=usa_cases_c.sum(axis=1))
    world_deaths_c = world_deaths_c.assign(USA=usa_deaths_c.sum(axis=1))

    df_world = pd.concat(
        (
            world_deaths_d.stack(),
            world_cases_d.stack(),
            world_deaths_c.stack(),
            world_cases_c.stack(),
        ),
        axis=1,
        keys=["Daily Deaths", "Daily Cases", "Deaths", "Cases"],
    )

    df_usa = pd.concat(
        (
            usa_deaths_d.stack(),
            usa_cases_d.stack(),
            usa_deaths_c.stack(),
            usa_cases_c.stack(),
        ),
        axis=1,
        keys=["Daily Deaths", "Daily Cases", "Deaths", "Cases"],
    )
    df_all = pd.concat(
        (df_world, df_usa), keys=["world", "usa"], names=["group", "date", "area"]
    )
    df_all = df_all.sort_index()
    df_all.to_csv("data/all_data.csv")
    return df_all


def create_summary_table(df_all, last_date):
    df = df_all.query("date == @last_date")
    pop = pd.read_csv("data/population.csv")
    df = df.merge(pop, how="left", on=["group", "area"])
    df["Deaths per Million"] = (df["Deaths"] / df["population"]).round(0)
    df["Cases per Million"] = (df["Cases"] / df["population"]).round(-1)
    df["date"] = last_date
    df.to_csv("data/summary.csv", index=False)
    return df

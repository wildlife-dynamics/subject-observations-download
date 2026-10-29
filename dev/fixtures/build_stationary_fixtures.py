"""
Generates two mock fixtures for ecoscope.platform.tasks.io.get_subjectgroup_observations,
both derived from the platform's get-subjectgroup-observations.example-return.parquet so the
schema stays identical to what the real task returns:

  - get-subjectgroup-observations-stationary.example-return.parquet
      Three stationary subjects (weather stations). Every observation of a subject sits on
      the same point, which is the case that made Download Subject Tracks fail (compose#3189).
      Sensor readings (temperature, rainfall, humidity) sit in the observation_details JSON,
      as EarthRanger returns them when observation details are included.

  - get-subjectgroup-observations-mixed.example-return.parquet
      The same three weather stations plus the upstream moving subjects, in one group.

Usage (from the repo root, with the workflow's pixi env):

    pixi run --manifest-path ecoscope-workflows-subject-observations-download-workflow/pixi.toml \
        python dev/fixtures/build_stationary_fixtures.py <path/to/get-subjectgroup-observations.example-return.parquet>

Re-run this script (instead of editing the parquets by hand) if the upstream schema changes.
"""

import sys
import uuid
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

OUT_DIR = Path(__file__).parent
OUT_STATIONARY = OUT_DIR / "get-subjectgroup-observations-stationary.example-return.parquet"
OUT_MIXED = OUT_DIR / "get-subjectgroup-observations-mixed.example-return.parquet"

N_STATIONS = 3
OBS_PER_STATION = 48

stations = [
    {"name": "Weather Station A", "lon": 36.8219, "lat": -1.2921},
    {"name": "Weather Station B", "lon": 37.0722, "lat": -0.4169},
    {"name": "Weather Station C", "lon": 35.2698, "lat": -0.0917},
]


def build_stations(upstream: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    rng = np.random.default_rng(0)
    template = upstream.iloc[[0]]
    frames = []
    for station in stations[:N_STATIONS]:
        subject_id = str(uuid.uuid5(uuid.NAMESPACE_URL, station["name"]))
        source_id = str(uuid.uuid5(uuid.NAMESPACE_URL, station["name"] + "/source"))
        fixtimes = pd.date_range("2015-01-01T00:00:00Z", periods=OBS_PER_STATION, freq="h")
        rows = pd.concat([template] * OBS_PER_STATION, ignore_index=True)
        rows["extra__id"] = [str(uuid.uuid4()) for _ in range(OBS_PER_STATION)]
        rows["fixtime"] = fixtimes
        rows["extra__recorded_at"] = fixtimes
        rows["extra__created_at"] = fixtimes
        rows["extra__exclusion_flags"] = 0.0
        rows["extra__source"] = source_id
        rows["extra__subject_id"] = subject_id
        rows["groupby_col"] = subject_id
        rows["extra__subject__id"] = subject_id
        rows["extra__subject__name"] = station["name"]
        rows["extra__subject__subject_type"] = "stationary-object"
        rows["extra__subject__subject_subtype"] = "weather_station"
        rows["extra__subject__sex"] = None
        rows["extra__subject__tracks_available"] = False
        rows["extra__subject__hex"] = None
        rows["extra__subject__last_position"] = None
        rows["extra__location"] = [{"latitude": station["lat"], "longitude": station["lon"]}] * OBS_PER_STATION
        # every observation of a stationary subject is at the same point
        rows["geometry"] = gpd.points_from_xy([station["lon"]] * OBS_PER_STATION, [station["lat"]] * OBS_PER_STATION)
        # sensor readings live in the observation_details JSON, as EarthRanger returns them
        # with include_details=true; the first reading of each station has no details
        temperature = rng.normal(22, 4, OBS_PER_STATION).round(1)
        rainfall = rng.gamma(0.5, 2, OBS_PER_STATION).round(1)
        humidity = rng.integers(40, 90, OBS_PER_STATION)
        rows["extra__observation_details"] = [None] + [
            {"temperature": float(t), "rainfall": float(r), "humidity": int(h)}
            for t, r, h in zip(temperature[1:], rainfall[1:], humidity[1:])
        ]
        frames.append(rows)

    out = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=upstream.crs)
    return out.set_index(pd.Index(out["extra__id"], name=upstream.index.name))


def main(upstream_path: str) -> None:
    upstream = gpd.read_parquet(upstream_path)
    stationary = build_stations(upstream)
    stationary.to_parquet(OUT_STATIONARY)

    mixed = pd.concat([upstream, stationary])
    gpd.GeoDataFrame(mixed, geometry="geometry", crs=upstream.crs).to_parquet(OUT_MIXED)

    print(f"wrote {OUT_STATIONARY.name}: {len(stationary)} rows")
    print(f"wrote {OUT_MIXED.name}: {len(mixed)} rows")


if __name__ == "__main__":
    main(sys.argv[1])

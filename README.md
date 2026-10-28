# Subject Observations Download

## Introduction

This workflow downloads the individual observations for an EarthRanger subject group, one row per observation.

**What this workflow does:**
- Downloads every observation for the subjects in a subject group
- Works with **stationary subjects** (e.g. weather stations, camera traps, fixed sensors) as well as moving subjects
- Keeps each observation's own readings (e.g. temperature, rainfall) as columns
- Filters observations by location, and optionally by EarthRanger exclusion flags
- Exports data in CSV and/or Parquet
- Optionally creates a map of the observation points

**How it differs from Download Subject Tracks:** Download Subject Tracks joins consecutive observations into trajectory segments (with speed, distance and duration), which needs the subject to move. This workflow never builds tracks, so it gives you the raw points and works for subjects that stay in one place.

**Who should use this:**
- Anyone needing the point data for a subject, not only its track
- Teams downloading weather station or other fixed-sensor readings from EarthRanger
- Data analysts who want the raw observations for their own processing

## Prerequisites

Before using this workflow, you need:

1. **Ecoscope Desktop** installed on your computer
   - If you haven't installed it yet, please follow the installation instructions for Ecoscope Desktop

2. **EarthRanger Data Source** configured in Ecoscope Desktop
   - You must have already set up a connection to your EarthRanger server
   - Your data source should be configured with proper authentication credentials
   - You'll need to know the name of your configured data source (e.g., "mep_dev")

3. **Subject Group** set up in EarthRanger
   - You need to have at least one subject group configured in your EarthRanger system
   - You'll need to know the exact name of the subject group you want to download
   - Note: Using a group with mixed subtypes (e.g., animal species with weather stations) shows a warning on the dashboard

## Installation

1. Open Ecoscope Desktop
2. Select "Workflow Templates"
3. Click "+ Add Template"
4. Copy and paste this URL https://github.com/wildlife-dynamics/subject-observations-download and wait for the workflow template to be downloaded and initialized
5. The template will now appear in your available template list

## Configuration Guide

Once you've added the workflow template, you'll need to configure it for your specific needs. The configuration form is organized into the sections below, in the order they appear in the form. Several fields are tucked inside an **Advanced Configurations** disclosure within their section — expand it to reveal them. Sensible defaults are provided throughout, so a basic run only requires the first four sections.

#### 1. Workflow Details
Give your workflow a name and description to help you identify it later.

- **Workflow Name** (required): A descriptive name for this workflow run and the dashboard title
  - Example: `"Weather Stations - January 2015"`
- **Workflow Description** (optional): Additional details about this download
  - Example: `"Hourly readings for all weather stations"`

#### 2. Time Range
Specify the time period for the observations you want to download.

- **Timezone** (required): Use the dropdown to select your timezone. Observation times in the output are converted to this timezone
- **Since** (required): Use the calendar picker to select the start date and time
  - Example: `01/01/2015, 12:00 AM`
- **Until** (required): Use the calendar picker to select the end date and time
  - Example: `01/07/2015, 11:59 PM`

#### 3. Data Source
Select your EarthRanger connection.

- **Data Source** (required): Choose from your configured data sources
  - Example: Select `mep_dev` from the dropdown

#### 4. Subject Group
Choose which subject group to download.

- **Subject Group Name** (required): Enter the exact name of the subject group as it appears in EarthRanger. You can find them at https://<your-site>.pamdas.org/admin/observations/subjectgroup/
  - Example: `"Weather Stations"`

The following fields live under **Advanced Configurations** in this section:

- **Include Details**: Include additional details from each observation
  - Default: `false` (not included) — check to include detailed observation information
- **Include Subject Source Details**: Include information about the tracking device/source
  - Default: `false` (not included) — check to include device and source information
- **Filter**: Control which observations are returned based on EarthRanger's exclusion flags (data quality markers set on each observation)
  - `clean` (default): Only observations that have not been flagged as problematic
  - `none`: All observations regardless of exclusion flags (raw data)
  - `manually_filtered`: Only observations that were manually flagged
  - `automatically_filtered`: Only observations that were automatically flagged
  - `manually_and_automatically_filtered`: Observations flagged either manually or automatically

#### 5. Filter Data
Location filters that remove out-of-area or known-bad points. These apply to **both the generated map and the downloaded files**. Both fields sit under **Advanced Configurations** — defaults keep everything.

- **Bounding Box**: Restrict observations to a geographic area
  - Default: entire world (-180 to 180 longitude, -90 to 90 latitude)
- **Filter Exact Point Coordinates**: Exclude observations recorded at specific exact coordinates (e.g. known bad GPS fixes or test data)
  - Example: `[{"Latitude": 0.0, "Longitude": 0.0}]`

There is no trajectory segment filter: this workflow does not build tracks.

#### 6. Group Data (Optional)
Organize your data into separate files and map views based on time periods or categories.

- **Group by**: Create separate outputs grouped by:
  - Time: Year, Month, Day of week, Hour, etc.
  - Category: Subject Name, Subject Subtype, or Subject Sex. Grouping by Subject Name gives one file per station or subject.

#### 7. Refine Data (Optional)
Reshape and organize your data before downloading. **These steps apply to the downloaded files only — not the generated map.** Both fields sit under **Advanced Configurations**.

- **Process Columns → Drop Columns**: List of columns to drop from the downloaded files
  - Default includes common internal/system columns (e.g. `location`, `subject__content_type`, `subject__user`, `subjectsource__source`, and others)
  - Modify the list based on your requirements — add columns you want to hide or remove columns you want to keep
- **Apply SQL Query → Query**: Filter or transform the data with SQL
  - Use `df` as the table name. Example: `SELECT * FROM df WHERE subject__name = 'Weather Station A'`
  - Leave empty to skip. Complex columns (lists/dicts) are handled automatically.

#### 8. Download File Format
Choose how your data is saved.

- **Filetypes** (required): Output format(s) for the observation files
  - **CSV**: Standard spreadsheet format, opens in Excel
  - **Parquet**: Efficient format for geospatial data
  - Default: `Parquet`
- **Filename prefix** (under **Advanced Configurations**): Prefix for the output files (default `subject_observations`). A unique ID is appended automatically.

#### 9. Generate Maps
Control whether to create map visualizations.

- **Generate maps in dashboard**: Checked = a map is generated and shown in the dashboard
  - Default: checked. Uncheck to skip map generation (recommended for large datasets)
- **Map Base Layers** (under **Advanced Configurations**): Select one or more base layers for your map background
  - Default: Terrain and Satellite layers. The first layer in the list appears on the bottom.

## Running the Workflow

1. **Review your configuration** — double-check your time range, data source, and subject group
2. **Save and run** — click "Submit"; the workflow shows up in the "My Workflows" table. Click "Run" to start processing
3. **Monitor progress** — processing time depends on the size of your date range and the number of observations. The workflow completes with status "Success" or "Failed"

## Understanding Your Results

### Data Outputs

Your observations are saved in the format(s) you selected under *Filetypes*, one row per observation. Any **Process Columns** drops and **SQL Query** transforms in *Refine Data* apply to these files only — not to the map.

- **Contents**:
  - **fixtime**: Time of the observation, in the timezone you selected
  - **geometry**: The observation's location (a point)
  - **subject__name**, **subject__id**, **subject__subject_type**, **subject__subject_subtype**, **subject__sex**: Subject information
  - **id**, **source**: Observation and source identifiers
  - The observation's own values (e.g. a weather station's readings), with EarthRanger's `extra__` prefix removed
  - Observation details and subject source details, if you enabled them
- There are no speed, distance or duration columns — use Download Subject Tracks for those.

### Visual Outputs (When Maps are Generated)

- **Interactive map** of observation points, colored by subject
  - We respect the subject colors set on EarthRanger unless there are subjects with missing/duplicate colors
  - Tooltip shows time, subject name, subtype and sex
  - Legend showing subject names and their colors

### Grouped Outputs

If you configured data grouping, you'll receive separate files for each group, and the map is split into one view per group, selectable in the dashboard.

## Common Use Cases & Examples

### Example 1: Weather station readings for a week
**Configuration**:
- **Time Range**: `2015-01-01T00:00:00` to `2015-01-07T23:59:59`, `Africa/Nairobi (UTC+03:00)`
- **Subject Group Name**: `"Weather Stations"`
- **Group Data**: Category → `Subject Name`
- **Download File Format → Filetypes**: `CSV`

**Result**: One CSV per weather station with every reading for the week.

---

### Example 2: Raw GPS points for a group of animals, by month
**Configuration**:
- **Time Range**: `2015-01-01T00:00:00` to `2015-12-31T23:59:59`
- **Subject Group Name**: Your subject group
- **Group Data**: Time → `"%B"` (month name)
- **Download File Format → Filetypes**: `Parquet`

**Result**: One Parquet file of observations per month, and a map view per month.

---

### Example 3: Large dataset — skip maps
**Configuration**:
- **Subject Group Name**: Your subject group
- **Download File Format → Filetypes**: `Parquet`
- **Generate maps in dashboard**: Unchecked

**Result**: Parquet output with faster processing and no map.

## Troubleshooting

#### No observations returned
- Verify the date range is correct and that the subject group has observations in it
- Check that the subject group name is spelled exactly as it appears in EarthRanger (`https://<your-site>.pamdas.org/admin/observations/subjectgroup/`)
- Check the **Filter** setting under Subject Group — `clean` excludes flagged observations
- Check the **Bounding Box** and **Filter Exact Point Coordinates** settings are not excluding your subjects

#### Map won't generate
- Ensure "Generate maps in dashboard" is checked
- Check that your observations have coordinate data (not just null values)

#### Workflow runs very slowly
- Uncheck "Generate maps in dashboard" for large datasets
- Reduce the date range, or use only Parquet output

#### Authentication errors
- Re-configure your EarthRanger data source in Ecoscope Desktop
- Verify your user account has permission to view the subject group

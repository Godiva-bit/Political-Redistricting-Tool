# Political Redistricting Tool

**Author:** Godiva Martha Nakayima\
**Project:** Master's GIS Capstone, The Ohio State University

## Overview

The Political Redistricting Tool is an interactive QGIS decision-support
system for initializing, editing, evaluating, and exporting political
district plans. It combines a QGIS Processing Tool with an interactive
QGIS plugin. Users can begin with an existing district plan, reassign
Census Blocks, and immediately review updated district statistics and
map displays.

The workflow separates fine-scale editing from demographic analysis:
**Census Blocks supply editing geometry and exact population counts**,
while **Census Block Groups supply optional Communities of Interest
(COI) demographic context**. Its statistics and status indicators are
analytical aids, not legal determinations.

Ohio was the primary development dataset. Iowa and Indiana have also
been used for cross-state testing, and the tool has run on macOS and
Windows.

## Main Features

-   Initializes geographic analysis units from an existing district
    plan.
-   Selects one or multiple Census Blocks (Ctrl on Windows; Command on
    macOS).
-   Reassigns selected Census Blocks among active districts.
-   Supports multi-level Undo.
-   Refreshes district colors and restores selection using **Update
    Map**.
-   Calculates current and ideal district population from Census Block
    counts.
-   Displays population deviation in people and percentages.
-   Evaluates compactness and contiguity, including reassignment
    warnings.
-   Displays optional COI values and percentages, including
    area-weighted estimates for multiple blocks.
-   Updates district-number and current-population labels.
-   Exports a district-level GeoPackage plan.

## Layer Architecture

The editor has **three user-selected layers**, plus an initialized
output created by the Processing Tool.

### 1. Existing Districts Layer

Baseline congressional district polygons with a district identifier such
as `CD118FP`. This layer hosts dynamic district labels showing district
number and current population. The displayed population is recalculated
from the current Census Block assignments, rather than read from the
baseline polygons.

### 2. COI Analysis Layer

Census Block Group polygons with demographic and socioeconomic
attributes, such as `white`, `black`, `asian`, `poverty_total`,
`below_50pct_poverty`, `50_99pct_poverty`, `median_household_income`,
`median_earnings`, `civilian_labour_force`, and `unemployed`.

This layer supports **COI analysis only**, not district population
totals. One selected block is associated with a Block Group through its
representative location; multiple selected blocks use area-weighted
estimates from intersecting Block Groups. Available fields depend on the
user's data.

### 3. Census Blocks Layer

The interactive editing units. Prepare each block with a unique
identifier, a district identifier corresponding to the Existing
Districts layer (such as `CD118FP`), and a numeric population field
(such as `POP20`). The layer supports selection, reassignment,
population totals, deviation, boundary reconstruction, compactness,
contiguity, and export.

**Exact Census Block population is the source of district population
calculations.** Demographic attributes do not need to be joined to every
block.

### 4. Initialized Processing Output (Internal)

The Processing Tool creates an initialized analysis layer, retaining
input attributes and adding `original_dist` (original district
assignment) and `user_dist` (working district assignment). The editor
uses this output internally, including to identify the district
configuration. It is **not a fourth layer dropdown** and should not be
confused with the COI Analysis Layer.

## Main Python Components

-   **`redistricting_data_initialization.py`:** QGIS Processing script. Accepts
    analysis geography, Existing Districts, district ID field, and
    population field; creates the initialized output and launches the
    editor.
-   **`redistricting_editor.py`:** Plugin/controller responsible for
    opening and managing the editor.
-   **`redistricting_editor_dialog.py`:** Interactive layer loading,
    selection, reassignment, Undo, population and geographic statistics,
    COI, symbology, labels, and export.

## Required Data and Preparation

1.  **Existing Districts:** baseline district polygons and a district
    identifier.
2.  **COI Analysis / Block Groups:** polygon geography with optional
    numeric demographic and socioeconomic fields and appropriate
    denominators where percentage calculations are needed.
3.  **Census Blocks:** polygons with a block ID, joined existing
    district identifier, and numeric block population such as `POP20`.

### Preparing the COI Analysis Layer

Provide demographic variables of interest and, when percentages are
needed, appropriate denominator fields. For example, race counts may use
the corresponding total population, poverty counts may use
`poverty_total`, and unemployment may use `civilian_labour_force`.
Median household income and median earnings are not counts and must not
be treated as percentages of total population.

### Preparing Census Blocks and Spatial Join Considerations

Spatially associate each Census Block with its baseline congressional
district. During Ohio testing, **Have Their Center In** produced NULL
district identifiers for some blocks; **INTERSECT** produced no NULL
district identifiers in the tested output, but can match multiple
districts along shared boundaries. A one-to-one join may therefore
assign an ambiguous boundary block to an unintended district. Review
such assignments when preparing data. Reassigning a block in the editor
changes district membership but does not repair overlapping source
geometries.

# Installation

Install both the complete **Redistricting Editor plugin folder** and the
**Processing Tool Python script**. Paths assume the QGIS `default`
profile.

## Windows

**Plugin folder:**

``` text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\redistricting_editor\
```

Press **Windows + R** and enter:

``` text
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins
```

Copy the **complete** `redistricting_editor` folder there.

**Processing script (`redistricting_data_initialization.py`):**

``` text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\
```

Quick access:

``` text
%APPDATA%\QGIS\QGIS3\profiles\default\processing\scripts
```

Create `scripts` inside `processing` if it does not exist.

## macOS

**Plugin folder:**

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/redistricting_editor/
```

In Finder press **Command + Shift + G**, enter the parent
`python/plugins/` directory, and copy the complete plugin folder.

**Processing script (`redistricting_data_initialization.py`):**

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/processing/scripts/
```

Use **Command + Shift + G** to open the location. Create the `scripts`
directory if necessary.

## After Installing

Restart QGIS. Enable the Redistricting Editor in the plugin interface if
necessary and locate the Processing script in the Processing Toolbox.
Keep all plugin support files together; do not install only one Python
file from the plugin folder.

# Running the Tool

## 1. Run the Processing Tool

Supply:

-   **Input Geographic Unit Layer:** prepared analysis geography, such
    as Census Block Groups.
-   **Existing Districts Layer:** baseline congressional district
    polygons.
-   **District ID Field:** such as `CD118FP`.
-   **Population Field:** numeric total-population field required for
    initialization.

The script creates the initialized output with `original_dist` and
`user_dist`, then launches the editor. **The initialization population
field does not replace Census Block population for interactive district
calculations.**

## 2. Load the Editor

Choose **Existing Districts Layer**, **COI Analysis Layer**, and
**Census Blocks Layer**; click **Load Layer**. The editor initializes
district information, colors blocks by district, and prepares selection.

## 3. Select and Reassign Blocks

Click one Census Block to select it. Use **Ctrl** (Windows) or
**Command** (macOS) to select multiple blocks. The interface displays
selection count, block/district information, and the exact population of
the selected block or sum of selected blocks. Choose a destination
active district and click **Reassign**. The tool does not create new
districts.

## 4. Undo

**Undo** reverses the latest reassignment. One Undo reverses a
multi-block reassignment as a group. Multiple actions can be undone in
sequence.

## 5. Update Map

**Update Map** refreshes district symbology based on effective
assignments and restores the custom selection tool after using QGIS Pan
or Zoom.

# District Statistics

## District Population

District population is the sum of `POP20` (or the configured block
population field) for all Census Blocks currently assigned to that
district:

``` text
District Population = Sum of assigned Census Block populations
```

Moving a block removes its population from the previous district and
adds it to the destination district. **Block Group area weighting is not
used for district population totals.**

## Ideal Population

``` text
Ideal Population = Total Census Block Population / Number of Active Districts
```

A ±1% reference range is displayed for project visualization; it is not
a legal determination.

## Population Deviation

``` text
Deviation in People = District Population - Ideal Population
Deviation (%) = (District Population - Ideal Population) / Ideal Population × 100
```

Positive deviations are above ideal; negative deviations are below
ideal.

## Compactness

The tool uses the Polsby--Popper measure:

``` text
Compactness = 4 × π × Area / Perimeter²
```

Higher values generally indicate greater compactness under this measure.
Compactness is not a standalone legal conclusion.

## Contiguity

The tool evaluates whether the effective district's assigned Census
Blocks are connected under its implemented geometry-based test. **Yes**
indicates connected; **No** indicates disconnected. The editor can warn
about contiguity during reassignment. Results reflect the implemented
algorithm, not a legal determination.

# Communities of Interest (COI) Analysis

COI analysis is optional demographic context, **not an automatic
identification or legal classification of a Community of Interest**.
Enable COI Analysis, select a numeric COI variable, and select one or
more Census Blocks.

## Single Census Block

For one block, the editor identifies the associated Block Group using
the block's representative location and displays the selected **Block
Group Value**. Where a suitable denominator exists, it displays **Block
Group (%)**.

Example:

``` text
Selected Census Block Population: 28
COI Variable: white
Block Group Value: 1,651
Block Group (%): 98.7%
```

The block population describes the individual Census Block; the
demographic count and percentage describe its **Block Group**, not the
individual block.

``` text
Block Group (%) = Demographic Value / Appropriate Block Group Denominator × 100
```

If no appropriate denominator exists, the percentage may show `N/A`.

## Multiple Census Blocks

For multiple selected blocks, the editor combines selected block
geometries, intersects them with Block Groups, and estimates demographic
counts by area-weighted allocation:

``` text
Overlap Ratio = Selected Geometry ∩ Block Group Area / Full Block Group Area
Allocated Count = Block Group Demographic Count × Overlap Ratio
Estimated Selected-Area Count = Sum of Allocated Counts
```

The implementation projects areas to **EPSG:6933**, an equal-area
coordinate reference system, for these calculations. For supported count
variables, it also estimates the relevant denominator and calculates:

``` text
Estimated COI (%) = Area-Weighted Demographic Count / Area-Weighted Denominator × 100
```

This assumes the demographic attribute is uniformly distributed across
each Block Group. **These are estimates, not exact demographic counts
for selected blocks.** Exact block population remains separate.

## Supported Variables and Interpretation

  -----------------------------------------------------------------------------
  Variable type           Example                     Appropriate denominator
                                                      or treatment
  ----------------------- --------------------------- -------------------------
  Race                    `white`, `black`, `asian`   Corresponding total
                                                      population

  Poverty                 `below_50pct_poverty`,      `poverty_total`
                          `50_99pct_poverty`          

  Employment              `unemployed`                `civilian_labour_force`

  Income                  `median_household_income`   Not a count-based
                                                      percentage

  Earnings                `median_earnings`           Not a count-based
                                                      percentage
  -----------------------------------------------------------------------------

Other numeric variables may display a value but `N/A` for percentage.
Non-additive measures such as medians may also display `N/A` for
multiple-block area-weighted totals. The demographic information is
intended for exploration alongside geographic, historical, social, and
community context.

# Dynamic District Labels

The Existing Districts layer displays district number and current
population. These labels update after reassignment using **exact Census
Block population totals**. District colors are displayed on the Census
Blocks layer.

# Saving a Redistricting Plan

Click **Save Redistricting Plan** to export the effective plan as a
district-level **GeoPackage**. The editor reconstructs district
boundaries from the current block assignments and includes district
identifier, population, and deviation information, with district
symbology and labels applied to the saved layer.

# Moving Data Between Windows and macOS

**GeoPackage (`.gpkg`)** is recommended for portability and to avoid
shapefile field-name limitations. For example:

``` text
Political_Redistricting_Project/
├── data/
│   ├── Existing_Districts.gpkg
│   ├── BlockGroups_Demographics.gpkg
│   └── CensusBlocks_Districts.gpkg
├── output/
└── project/
```

Copy the actual datasets, not shortcuts. Data files should remain
outside the plugin installation directory.

# Tested Workflow

-   **Ohio:** primary development and testing dataset; selection,
    reassignment, multi-selection, population, deviation, compactness,
    contiguity, labels, COI, Undo, map updates, and export.
-   **Iowa:** earlier independently prepared cross-state dataset used to
    evaluate the workflow with a different district configuration and
    demographic fields.
-   **Indiana:** additional cross-state testing; core workflow operated,
    with some minor irregular or overlapping boundary areas remaining
    selectable for reassignment.
-   **Operating systems:** QGIS on macOS and Windows.

The tool is designed for use with different state datasets, but
successful testing in these states does **not** establish validation for
all 50 states.

# Performance Design

The editor uses spatial indexes, cached district geometries, cached
population totals, cached contiguity results, and district-based
calculations to reduce repeated spatial operations. Performance depends
on dataset size, geometry complexity, hardware, and the operation being
performed.

# Troubleshooting

-   **Plugin missing:** check the complete folder is installed in
    `python/plugins`, restart QGIS, and enable the plugin.
-   **Processing Tool missing:** check `redistricting_tool.py` is in
    `processing/scripts` and restart QGIS.
-   **Reassignment fails or looks incorrect:** confirm Census Blocks
    contain the appropriate district identifier matching the Existing
    Districts layer.
-   **District population missing or incorrect:** check the Census Block
    numeric population field (for example, `POP20`) and district
    assignments.
-   **COI missing:** check that the COI Analysis Layer covers selected
    blocks and contains valid numeric demographic attributes.
-   **COI percentage `N/A`:** the variable may lack an appropriate
    denominator or percentage interpretation.
-   **White gaps:** inspect NULL/unmatched district identifiers,
    geometry coverage, boundary inconsistencies, and renderer coverage.
-   **Spatial join NULLs:** center-based matching may leave unmatched
    blocks; intersection matching may yield ambiguous boundary
    assignments.
-   **Selection stops after Pan/Zoom:** click **Update Map** to restore
    the custom selection tool.

# Workflow Summary

``` text
Prepare Existing Districts
       +
Prepare Census Block Groups with COI demographics
       +
Prepare Census Blocks with district ID and POP20
       ↓
Run Political Redistricting Processing Tool
       ↓
Create Initialized Output
       ↓
Launch Redistricting Editor
       ↓
Load Existing Districts + COI Analysis + Census Blocks
       ↓
Select Census Block(s)
       ↓
Review exact Block Population and optional COI context
       ↓
Reassign / Undo / Update Map
       ↓
Review Population, Deviation, Compactness,
Contiguity, and Dynamic Labels
       ↓
Save Redistricting Plan
```

# Limitations and Future Improvements

## Spatial Join and Boundary Alignment

Ohio testing found that center-based spatial matching produced some NULL
district assignments, whereas `INTERSECT` matched all tested blocks but
could create ambiguous matches along district boundaries. Minor
irregularities were also observed during cross-state testing. Block
reassignment can correct district membership, but it does not repair
overlapping source geometries. Future versions could flag unmatched and
multiply matched blocks, validate boundaries, and provide targeted
geometry-repair or matching options.

## Expanded COI Calculations

A future version could recognize more demographic and socioeconomic
variable types, their appropriate denominators, and non-additive
measures such as rates and medians. This would extend meaningful derived
calculations beyond currently supported counts.

## Neighbor-Constrained Reassignment

A future enhancement could identify or restrict destination districts
based on adjacency to the selected blocks, updating candidate neighbors
dynamically as boundaries change. The current editor allows assignment
among active districts and evaluates contiguity through its existing
checks.

## Cross-State Validation and Performance

Additional states, especially those with complex coastlines,
disconnected areas, or unusual source geometry, could be tested. Larger
datasets could benefit from further rendering and geometry-processing
optimization.

# Project Scope

The Political Redistricting Tool is a GIS decision-support and
educational capstone prototype. It supports interactive geographic
editing, population analysis, demographic context, district evaluation,
and plan export. It does not determine legal compliance or make
political or electoral recommendations.

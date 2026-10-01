# Political Redistricting Tool

**Author:** Godiva Martha Nakayima\
**Project:** Master's GIS Capstone, The Ohio State University

## Overview

The Political Redistricting Tool is an interactive QGIS decision-support
system for initializing, editing, evaluating, and exporting political
district plans. It combines a QGIS Processing Tool with an interactive
QGIS plugin so a user can begin with an existing district plan, reassign
Census Blocks, and immediately review updated district statistics and
map displays.

The tool is designed to support exploration and evaluation. Statistics,
demographic information, and visual status indicators produced by the
tool are analytical aids and are not legal determinations.

The completed tool has been tested successfully with Ohio and Iowa data
and has run successfully in QGIS on both macOS and Windows.

## Main Features

-   Initializes geographic analysis units from an existing district
    plan.
-   Supports single and multiple Census Block selection.
-   Reassigns selected Census Blocks to another active district.
-   Provides multi-level Undo for reassignment actions.
-   Refreshes Census Block district symbology with **Update Map**.
-   Displays current district population and ideal population.
-   Reports population deviation as both a percentage and a number of
    people.
-   Calculates compactness.
-   Checks district contiguity.
-   Provides optional Communities of Interest (COI) demographic context.
-   Updates district labels with district number and current population.
-   Exports the current plan as a district-level GeoPackage layer.

## Three-Layer Architecture

### 1. Existing Districts Layer

The baseline district plan. It contains the original district polygons
and a district identifier such as `CD118FP`. It also hosts the live
district labels showing district number and current population.

### 2. Initialized / Analysis Layer

Created by the Processing Tool from an analysis geography containing
population and optional demographic attributes. Census Block Groups were
used for the capstone datasets.

The Processing Tool preserves the input attributes and adds:

-   `original_dist` --- original district assignment
-   `user_dist` --- working district assignment

Population and demographic variables used for statistics and COI
analysis originate from this analysis layer.

### 3. Census Blocks Layer

Census Blocks are the fine-scale interactive editing units. Before use,
they should contain the district identifier from the Existing Districts
layer, such as `CD118FP`.

The Census Block layer is intentionally separate from the demographic
analysis layer. Detailed demographic attributes do not need to be joined
to every Census Block.

## Main Python Components

### `redistricting_tool.py`

The QGIS Processing Tool. The user supplies the geographic analysis
units, Existing Districts, district ID field, and population field. It
creates the Initialized / Analysis Layer and launches the editor.

### `redistricting_editor.py`

Plugin/controller component responsible for loading and managing the
Redistricting Editor interface.

### `redistricting_editor_dialog.py`

Contains the principal interactive logic, including layer loading,
Census Block selection, reassignment, Undo, district statistics, COI
analysis, map updates, labeling, and plan export.

## Required Data

A test dataset should contain:

1.  **Existing district polygons** with a district identifier.
2.  **Census Block Groups or another analysis geography** containing a
    numeric total-population field and optional demographic variables.
3.  **Census Blocks** with the existing district identifier joined to
    them.

For the capstone workflow, Census Blocks provide interactive boundary
editing while Block Groups provide population and demographic analysis
information.

## Preparing the Analysis Layer

The Block Group layer should contain a numeric total-population field
before running the Processing Tool. Optional numeric demographic
attributes may also be included for COI analysis.

Example prepared fields include:

-   `total_population`
-   `white`
-   `black`
-   `others`
-   `poverty_population`
-   `poverty_percentage`

The exact demographic fields depend on the data supplied by the user.

## Preparing the Census Blocks

Spatially associate the Census Blocks with the Existing Districts before
loading them into the editor. The resulting Block layer should contain
the existing district identifier, such as `CD118FP`.

Only the district assignment is required for the redistricting workflow.
Population and demographic variables do not need to be copied from the
analysis layer onto the Census Blocks.

# Installation

The project contains two QGIS components that must be saved in the
appropriate QGIS user-profile folders:

1.  the **Redistricting Editor plugin folder**
2.  the **Processing Tool Python script**

The paths below assume the QGIS `default` profile.

## Windows Installation

### Redistricting Editor plugin

Save the complete plugin folder in:

``` text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS4\profiles\default\python\plugins\
```

The resulting path should resemble:

``` text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS4\profiles\default\python\plugins\redistricting_editor\
```

Quick access:

1.  Press **Windows + R**.
2.  Enter:

``` text
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins
```

3.  Press **Enter**.
4.  Copy the complete `redistricting_editor` folder into this directory.

### Processing Tool on Windows

Save `redistricting_tool.py` in:

``` text
C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\
```

Quick access:

``` text
%APPDATA%\QGIS\QGIS3\profiles\default\processing\scripts
```

If the `scripts` directory does not exist, create it inside the
`processing` directory.

## macOS Installation

### Redistricting Editor plugin

Save the complete plugin folder in:

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

The resulting path should resemble:

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/redistricting_editor/
```

To open the folder:

1.  Open **Finder**.
2.  Press **Command + Shift + G**.
3.  Enter:

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
```

4.  Press **Return**.
5.  Copy the complete `redistricting_editor` folder into this directory.

### Processing Tool on macOS

Save `redistricting_tool.py` in:

``` text
~/Library/Application Support/QGIS/QGIS3/profiles/default/processing/scripts/
```

Use **Command + Shift + G** in Finder and enter that path directly. If
the `scripts` directory does not exist, create it inside `processing`.

## After Installing

Restart QGIS after copying the files. Enable the Redistricting Editor
through the QGIS plugin interface if necessary. The Processing Tool
should appear in the Processing Toolbox after QGIS recognizes the
script.

Keep the plugin folder intact. Do not copy only one Python file into the
plugin directory; the plugin depends on its complete folder structure
and supporting files.

# Running the Tool

## Processing Tool

Run the Political Redistricting Processing Tool and provide:

-   **Input Geographic Unit Layer:** prepared analysis layer, such as
    Census Block Groups
-   **Existing Districts Layer:** baseline district polygons
-   **District ID Field:** district identifier, such as `CD118FP`
-   **Population Field:** numeric total-population field from the
    analysis layer

The Processing Tool creates the Initialized / Analysis Layer with
`original_dist` and `user_dist` and launches the Redistricting Editor.

## Loading the Editor

Select:

-   **Existing Districts Layer**
-   **Initialized / Analysis Layer**
-   **Census Blocks Layer**

Then click **Load Layer**.

## Selecting and Reassigning Census Blocks

Click a Census Block to select it. Multiple blocks can be selected using
**Ctrl** on Windows or **Command** on macOS.

The editor reports Block ID, current district, number of selected
blocks, and estimated Block Population.

Choose a destination district and click **Reassign**. All currently
selected blocks are reassigned together.

The tool does not create new districts; reassignment occurs among active
districts in the loaded plan.

## Undo

**Undo** reverses the most recent reassignment action. If multiple
blocks were reassigned in one action, one Undo restores the entire
group. Multiple actions can be undone sequentially.

## Update Map

**Update Map** refreshes Census Block symbology using the current
effective district assignments. It also restores the custom Census Block
selection tool after QGIS Pan or Zoom tools have been used.

# District Statistics

## Population

Population statistics are derived from the Initialized / Analysis Layer.

When an analysis unit overlaps a district or selected editing geometry,
the tool uses area-weighted allocation:

``` text
overlap ratio = intersection area / analysis-unit area
allocated population = analysis-unit population × overlap ratio
```

Allocated contributions are summed to estimate population for the
effective district geometry. This allows population stored at the Block
Group level to be allocated when current Census Block-based boundaries
divide an analysis unit.

## Ideal Population

``` text
Ideal Population = Total Population / Number of Active Districts
```

The interface also displays a ±1% range as a project
visualization/reference value. This display is not a legal
determination.

## Population Deviation

**Deviation (%)** reports the percentage difference between current
district population and ideal population.

**Deviation in People** is:

``` text
District Population - Ideal Population
```

Positive values indicate population above the ideal and negative values
indicate population below the ideal.

## Compactness

The tool calculates:

``` text
4 × π × Area / Perimeter²
```

Values closer to 1 are more compact under this measure. Compactness is
one analytical characteristic and is not a legal determination.

## Contiguity

The tool evaluates whether the effective district geometry remains
spatially connected after reassignment.

-   **Yes** --- evaluated as contiguous by the implemented geometry
    test.
-   **No** --- evaluated as disconnected.

This is an algorithmic status rather than a legal conclusion.

# Communities of Interest (COI) Analysis

The **Communities of Interest Analysis** section provides demographic
context for the area associated with a selected Census Block. It does
**not** automatically identify, classify, or define a Community of
Interest.

COI analysis is optional. It uses numeric demographic attributes
supplied with the Initialized / Analysis Block Group layer. The plugin
does not contain a built-in list of demographic groups and does not
require a separate Community of Interest shapefile.

Possible variables include race/ethnicity counts, poverty measures,
labor-force characteristics, or other numeric demographic variables
included in the user's analysis data.

## What Happens When COI Analysis Is Enabled

1.  Enable **COI Analysis**.
2.  Select a numeric demographic variable from **COI Variable**.
3.  Click a Census Block.
4.  The tool identifies the analysis Block Group associated with that
    Census Block.
5.  The interface displays the selected demographic quantity and, when
    an appropriate denominator is available, its percentage.

## Block Group Value

**Block Group Value** is the quantity recorded for the selected
demographic variable in the Block Group associated with the selected
Census Block.

For example:

``` text
COI Variable: black
Block Group Value: 350
```

This means the associated Block Group contains a value of 350 for the
selected Black-population variable.

It does **not** mean that the individual Census Block clicked on the map
contains 350 Black residents. The demographic value comes from the Block
Group analysis layer.

## Block Group (%)

**Block Group (%)** expresses the selected value as a percentage when
the tool can identify an appropriate denominator.

For example:

``` text
COI Variable: black
Block Group Value: 350
Block Group (%): 35.0%
```

If the relevant Block Group denominator is 1,000:

``` text
350 / 1,000 × 100 = 35.0%
```

The percentage therefore describes the selected demographic
characteristic in the associated **Block Group**, not necessarily in the
individual Census Block that was clicked.

If the tool cannot identify an appropriate denominator, the percentage
may display **N/A** rather than presenting an unsupported percentage.

## How to Interpret COI Information

The COI section is an exploratory demographic-context feature. It allows
a user to see the **quantity and, where supported, percentage** of a
selected demographic characteristic around the selected Census Block at
the Block Group analysis level.

The tool does not decide that a geographic area is or is not a Community
of Interest. The demographic information is available for the user to
consider alongside other relevant geographic or community information.

## Preparing COI Data

COI variables should be prepared on the Block Group analysis layer
before running the Processing Tool. The Processing Tool preserves those
numeric attributes when it creates the Initialized / Analysis Layer.

A secondary test dataset may use a simplified set of demographic
variables. The Iowa test, for example, used a smaller set of demographic
fields for demonstration. Other projects can supply different or
additional numeric variables.

## COI Variable Flexibility and Current Limitations

Users are free to include as many demographic attributes as appropriate
in the Block Group analysis layer. These attributes are preserved in the
Initialized / Analysis Layer and can provide additional demographic
context.

However, not every demographic variable is automatically compatible with
the current COI percentage calculation. The current implementation works
best with demographic count variables for which the tool can identify an
appropriate population-based denominator, including selected population
and race characteristics.

Other numeric variables may still provide a **Block Group Value**, while
**Block Group (%)** may display `N/A` when the tool cannot identify an
appropriate denominator. This does not mean that the underlying
demographic data are invalid. Different demographic and socioeconomic
variables can require different denominators or calculation methods.

# Dynamic District Labels

The Existing Districts layer displays labels containing the district
number and current district population. Population labels update to
reflect the effective Census Block assignments after reassignment.

# Saving a Redistricting Plan

Click **Save Redistricting Plan** to export the current effective plan.

The output is a district-level GeoPackage layer with one feature per
active district and includes district identifier, current population,
and population deviation. The saved layer receives district symbology,
boundaries, and population labels.

# Saving and Moving Data Between Windows and macOS

Project data can be stored anywhere QGIS can read it, including a local
project folder, external drive, or USB/thumb drive.

**GeoPackage (`.gpkg`) is recommended** for prepared layers and saved
plans because it works in QGIS on Windows and macOS and avoids shapefile
field-name limitations.

A portable data folder can be organized as:

``` text
Political_Redistricting_Project/
├── data/
│   ├── Existing_Districts.gpkg
│   ├── BlockGroups_Demographics.gpkg
│   └── CensusBlocks_Districts.gpkg
├── output/
└── project/
```

When using a thumb drive, copy the actual GeoPackage files rather than
shortcuts to files stored on the original computer.

The **data files do not belong inside the QGIS plugin directory**. Only
the plugin files and Processing script should be placed in the QGIS
profile paths described above.

# Tested Workflow

The completed workflow has been tested with:

-   Ohio as the primary development dataset.
-   Iowa as an independently prepared second-state dataset.
-   QGIS on macOS.
-   QGIS on Windows.

The Iowa test used the same three-layer architecture and successfully
completed the redistricting workflow.

# Performance Design

The editor uses spatial indexes, cached geometries, cached population
totals, cached contiguity results, and district-based calculations to
reduce repeated spatial operations.

The Initialized / Analysis Layer remains the source for population and
demographic analysis, while Census Blocks provide the fine-grained
editing geometry.

# Troubleshooting

**Plugin does not appear:** confirm that the complete plugin folder is
inside the correct `python/plugins` directory, restart QGIS, and confirm
that the plugin is enabled.

**Processing Tool does not appear:** confirm that
`redistricting_tool.py` is inside the profile's `processing/scripts`
directory and restart QGIS.

**Census Blocks cannot be reassigned correctly:** confirm that the
Census Blocks contain the existing district identifier corresponding to
the loaded Existing Districts layer.

**Population or COI information is missing:** confirm that the
Initialized / Analysis Layer was created from a layer containing a valid
numeric population field and the desired numeric demographic fields.

**COI percentage displays N/A:** the tool may not have identified an
appropriate denominator for the selected variable. The Block Group Value
may still be available.

**Selection stops after using Pan or Zoom:** click **Update Map** to
refresh the display and reactivate the custom Census Block selection
tool.

# Workflow Summary

``` text
Prepare Existing Districts
        +
Prepare Block Groups with Population / Demographics
        +
Prepare Census Blocks with Existing District ID
        ↓
Run Political Redistricting Processing Tool
        ↓
Create Initialized / Analysis Layer
        ↓
Launch Redistricting Editor
        ↓
Load Three Layers
        ↓
Select Census Block(s)
        ↓
Reassign / Undo / Update Map
        ↓
Review Population, Deviation, Compactness,
Contiguity, Labels, and optional COI context
        ↓
Save Redistricting Plan
```

# Future Improvements

The completed tool provides the core interactive redistricting workflow,
while several extensions could broaden its analytical and editing
capabilities.

## Expanded COI Calculations

A future version could expand the COI component so that it recognizes
additional demographic and socioeconomic variable types and
automatically identifies the appropriate denominator or calculation
method for each one. This would allow a wider range of user-supplied
variables to produce meaningful percentages or other derived measures
rather than limiting automatic calculations primarily to variables
compatible with the current population-based logic.

Users could therefore continue to prepare as many demographic attributes
as needed, while an expanded COI engine could determine how different
types of variables should be interpreted and calculated.

## Neighbor-Constrained Reassignment

A future enhancement could constrain the **New District** choices during
reassignment to districts that are spatially adjacent to the selected
Census Block or group of Census Blocks.

The current version allows reassignment among the active districts in
the loaded plan and then evaluates the resulting geometry, including
contiguity. A neighbor-aware reassignment option could provide
additional guidance before the reassignment occurs by limiting or
identifying destination districts that share a relevant boundary with
the selected editing units.

Implementing this dynamically would require adjacency to be reevaluated
as district boundaries change during an editing session, particularly
when multiple Census Blocks are selected. This is therefore identified
as a future interface and spatial-analysis enhancement rather than part
of the current implementation.

# Project Scope

The Political Redistricting Tool is a GIS decision-support and
educational capstone project. It provides interactive geographic and
demographic analysis capabilities for exploring district configurations.
It does not determine whether a plan complies with any particular legal
standard and does not make political or electoral recommendations.

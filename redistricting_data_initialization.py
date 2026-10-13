"""
***************************************************************************
*                                                                         *
*                Interactive Political Redistricting Tool                 *
*                                                                         *
***************************************************************************
"""

# Typing imports used by the Processing script.
from typing import Any, Optional

# QGIS Processing, feature, field, spatial index, feedback, and logging
# classes used to initialize the redistricting analysis layer.
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFeatureSink,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsSpatialIndex,
    Qgis,
    QgsMessageLog
)

# Qt classes used for field types, dock placement, and scheduling the
# Redistricting Editor to open after Processing has completed.
from qgis.PyQt.QtCore import QVariant, Qt, QTimer
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.utils import iface

# Import the main interactive Redistricting Editor.
# The Processing Tool prepares the analysis data first and then opens
# this editor so the user can continue with interactive redistricting.
from redistricting_editor.redistricting_editor_dialog import RedistrictingEditorDialog


# -------------------------------------------------------------------------
# Political Redistricting Processing Tool
# -------------------------------------------------------------------------
# This Processing algorithm initializes a geographic analysis-unit layer
# for use by the interactive Redistricting Editor.
#
# The tool:
# 1. Accepts geographic analysis units containing population/demographics.
# 2. Accepts the existing district boundary layer.
# 3. Determines the starting district for each analysis unit.
# 4. Creates original_dist and user_dist fields.
# 5. Preserves the original attributes and demographic information.
# 6. Produces the initialized analysis layer.
# 7. Opens the interactive Redistricting Editor after processing finishes.
class Redistricting(QgsProcessingAlgorithm):

    # Parameter names used internally by the QGIS Processing framework.
    input_units = "input_units"
    input_existing_districts = "input_existing_districts"
    input_district_id_field = "input_district_id_field"
    input_population_field = "input_population_field"
    output = "output"

    # original_dist stores the district assigned during initialization.
    # user_dist begins with the same value and provides the initialized
    # district field used by the redistricting workflow.
    original_assignment_field = "original_dist"
    assignment_field = "user_dist"

    # Initialize references to the dock and editor that may be opened after
    # the Processing algorithm finishes.
    def __init__(self):
        super().__init__()
        self.redistricting_dock = None
        self.redistricting_dialog = None

    # ---------------------------------------------------------------------
    # Processing Tool identification
    # ---------------------------------------------------------------------
    # Internal algorithm name used by QGIS Processing.
    def name(self):
        return "redistricting"

    # Human-readable name displayed in the Processing interface.
    def displayName(self):
        return "Redistricting Data Initialization"

    # Processing Toolbox group displayed to the user.
    def group(self):
        return "Redistricting"

    # Internal identifier for the Processing Toolbox group.
    def groupId(self):
        return "redistricting"

    # Short description displayed by QGIS for the Processing Tool.
    def shortDescription(self):
        return "Initializes census geographic units for interactive redistricting."

    # Provide the user with a longer explanation of the initialization
    # workflow and the layers needed by the interactive editor.
    def shortHelpString(self):
        return (
            "This tool prepares a geographic unit for interactive political redistricting. "
            "It uses an existing district boundary layer to assign each geographic unit an initial "
            "district value in new fields called original_dist and user_dist. "
            "After initialization is complete, the interactive redistricting interface opens. "
            "The user can then select the appropriate existing district, initialized analysis, "
            "and Census Block layers already available in QGIS."
        )

    # ---------------------------------------------------------------------
    # Processing Tool parameters
    # ---------------------------------------------------------------------
    # Define the layers, fields, and output that appear when the user opens
    # the Redistricting Tool from the QGIS Processing Toolbox.
    def initAlgorithm(self, config=None):

        # Analysis-unit polygon layer. In the current workflow this is the
        # demographic geographic layer that contains population and other
        # attributes used later by the Redistricting Editor.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.input_units,
                "Input geographic unit layer",
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

        # Existing district polygon layer representing the starting district
        # boundaries used to initialize district membership.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.input_existing_districts,
                "Existing district layer",
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

        # Allow the user to specify which field in the existing district
        # layer contains the district identifier.
        self.addParameter(
            QgsProcessingParameterField(
                self.input_district_id_field,
                "Existing district ID field",
                parentLayerParameterName=self.input_existing_districts,
                type=QgsProcessingParameterField.Any
            )
        )

        # Population field comes from the geographic analysis-unit layer.
        # The field is retained in the initialized output and is later used
        # by the interactive editor for population calculations.
        self.addParameter(
            QgsProcessingParameterField(
                self.input_population_field,
                "Population field",
                parentLayerParameterName=self.input_units,
                type=QgsProcessingParameterField.Numeric
            )
        )

        # Output initialized analysis layer. This preserves the input fields
        # and adds the original_dist and user_dist district fields.
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.output,
                "Output initialized geographic unit layer"
            )
        )

    # ---------------------------------------------------------------------
    # Initialize the redistricting analysis layer
    # ---------------------------------------------------------------------
    # This is the main Processing operation. Each geographic analysis unit
    # is assigned to an existing district using a representative point.
    # The input attributes are preserved and two district-assignment fields
    # are added to the output.
    def processAlgorithm(self, parameters, context, feedback):

        # Read the geographic analysis-unit layer selected by the user.
        units = self.parameterAsSource(
            parameters,
            self.input_units,
            context
        )

        # Read the existing district boundary layer selected by the user.
        existing_districts = self.parameterAsSource(
            parameters,
            self.input_existing_districts,
            context
        )

        # Stop processing if the analysis-unit source could not be loaded.
        if units is None:
            raise QgsProcessingException(
                self.invalidSourceError(
                    parameters,
                    self.input_units
                )
            )

        # Stop processing if the existing district source could not be loaded.
        if existing_districts is None:
            raise QgsProcessingException(
                self.invalidSourceError(
                    parameters,
                    self.input_existing_districts
                )
            )

        # Get the field containing the district identifier from the existing
        # district layer.
        district_id_field = self.parameterAsString(
            parameters,
            self.input_district_id_field,
            context
        )

        # Get the numeric population field from the geographic analysis layer.
        population_field = self.parameterAsString(
            parameters,
            self.input_population_field,
            context
        )

        # Copy all original analysis-unit fields so demographics and other
        # attributes are preserved in the initialized output.
        output_fields = QgsFields(units.fields())

        field_names = [
            field.name()
            for field in output_fields
        ]

        # Add original_dist when it does not already exist.
        # This records the district assigned during initialization.
        if self.original_assignment_field not in field_names:
            output_fields.append(
                QgsField(
                    self.original_assignment_field,
                    QVariant.Int
                )
            )

        # Add user_dist when it does not already exist.
        # It begins with the same district assignment as original_dist.
        if self.assignment_field not in field_names:
            output_fields.append(
                QgsField(
                    self.assignment_field,
                    QVariant.Int
                )
            )

        # Find the positions of the two district fields in the final
        # output field structure.
        original_assignment_index = output_fields.indexFromName(
            self.original_assignment_field
        )

        assignment_index = output_fields.indexFromName(
            self.assignment_field
        )

        # Create the Processing output using the same geometry type and CRS
        # as the input geographic analysis-unit layer.
        output_layer, output_id = self.parameterAsSink(
            parameters,
            self.output,
            context,
            output_fields,
            units.wkbType(),
            units.sourceCrs()
        )

        # Stop if QGIS cannot create the requested output layer.
        if output_layer is None:
            raise QgsProcessingException(
                self.invalidSinkError(
                    parameters,
                    self.output
                )
            )

        # -----------------------------------------------------------------
        # Existing district spatial index
        # -----------------------------------------------------------------
        # Build a spatial index once so each analysis unit does not have to
        # be compared with every district polygon.
        district_index = QgsSpatialIndex()

        # Keep a feature lookup by feature ID so candidate district features
        # returned by the spatial index can be retrieved immediately.
        district_features = {}

        for district in existing_districts.getFeatures():
            district_index.addFeature(district)
            district_features[district.id()] = QgsFeature(district)

        # Calculate the progress increment for each analysis unit.
        total = (
            100.0 / units.featureCount()
            if units.featureCount()
            else 0
        )

        # Track initialization results for the Processing feedback report.
        assigned_count = 0
        unassigned_count = 0
        total_population = 0

        # -----------------------------------------------------------------
        # Assign every geographic analysis unit to an existing district
        # -----------------------------------------------------------------
        for current, unit in enumerate(units.getFeatures()):

            # Respect the QGIS Processing cancel button.
            if feedback.isCanceled():
                break

            # Get the polygon geometry for the current analysis unit.
            geometry = unit.geometry()

            # Units without usable geometry cannot be spatially assigned.
            if geometry is None or geometry.isEmpty():
                unassigned_count += 1
                continue

            # Create a point located on the analysis-unit surface.
            # The district containing this representative point determines
            # the analysis unit's initial district assignment.
            representative_point = geometry.pointOnSurface()

            assigned_district = None

            # Use the district spatial index to find only district polygons
            # whose bounding boxes may contain the representative point.
            candidate_ids = district_index.intersects(
                representative_point.boundingBox()
            )

            # Test the candidate district polygons using the actual geometry,
            # rather than relying only on the bounding-box result.
            for candidate_id in candidate_ids:

                district = district_features[candidate_id]

                if district.geometry().contains(
                    representative_point
                ):
                    # Read the selected district ID and convert it to a
                    # consistent integer value before storing it.
                    assigned_district = self.clean_district_value(
                        district[district_id_field]
                    )
                    break

            # Track whether the analysis unit received a district assignment.
            if assigned_district is None:
                unassigned_count += 1
            else:
                assigned_count += 1

            # -----------------------------------------------------------------
            # Population total
            # -----------------------------------------------------------------
            # Population is read directly from the user-selected population
            # field on the geographic analysis-unit layer. Census Blocks are
            # not being used as the population source during initialization.
            population_value = unit[population_field]

            if population_value is not None:
                try:
                    total_population += float(
                        population_value
                    )
                except Exception:
                    pass

            # Create the output feature using the complete output field
            # structure, including original_dist and user_dist.
            output_feature = QgsFeature(
                output_fields
            )

            # Preserve the original geographic analysis-unit geometry.
            output_feature.setGeometry(
                geometry
            )

            # Begin with all attributes from the input analysis unit.
            # This preserves population, demographics, IDs, and other
            # existing fields in the initialized output.
            attributes = unit.attributes()

            # Store the starting district in original_dist.
            # If the field already existed in the input, replace its value;
            # otherwise append the new value to the attribute list.
            if self.original_assignment_field in field_names:
                attributes[
                    original_assignment_index
                ] = assigned_district
            else:
                attributes.append(
                    assigned_district
                )

            # Initialize user_dist with the same district value.
            if self.assignment_field in field_names:
                attributes[
                    assignment_index
                ] = assigned_district
            else:
                attributes.append(
                    assigned_district
                )

            output_feature.setAttributes(
                attributes
            )

            # Write the initialized feature to the Processing output.
            output_layer.addFeature(
                output_feature,
                QgsFeatureSink.Flag.FastInsert
            )

            # Update the QGIS Processing progress indicator.
            feedback.setProgress(
                int(current * total)
            )

        # -----------------------------------------------------------------
        # Processing summary
        # -----------------------------------------------------------------
        # Report the number of successfully assigned and unassigned units.
        feedback.pushInfo(
            f"Assigned units: {assigned_count}"
        )

        feedback.pushInfo(
            f"Unassigned units: {unassigned_count}"
        )

        # Report the population total calculated from the selected population
        # field of the analysis-unit layer.
        feedback.pushInfo(
            f"Total population from selected field: {total_population:,.0f}"
        )

        # Report the district fields created/used by the initialized layer.
        feedback.pushInfo(
            f"Original district field: {self.original_assignment_field}"
        )

        feedback.pushInfo(
            f"Editable district field: {self.assignment_field}"
        )

        # Write completion information to the QGIS Processing message log.
        QgsMessageLog.logMessage(
            "Redistricting initialization completed.",
            "Processing",
            level=Qgis.Info
        )

        # Return the initialized geographic analysis layer to QGIS.
        return {
            self.output: output_id
        }

    # ---------------------------------------------------------------------
    # Open the interactive editor after Processing
    # ---------------------------------------------------------------------
    # QGIS calls this after the main Processing operation is complete.
    # The editor is scheduled through Qt so it opens after Processing has
    # finished returning control to the QGIS interface.
    def postProcessAlgorithm(
        self,
        context,
        feedback
    ):

        QTimer.singleShot(
            0,
            self.open_redistricting_editor
        )

        return {}

    # ---------------------------------------------------------------------
    # Redistricting Editor dock
    # ---------------------------------------------------------------------
    # Open the interactive Redistricting Editor in the QGIS main window.
    # Before creating a new dock, search for an existing editor dock so
    # duplicate interfaces are not created.
    def open_redistricting_editor(self):

        # The editor requires access to the active QGIS interface.
        if iface is None:
            return

        main_window = iface.mainWindow()

        existing_dock = None

        # Search the current QGIS window for an already-open Redistricting
        # Editor dock by its visible window title.
        for dock in main_window.findChildren(QDockWidget):
            if dock.windowTitle() == "Redistricting Editor":
                existing_dock = dock
                break

        # If an editor already exists, show and raise that same dock instead
        # of creating another dialog.
        if existing_dock is not None:

            existing_dock.show()
            existing_dock.raise_()

            return

        # Create the main interactive Redistricting Editor dialog.
        self.redistricting_dialog = (
            RedistrictingEditorDialog()
        )

        # Place the dialog inside a QGIS dock widget.
        self.redistricting_dock = QDockWidget(
            "Redistricting Editor",
            main_window
        )

        self.redistricting_dock.setObjectName(
            "RedistrictingEditorDock"
        )

        self.redistricting_dock.setWidget(
            self.redistricting_dialog
        )

        # Add the dock to the right side of the QGIS interface.
        iface.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self.redistricting_dock
        )

        # Make the editor visible and bring it to the front.
        self.redistricting_dock.show()
        self.redistricting_dock.raise_()

    # ---------------------------------------------------------------------
    # District ID cleanup
    # ---------------------------------------------------------------------
    # Convert district identifiers to integer values before they are written
    # to original_dist and user_dist. Empty or unusable values return None.
    def clean_district_value(
        self,
        value
    ):

        if value is None:
            return None

        # Convert the source value to text and remove surrounding whitespace.
        text_value = str(
            value
        ).strip()

        if text_value == "":
            return None

        # First attempt a direct integer conversion.
        try:
            return int(
                text_value
            )
        except Exception:
            pass

        # If needed, remove leading zeros before attempting conversion again.
        try:
            return int(
                text_value.lstrip("0")
            )
        except Exception:
            return None

    # ---------------------------------------------------------------------
    # Processing algorithm instance
    # ---------------------------------------------------------------------
    # QGIS uses this method to create a new instance of the algorithm.
    def createInstance(self):
        return self.__class__()

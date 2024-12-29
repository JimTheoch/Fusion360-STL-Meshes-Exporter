import adsk.core, adsk.fusion, adsk.cam, traceback
import os
import time

def file_dialog(ui):
    """Display the dialog to pick a folder"""
    folderDlg = ui.createFolderDialog()
    folderDlg.title = 'Select Folder to Export'

    dlgResult = folderDlg.showDialog()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        return folderDlg.folder  # Return the folder path
    return False

def export_to_stl(folder_path, components, ui, progress_dialog):
    """Exports each component as an STL file with progress updates."""
    app = adsk.core.Application.get()
    design = app.activeProduct
    export_mgr = design.exportManager

    exported_files = []

    # Total number of components to be exported
    total_components = len(components)
    
    # Start exporting components one by one
    for i, component in enumerate(components):
        try:
            file_name = f"{component.name}.stl"
            full_path = os.path.join(folder_path, file_name)

            # Create the export options for STL
            stl_options = export_mgr.createSTLExportOptions(component)
            stl_options.isBinaryFormat = True  # Set binary STL format
            stl_options.filename = full_path

            # Export the component
            export_mgr.execute(stl_options)

            exported_files.append(file_name)

            # Update the progress bar after each export with minimal delay
            progress_value = int((i + 1) / total_components * 100)
            progress_dialog.progressValue = progress_value
            progress_dialog.message = f"Exporting {component.name}..."

            # Reduce sleep time to make the progress bar update quickly
            time.sleep(0.001)  # Allow the UI to refresh, but very little delay
        except Exception as e:
            ui.messageBox(f"Error exporting component {component.name}: {str(e)}")

    return exported_files

def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        ui.messageBox("Fusion360_STL_Exporter By Dimitris (Jim) Theocharopoulos")

        # Ensure we have an active design
        design = app.activeProduct
        if not design:
            ui.messageBox("No active design found.")
            return

        # Check root component
        root_comp = design.rootComponent

        # Fetch components directly under the root component or any top-level component
        components = [occ.component for occ in root_comp.occurrences]

        # If no components are directly under root, check if there's only a single standalone component (non-hierarchical)
        if not components:
            components = [root_comp]  # Fallback to just the root component if there are no subcomponents

        if components:
            components_list = "\n".join([comp.name for comp in components])
            message = f"Detected Root Component Name: {root_comp.name}\n\n" \
                      f"Fetched {len(components)} components, that are:\n\n" \
                      f"{components_list}\n\n" \
                      f"Do you want to continue?"

            dialog_result = ui.messageBox(
                message,
                "Root Component Detection and SubComps Check",
                adsk.core.MessageBoxButtonTypes.YesNoButtonType,
                adsk.core.MessageBoxIconTypes.InformationIconType
            )

            if dialog_result == adsk.core.DialogResults.DialogYes:
                while True:
                    selected_folder = file_dialog(ui)
                    if selected_folder:
                        folder_message = f"Folder selected: {selected_folder}\n\n" \
                                         f"Do you want to export said components as STL files?\n\n" \
                                         f"Press Cancel to reselect folder if needed."

                        choice = ui.messageBox(
                            folder_message,
                            "Export Confirmation",
                            adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType,
                            adsk.core.MessageBoxIconTypes.InformationIconType
                        )

                        if choice == adsk.core.DialogResults.DialogYes:
                            # Display "please wait" message
                            progress_dialog = ui.createProgressDialog()
                            progress_dialog.isBackgroundTranslucent = False
                            progress_dialog.show("Exporting Components", "Please wait while components are being exported.", 0, 100, 0)

                            try:
                                exported_files = export_to_stl(selected_folder, components, ui, progress_dialog)
                            finally:
                                progress_dialog.hide()  # Hide the progress dialog once done

                            if exported_files:
                                export_summary = "\n".join(exported_files)
                                # Modified final message to include destination
                                ui.messageBox(f"Export Completed at {selected_folder}.\n\nFiles exported:\n\n{export_summary}")
                            else:
                                ui.messageBox("No files were exported.")
                            break
                        elif choice == adsk.core.DialogResults.DialogNo:
                            ui.messageBox("User aborted the process. Bye Bye!")
                            break
                        elif choice == adsk.core.DialogResults.DialogCancel:
                            continue
                    else:
                        ui.messageBox("No folder selected. Script ending.")
                        break
            else:
                ui.messageBox("User aborted the process. Bye Bye!")
        else:
            ui.messageBox("No components found/unsaved components :(")

    except Exception as e:
        ui.messageBox(f"Error: {str(e)}")

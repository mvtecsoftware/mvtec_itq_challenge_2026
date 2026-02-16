"""
Simple example of using HALCON HDevEngine with Python.

This script shows how to:
1. Load and execute a full HDevelop program (.hdev)
2. Call a local procedure from a HDevelop program
3. Pass input images and retrieve output results
4. Print the results

You can adapt this script to your own HALCON programs and procedures.
"""

import halcon as ha
import os

# -------------------------------
# CONFIGURATION (relative paths)
# -------------------------------

# Assume HDevelop programs and images are in the same folder as this script
BASE_PATH = os.path.dirname(__file__)

# Example HDevelop program and procedure
HDEV_PROGRAM_FILE = os.path.join(BASE_PATH, 'python_hdevengine_example.hdev')
HDEV_PROCEDURE_NAME = 'process_apples'

# Example image to process
IMAGE_FILE = os.path.join(BASE_PATH, 'Fotolia_45332982_S.jpg')


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def call_full_program():
    """
    Load and execute a full HDevelop program (.hdev)
    Returns: iconic and control output variables
    """
    program = ha.HDevProgram(HDEV_PROGRAM_FILE)
    program_call = ha.HDevProgramCall(program)
    program_call.execute()

    # Retrieve outputs (iconic images and control variables)
    region_closing = program_call.get_iconic_var_by_name('RegionClosing')
    area = program_call.get_control_var_by_name('Area')
    row = program_call.get_control_var_by_name('Row')
    column = program_call.get_control_var_by_name('Column')

    return region_closing, area, row, column


def call_local_procedure():
    """
    Call a specific procedure from a HDevelop program
    Returns: iconic and control output variables
    """
    program = ha.HDevProgram(HDEV_PROGRAM_FILE)
    procedure = ha.HDevProcedure.load_local(program, HDEV_PROCEDURE_NAME)

    # Read input image
    img = ha.read_image(IMAGE_FILE)

    # Prepare a procedure call
    proc_call = ha.HDevProcedureCall(procedure)
    proc_call.set_input_iconic_param_by_name('Image', img)
    proc_call.execute()

    # Retrieve outputs
    region_closing = proc_call.get_output_iconic_param_by_name('RegionClosing')
    area = proc_call.get_output_control_param_by_name('Area')
    row = proc_call.get_output_control_param_by_name('Row')
    column = proc_call.get_output_control_param_by_name('Column')

    return region_closing, area, row, column


# -------------------------------
# MAIN SCRIPT
# -------------------------------

if __name__ == '__main__':

    # Start the HALCON HDevEngine
    engine = ha.HDevEngine()
    
    # Set path where procedures are stored
    engine.set_procedure_path(BASE_PATH)
    
    # Optional: start the debug server
    engine.set_attribute('debug_port', 7786)
    engine.start_debug_server()

    # -------------------------------
    # Example 1: Call the full HDevelop program
    # -------------------------------
    print("=== Calling full HDevelop program ===")
    region_closing, area, row, column = call_full_program()
    print("Number of apples detected:", len(area))
    print("Pixel areas of apples:", area)
    print("Center rows of apples:", row)
    print("Center columns of apples:", column)
    print()

    # -------------------------------
    # Example 2: Call a specific procedure
    # -------------------------------
    print("=== Calling local procedure ===")
    region_closing, area, row, column = call_local_procedure()
    print("Number of apples detected:", len(area))
    print("Pixel areas of apples:", area)
    print("Center rows of apples:", row)
    print("Center columns of apples:", column)

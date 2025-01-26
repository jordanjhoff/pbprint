import os
import cups

def send_print_job(file) -> bool:
    try:
        conn = cups.Connection()
        printer_name = "Dai_Nippon_Printing_DS-RX1"
        conn.printFile(printer_name, file, "Print Job", {})
        print("Connected")
        return True
    except Exception as e:
        print(f"FAILED TO SEND JOB TO PRINTER: {e}")
        return False

# Define the output directory
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

if __name__ == "__main__":
    # Construct the output file path
    output = os.path.join(output_dir, "final_photo.png")

    # Debugging: Print paths
    print(f"Output directory: {output_dir}")
    print(f"Output file path: {output}")

    # Check if the file exists
    if not os.path.isfile(output):
        print(f"Error: File not found at path {output}")
    else:
        # Send the file to the printer
        send_print_job(output)

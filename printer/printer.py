import os
import subprocess

import cups

def send_print_job(file) -> bool:
    try:
        conn = cups.Connection()
        printer_name = "Dai_Nippon_Printing_DS-RX1"
        conn.printFile(printer_name, file, "Print Job", {})
        print("Connected")
        return True
    except Exception as e:
        clear_cups_queue()
        print(f"FAILED TO SEND JOB TO PRINTER: {e}")
        return False


def clear_cups_queue():
    try:
        subprocess.run(["cancel", "-a"], check=True)
        print("CUPS queue cleared.")
    except subprocess.CalledProcessError as e:
        print(f"Error clearing CUPS queue: {e}")

output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

if __name__ == "__main__":
    output = os.path.join(output_dir, "final_photo.png")

    print(f"Output directory: {output_dir}")
    print(f"Output file path: {output}")

    if not os.path.isfile(output):
        print(f"Error: File not found at path {output}")
    else:
        send_print_job(output)

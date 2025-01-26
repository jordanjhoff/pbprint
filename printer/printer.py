import cups


def send_print_job(file) -> bool:
    try:
        conn = cups.Connection()

        printer_name = "Dai_Nippon_Printing_DS_RX1"
        conn.printFile(printer_name, file, "Print Job", {})
        return True
    except Exception as e:
        print(f"FAILED TO SEND JOB TO PRINTER: {e}")
        return False
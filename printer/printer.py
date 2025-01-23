import cups


def send_print_job(file):

    conn = cups.Connection()

    printer_name = "Dai_Nippon_Printing_DS_RX1"
    conn.printFile(printer_name, file, "Print Job", {})
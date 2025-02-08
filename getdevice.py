import subprocess

def get_device_id(device_name):
    try:
        result = subprocess.run(['xinput'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            print(line)
            if device_name in line:
                print(line)
                parts = line.split()
                for part in parts:
                    print(part)
                    if "id=" in part:
                        return part.split('=')[1]
        
        print(f"Device '{device_name}' not found.")
        return None
    except Exception as e:
        print(f"Error finding device ID: {e}")
        return None

def map_device_to_output(device_id, output_name):
    try:
        subprocess.run(['xinput', 'map-to-output', device_id, output_name], check=True)
        print(f"Mapped device ID {device_id} to output {output_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to map device: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


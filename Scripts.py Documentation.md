{"id":16202,"uuid":"8f6b80a7-3a43-46ca-81fe-5e28207ec352","user_id":11451,"filename":"scripts.py","source":"Multiple","generated":"# \ud83c\udf1f Scripts.py Documentation \ud83c\udf1f\n\nWelcome to the detailed documentation for `scripts.py`! This file is a Flask-based web application used to manage Virtual Machines (VMs) via **Libvirt** and **QEMU\/KVM**. Here's a comprehensive guide to understanding and using this script.\n\n## \ud83d\udccb Index\n\n1. [Overview](#overview)\n2. [Installation](#installation)\n3. [API Endpoints](#api-endpoints)\n    - [Create VM](#create-vm)\n    - [Modify VM](#modify-vm)\n    - [Unmount ISO](#unmount-iso)\n    - [List VMs](#list-vms)\n    - [Delete VM](#delete-vm)\n    - [Start VM](#start-vm)\n    - [Stop VM](#stop-vm)\n    - [Export VM](#export-vm)\n    - [Export Compressed VM](#export-compressed-vm)\n    - [Import VM](#import-vm)\n    - [Import Compressed VM](#import-compressed-vm)\n4. [Helper Functions](#helper-functions)\n\n## \ud83c\udf10 Overview <a name=\"overview\"><\/a>\n\nThis script provides a REST API for managing VMs on a Linux host using Libvirt and QEMU\/KVM. The primary functionalities include creating, modifying, starting, stopping, deleting, exporting, and importing VMs.\n\n## \ud83d\ude80 Installation <a name=\"installation\"><\/a>\n\nTo use this script, you'll need to set up a Flask environment with the necessary dependencies:\n\n```bash\n# Clone the repository\ngit clone <repository-url>\n\n# Navigate to the project directory\ncd <project-directory>\n\n# Create a virtual environment\npython3 -m venv venv\n\n# Activate the virtual environment\nsource venv\/bin\/activate\n\n# Install the required packages\npip install -r requirements.txt\n```\n\nMake sure you have `libvirt`, `qemu`, and `wget` installed on your system. You can install them using:\n\n```bash\nsudo apt-get install libvirt-bin qemu-kvm wget\n```\n\n## \ud83d\udce2 API Endpoints <a name=\"api-endpoints\"><\/a>\n\n### \u2795 Create VM <a name=\"create-vm\"><\/a>\n\n**Endpoint:** `\/vms`  \n**Method:** `POST`  \n**Description:** Creates a new VM with given specifications.\n\n**Request Body:**\n```json\n{\n    \"name\": \"vm-name\",\n    \"iso_url\": \"http:\/\/example.com\/path\/to\/iso\",\n    \"disk_size_gb\": 30,\n    \"memory_mb\": 4096,\n    \"vcpu_count\": 2\n}\n```\n\n**Response:**\n- `202 VM creation started`: VM creation has been initiated.\n- `500 Failed to download ISO`: Error in downloading the ISO file.\n\n### \u270f\ufe0f Modify VM <a name=\"modify-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/modify`  \n**Method:** `POST`  \n**Description:** Modifies the configuration of an existing VM.\n\n**Request Body:**\n```json\n{\n    \"memory_mb\": 8192,\n    \"vcpu_count\": 4,\n    \"disk_size_gb\": 50,\n    \"new_name\": \"new-vm-name\"\n}\n```\n\n**Response:**\n- `200 VM modified successfully`: VM has been modified.\n- `404 VM not found`: VM does not exist.\n- `400 VM must be stopped before modification`: VM must be stopped to modify its configuration.\n\n### \ud83d\udcbf Unmount ISO <a name=\"unmount-iso\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/unmount_iso`  \n**Method:** `POST`  \n**Description:** Unmounts the ISO from the VM's CDROM drive.\n\n**Response:**\n- `200 ISO unmounted and VM configuration updated`: ISO has been unmounted.\n- `404 VM not found`: VM does not exist.\n- `400 No CDROM device found`: No CDROM device to unmount.\n\n### \ud83d\udcdc List VMs <a name=\"list-vms\"><\/a>\n\n**Endpoint:** `\/vms`  \n**Method:** `GET`  \n**Description:** Returns a list of all VMs with their IDs, names, and states.\n\n**Response:**\n```json\n[\n    {\n        \"id\": 1,\n        \"name\": \"vm1\",\n        \"state\": 1\n    },\n    {\n        \"id\": 2,\n        \"name\": \"vm2\",\n        \"state\": 3\n    }\n]\n```\n\n### \u274c Delete VM <a name=\"delete-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>`  \n**Method:** `DELETE`  \n**Description:** Deletes an existing VM.\n\n**Response:**\n- `204 VM deleted`: VM has been deleted.\n- `404 VM not found`: VM does not exist.\n\n### \u25b6\ufe0f Start VM <a name=\"start-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/start`  \n**Method:** `POST`  \n**Description:** Starts an existing VM.\n\n**Response:**\n- `200 VM started`: VM has been started.\n- `404 VM not found`: VM does not exist.\n- `404 Disk image not found`: Disk image does not exist.\n\n### \u23f9\ufe0f Stop VM <a name=\"stop-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/stop`  \n**Method:** `POST`  \n**Description:** Stops a running VM.\n\n**Response:**\n- `200 VM stopped`: VM has been stopped.\n- `404 VM not found`: VM does not exist.\n\n### \ud83d\udce6 Export VM <a name=\"export-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/export`  \n**Method:** `GET`  \n**Description:** Exports a VM's configuration and disk image to a tar file on the user's desktop.\n\n**Response:**\n- `200 VM exported to <path>`: VM has been exported.\n- `404 VM not found`: VM does not exist.\n- `400 VM must be stopped before export`: VM must be stopped to export.\n- `404 Disk image not found`: Disk image does not exist.\n\n### \ud83d\udce6 Export Compressed VM <a name=\"export-compressed-vm\"><\/a>\n\n**Endpoint:** `\/vms\/<vm_name>\/exportCompressed`  \n**Method:** `GET`  \n**Description:** Exports a VM's configuration and disk image to a tar.gz file on the user's desktop.\n\n**Response:**\n- `200 VM exported to <path>`: VM has been exported.\n- `404 VM not found`: VM does not exist.\n- `400 VM must be stopped before export`: VM must be stopped to export.\n- `404 Disk image not found`: Disk image does not exist.\n\n### \u2b06\ufe0f Import VM <a name=\"import-vm\"><\/a>\n\n**Endpoint:** `\/vms\/import`  \n**Method:** `POST`  \n**Description:** Imports a VM from a tar file.\n\n**Request Example:**\n```bash\ncurl -X POST -F \"file=@\/path\/to\/vm.tar\" http:\/\/localhost:5000\/vms\/import\n```\n\n**Response:**\n- `200 VM <name> imported successfully`: VM has been imported.\n- `400 No file part`: No file provided.\n- `400 No selected file`: No file selected.\n- `404 Desktop directory not found`: Desktop directory not found.\n- `500 Failed to extract tar file`: Error in extracting tar file.\n- `500 Failed to define VM`: Error in defining VM.\n\n### \u2b06\ufe0f Import Compressed VM <a name=\"import-compressed-vm\"><\/a>\n\n**Endpoint:** `\/vms\/importCompressed`  \n**Method:** `POST`  \n**Description:** Imports a VM from a tar.gz file.\n\n**Request Example:**\n```bash\ncurl -X POST -F \"file=@\/path\/to\/vm.tar.gz\" http:\/\/localhost:5000\/vms\/importCompressed\n```\n\n**Response:**\n- `200 VM <name> imported successfully`: VM has been imported.\n- `400 No file part`: No file provided.\n- `400 No selected file`: No file selected.\n- `404 Desktop directory not found`: Desktop directory not found.\n- `500 Failed to extract tar.gz file`: Error in extracting tar.gz file.\n- `500 Failed to define VM`: Error in defining VM.\n\n## \u2699\ufe0f Helper Functions <a name=\"helper-functions\"><\/a>\n\n### `connect_libvirt()`\nConnects to the **Libvirt** service and returns a connection object.\n\n### `ensure_iso_exists(iso_url, iso_path)`\nChecks if an ISO file exists at the specified path; if not, downloads it from the given URL.\n\n### `create_disk_image(disk_path, disk_size_gb)`\nCreates a new disk image of the specified size using `qemu-img`.\n\n### `generate_vm_xml(vm_name, disk_path, iso_path, memory_mb, vcpu_count)`\nGenerates the XML configuration for a VM.\n\n### `create_vm_in_background(vm_name, config_xml)`\nDefines and starts a VM in a background thread.\n\n## \ud83d\ude80 Running the Application\n\nTo start the Flask application, run the following command:\n\n```bash\npython scripts.py\n```\n\nThe application will be accessible at `http:\/\/localhost:5000`.\n\n## \ud83d\udcdd Example Usage\n\nTo create a new VM, you can use the following `cURL` command:\n\n```bash\ncurl -X POST -H \"Content-Type: application\/json\" -d '{\n    \"name\": \"test-vm\",\n    \"iso_url\": \"http:\/\/example.com\/path\/to\/iso\",\n    \"disk_size_gb\": 30,\n    \"memory_mb\": 4096,\n    \"vcpu_count\": 2\n}' http:\/\/localhost:5000\/vms\n```\n\n## \u2728 Conclusion\n\nThis documentation covers the primary functionalities of the `scripts.py` file, providing a REST API for managing VMs using Libvirt and QEMU\/KVM. Feel free to explore the endpoints and customize the script to suit your needs!\n\nHappy VM managing! \ud83d\ude80","created_at":"2024-07-02T05:24:28.000000Z","updated_at":"2024-07-02T05:24:28.000000Z","deleted_at":null,"model_type":1,"generation_type":0,"generation_from":0,"tag":null,"archived":0}
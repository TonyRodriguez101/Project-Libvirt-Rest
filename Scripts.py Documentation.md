# 🌟 Scripts.py Documentation 🌟

Welcome to the detailed documentation for `scripts.py`! This file is a Flask-based web application used to manage Virtual Machines (VMs) via **Libvirt** and **QEMU/KVM**. Here's a comprehensive guide to understanding and using this script.

## 📋 Index

1. [Overview](#overview)
2. [Installation](#installation)
3. [API Endpoints](#api-endpoints)
    - [Create VM](#create-vm)
    - [Modify VM](#modify-vm)
    - [Unmount ISO](#unmount-iso)
    - [List VMs](#list-vms)
    - [Delete VM](#delete-vm)
    - [Start VM](#start-vm)
    - [Stop VM](#stop-vm)
    - [Export VM](#export-vm)
    - [Export Compressed VM](#export-compressed-vm)
    - [Import VM](#import-vm)
    - [Import Compressed VM](#import-compressed-vm)
4. [Helper Functions](#helper-functions)

## 🌐 Overview <a name="overview"></a>

This script provides a REST API for managing VMs on a Linux host using Libvirt and QEMU/KVM. The primary functionalities include creating, modifying, starting, stopping, deleting, exporting, and importing VMs.

## 🚀 Installation <a name="installation"></a>

To use this script, you'll need to set up a Flask environment with the necessary dependencies:

```bash
# Clone the repository
git clone https://github.com/TonyRodriguez101/Project-Libvirt-Rest.git

# Navigate to the project directory
cd <project-directory>

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

Make sure you have `libvirt`, `qemu`, and `wget` installed on your system. You can install them using:

```bash
sudo apt-get install libvirt-bin qemu-kvm wget
```

## 📢 API Endpoints <a name="api-endpoints"></a>

### ➕ Create VM <a name="create-vm"></a>

**Endpoint:** `/vms`  
**Method:** `POST`  
**Description:** Creates a new VM with given specifications.

**Request Body:**
```json
{
    "name": "vm-name",
    "iso_url": "http://example.com/path/to/iso",
    "disk_size_gb": 30,
    "memory_mb": 4096,
    "vcpu_count": 2
}
```

**Response:**
- `202 VM creation started`: VM creation has been initiated.
- `500 Failed to download ISO`: Error in downloading the ISO file.

### ✏️ Modify VM <a name="modify-vm"></a>

**Endpoint:** `/vms/<vm_name>/modify`  
**Method:** `POST`  
**Description:** Modifies the configuration of an existing VM.

**Request Body:**
```json
{
    "memory_mb": 8192,
    "vcpu_count": 4,
    "disk_size_gb": 50,
    "new_name": "new-vm-name"
}
```

**Response:**
- `200 VM modified successfully`: VM has been modified.
- `404 VM not found`: VM does not exist.
- `400 VM must be stopped before modification`: VM must be stopped to modify its configuration.

### 💿 Unmount ISO <a name="unmount-iso"></a>

**Endpoint:** `/vms/<vm_name>/unmount_iso`  
**Method:** `POST`  
**Description:** Unmounts the ISO from the VM's CDROM drive.

**Response:**
- `200 ISO unmounted and VM configuration updated`: ISO has been unmounted.
- `404 VM not found`: VM does not exist.
- `400 No CDROM device found`: No CDROM device to unmount.

### 📜 List VMs <a name="list-vms"></a>

**Endpoint:** `/vms`  
**Method:** `GET`  
**Description:** Returns a list of all VMs with their IDs, names, and states.

**Response:**
```json
[
    {
        "id": 1,
        "name": "vm1",
        "state": 1
    },
    {
        "id": 2,
        "name": "vm2",
        "state": 3
    }
]
```

### ❌ Delete VM <a name="delete-vm"></a>

**Endpoint:** `/vms/<vm_name>`  
**Method:** `DELETE`  
**Description:** Deletes an existing VM.

**Response:**
- `204 VM deleted`: VM has been deleted.
- `404 VM not found`: VM does not exist.

### ▶️ Start VM <a name="start-vm"></a>

**Endpoint:** `/vms/<vm_name>/start`  
**Method:** `POST`  
**Description:** Starts an existing VM.

**Response:**
- `200 VM started`: VM has been started.
- `404 VM not found`: VM does not exist.
- `404 Disk image not found`: Disk image does not exist.

### ⏹️ Stop VM <a name="stop-vm"></a>

**Endpoint:** `/vms/<vm_name>/stop`  
**Method:** `POST`  
**Description:** Stops a running VM.

**Response:**
- `200 VM stopped`: VM has been stopped.
- `404 VM not found`: VM does not exist.

### 📦 Export VM <a name="export-vm"></a>

**Endpoint:** `/vms/<vm_name>/export`  
**Method:** `GET`  
**Description:** Exports a VM's configuration and disk image to a tar file on the user's desktop.

**Response:**
- `200 VM exported to <path>`: VM has been exported.
- `404 VM not found`: VM does not exist.
- `400 VM must be stopped before export`: VM must be stopped to export.
- `404 Disk image not found`: Disk image does not exist.

### 📦 Export Compressed VM <a name="export-compressed-vm"></a>

**Endpoint:** `/vms/<vm_name>/exportCompressed`  
**Method:** `GET`  
**Description:** Exports a VM's configuration and disk image to a tar.gz file on the user's desktop.

**Response:**
- `200 VM exported to <path>`: VM has been exported.
- `404 VM not found`: VM does not exist.
- `400 VM must be stopped before export`: VM must be stopped to export.
- `404 Disk image not found`: Disk image does not exist.

### ⬆️ Import VM <a name="import-vm"></a>

**Endpoint:** `/vms/import`  
**Method:** `POST`  
**Description:** Imports a VM from a tar file.

**Request Example:**
```bash
curl -X POST -F "file=@/path/to/vm.tar" http://localhost:5000/vms/import
```

**Response:**
- `200 VM <name> imported successfully`: VM has been imported.
- `400 No file part`: No file provided.
- `400 No selected file`: No file selected.
- `404 Desktop directory not found`: Desktop directory not found.
- `500 Failed to extract tar file`: Error in extracting tar file.
- `500 Failed to define VM`: Error in defining VM.

### ⬆️ Import Compressed VM <a name="import-compressed-vm"></a>

**Endpoint:** `/vms/importCompressed`  
**Method:** `POST`  
**Description:** Imports a VM from a tar.gz file.

**Request Example:**
```bash
curl -X POST -F "file=@/path/to/vm.tar.gz" http://localhost:5000/vms/importCompressed
```

**Response:**
- `200 VM <name> imported successfully`: VM has been imported.
- `400 No file part`: No file provided.
- `400 No selected file`: No file selected.
- `404 Desktop directory not found`: Desktop directory not found.
- `500 Failed to extract tar.gz file`: Error in extracting tar.gz file.
- `500 Failed to define VM`: Error in defining VM.

## ⚙️ Helper Functions <a name="helper-functions"></a>

### `connect_libvirt()`
Connects to the **Libvirt** service and returns a connection object.

### `ensure_iso_exists(iso_url, iso_path)`
Checks if an ISO file exists at the specified path; if not, downloads it from the given URL.

### `create_disk_image(disk_path, disk_size_gb)`
Creates a new disk image of the specified size using `qemu-img`.

### `generate_vm_xml(vm_name, disk_path, iso_path, memory_mb, vcpu_count)`
Generates the XML configuration for a VM.

### `create_vm_in_background(vm_name, config_xml)`
Defines and starts a VM in a background thread.

## 🚀 Running the Application

To start the Flask application, run the following command:

```bash
python scripts.py
```

The application will be accessible at `http://localhost:5000`.

## 📝 Example Usage

To create a new VM, you can use the following `cURL` command:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "test-vm",
    "iso_url": "http://example.com/path/to/iso",
    "disk_size_gb": 30,
    "memory_mb": 4096,
    "vcpu_count": 2
}' http://localhost:5000/vms
```

## ✨ Conclusion

This documentation covers the primary functionalities of the `scripts.py` file, providing a REST API for managing VMs using Libvirt and QEMU/KVM. Feel free to explore the endpoints and customize the script to suit your needs!

Happy VM managing! 🚀

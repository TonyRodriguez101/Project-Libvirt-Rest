# Virtual Machine Management API Documentation 📚🚀

## Table of Contents
1. [Introduction](#introduction)
2. [Setup](#setup)
3. [API Endpoints](#api-endpoints)
   1. [Create VM](#create-vm)
   2. [Modify VM](#modify-vm)
   3. [Unmount ISO](#unmount-iso)
   4. [List VMs](#list-vms)
   5. [Delete VM](#delete-vm)
   6. [Start VM](#start-vm)
   7. [Stop VM](#stop-vm)
   8. [Export VM](#export-vm)
   9. [Export Compressed VM](#export-compressed-vm)
   10. [Import VM](#import-vm)
   11. [Import Compressed VM](#import-compressed-vm)
4. [Utility Functions](#utility-functions)
5. [Conclusion](#conclusion)

---

## Introduction

Welcome to the **Virtual Machine Management API** documentation! This document provides a comprehensive guide to using the API for managing virtual machines using **libvirt** and **Flask**. This API allows you to create, modify, start, stop, export, and import virtual machines (VMs) easily.

## Setup

To set up this API, please ensure you have the following requirements installed:

- Python 3.x
- Flask
- libvirt
- qemu-img
- wget
- virt-viewer

**Installation:**
```bash
pip install flask libvirt-python
```

## API Endpoints

### 1. Create VM

**Endpoint:** `/vms`  
**Method:** `POST`  
**Description:** Creates a new VM.

#### Request Body Parameters:
- `name` (optional): Name of the VM.
- `iso_url` (required): URL of the ISO image.
- `disk_size_gb` (optional): Size of the disk in GB (default: 30).
- `memory_mb` (optional): Memory in MB (default: 4096).
- `vcpu_count` (optional): Number of VCPUs (default: 2).

#### Example Request:
```json
{
    "name": "test-vm",
    "iso_url": "http://example.com/path/to/iso",
    "disk_size_gb": 40,
    "memory_mb": 8192,
    "vcpu_count": 4
}
```

**Response:**
- `202`: VM creation started.
- `500`: Failed to download ISO.

### 2. Modify VM

**Endpoint:** `/vms/<vm_name>/modify`  
**Method:** `POST`  
**Description:** Modifies the configuration of an existing VM.

#### Request Body Parameters:
- `memory_mb` (optional): New memory size in MB.
- `vcpu_count` (optional): New number of VCPUs.
- `disk_size_gb` (optional): New disk size in GB.
- `new_name` (optional): New name for the VM.

#### Example Request:
```json
{
    "memory_mb": 16384,
    "vcpu_count": 8,
    "disk_size_gb": 60,
    "new_name": "new-vm-name"
}
```

**Response:**
- `200`: VM modified successfully.
- `400`: VM must be stopped before modification.
- `404`: VM not found.
- `500`: Failed to modify VM configuration.

### 3. Unmount ISO

**Endpoint:** `/vms/<vm_name>/unmount_iso`  
**Method:** `POST`  
**Description:** Unmounts the ISO image from the specified VM.

**Response:**
- `200`: ISO unmounted and VM configuration updated.
- `400`: No CDROM device found.
- `404`: VM not found.

### 4. List VMs

**Endpoint:** `/vms`  
**Method:** `GET`  
**Description:** Lists all VMs along with their IDs, names, and states.

**Response:** JSON array of VMs.

#### Example Response:
```json
[
    {
        "id": 1,
        "name": "vm-123",
        "state": 1
    },
    {
        "id": 2,
        "name": "vm-456",
        "state": 3
    }
]
```

### 5. Delete VM

**Endpoint:** `/vms/<vm_name>`  
**Method:** `DELETE`  
**Description:** Deletes the specified VM and its associated disk image.

**Response:**
- `204`: VM deleted.
- `404`: VM not found.

### 6. Start VM

**Endpoint:** `/vms/<vm_name>/start`  
**Method:** `POST`  
**Description:** Starts the specified VM.

**Response:**
- `200`: VM started.
- `404`: VM or disk image not found.
- `400`: Failed to start VM.

### 7. Stop VM

**Endpoint:** `/vms/<vm_name>/stop`  
**Method:** `POST`  
**Description:** Stops the specified VM.

**Response:**
- `200`: VM stopped.
- `404`: VM not found.
- `400`: Failed to stop VM.

### 8. Export VM

**Endpoint:** `/vms/<vm_name>/export`  
**Method:** `GET`  
**Description:** Exports the specified VM to the user's desktop as a tar file.

**Response:**
- `200`: VM exported.
- `404`: VM or disk image not found.
- `400`: VM must be stopped before export.

### 9. Export Compressed VM

**Endpoint:** `/vms/<vm_name>/exportCompressed`  
**Method:** `GET`  
**Description:** Exports the specified VM to the user's desktop as a compressed tar.gz file.

**Response:**
- `200`: VM exported.
- `404`: VM or disk image not found.
- `400`: VM must be stopped before export.

### 10. Import VM

**Endpoint:** `/vms/import`  
**Method:** `POST`  
**Description:** Imports a VM from a tar file.

**Request Form Data:**
- `file` (required): The tar file containing the VM's configuration and disk image.

**Response:**
- `200`: VM imported successfully.
- `400`: No file part or invalid tar file contents.
- `500`: Failed to define VM or extract tar file.

### 11. Import Compressed VM

**Endpoint:** `/vms/importCompressed`  
**Method:** `POST`  
**Description:** Imports a VM from a compressed tar.gz file.

**Request Form Data:**
- `file` (required): The tar.gz file containing the VM's configuration and disk image.

**Response:**
- `200`: VM imported successfully.
- `400`: No file part or invalid tar.gz file contents.
- `500`: Failed to define VM or extract tar.gz file.

## Utility Functions

### `connect_libvirt()`

**Description:** Establishes a connection to the libvirt daemon.

**Returns:** libvirt connection object.

### `ensure_iso_exists(iso_url, iso_path)`

**Description:** Checks if the ISO exists at the specified path, and downloads it if necessary.

### `create_disk_image(disk_path, disk_size_gb)`

**Description:** Creates a disk image with the specified size.

### `generate_vm_xml(vm_name, disk_path, iso_path, memory_mb, vcpu_count)`

**Description:** Generates the XML configuration for the VM.

### `create_vm_in_background(vm_name, config_xml)`

**Description:** Creates the VM in the background using a separate thread.

## Conclusion

The **Virtual Machine Management API** provides a powerful and convenient way to manage virtual machines using HTTP requests. By following this documentation, you should be able to easily create, modify, start, stop, export, and import VMs. Happy VM managing! 🎉

**Note:** Always ensure you have appropriate permissions and configurations set up in your environment to avoid any issues during VM management.

---

If you encounter any issues or have questions, feel free to reach out!

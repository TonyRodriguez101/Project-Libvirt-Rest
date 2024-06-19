from flask import Flask, request, jsonify
import libvirt
import os
import requests
import uuid
import threading

app = Flask(__name__)

def connect_libvirt():
    return libvirt.open('qemu:///system')

def ensure_iso_exists(iso_url, iso_path):
    if not os.path.exists(iso_path):
        try:
            response = requests.get(iso_url, stream=True)
            response.raise_for_status()
            with open(iso_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f'ISO downloaded successfully: {iso_path}')
            return True
        except requests.RequestException as e:
            print(f'Failed to download ISO: {e}')
            return False
    else:
        print(f'ISO already exists: {iso_path}')
    return True

ISO_URL = 'https://mirror.leitecastro.com/ubuntu-releases/22.04.4/ubuntu-22.04.4-desktop-amd64.iso'
ISO_PATH = '/var/lib/libvirt/images/ubuntu-22.04.4-desktop-amd64.iso'

def create_disk_image(disk_path, size_gb):
    os.system(f'qemu-img create -f qcow2 {disk_path} {size_gb}G')

def generate_vm_xml(vm_name, disk_path, iso_path=ISO_PATH):
    return f"""
    <domain type='kvm'>
      <name>{vm_name}</name>
      <memory unit='KiB'>4194304</memory>
      <vcpu placement='static'>3</vcpu>
      <os>
        <type arch='x86_64' machine='pc-i440fx-2.9'>hvm</type>
        <boot dev='cdrom'/>
      </os>
      <devices>
        <disk type='file' device='disk'>
          <driver name='qemu' type='qcow2'/>
          <source file='{disk_path}'/>
          <target dev='vda' bus='virtio'/>
        </disk>
        <disk type='file' device='cdrom'>
          <driver name='qemu' type='raw'/>
          <source file='{iso_path}'/>
          <target dev='hdc' bus='ide'/>
          <readonly/>
        </disk>
        <interface type='network'>
          <mac address='52:54:00:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}:{uuid.uuid4().hex[:2]}'/>
          <source network='default'/>
          <model type='virtio'/>
        </interface>
        <graphics type='vnc' port='-1' autoport='yes'/>
      </devices>
    </domain>
    """

def create_vm_in_background(vm_name, disk_path, config_xml):
    conn = connect_libvirt()
    try:
        dom = conn.defineXML(config_xml)  # Define the VM in libvirt
        dom.create()  # Start the VM
        print(f'VM {vm_name} created successfully')
        conn.close()
    except libvirt.libvirtError as e:
        print(f'Failed to create VM {vm_name}: {str(e)}')
        conn.close()

@app.route('/vms', methods=['POST'])
def create_vm():
    vm_name = request.json.get('name', f'vm-{uuid.uuid4()}')
    disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'

    # Ensure ISO exists
    if not ensure_iso_exists(ISO_URL, ISO_PATH):
        return 'Failed to download ISO', 500

    # Create a new disk image
    create_disk_image(disk_path, 30)  # Create a 30GB disk image

    # Generate VM XML configuration
    config_xml = generate_vm_xml(vm_name, disk_path)

    # Run VM creation in a background thread
    threading.Thread(target=create_vm_in_background, args=(vm_name, disk_path, config_xml)).start()

    return 'VM creation started', 202

#-------------------------------------------------
# UnMount ISO and change boot configuration
@app.route('/vms/<vm_name>/unmount_iso', methods=['POST'])
def unmount_iso(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if not domain:
        conn.close()
        return 'VM not found', 404

    # Get the current XML configuration
    current_xml = domain.XMLDesc(0)

    # Modify the boot device to the disk and remove the ISO source
    new_xml = current_xml.replace(f"<source file='{ISO_PATH}'/>", "<source file=''/>").replace("<boot dev='cdrom'/>", "<boot dev='hd'/>")

    try:
        # Update the VM configuration
        domain.undefine()
        conn.defineXML(new_xml)
        conn.close()
        return 'ISO unmounted and boot configuration changed', 200
    except libvirt.libvirtError as e:
        conn.close()
        return f'Failed to update VM configuration: {str(e)}', 400

#-------------------------------------------------
# List VMs
@app.route('/vms', methods=['GET'])
def list_vms():
    conn = connect_libvirt()
    domains = conn.listAllDomains()
    vms = []
    for domain in domains:
        vms.append({
            'id': domain.ID(),
            'name': domain.name(),
            'state': domain.state()[0]
        })
    conn.close()
    return jsonify(vms)

#-------------------------------------------------
# Delete VM
@app.route('/vms/<vm_name>', methods=['DELETE'])
def delete_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        if domain.isActive():
            domain.destroy()
        domain.undefine()
        conn.close()
        # Optionally delete the disk file
        disk_path = f'/var/lib/libvirt/images/{vm_name}.qcow2'
        if os.path.exists(disk_path):
            os.remove(disk_path)
        return 'VM deleted', 204
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Start VM
@app.route('/vms/<vm_name>/start', methods=['POST'])
def start_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        domain.create()
        conn.close()
        return 'VM started', 200
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Stop VM definitively (power off)
@app.route('/vms/<vm_name>/stop', methods=['POST'])
def stop_vm(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        try:
            domain.destroy()
            conn.close()
            return 'VM stopped', 200
        except libvirt.libvirtError as e:
            conn.close()
            return f'Failed to stop VM: {str(e)}', 500
    else:
        conn.close()
        return 'VM not found', 404

#-------------------------------------------------
# Extraction of VM XML data configuration
@app.route('/vms/<vm_name>/xml', methods=['GET'])
def get_vm_xml(vm_name):
    conn = connect_libvirt()
    domain = conn.lookupByName(vm_name)
    if domain:
        xml = domain.XMLDesc(0)
        conn.close()
        return xml, 200
    else:
        conn.close()
        return 'VM not found', 404

if __name__ == '__main__':
    app.run(debug=True)
